"""
快捷键启动程序与防休眠工具
主程序入口 - PyQt5 GUI
"""
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


def run_as_admin():
    """请求管理员权限重新启动程序"""
    try:
        if sys.platform == 'win32':
            # 获取当前脚本路径
            script = sys.argv[0]
            params = ' '.join(sys.argv[1:])
            
            # 使用 ShellExecute 以管理员权限运行
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                f'"{script}" {params}',
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
        # 检查管理员权限
        if not is_admin():
            print("需要管理员权限，正在请求...")
            if run_as_admin():
                # 成功请求管理员权限，退出当前进程
                sys.exit(0)
            else:
                # 请求失败，继续运行但会有功能限制
                print("警告: 未获得管理员权限，快捷键功能可能无法正常工作")
        
        app = QApplication(sys.argv)
        
        # 设置全局 QMessageBox 样式
        app.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #334155;
                font-size: 14px;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2563EB;
            }
            QMessageBox QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        
        window = HotkeyManagerQt()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
