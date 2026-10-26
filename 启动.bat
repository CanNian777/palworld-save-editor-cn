@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem ============================================================
rem  幻兽帕鲁存档编辑器 1.0 — 启动脚本
rem  双击即可运行，不需要命令行。
rem ============================================================

rem ---- 1. 找 Python：优先随附运行时，其次系统 Python ----
set "PYW=C:\Users\User\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\pythonw.exe"
set "PY=C:\Users\User\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

if exist "%PYW%" goto :found

where python >nul 2>nul
if errorlevel 1 goto :nopython

rem 系统 Python 可能是商店占位符，实际运行会弹应用商店
for /f "delims=" %%i in ('where python') do (
    echo %%i | findstr /i "WindowsApps" >nul || set "PY=%%i"
)
if not defined PY goto :nopython
set "PYW=%PY%"
goto :found

:nopython
echo.
echo   没有找到可用的 Python。
echo.
echo   请安装 Python 3.11 或更高版本：
echo   https://www.python.org/downloads/
echo.
pause
exit /b 1

:found
rem ---- 2. Oodle 运行时（保存存档需要）----
if not defined PALFORGE_OODLE (
    if exist "E:\WeGameApps\rail_apps\DeltaForce(2001918)\DeltaForce\Binaries\Win64\oo2core_8_win64.dll" (
        set "PALFORGE_OODLE=E:\WeGameApps\rail_apps\DeltaForce(2001918)\DeltaForce\Binaries\Win64\oo2core_8_win64.dll"
    )
)

rem ---- 3. 启动（保留控制台但最小化，便于排查问题）----
start /min "" "%PY%" -m palworld_save_studio --mode gui --nocli
exit /b 0
