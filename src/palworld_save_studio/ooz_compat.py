"""用系统自带的 oo2core DLL 提供 Oodle 压缩 / 解压。

背景：
    pip 上的 `pyooz` 0.0.8 只导出了 `decompress`，没有 `compress`。
    palworld-save-tools 的 `oozlib.compress()` 会调用 `ooz.compress(...)`，
    因此任何「保存」动作都会抛 AttributeError，表现为
    "The save could not be validated"。

    这里在导入 palworld_save_tools 之前注册一个同名的 `ooz` 模块，
    用本机其他 Unreal 游戏附带的 oo2core_*_win64.dll 完成压缩，
    不随本项目分发任何 Oodle 二进制。

可通过环境变量 PALFORGE_OODLE 指定 DLL 路径。
"""
from __future__ import annotations

import ctypes
import os
import sys
import types
from ctypes import c_int, c_ssize_t, c_void_p
from pathlib import Path
from typing import Optional

# 官方 OodleLZ_Compressor 编号
KRAKEN = 8
MERMAID = 10
SELKIE = 11
LEVIATHAN = 9

# OodleLZ_CompressionLevel
LEVEL_NORMAL = 4

_DLL_NAME = "oo2core_8_win64.dll"

_FALLBACK_PATHS = (
    r"C:\Program Files\Epic Games\Fortnite\FortniteGame\Binaries\Win64\oo2core_8_win64.dll",
    r"C:\Program Files (x86)\Steam\steamapps\common\Palworld\Pal\Binaries\Win64\oo2core_9_win64.dll",
)


def _candidate_roots() -> list[str]:
    """按盘符生成常见游戏库目录，避免把某台机器的路径写死。"""
    import string

    roots: list[str] = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if not os.path.isdir(drive):
            continue
        for relative in (
            r"SteamLibrary\steamapps\common",
            r"steam\steamapps\common",
            r"Steam\steamapps\common",
            r"Program Files (x86)\Steam\steamapps\common",
            r"Program Files\Steam\steamapps\common",
            r"Program Files\Epic Games",
            r"Program Files (x86)\Epic Games",
            r"WeGameApps\rail_apps",
            r"Games",
        ):
            candidate = os.path.join(drive, relative)
            if os.path.isdir(candidate):
                roots.append(candidate)
    return roots


def _scan_roots(max_depth: int = 6) -> Optional[str]:
    for root in _candidate_roots():
        base_depth = root.rstrip("\\/").count(os.sep)
        for dirpath, dirnames, filenames in os.walk(root):
            if dirpath.count(os.sep) - base_depth >= max_depth:
                dirnames[:] = []
                continue
            for name in filenames:
                if name.lower().startswith("oo2core") and name.lower().endswith(".dll"):
                    return os.path.join(dirpath, name)
    return None


def find_oodle_dll() -> Optional[str]:
    env = os.environ.get("PALFORGE_OODLE")
    if env and os.path.isfile(env):
        return env
    for path in _FALLBACK_PATHS:
        if os.path.isfile(path):
            return path
    return _scan_roots()


class _OodleRuntime:
    def __init__(self, dll_path: str) -> None:
        self.dll_path = dll_path
        self._lib = ctypes.WinDLL(dll_path)

        decompress = self._lib.OodleLZ_Decompress
        decompress.argtypes = [
            c_void_p, c_ssize_t, c_void_p, c_ssize_t,
            c_int, c_int, c_int, c_void_p, c_ssize_t,
            c_void_p, c_void_p, c_void_p, c_ssize_t, c_int,
        ]
        decompress.restype = c_ssize_t
        self._decompress = decompress

        compress = self._lib.OodleLZ_Compress
        compress.argtypes = [
            c_int, c_void_p, c_ssize_t, c_void_p,
            c_int, c_void_p, c_void_p, c_void_p, c_void_p, c_ssize_t,
        ]
        compress.restype = c_ssize_t
        self._compress = compress

    def decompress_bytes(self, data: bytes, size: int) -> bytes:
        out = ctypes.create_string_buffer(size)
        written = self._decompress(
            data, len(data), out, size, 1, 0, 0, None, 0, None, None, None, 0, 3
        )
        if written != size:
            raise RuntimeError(f"Oodle 解压失败：期望 {size}，实际 {written}")
        return out.raw[:written]

    def compress_bytes(self, data: bytes, compressor: int = KRAKEN, level: int = LEVEL_NORMAL) -> bytes:
        capacity = len(data) + 274 * ((len(data) + 0x3FFFF) // 0x40000) + 4096
        out = ctypes.create_string_buffer(capacity)
        written = self._compress(compressor, data, len(data), out, level, None, None, None, None, 0)
        if written <= 0:
            raise RuntimeError("Oodle 压缩失败：返回 0")
        return out.raw[:written]


_runtime: Optional[_OodleRuntime] = None


def get_runtime() -> _OodleRuntime:
    global _runtime
    if _runtime is None:
        dll = find_oodle_dll()
        if not dll:
            raise RuntimeError(
                "未找到 Oodle 运行时（oo2core_*_win64.dll）。"
                "请设置环境变量 PALFORGE_OODLE 指向本机其他 Unreal 游戏附带的该文件。"
            )
        _runtime = _OodleRuntime(dll)
    return _runtime


def _ooz_compress(compressor, level, data, size):
    """兼容 pyooz 的签名：compress(compressor, level, data, size)"""
    runtime = get_runtime()
    # oozlib 传的是它自己的枚举，统一映射到官方编号
    mapped = {8: KRAKEN, 9: LEVIATHAN, 10: MERMAID, 11: SELKIE, 13: LEVIATHAN}.get(
        int(compressor), KRAKEN
    )
    return runtime.compress_bytes(bytes(data), mapped, int(level) if int(level) > 0 else LEVEL_NORMAL)


def _ooz_decompress(data, size):
    """兼容 pyooz 的签名：decompress(data, size)"""
    return get_runtime().decompress_bytes(bytes(data), int(size))


def install() -> bool:
    """把兼容模块注册为 `ooz`，必须在 palworld_save_tools 之前调用。"""
    existing = sys.modules.get("ooz")
    if existing is not None and hasattr(existing, "compress"):
        return False

    module = types.ModuleType("ooz")
    module.compress = _ooz_compress  # type: ignore[attr-defined]
    module.decompress = _ooz_decompress  # type: ignore[attr-defined]
    sys.modules["ooz"] = module
    return True
