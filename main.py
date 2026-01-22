"""
快捷键启动程序与防休眠工具
主程序入口 - PyQt5 GUI
"""
import os
import sys
import ctypes
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui_qt import HotkeyManagerQt


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def _truthy(value: str) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def should_start_hidden() -> bool:
    if _truthy(os.environ.get("PYQS_START_HIDDEN")):
        return True
    return "--hidden" in sys.argv


def should_skip_admin_relaunch() -> bool:
    if _truthy(os.environ.get("PYQS_SKIP_ADMIN")):
        return True
    return "--no-admin" in sys.argv


def hide_console_window():
    if sys.platform != 'win32':
        return
    if os.environ.get('PYQS_SHOW_CONSOLE'):
        return
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        return


def run_as_admin():
    """请求管理员权限重新启动程序"""
    try:
        if sys.platform == 'win32':
            params = ' '.join(sys.argv[1:])

            if getattr(sys, 'frozen', False):
                executable = sys.executable
                args = params
            else:
                script = sys.argv[0]
                executable = sys.executable
                args = f'"{script}" {params}'.strip()

            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                executable,
                args,
                None,
                1  # SW_SHOWNORMAL
            )
            return True
    except Exception as e:
        print(f"请求管理员权限失败: {e}")
        return False
    return False


def main():
    """主函数"""
    try:
        hide_console_window()

        start_hidden = should_start_hidden()
        skip_admin = should_skip_admin_relaunch()
        # 检查管理员权限
        if not skip_admin and not is_admin():
            print("需要管理员权限，正在请求...")
            if run_as_admin():
                # 成功请求管理员权限，退出当前进程
                sys.exit(0)
            else:
                # 请求失败，继续运行但会有功能限制
                print("警告: 未获得管理员权限，快捷键功能可能无法正常工作")
        
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        window = HotkeyManagerQt()
        if not start_hidden:
            window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
