"""
快速测试脚本 - 验证快捷键冲突检测功能
"""
from hotkey_manager import HotkeyManager


def test_conflict_detection():
    """测试冲突检测"""
    manager = HotkeyManager()
    
    print("=" * 60)
    print("快捷键冲突检测测试")
    print("=" * 60)
    print()
    
    # 测试用例
    test_cases = [
        ("ctrl+alt+n", "C:\\Windows\\notepad.exe", False),
        ("ctrl+alt+delete", "C:\\Windows\\notepad.exe", True),
        ("win+l", "C:\\Windows\\notepad.exe", True),
        ("alt+tab", "C:\\Windows\\notepad.exe", True),
        ("ctrl+shift+esc", "C:\\Windows\\notepad.exe", True),
        ("ctrl+q", "D:\\Chrome\\Application\\chrome.exe", False),
    ]
    
    for hotkey, path, should_conflict in test_cases:
        has_conflict, msg = manager.check_system_conflict(hotkey)
        
        status = "✓" if has_conflict == should_conflict else "×"
        print(f"{status} 快捷键: {hotkey:20s} ", end="")
        
        if has_conflict:
            print(f"冲突: {msg}")
        else:
            print("无冲突")
    
    print()
    print("=" * 60)
    print()
    
    # 测试管理员权限检测
    print("管理员权限检测:")
    if manager.is_admin():
        print("✓ 当前以管理员权限运行")
    else:
        print("× 当前未以管理员权限运行")
        print("  提示: 右键选择'以管理员身份运行'")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    test_conflict_detection()
    input("\n按回车键退出...")
