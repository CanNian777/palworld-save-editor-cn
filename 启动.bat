@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem ============================================================
rem  幻兽帕鲁存档编辑器 1.0 — 从源码启动
rem  双击运行。需要已安装 Python 3.11+ 并执行过 pip install -e .
rem ============================================================

rem ---- 1. 定位 Python（跳过 Microsoft Store 的占位符）----
set "PY="
for /f "delims=" %%i in ('where python 2^>nul') do (
    echo %%i | findstr /i "WindowsApps" >nul || set "PY=%%i"
)

if not defined PY (
    echo.
    echo   没有找到可用的 Python。
    echo.
    echo   请先安装 Python 3.11 或更高版本：
    echo   https://www.python.org/downloads/
    echo.
    echo   安装完成后，在本目录执行：
    echo     pip install -r requirements.txt
    echo     pip install -e .
    echo.
    pause
    exit /b 1
)

rem ---- 2. 启动 ----
rem Oodle 运行时由程序自动搜索；也可先设置环境变量手动指定：
rem   set PALFORGE_OODLE=D:\path\to\oo2core_8_win64.dll
start /min "" "%PY%" -m palworld_save_studio --mode gui --nocli
exit /b 0
