from pathlib import Path
import os
import re
import string
from functools import wraps
import sys
from typing import Callable, Optional, get_type_hints, Union, _GenericAlias
import socket

from palworld_save_studio.utils import LOGGER

from flask import jsonify

def reply(status, data=None, msg=None):
    return jsonify({"status": status, "data": data, "msg": zh_message(msg) if status != 0 else msg})


# ---------------------------------------------------------------- 错误文案中文化
_MESSAGE_MAP = {
    "BackupEnabled must be a boolean.": "BackupEnabled 必须是布尔值。",
    "CharacterID is not an editable Palworld 1.0 species.": "该物种不是可编辑的 Palworld 1.0 物种。",
    "Choose an owner before duplicating this object.": "复制前请先选择归属玩家。",
    "Dedicated-server backups cannot be disabled.": "专用服务器模式的备份不能关闭。",
    "Enabled must be a boolean.": "Enabled 必须是布尔值。",
    "OwnerPlayerUId is invalid.": "所属玩家 ID 无效。",
    "Permission denied while opening this directory.": "没有权限打开该目录。",
    "SaveKind must be 'local' or 'dedicated'.": "存档类型必须是 local 或 dedicated。",
    "The directory could not be opened.": "无法打开该目录。",
    "The in-memory draft could not be discarded.": "无法丢弃内存中的草稿。",
    "The item operation could not be completed.": "物品操作未能完成。",
    "The offline item catalog could not be loaded.": "离线物品目录加载失败。",
    "The owner's Palbox has no free slot.": "归属玩家的帕鲁箱子已满。",
    "The Pal could not be updated.": "帕鲁更新失败。",
    "The path does not exist or the network location is unavailable.": "路径不存在，或网络位置不可用。",
    "The path must be an absolute directory.": "路径必须是绝对目录。",
    "The player could not be updated.": "玩家更新失败。",
    "The player's item inventory could not be loaded.": "玩家背包加载失败。",
    "The save could not be committed.": "存档写入失败。",
    "The save could not be validated.": "存档校验未通过，未写入任何文件。",
    "The selected player's Palbox has no free slot.": "所选玩家的帕鲁箱子已满。",
    "This object has no recoverable owner.": "该对象没有可恢复的归属玩家。",
}

_MESSAGE_PATTERNS = (
    (r"^Pal (.+) was not found\.$", r"找不到帕鲁：\1"),
    (r"^Pal (.+) could not be deleted\.$", r"帕鲁删除失败：\1"),
    (r"^Player (.+) was not found\.$", r"找不到玩家：\1"),
    (r"^Technology (.+) is unknown\.$", r"未知科技：\1"),
    (r"^I18n code (.+) not available\.$", r"不支持的语言代码：\1"),
    (r"^No Palworld save was found at: (.+)$", r"未在该路径找到帕鲁存档：\1（需要包含 Level.sav 的文件夹）"),
)


def zh_message(msg):
    """把后端英文错误信息转成中文；未命中则原样返回。"""
    if not msg or not isinstance(msg, str):
        return msg
    mapped = _MESSAGE_MAP.get(msg)
    if mapped:
        return mapped
    for pattern, repl in _MESSAGE_PATTERNS:
        if re.match(pattern, msg):
            return re.sub(pattern, repl, msg)
    return msg


def _windows_drive_candidates() -> list[str]:
    list_drives = getattr(os, "listdrives", None)
    if callable(list_drives):
        return list(list_drives())
    return [f"{letter}:\\" for letter in string.ascii_uppercase]


def get_path_roots() -> list[str]:
    if os.name != "nt":
        return [str(Path(Path.cwd().anchor or os.sep).resolve())]

    roots: list[str] = []
    for root in _windows_drive_candidates():
        try:
            if os.path.isdir(root):
                roots.append(root)
        except OSError:
            continue
    return roots


def get_path_context(path: Path) -> dict:
    current_path = path.expanduser().resolve(strict=True)
    if not current_path.is_dir():
        raise NotADirectoryError(str(current_path))

    entries: list[tuple[Path, bool]] = []
    for child in current_path.iterdir():
        try:
            is_directory = child.is_dir()
        except OSError:
            is_directory = False
        entries.append((child, is_directory))
    entries.sort(key=lambda item: (not item[1], item[0].name.casefold()))

    children = {
        str(child.resolve()): {
            "filename": child.name,
            "isDir": is_directory,
        }
        for child, is_directory in entries
    }

    names = [child.name for child, _ in entries]
    is_pal_dir = "Level.sav" in names and "Players" in names

    return {
        "currentPath": str(current_path),
        "roots": get_path_roots(),
        "children": children,
        "isPalDir": is_pal_dir
    }


def alphanumeric_key(key: str):
    """Converts a string into a list of integer and string fragments for sorting."""
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanumeric_list = [convert(c) for c in re.split("([0-9]+)", key)]
    return alphanumeric_list


def clamp(min_value: int, max_value: int, val: int) -> int:
    return max(min_value, min(max_value, val))


def is_union_type(hint):
    import types
    return isinstance(hint, types.UnionType)


def is_instance(obj, hint):
    if is_union_type(hint):
        return any(is_instance(obj, sub_hint) for sub_hint in getattr(hint, '__args__', []))
    else:
        return isinstance(obj, hint)


def convert_type(value, to_type):
    if is_union_type(to_type):
        for sub_type in getattr(to_type, '__args__', []):
            try:
                return sub_type(value)
            except (ValueError, TypeError):
                continue
        raise TypeError(f"Cannot convert value '{value}' to any of {to_type}")
    else:
        try:
            return to_type(value)
        except (ValueError, TypeError) as e:
            raise TypeError(f"Cannot convert value '{value}' of type {type(value).__name__} to {to_type.__name__}") from e


def type_guard(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        hints = get_type_hints(func)
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        all_args = dict(zip(arg_names, args))
        all_args.update(kwargs)

        for arg_name, arg_value in all_args.items():
            hint = hints.get(arg_name)
            if hint and not is_instance(arg_value, hint):
                try:
                    all_args[arg_name] = convert_type(arg_value, hint)
                except TypeError as e:
                    LOGGER.warning(f"Argument '{arg_name}' of {func.__name__} expected {hint}, got {type(arg_value).__name__}. Error: {e}")
                    raise e  # Raise the error instead of returning TypeError
        return func(**all_args)

    return wrapper


def check_or_generate_port(preferred_port: int, host: str='127.0.0.1') -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, preferred_port))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return preferred_port
        except socket.error:
            pass

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = s.getsockname()[1]
        return port
