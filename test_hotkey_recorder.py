"""
测试快捷键录制功能
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from gui_qt import HotkeyRecorder


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("快捷键录制测试")
        self.setGeometry(100, 100, 500, 300)
        
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("快捷键录制功能测试")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 说明
        instruction = QLabel(
            "使用方法：\n"
            "1. 点击下方输入框\n"
            "2. 按下快捷键组合（如：Ctrl+Alt+A）\n"
            "3. 输入框会显示录制的快捷键"
        )
        instruction.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(instruction)
        
        # 快捷键录制器
        self.recorder = HotkeyRecorder()
        self.recorder.setStyleSheet("font-size: 14px; padding: 8px;")
        self.recorder.textChanged.connect(self.on_hotkey_changed)
        layout.addWidget(self.recorder)
        
        # 结果显示
        self.result_label = QLabel("等待录制...")
        self.result_label.setStyleSheet(
            "font-size: 14px; padding: 10px; "
            "background-color: #e8f5e9; border: 1px solid #4caf50;"
        )
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)
        
        # 清空按钮
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.recorder.clear)
        layout.addWidget(clear_btn)
        
        # 测试示例
        examples = QLabel(
            "测试示例：\n"
            "• Ctrl+Alt+A\n"
            "• Ctrl+Shift+F1\n"
            "• Win+E\n"
            "• Alt+Space"
        )
        examples.setStyleSheet("margin: 10px; font-size: 12px; color: #666;")
        layout.addWidget(examples)
        
        self.setLayout(layout)
    
    def on_hotkey_changed(self, text):
        """快捷键改变时更新显示"""
        if text:
            self.result_label.setText(f"✓ 录制成功: {text}")
            self.result_label.setStyleSheet(
                "font-size: 14px; padding: 10px; "
                "background-color: #e8f5e9; border: 1px solid #4caf50;"
            )
        else:
            self.result_label.setText("等待录制...")
            self.result_label.setStyleSheet(
                "font-size: 14px; padding: 10px; "
                "background-color: #fff3e0; border: 1px solid #ff9800;"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
