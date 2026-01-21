"""
快捷键启动工具 - 启动脚本
可以选择使用 Web UI 或 Tkinter UI
"""
import sys
import os


def check_pywebview():
    """检查 pywebview 是否已安装"""
    try:
        import webview
        return True
    except ImportError:
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("快捷键启动工具")
    print("=" * 60)
    print()
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode in ['web', 'w']:
            start_web_ui()
            return
        elif mode in ['tkinter', 'tk', 't']:
            start_tkinter_ui()
            return
    
    # 显示选择菜单
    print("请选择界面模式:")
    print()
    
    # 检查 Web UI 是否可用
    webview_available = check_pywebview()
    
    if webview_available:
        print("1. Web UI (现代化界面，推荐)")
        print("   - 现代化设计")
        print("   - 流畅动画")
        print("   - 更好的用户体验")
        print()
    else:
        print("1. Web UI (需要安装 pywebview)")
        print("   运行: pip install pywebview")
        print()
    
    print("2. Tkinter UI (传统界面)")
    print("   - 无需额外依赖")
    print("   - 轻量级")
    print("   - 稳定可靠")
    print()
    
    print("=" * 60)
    
    # 获取用户选择
    while True:
        choice = input("请输入选项 (1 或 2): ").strip()
        
        if choice == '1':
            if webview_available:
                start_web_ui()
            else:
                print()
                print("错误: pywebview 未安装")
                print("请运行: pip install pywebview")
                print()
                install = input("是否现在安装? (y/n): ").strip().lower()
                if install == 'y':
                    os.system('pip install pywebview')
                    print()
                    print("安装完成，请重新运行程序")
                sys.exit(1)
            break
        elif choice == '2':
            start_tkinter_ui()
            break
        else:
            print("无效选项，请输入 1 或 2")


def start_web_ui():
    """启动 Web UI"""
    print()
    print("正在启动 Web UI...")
    print()
    
    try:
        from web_gui import WebGUI
        app = WebGUI()
        app.run()
    except Exception as e:
        print(f"启动 Web UI 失败: {e}")
        print()
        print("尝试启动 Tkinter UI...")
        start_tkinter_ui()


def start_tkinter_ui():
    """启动 Tkinter UI"""
    print()
    print("正在启动 Tkinter UI...")
    print()
    
    try:
        from gui import HotkeyManagerGUI
        app = HotkeyManagerGUI()
        app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("程序已取消")
        sys.exit(0)
    except Exception as e:
        print(f"程序错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
