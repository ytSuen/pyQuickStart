"""
快捷键启动程序与防休眠工具
主程序入口 - PyQt5 GUI
"""
import sys
from PyQt5.QtWidgets import QApplication
from gui_qt import HotkeyManagerQt


def main():
    """主函数"""
    try:
        app = QApplication(sys.argv)
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
