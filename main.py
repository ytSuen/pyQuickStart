"""
快捷键启动程序与防休眠工具
主程序入口
"""
import sys
from gui import HotkeyManagerGUI


def main():
    """主函数"""
    try:
        app = HotkeyManagerGUI()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
