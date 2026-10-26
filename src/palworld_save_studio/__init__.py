"""幻兽帕鲁存档编辑器 — 包入口。

必须在导入 core（进而导入 palworld_save_tools）之前安装 ooz 兼容层，
否则「保存」会因 pyooz 缺少 compress 而失败。
"""
from palworld_save_studio.ooz_compat import install as _install_ooz

_install_ooz()

from palworld_save_studio.core import *  # noqa: E402,F401,F403
