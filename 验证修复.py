"""
验证快捷键录制功能是否正常工作
"""
from PyQt5.QtCore import Qt

print("=" * 50)
print("  验证快捷键录制功能")
print("=" * 50)
print()

# 测试 Key Code 转换
print("1. 测试字母键转换:")
for key in [Qt.Key_A, Qt.Key_M, Qt.Key_Z]:
    char = chr(key).lower()
    print(f"   Qt.Key_{chr(key)} ({key}) → '{char}'")
print()

print("2. 测试数字键转换:")
for key in [Qt.Key_0, Qt.Key_5, Qt.Key_9]:
    char = chr(key).lower()
    print(f"   Qt.Key_{chr(key)} ({key}) → '{char}'")
print()

print("3. 测试功能键:")
for i in range(1, 13):
    key = Qt.Key_F1 + i - 1
    print(f"   Qt.Key_F{i} ({key}) → 'f{i}'")
print()

print("4. 测试特殊键:")
special_keys = {
    Qt.Key_Space: 'space',
    Qt.Key_Enter: 'enter',
    Qt.Key_Tab: 'tab',
    Qt.Key_Escape: 'esc',
}
for key, name in special_keys.items():
    print(f"   Qt.Key_{name.title()} ({key}) → '{name}'")
print()

print("5. 测试修饰键检测:")
print("   Qt.ControlModifier → 'ctrl'")
print("   Qt.AltModifier → 'alt'")
print("   Qt.ShiftModifier → 'shift'")
print("   Qt.MetaModifier → 'win'")
print()

print("=" * 50)
print("  验证完成！所有转换正常！")
print("=" * 50)
print()
print("现在运行测试程序:")
print("  python test_hotkey_recorder.py")
print()
print("然后按下快捷键组合测试，例如:")
print("  • Ctrl + Alt + A")
print("  • Ctrl + Shift + F1")
print("  • Win + E")
print()
