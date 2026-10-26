import sys
import os
import threading
import time
import requests
import traceback
import webbrowser
import webview
from palworld_save_studio.config import version_info, Config, ASSETS_PATH
from palworld_save_studio.utils import LOGGER
from palworld_save_studio.webui import main as web_main


def _apply_window_icon() -> None:
    """把标题栏 / 任务栏图标换成项目头像（pywebview 不提供 icon 参数）。

    这个回调在 GUI 线程启动时触发，此时窗口可能还没创建，所以轮询等待。
    """
    try:
        import ctypes

        title = f"幻兽帕鲁存档编辑器 {version_info()}"
        icon_path = str(ASSETS_PATH / "avatar.ico")
        if not os.path.exists(icon_path):
            LOGGER.warning(f"Window icon not found: {icon_path}")
            return

        hwnd = 0
        for _ in range(60):
            hwnd = ctypes.windll.user32.FindWindowW(None, title)
            if hwnd:
                break
            time.sleep(0.1)
        if not hwnd:
            LOGGER.warning(f"Window icon skipped: window '{title}' not found")
            return

        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x0010
        LR_DEFAULTSIZE = 0x0040
        hicon = ctypes.windll.user32.LoadImageW(
            None, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE
        )
        if not hicon:
            LOGGER.warning("Window icon skipped: LoadImageW failed")
            return

        WM_SETICON = 0x0080
        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon)  # ICON_BIG
        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon)  # ICON_SMALL
        LOGGER.info(f"Window icon applied: {icon_path}")
    except Exception:
        LOGGER.warning(f"Failed to apply window icon: {traceback.format_exc()}")


def main():
    t = threading.Thread(target=web_main)
    t.daemon = True
    t.start()

    while True:
        LOGGER.info("Waiting for backend response...")
        try:
            response = requests.get(f"http://127.0.0.1:{Config.port}/api/ready")
            if response.status_code == 200:
                LOGGER.info("Backend ready, launching GUI...")
                break
            time.sleep(0.5)
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)

    try:
        webview.create_window(
            f"幻兽帕鲁存档编辑器 {version_info()}",
            url=f"http://127.0.0.1:{Config.port}/",
            width=1600,
            height=1000,
            min_size=(1280, 720),
        )
        webview.start(_apply_window_icon)
    except KeyboardInterrupt:
        pass
    except:
        LOGGER.warning(f"Failed Launching pywebview: {traceback.format_exc()}")
        LOGGER.info(f"Fallback to web browser, opening http://127.0.0.1:{Config.port} ...")
        threading.Timer(1, lambda: webbrowser.open(f"http://127.0.0.1:{Config.port}") ).start()
        t.join()
    sys.exit()

if __name__ == "__main__":
    main()
