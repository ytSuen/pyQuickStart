"""
PyQt5 图形界面
现代化的快捷键管理界面
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon
from hotkey_manager import HotkeyManager
from power_manager import PowerManager
from config_manager import ConfigManager
from logger import Logger
import keyboard as kb


class HotkeyRecorder(QLineEdit):
    """快捷键录制输入框"""
    
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("点击此处，然后按下快捷键组合")
        self.setFocusPolicy(Qt.StrongFocus)
        
    def keyPressEvent(self, event):
        """按键按下事件"""
        # 忽略单独的修饰键
        if event.key() in (Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta):
            event.ignore()
            return
        
        modifiers = []
        
        # 检查修饰键
        if event.modifiers() & Qt.ControlModifier:
            modifiers.append('ctrl')
        if event.modifiers() & Qt.AltModifier:
            modifiers.append('alt')
        if event.modifiers() & Qt.ShiftModifier:
            modifiers.append('shift')
        if event.modifiers() & Qt.MetaModifier:
            modifiers.append('win')
        
        # 获取按键
        key = event.key()
        
        # 映射特殊按键
        key_map = {
            Qt.Key_Space: 'space',
            Qt.Key_Return: 'enter',
            Qt.Key_Enter: 'enter',
            Qt.Key_Tab: 'tab',
            Qt.Key_Backspace: 'backspace',
            Qt.Key_Delete: 'delete',
            Qt.Key_Escape: 'esc',
            Qt.Key_Up: 'up',
            Qt.Key_Down: 'down',
            Qt.Key_Left: 'left',
            Qt.Key_Right: 'right',
            Qt.Key_Home: 'home',
            Qt.Key_End: 'end',
            Qt.Key_PageUp: 'page_up',
            Qt.Key_PageDown: 'page_down',
        }
        
        # 确定按键名称
        key_name = None
        
        # 处理 F1-F12
        if Qt.Key_F1 <= key <= Qt.Key_F12:
            key_name = f'f{key - Qt.Key_F1 + 1}'
        # 处理特殊键
        elif key in key_map:
            key_name = key_map[key]
        # 处理字母 A-Z
        elif Qt.Key_A <= key <= Qt.Key_Z:
            key_name = chr(key).lower()
        # 处理数字 0-9
        elif Qt.Key_0 <= key <= Qt.Key_9:
            key_name = chr(key).lower()
        # 尝试从 text() 获取
        else:
            key_text = event.text().lower()
            if key_text and key_text.isprintable() and key_text.strip():
                key_name = key_text
        
        # 如果无法识别按键，忽略
        if not key_name:
            event.ignore()
            return
        
        # 构建快捷键字符串
        if modifiers:
            hotkey = '+'.join(modifiers + [key_name])
        else:
            hotkey = key_name
        
        self.setText(hotkey)
        event.accept()
    
    def focusInEvent(self, event):
        """获得焦点时清空内容"""
        self.clear()
        super().focusInEvent(event)


class HotkeyManagerQt(QMainWindow):
    """PyQt5 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.hotkey_manager = HotkeyManager()
        self.power_manager = PowerManager()
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self.is_monitoring = False
        
        self.init_ui()
        self.load_config()
        
        # 定时更新状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("快捷键启动工具")
        self.setGeometry(100, 100, 900, 600)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部控制栏
        top_layout = QHBoxLayout()
        
        self.status_label = QLabel("状态: 未启动")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        top_layout.addWidget(self.status_label)
        
        self.process_label = QLabel("运行中程序: 0")
        top_layout.addWidget(self.process_label)
        
        top_layout.addStretch()
        
        self.start_btn = QPushButton("启动监听")
        self.start_btn.clicked.connect(self.toggle_monitoring)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        top_layout.addWidget(self.start_btn)
        
        main_layout.addLayout(top_layout)
        
        # 添加快捷键区域
        add_layout = QVBoxLayout()
        add_label = QLabel("添加快捷键")
        add_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        add_layout.addWidget(add_label)
        
        # 快捷键输入
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("快捷键:"))
        self.hotkey_input = HotkeyRecorder()
        hotkey_layout.addWidget(self.hotkey_input)
        add_layout.addLayout(hotkey_layout)
        
        # 目标路径输入
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("目标路径:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("程序、网页URL、文件夹等")
        path_layout.addWidget(self.path_input)
        
        browse_file_btn = QPushButton("浏览文件")
        browse_file_btn.clicked.connect(self.browse_file)
        path_layout.addWidget(browse_file_btn)
        
        browse_folder_btn = QPushButton("浏览文件夹")
        browse_folder_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_folder_btn)
        
        add_layout.addLayout(path_layout)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加快捷键")
        add_btn.clicked.connect(self.add_hotkey)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        btn_layout.addWidget(add_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_inputs)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        add_layout.addLayout(btn_layout)
        
        main_layout.addLayout(add_layout)
        
        # 快捷键列表
        list_label = QLabel("快捷键列表")
        list_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(list_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["快捷键", "目标路径", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.table)
        
        # 删除按钮
        delete_btn = QPushButton("删除选中")
        delete_btn.clicked.connect(self.delete_selected)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        main_layout.addWidget(delete_btn)
        
    def load_config(self):
        """加载配置"""
        hotkeys = self.config_manager.get_hotkeys()
        for hotkey, path in hotkeys.items():
            self.hotkey_manager.add_hotkey(hotkey, path)
            self.add_table_row(hotkey, path)
    
    def add_table_row(self, hotkey, path):
        """添加表格行"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(hotkey))
        self.table.setItem(row, 1, QTableWidgetItem(path))
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self.delete_row(row))
        self.table.setCellWidget(row, 2, delete_btn)
    
    def add_hotkey(self):
        """添加快捷键"""
        hotkey = self.hotkey_input.text().strip()
        path = self.path_input.text().strip()
        
        if not hotkey or not path:
            QMessageBox.warning(self, "输入不完整", "请填写快捷键和目标路径")
            return
        
        if self.hotkey_manager.add_hotkey(hotkey, path):
            self.config_manager.add_hotkey(hotkey, path)
            self.add_table_row(hotkey, path)
            
            if self.is_monitoring:
                self.hotkey_manager.stop()
                self.hotkey_manager.start()
            
            self.hotkey_input.clear()
            self.path_input.clear()
            QMessageBox.information(self, "成功", f"快捷键 '{hotkey}' 已添加")
            self.logger.info(f"添加快捷键: {hotkey} -> {path}")
        else:
            QMessageBox.critical(self, "失败", "添加快捷键失败")
    
    def delete_row(self, row):
        """删除指定行"""
        hotkey = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, "确认删除", 
                                     f"确定要删除快捷键 '{hotkey}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.hotkey_manager.remove_hotkey(hotkey)
            self.config_manager.remove_hotkey(hotkey)
            self.table.removeRow(row)
            self.logger.info(f"删除快捷键: {hotkey}")
    
    def delete_selected(self):
        """删除选中的行"""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "未选择", "请先选择要删除的快捷键")
            return
        
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除选中的 {len(selected_rows)} 个快捷键吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for row in sorted(selected_rows, reverse=True):
                hotkey = self.table.item(row, 0).text()
                self.hotkey_manager.remove_hotkey(hotkey)
                self.config_manager.remove_hotkey(hotkey)
                self.table.removeRow(row)
    
    def browse_file(self):
        """浏览文件"""
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*.*)")
        if filename:
            self.path_input.setText(filename)
    
    def browse_folder(self):
        """浏览文件夹"""
        foldername = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if foldername:
            self.path_input.setText(foldername)
    
    def clear_inputs(self):
        """清空输入"""
        self.hotkey_input.clear()
        self.path_input.clear()
    
    def toggle_monitoring(self):
        """切换监听状态"""
        if not self.is_monitoring:
            if len(self.config_manager.get_hotkeys()) == 0:
                QMessageBox.warning(self, "无快捷键", "请先添加至少一个快捷键")
                return
            
            try:
                self.hotkey_manager.start()
                self.is_monitoring = True
                self.start_btn.setText("停止监听")
                self.status_label.setText("状态: 运行中")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.logger.info("启动监听")
                QMessageBox.information(self, "成功", "快捷键监听已启动")
            except Exception as e:
                QMessageBox.critical(self, "失败", f"启动失败: {e}")
        else:
            try:
                self.hotkey_manager.stop()
                self.power_manager.allow_sleep()
                self.is_monitoring = False
                self.start_btn.setText("启动监听")
                self.status_label.setText("状态: 已停止")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                self.logger.info("停止监听")
                QMessageBox.information(self, "成功", "快捷键监听已停止")
            except Exception as e:
                QMessageBox.critical(self, "失败", f"停止失败: {e}")
    
    def update_status(self):
        """更新状态"""
        count = self.hotkey_manager.get_running_count()
        self.process_label.setText(f"运行中程序: {count}")
        
        if count > 0:
            self.power_manager.prevent_sleep()
        else:
            self.power_manager.allow_sleep()
    
    def closeEvent(self, event):
        """关闭事件"""
        self.logger.info("窗口关闭")
        if self.is_monitoring:
            self.hotkey_manager.stop()
        self.power_manager.allow_sleep()
        event.accept()
