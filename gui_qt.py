"""
PyQt5 图形界面
现代化的快捷键管理界面
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap
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
        
        # 设置窗口图标
        icon_path = "resources/SYT.png"
        if QIcon(icon_path).isNull():
            self.logger.warning(f"无法加载图标: {icon_path}")
        else:
            self.setWindowIcon(QIcon(icon_path))
        
        self.init_ui()
        self.load_config()
        
        # 定时更新状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("快捷键启动工具")
        self.setGeometry(100, 100, 1000, 680)
        
        # 设置浅色商务风格主题
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8FAFC;
            }
            QWidget {
                background-color: transparent;
                color: #1E293B;
                font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #1E293B;
                background-color: transparent;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 10px 14px;
                color: #1E293B;
                selection-background-color: #3B82F6;
            }
            QLineEdit:focus {
                border: 1.5px solid #3B82F6;
                background-color: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #94A3B8;
            }
            QPushButton {
                background-color: #FFFFFF;
                color: #475569;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                border-color: #CBD5E1;
            }
            QPushButton:pressed {
                background-color: #E2E8F0;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
                gridline-color: #F1F5F9;
                color: #1E293B;
            }
            QTableWidget::item {
                padding: 12px;
                border: none;
                border-bottom: 1px solid #F1F5F9;
            }
            QTableWidget::item:selected {
                background-color: #EFF6FF;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                color: #64748B;
                padding: 12px;
                border: none;
                border-bottom: 1.5px solid #E2E8F0;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 11px;
                letter-spacing: 0.8px;
            }
        """)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 顶部控制栏 - 白色卡片
        top_container = QWidget()
        top_container.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        top_container_layout = QVBoxLayout(top_container)
        top_container_layout.setContentsMargins(20, 16, 20, 16)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/SYT.png")
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setStyleSheet("background-color: transparent; padding: 0px;")
            top_layout.addWidget(logo_label)
        
        # 状态指示器
        status_widget = QWidget()
        status_widget.setStyleSheet("background-color: transparent; border: none;")
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            color: #EF4444;
            font-size: 18px;
            background-color: transparent;
        """)
        status_layout.addWidget(self.status_indicator)
        
        status_text_layout = QVBoxLayout()
        status_text_layout.setSpacing(2)
        
        status_title = QLabel("状态")
        status_title.setStyleSheet("color: #64748B; font-size: 11px; background-color: transparent; font-weight: 500;")
        status_text_layout.addWidget(status_title)
        
        self.status_label = QLabel("未启动")
        self.status_label.setStyleSheet("color: #1E293B; font-weight: 600; font-size: 14px; background-color: transparent;")
        status_text_layout.addWidget(self.status_label)
        
        status_layout.addLayout(status_text_layout)
        top_layout.addWidget(status_widget)
        
        # 分隔线
        separator = QLabel("|")
        separator.setStyleSheet("color: #E2E8F0; font-size: 20px; background-color: transparent;")
        top_layout.addWidget(separator)
        
        # 进程计数器
        process_widget = QWidget()
        process_widget.setStyleSheet("background-color: transparent; border: none;")
        process_layout = QVBoxLayout(process_widget)
        process_layout.setContentsMargins(0, 0, 0, 0)
        process_layout.setSpacing(2)
        
        process_title = QLabel("运行中程序")
        process_title.setStyleSheet("color: #64748B; font-size: 11px; background-color: transparent; font-weight: 500;")
        process_layout.addWidget(process_title)
        
        self.process_label = QLabel("0")
        self.process_label.setStyleSheet("color: #1E293B; font-weight: 600; font-size: 14px; background-color: transparent;")
        process_layout.addWidget(self.process_label)
        
        top_layout.addWidget(process_widget)
        
        top_layout.addStretch()
        
        # 启动按钮 - 蓝色实心
        self.start_btn = QPushButton("启动监听")
        self.start_btn.clicked.connect(self.toggle_monitoring)
        self.start_btn.setMinimumHeight(44)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 12px 28px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        top_layout.addWidget(self.start_btn)
        
        top_container_layout.addLayout(top_layout)
        main_layout.addWidget(top_container)
        
        # 添加快捷键区域 - 白色卡片
        add_container = QWidget()
        add_container.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        add_layout = QVBoxLayout(add_container)
        add_layout.setContentsMargins(24, 20, 24, 20)
        add_layout.setSpacing(18)
        
        add_label = QLabel("添加快捷键")
        add_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #1E293B;
            background-color: transparent;
        """)
        add_layout.addWidget(add_label)
        
        # 快捷键输入
        hotkey_layout = QHBoxLayout()
        hotkey_layout.setSpacing(14)
        
        hotkey_label = QLabel("快捷键")
        hotkey_label.setStyleSheet("color: #64748B; min-width: 80px; font-weight: 500; background-color: transparent;")
        hotkey_layout.addWidget(hotkey_label)
        
        self.hotkey_input = HotkeyRecorder()
        self.hotkey_input.setMinimumHeight(44)
        hotkey_layout.addWidget(self.hotkey_input)
        
        add_layout.addLayout(hotkey_layout)
        
        # 目标路径输入
        path_layout = QHBoxLayout()
        path_layout.setSpacing(14)
        
        path_label = QLabel("目标路径")
        path_label.setStyleSheet("color: #64748B; min-width: 80px; font-weight: 500; background-color: transparent;")
        path_layout.addWidget(path_label)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("程序路径、网页URL、文件夹路径...")
        self.path_input.setMinimumHeight(44)
        path_layout.addWidget(self.path_input)
        
        browse_file_btn = QPushButton("📁 浏览文件")
        browse_file_btn.clicked.connect(self.browse_file)
        browse_file_btn.setMinimumHeight(44)
        browse_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                color: #475569;
                min-width: 110px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                border-color: #CBD5E1;
            }
        """)
        path_layout.addWidget(browse_file_btn)
        
        browse_folder_btn = QPushButton("📂 浏览文件夹")
        browse_folder_btn.clicked.connect(self.browse_folder)
        browse_folder_btn.setMinimumHeight(44)
        browse_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                color: #475569;
                min-width: 120px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                border-color: #CBD5E1;
            }
        """)
        path_layout.addWidget(browse_folder_btn)
        
        add_layout.addLayout(path_layout)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        add_btn = QPushButton("✓ 添加快捷键")
        add_btn.clicked.connect(self.add_hotkey)
        add_btn.setMinimumHeight(44)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        btn_layout.addWidget(add_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_inputs)
        clear_btn.setMinimumHeight(44)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1.5px solid #E2E8F0;
                color: #64748B;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #F8FAFC;
                color: #475569;
                border-color: #CBD5E1;
            }
        """)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        add_layout.addLayout(btn_layout)
        
        main_layout.addWidget(add_container)
        
        # 快捷键列表
        list_label = QLabel("快捷键列表")
        list_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #1E293B;
            margin-top: 4px;
            background-color: transparent;
        """)
        main_layout.addWidget(list_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["快捷键", "目标路径", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)
        main_layout.addWidget(self.table)
        
        # 删除按钮
        delete_btn = QPushButton("🗑 删除选中")
        delete_btn.clicked.connect(self.delete_selected)
        delete_btn.setMinimumHeight(44)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #EF4444;
                border: 1.5px solid #FCA5A5;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: white;
                border-color: #EF4444;
            }
            QPushButton:pressed {
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
        
        hotkey_item = QTableWidgetItem(hotkey)
        hotkey_item.setForeground(Qt.black)
        self.table.setItem(row, 0, hotkey_item)
        
        path_item = QTableWidgetItem(path)
        path_item.setForeground(Qt.black)
        self.table.setItem(row, 1, path_item)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self.delete_row(row))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #EF4444;
                border: 1.5px solid #FCA5A5;
                padding: 6px 18px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #FEF2F2;
                color: #DC2626;
                border-color: #EF4444;
            }
        """)
        self.table.setCellWidget(row, 2, delete_btn)
    
    def add_hotkey(self):
        """添加快捷键"""
        hotkey = self.hotkey_input.text().strip()
        path = self.path_input.text().strip()
        
        if not hotkey or not path:
            QMessageBox.warning(self, "输入不完整", "请填写快捷键和目标路径")
            return
        
        # 检查冲突
        has_conflict, conflict_msg = self.hotkey_manager.check_system_conflict(hotkey)
        if has_conflict:
            reply = QMessageBox.question(
                self, "快捷键冲突", 
                f"{conflict_msg}\n\n是否仍要继续添加？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        success, msg = self.hotkey_manager.add_hotkey(hotkey, path)
        if success:
            self.config_manager.add_hotkey(hotkey, path)
            self.add_table_row(hotkey, path)
            
            if self.is_monitoring:
                self.hotkey_manager.stop()
                success, start_msg = self.hotkey_manager.start()
                if not success:
                    QMessageBox.warning(self, "重启监听失败", start_msg)
            
            self.hotkey_input.clear()
            self.path_input.clear()
            
            if has_conflict:
                QMessageBox.information(self, "添加成功（有警告）", f"快捷键 '{hotkey}' 已添加\n\n警告: {conflict_msg}")
            else:
                QMessageBox.information(self, "成功", f"快捷键 '{hotkey}' 已添加")
            self.logger.info(f"添加快捷键: {hotkey} -> {path}")
        else:
            QMessageBox.critical(self, "失败", msg)
    
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
                success, msg = self.hotkey_manager.start()
                if not success:
                    QMessageBox.critical(self, "启动失败", msg)
                    return
                
                self.is_monitoring = True
                self.start_btn.setText("停止监听")
                self.start_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #EF4444;
                        color: white;
                        border: none;
                        padding: 12px 28px;
                        border-radius: 8px;
                        font-weight: 600;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #DC2626;
                    }
                    QPushButton:pressed {
                        background-color: #B91C1C;
                    }
                """)
                self.status_label.setText("运行中")
                self.status_label.setStyleSheet("color: #1E293B; font-weight: 600; font-size: 14px; background-color: transparent;")
                self.status_indicator.setStyleSheet("color: #10B981; font-size: 18px; background-color: transparent;")
                self.logger.info("启动监听")
                QMessageBox.information(self, "成功", "快捷键监听已启动\n\n提示: 如果快捷键无响应，请确保以管理员身份运行程序")
            except Exception as e:
                QMessageBox.critical(self, "失败", f"启动失败: {e}")
        else:
            try:
                self.hotkey_manager.stop()
                self.power_manager.allow_sleep()
                self.is_monitoring = False
                self.start_btn.setText("启动监听")
                self.start_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3B82F6;
                        color: white;
                        border: none;
                        padding: 12px 28px;
                        border-radius: 8px;
                        font-weight: 600;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #2563EB;
                    }
                    QPushButton:pressed {
                        background-color: #1D4ED8;
                    }
                """)
                self.status_label.setText("未启动")
                self.status_label.setStyleSheet("color: #1E293B; font-weight: 600; font-size: 14px; background-color: transparent;")
                self.status_indicator.setStyleSheet("color: #EF4444; font-size: 18px; background-color: transparent;")
                self.logger.info("停止监听")
                QMessageBox.information(self, "成功", "快捷键监听已停止")
            except Exception as e:
                QMessageBox.critical(self, "失败", f"停止失败: {e}")
    
    def update_status(self):
        """更新状态"""
        count = self.hotkey_manager.get_running_count()
        self.process_label.setText(str(count))
        
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
