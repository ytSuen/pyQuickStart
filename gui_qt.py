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
        self.sleep_prevention_enabled = False  # 防休眠独立状态
        
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

    def build_stylesheet(self):
        return """
            QMainWindow {
                background-color: #F8FAFC;
            }
            QWidget {
                color: #334155;
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC', sans-serif;
                font-size: 14px;
            }
            QWidget#centralWidget {
                background-color: #F8FAFC;
            }
            QLabel {
                color: #334155;
                background-color: transparent;
                border: none;
            }
            QLabel[role="pageTitle"] {
                font-size: 18px;
                font-weight: 600;
                color: #0F172A;
            }
            QLabel[role="subtitle"] {
                font-size: 12px;
                color: #64748B;
            }
            QLabel[role="sectionTitle"] {
                font-size: 16px;
                font-weight: 600;
                color: #334155;
            }
            QLabel[role="statTitle"] {
                font-size: 13px;
                color: #64748B;
            }
            QLabel[role="statValue"] {
                font-size: 28px;
                font-weight: 600;
                color: #0F172A;
            }
            QLabel[role="statValue"][state="on"] {
                color: #10B981;
            }
            QLabel[role="statValue"][state="off"] {
                color: #64748B;
            }
            QLabel[role="fieldLabel"] {
                color: #64748B;
                font-weight: 500;
                font-size: 14px;
            }
            QLabel[role="statusDot"] {
                font-size: 16px;
            }
            QLabel[role="statusDot"][state="running"] {
                font-size: 18px;
            }
            QLabel[role="statusDot"][state="running"] {
                color: #10B981;
            }
            QLabel[role="statusDot"][state="stopped"] {
                color: #EF4444;
            }
            QLabel[role="statusText"] {
                font-weight: 600;
                font-size: 14px;
            }
            QLabel[role="statusText"][state="running"] {
                color: #334155;
            }
            QLabel[role="statusText"][state="stopped"] {
                color: #475569;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 10px 14px;
                color: #1E293B;
                selection-background-color: #3B82F6;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
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
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F8FAFC;
                border-color: #CBD5E1;
            }
            QPushButton:pressed {
                background-color: #E2E8F0;
            }
            QPushButton[size="sm"] {
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton[size="md"] {
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton[size="lg"] {
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton[size="xl"] {
                padding: 12px 28px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton[variant="primary"] {
                background-color: #3B82F6;
                color: white;
                border: none;
            }
            QPushButton[variant="primary"]:hover {
                background-color: #2563EB;
            }
            QPushButton[variant="primary"]:pressed {
                background-color: #1D4ED8;
            }
            QPushButton[variant="warning"] {
                background-color: #F97316;
                color: white;
                border: none;
            }
            QPushButton[variant="warning"]:hover {
                background-color: #EA580C;
            }
            QPushButton[variant="warning"]:pressed {
                background-color: #C2410C;
            }
            QPushButton[variant="success"] {
                background-color: #10B981;
                color: white;
                border: none;
            }
            QPushButton[variant="success"]:hover {
                background-color: #059669;
            }
            QPushButton[variant="success"]:pressed {
                background-color: #047857;
            }
            QPushButton[variant="danger"] {
                background-color: #EF4444;
                color: white;
                border: none;
            }
            QPushButton[variant="danger"]:hover {
                background-color: #DC2626;
            }
            QPushButton[variant="danger"]:pressed {
                background-color: #B91C1C;
            }
            QPushButton[variant="muted"] {
                background-color: #64748B;
                color: white;
                border: none;
            }
            QPushButton[variant="muted"]:hover {
                background-color: #475569;
            }
            QPushButton[variant="muted"]:pressed {
                background-color: #334155;
            }
            QPushButton[variant="soft"] {
                background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                color: #475569;
            }
            QPushButton[variant="soft"]:hover {
                background-color: #F1F5F9;
                border-color: #CBD5E1;
            }
            QPushButton[variant="outline"] {
                background-color: transparent;
                border: 1.5px solid #E2E8F0;
                color: #64748B;
            }
            QPushButton[variant="outline"]:hover {
                background-color: #F8FAFC;
                color: #475569;
                border-color: #CBD5E1;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
                gridline-color: #F1F5F9;
                color: #334155;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 16px 12px;
                border: none;
                border-bottom: 1px solid #F1F5F9;
                background-color: #FFFFFF;
            }
            QTableWidget::item:selected {
                background-color: #F8FAFC;
            }
            QTableCornerButton::section {
                background-color: #F8FAFC;
                border: none;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                color: #64748B;
                padding: 12px;
                border: none;
                border-bottom: 1.5px solid #E2E8F0;
                font-weight: 600;
                font-size: 12px;
            }
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
                font-size: 14px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2563EB;
            }
            QMessageBox QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """

    def refresh_widget_style(self, widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
    
    def create_stat_card(self, title, value, bg_color, icon_color):
        """创建统计卡片"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
            }}
        """)
        card.setMinimumHeight(100)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        
        # 左侧文本
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setProperty("role", "statTitle")
        text_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setProperty("role", "statValue")
        text_layout.addWidget(value_label)
        
        card_layout.addLayout(text_layout)
        card_layout.addStretch()
        
        # 右侧图标
        icon_container = QWidget()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 10px;
                border: none;
            }}
        """)
        
        card_layout.addWidget(icon_container)
        
        return card
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("快捷键启动工具")
        self.setGeometry(100, 100, 1100, 750)
        
        self.setStyleSheet(self.build_stylesheet())
        
        # 主窗口部件
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(20)
        
        # 顶部标题栏 - 参考 HTML 设计
        header_container = QWidget()
        header_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(16)
        
        # Logo 和标题
        logo_title_layout = QHBoxLayout()
        logo_title_layout.setSpacing(12)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title_label = QLabel("快捷键启动工具")
        title_label.setProperty("role", "pageTitle")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("全局快捷键 · 智能防休眠")
        subtitle_label.setProperty("role", "subtitle")
        title_layout.addWidget(subtitle_label)
        
        logo_title_layout.addLayout(title_layout)
        header_layout.addLayout(logo_title_layout)
        
        header_layout.addStretch()
        
        # 状态指示器
        status_container = QWidget()
        status_container.setStyleSheet("""
            QWidget {
                background-color: #F1F5F9;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
            }
        """)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(8, 6, 8, 6)
        status_layout.setSpacing(8)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setProperty("role", "statusDot")
        self.status_indicator.setProperty("state", "stopped")
        status_layout.addWidget(self.status_indicator)
        
        self.status_label = QLabel("未启动")
        self.status_label.setProperty("role", "statusText")
        self.status_label.setProperty("state", "stopped")
        status_layout.addWidget(self.status_label)
        
        header_layout.addWidget(status_container)
        
        # 防休眠按钮
        self.sleep_btn = QPushButton("开启防休眠")
        self.sleep_btn.clicked.connect(self.toggle_sleep_prevention)
        self.sleep_btn.setMinimumHeight(44)
        self.sleep_btn.setProperty("variant", "warning")
        self.sleep_btn.setProperty("size", "md")
        header_layout.addWidget(self.sleep_btn)
        
        # 启动按钮
        self.start_btn = QPushButton("启动监听")
        self.start_btn.clicked.connect(self.toggle_monitoring)
        self.start_btn.setMinimumHeight(44)
        self.start_btn.setProperty("variant", "primary")
        self.start_btn.setProperty("size", "md")
        header_layout.addWidget(self.start_btn)
        
        main_layout.addWidget(header_container)
        
        # 统计卡片区域 - 参考 HTML 设计
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        # 卡片1: 配置快捷键
        card1 = self.create_stat_card("配置快捷键", "0", "#DBEAFE", "#3B82F6")
        self.hotkey_count_label = card1.findChild(QLabel, "value_label")
        stats_layout.addWidget(card1)
        
        # 卡片2: 运行中程序
        card2 = self.create_stat_card("运行中程序", "0", "#D1FAE5", "#10B981")
        self.process_count_label = card2.findChild(QLabel, "value_label")
        stats_layout.addWidget(card2)
        
        # 卡片3: 防休眠状态
        card3 = self.create_stat_card("防休眠状态", "关闭", "#FED7AA", "#F97316")
        self.sleep_status_label = card3.findChild(QLabel, "value_label")
        self.sleep_status_label.setProperty("state", "off")
        stats_layout.addWidget(card3)
        
        main_layout.addLayout(stats_layout)
        
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
        add_label.setProperty("role", "sectionTitle")
        add_layout.addWidget(add_label)
        
        # 快捷键输入
        hotkey_layout = QHBoxLayout()
        hotkey_layout.setSpacing(14)
        
        hotkey_label = QLabel("快捷键")
        hotkey_label.setMinimumWidth(80)
        hotkey_label.setProperty("role", "fieldLabel")
        hotkey_layout.addWidget(hotkey_label)
        
        self.hotkey_input = HotkeyRecorder()
        self.hotkey_input.setMinimumHeight(44)
        hotkey_layout.addWidget(self.hotkey_input)
        
        add_layout.addLayout(hotkey_layout)
        
        # 目标路径输入
        path_layout = QHBoxLayout()
        path_layout.setSpacing(14)
        
        path_label = QLabel("目标路径")
        path_label.setMinimumWidth(80)
        path_label.setProperty("role", "fieldLabel")
        path_layout.addWidget(path_label)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("程序路径、网页URL、文件夹路径...")
        self.path_input.setMinimumHeight(44)
        path_layout.addWidget(self.path_input)
        
        browse_file_btn = QPushButton("📁 浏览文件")
        browse_file_btn.clicked.connect(self.browse_file)
        browse_file_btn.setMinimumHeight(44)
        browse_file_btn.setMinimumWidth(110)
        browse_file_btn.setProperty("variant", "soft")
        browse_file_btn.setProperty("size", "md")
        path_layout.addWidget(browse_file_btn)
        
        browse_folder_btn = QPushButton("📂 浏览文件夹")
        browse_folder_btn.clicked.connect(self.browse_folder)
        browse_folder_btn.setMinimumHeight(44)
        browse_folder_btn.setMinimumWidth(120)
        browse_folder_btn.setProperty("variant", "soft")
        browse_folder_btn.setProperty("size", "md")
        path_layout.addWidget(browse_folder_btn)
        
        add_layout.addLayout(path_layout)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        add_btn = QPushButton("✓ 添加快捷键")
        add_btn.clicked.connect(self.add_hotkey)
        add_btn.setMinimumHeight(44)
        add_btn.setProperty("variant", "success")
        add_btn.setProperty("size", "lg")
        btn_layout.addWidget(add_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_inputs)
        clear_btn.setMinimumHeight(44)
        clear_btn.setProperty("variant", "outline")
        clear_btn.setProperty("size", "lg")
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        add_layout.addLayout(btn_layout)
        
        main_layout.addWidget(add_container)
        
        # 快捷键列表
        list_label = QLabel("快捷键列表")
        list_label.setProperty("role", "sectionTitle")
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
        self.table.setRowHeight(row, 60)  # 设置行高
        
        hotkey_item = QTableWidgetItem(hotkey)
        self.table.setItem(row, 0, hotkey_item)
        
        path_item = QTableWidgetItem(path)
        self.table.setItem(row, 1, path_item)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self.delete_row(row))
        delete_btn.setMinimumHeight(36)
        delete_btn.setProperty("variant", "danger")
        delete_btn.setProperty("size", "sm")
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
    
    def toggle_sleep_prevention(self):
        """切换防休眠状态"""
        self.sleep_prevention_enabled = not self.sleep_prevention_enabled
        
        if self.sleep_prevention_enabled:
            self.power_manager.prevent_sleep()
            self.sleep_btn.setText("关闭防休眠")
            self.sleep_btn.setProperty("variant", "muted")
            self.refresh_widget_style(self.sleep_btn)
            self.sleep_status_label.setText("开启")
            self.sleep_status_label.setProperty("state", "on")
            self.refresh_widget_style(self.sleep_status_label)
            self.logger.info("手动开启防休眠")
        else:
            self.power_manager.allow_sleep()
            self.sleep_btn.setText("开启防休眠")
            self.sleep_btn.setProperty("variant", "warning")
            self.refresh_widget_style(self.sleep_btn)
            self.sleep_status_label.setText("关闭")
            self.sleep_status_label.setProperty("state", "off")
            self.refresh_widget_style(self.sleep_status_label)
            self.logger.info("手动关闭防休眠")
    
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
                self.start_btn.setProperty("variant", "danger")
                self.start_btn.setProperty("size", "xl")
                self.refresh_widget_style(self.start_btn)
                self.status_label.setText("运行中")
                self.status_label.setProperty("state", "running")
                self.status_indicator.setProperty("state", "running")
                self.refresh_widget_style(self.status_label)
                self.refresh_widget_style(self.status_indicator)
                
                # 不再自动启动防休眠，由用户手动控制
                self.logger.info("启动监听")
                QMessageBox.information(self, "成功", "快捷键监听已启动\n\n提示: 如果快捷键无响应，请确保以管理员身份运行程序")
            except Exception as e:
                QMessageBox.critical(self, "失败", f"启动失败: {e}")
        else:
            try:
                self.hotkey_manager.stop()
                # 不再自动关闭防休眠，由用户手动控制
                self.is_monitoring = False
                self.start_btn.setText("启动监听")
                self.start_btn.setProperty("variant", "primary")
                self.start_btn.setProperty("size", "md")
                self.refresh_widget_style(self.start_btn)
                self.status_label.setText("未启动")
                self.status_label.setProperty("state", "stopped")
                self.status_indicator.setProperty("state", "stopped")
                self.refresh_widget_style(self.status_label)
                self.refresh_widget_style(self.status_indicator)
                
                # 不再自动关闭防休眠，由用户手动控制
                self.logger.info("停止监听")
                QMessageBox.information(self, "成功", "快捷键监听已停止")
            except Exception as e:
                QMessageBox.critical(self, "失败", f"停止失败: {e}")
    
    def update_status(self):
        """更新状态"""
        count = self.hotkey_manager.get_running_count()
        self.process_count_label.setText(str(count))
        
        # 更新快捷键数量
        hotkey_count = len(self.config_manager.get_hotkeys())
        self.hotkey_count_label.setText(str(hotkey_count))
        
        # 防休眠状态由用户手动控制，不再自动切换
    
    def closeEvent(self, event):
        """关闭事件"""
        self.logger.info("窗口关闭")
        if self.is_monitoring:
            self.hotkey_manager.stop()
        # 不再自动关闭防休眠，保持用户设置的状态
        event.accept()
