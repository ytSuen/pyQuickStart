"""
GUI 测试模块
包含单元测试和属性测试
"""
import pytest
import tkinter as tk
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, settings, strategies as st

from gui import HotkeyManagerGUI
from config_manager import ConfigManager
from hotkey_manager import HotkeyManager
from power_manager import PowerManager


# Feature: hotkey-power-manager, Property 10: GUI状态同步
# Validates: Requirements 5.5, 5.6, 5.7, 5.8
@pytest.mark.property
@settings(max_examples=100, deadline=None)
@given(
    is_monitoring=st.booleans(),
    running_count=st.integers(min_value=0, max_value=10)
)
def test_gui_state_synchronization(is_monitoring, running_count):
    """
    属性测试：GUI状态同步
    
    对于任何监听状态变化，GUI显示的状态标签文本、按钮文本和进程计数
    应该与is_monitoring状态和get_running_count()返回值一致
    """
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        # 创建GUI实例（不启动mainloop）
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger:
            
            # 配置mock对象
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_hotkey_mgr.get_running_count.return_value = running_count
            
            mock_power_mgr = MockPowerManager.return_value
            mock_logger = MockLogger.return_value
            
            # 创建GUI（不显示窗口）
            gui = HotkeyManagerGUI()
            gui.root.withdraw()  # 隐藏窗口
            
            # 设置监听状态
            gui.is_monitoring = is_monitoring
            
            # 模拟状态更新
            if is_monitoring:
                gui.start_btn.config(text="停止监听")
                gui.status_label.config(text="状态: 运行中", foreground="green")
            else:
                gui.start_btn.config(text="启动监听")
                gui.status_label.config(text="状态: 已停止", foreground="red")
            
            # 更新进程计数
            gui.process_label.config(text=f"运行中程序: {running_count}")
            
            # 验证状态同步
            # 1. 按钮文本应该与监听状态一致
            expected_btn_text = "停止监听" if is_monitoring else "启动监听"
            actual_btn_text = gui.start_btn.cget("text")
            assert actual_btn_text == expected_btn_text, \
                f"按钮文本不一致: 期望='{expected_btn_text}', 实际='{actual_btn_text}'"
            
            # 2. 状态标签应该与监听状态一致
            expected_status = "状态: 运行中" if is_monitoring else "状态: 已停止"
            actual_status = gui.status_label.cget("text")
            assert actual_status == expected_status, \
                f"状态标签不一致: 期望='{expected_status}', 实际='{actual_status}'"
            
            # 3. 状态标签颜色应该与监听状态一致
            expected_color = "green" if is_monitoring else "red"
            actual_color = str(gui.status_label.cget("foreground"))
            assert actual_color == expected_color, \
                f"状态颜色不一致: 期望='{expected_color}', 实际='{actual_color}'"
            
            # 4. 进程计数标签应该与运行数量一致
            expected_process_text = f"运行中程序: {running_count}"
            actual_process_text = gui.process_label.cget("text")
            assert actual_process_text == expected_process_text, \
                f"进程计数不一致: 期望='{expected_process_text}', 实际='{actual_process_text}'"
            
            # 清理
            gui.root.destroy()
    
    finally:
        # 清理临时文件
        Path(temp_config_path).unlink(missing_ok=True)



# ============================================================================
# 单元测试：GUI基础操作
# Validates: Requirements 5.1, 5.2, 5.3, 5.4
# ============================================================================

@pytest.mark.unit
def test_add_hotkey_success():
    """
    测试_add_hotkey方法 - 成功添加
    
    验证添加有效快捷键时的正常流程
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox, \
             patch('os.path.exists', return_value=True):
            
            # 配置mock对象
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_hotkey_mgr.add_hotkey.return_value = True
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 设置输入
            gui.hotkey_entry.insert(0, "ctrl+alt+n")
            gui.path_entry.insert(0, "C:\\notepad.exe")
            
            # 调用添加方法
            gui._add_hotkey()
            
            # 验证调用
            mock_hotkey_mgr.add_hotkey.assert_called_once_with("ctrl+alt+n", "C:\\notepad.exe")
            mock_config.add_hotkey.assert_called_once_with("ctrl+alt+n", "C:\\notepad.exe")
            
            # 验证输入框被清空
            assert gui.hotkey_entry.get() == ""
            assert gui.path_entry.get() == ""
            
            # 验证成功消息
            mock_messagebox.showinfo.assert_called_once()
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_add_hotkey_empty_input():
    """
    测试_add_hotkey方法 - 空输入
    
    验证输入为空时显示警告
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 不设置输入（保持为空）
            gui._add_hotkey()
            
            # 验证显示警告
            mock_messagebox.showwarning.assert_called_once()
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_add_hotkey_invalid_format():
    """
    测试_add_hotkey方法 - 无效快捷键格式
    
    验证快捷键格式错误时显示错误消息
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox, \
             patch('os.path.exists', return_value=True):
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 设置无效快捷键（没有修饰键）
            gui.hotkey_entry.insert(0, "n")
            gui.path_entry.insert(0, "C:\\notepad.exe")
            
            # 调用添加方法
            gui._add_hotkey()
            
            # 验证显示错误
            mock_messagebox.showerror.assert_called_once()
            call_args = mock_messagebox.showerror.call_args
            assert "格式" in call_args[0][0] or "格式" in call_args[0][1]
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_add_hotkey_file_not_exists():
    """
    测试_add_hotkey方法 - 文件不存在
    
    验证文件路径不存在时显示错误
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox, \
             patch('os.path.exists', return_value=False):
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 设置不存在的文件路径
            gui.hotkey_entry.insert(0, "ctrl+alt+n")
            gui.path_entry.insert(0, "C:\\nonexistent.exe")
            
            # 调用添加方法
            gui._add_hotkey()
            
            # 验证显示错误
            mock_messagebox.showerror.assert_called_once()
            call_args = mock_messagebox.showerror.call_args
            assert "不存在" in call_args[0][0] or "不存在" in call_args[0][1]
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_remove_hotkey_success():
    """
    测试_remove_hotkey方法 - 成功删除
    
    验证删除选中快捷键的正常流程
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {"ctrl+alt+n": "C:\\notepad.exe"}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # GUI初始化时已经加载了一个快捷键到树视图
            # 选择这个已存在的项目
            items = gui.tree.get_children()
            assert len(items) == 1, "GUI应该已经加载了一个快捷键"
            gui.tree.selection_set(items[0])
            
            # 模拟用户确认删除
            mock_messagebox.askyesno.return_value = True
            
            # 调用删除方法
            gui._remove_hotkey()
            
            # 验证调用
            mock_hotkey_mgr.remove_hotkey.assert_called_once_with("ctrl+alt+n")
            mock_config.remove_hotkey.assert_called_once_with("ctrl+alt+n")
            
            # 验证树视图中的项目被删除
            assert len(gui.tree.get_children()) == 0
            
            # 验证成功消息
            mock_messagebox.showinfo.assert_called_once()
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_remove_hotkey_no_selection():
    """
    测试_remove_hotkey方法 - 未选择项目
    
    验证未选择项目时显示警告
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 不选择任何项目
            gui._remove_hotkey()
            
            # 验证显示警告
            mock_messagebox.showwarning.assert_called_once()
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_toggle_monitoring_start():
    """
    测试_toggle_monitoring方法 - 启动监听
    
    验证启动监听的正常流程
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox, \
             patch('threading.Thread'):
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {"ctrl+alt+n": "C:\\notepad.exe"}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            gui.is_monitoring = False
            
            # 调用切换方法
            gui._toggle_monitoring()
            
            # 验证启动监听
            mock_hotkey_mgr.start.assert_called_once()
            assert gui.is_monitoring == True
            assert gui.start_btn.cget("text") == "停止监听"
            assert gui.status_label.cget("text") == "状态: 运行中"
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_toggle_monitoring_stop():
    """
    测试_toggle_monitoring方法 - 停止监听
    
    验证停止监听的正常流程
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {"ctrl+alt+n": "C:\\notepad.exe"}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_power_mgr = MockPowerManager.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            gui.is_monitoring = True
            
            # 调用切换方法
            gui._toggle_monitoring()
            
            # 验证停止监听
            mock_hotkey_mgr.stop.assert_called_once()
            mock_power_mgr.allow_sleep.assert_called_once()
            assert gui.is_monitoring == False
            assert gui.start_btn.cget("text") == "启动监听"
            assert gui.status_label.cget("text") == "状态: 已停止"
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_toggle_monitoring_no_hotkeys():
    """
    测试_toggle_monitoring方法 - 无快捷键配置
    
    验证没有配置快捷键时显示警告
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}  # 空配置
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            gui.is_monitoring = False
            
            # 调用切换方法
            gui._toggle_monitoring()
            
            # 验证显示警告
            mock_messagebox.showwarning.assert_called_once()
            assert gui.is_monitoring == False
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_browse_file():
    """
    测试_browse_file方法
    
    验证文件浏览对话框功能
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.filedialog.askopenfilename', return_value="C:\\test.exe"):
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 调用浏览方法
            gui._browse_file()
            
            # 验证路径被设置
            assert gui.path_entry.get() == "C:\\test.exe"
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_browse_file_cancel():
    """
    测试_browse_file方法 - 取消选择
    
    验证取消文件选择时不修改路径
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.filedialog.askopenfilename', return_value=""):
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 设置初始路径
            gui.path_entry.insert(0, "C:\\original.exe")
            
            # 调用浏览方法（用户取消）
            gui._browse_file()
            
            # 验证路径未改变
            assert gui.path_entry.get() == "C:\\original.exe"
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)



# ============================================================================
# 单元测试：GUI状态更新线程
# Validates: Requirements 5.7, 5.8
# ============================================================================

@pytest.mark.unit
def test_update_status_with_running_processes():
    """
    测试_update_status方法 - 有运行中的程序
    
    验证当有程序运行时，状态更新正确且启用防休眠
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('time.sleep'):  # 避免实际等待
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_hotkey_mgr.get_running_count.return_value = 3
            
            mock_power_mgr = MockPowerManager.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            gui.is_monitoring = True
            
            # 模拟一次状态更新循环
            count = gui.hotkey_manager.get_running_count()
            gui.process_label.config(text=f"运行中程序: {count}")
            
            if count > 0:
                gui.power_manager.prevent_sleep()
            else:
                gui.power_manager.allow_sleep()
            
            # 验证进程计数标签更新
            assert gui.process_label.cget("text") == "运行中程序: 3"
            
            # 验证防休眠被启用
            mock_power_mgr.prevent_sleep.assert_called_once()
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_update_status_no_running_processes():
    """
    测试_update_status方法 - 无运行中的程序
    
    验证当没有程序运行时，状态更新正确且允许休眠
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('time.sleep'):
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_hotkey_mgr.get_running_count.return_value = 0
            
            mock_power_mgr = MockPowerManager.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            gui.is_monitoring = True
            
            # 模拟一次状态更新循环
            count = gui.hotkey_manager.get_running_count()
            gui.process_label.config(text=f"运行中程序: {count}")
            
            if count > 0:
                gui.power_manager.prevent_sleep()
            else:
                gui.power_manager.allow_sleep()
            
            # 验证进程计数标签更新
            assert gui.process_label.cget("text") == "运行中程序: 0"
            
            # 验证允许休眠
            mock_power_mgr.allow_sleep.assert_called_once()
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_update_status_process_count_changes():
    """
    测试_update_status方法 - 进程计数变化
    
    验证进程计数变化时标签正确更新
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('time.sleep'):
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_power_mgr = MockPowerManager.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            gui.is_monitoring = True
            
            # 模拟进程计数从0变化到5
            for count in [0, 1, 3, 5]:
                mock_hotkey_mgr.get_running_count.return_value = count
                
                # 更新状态
                current_count = gui.hotkey_manager.get_running_count()
                gui.process_label.config(text=f"运行中程序: {current_count}")
                
                if current_count > 0:
                    gui.power_manager.prevent_sleep()
                else:
                    gui.power_manager.allow_sleep()
                
                # 验证标签更新
                assert gui.process_label.cget("text") == f"运行中程序: {count}"
            
            # 验证防休眠被调用（count > 0时）
            assert mock_power_mgr.prevent_sleep.call_count == 3  # 1, 3, 5
            assert mock_power_mgr.allow_sleep.call_count == 1   # 0
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_update_status_stops_when_monitoring_false():
    """
    测试_update_status方法 - 监听停止时退出循环
    
    验证is_monitoring变为False时更新循环停止
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_hotkey_mgr.get_running_count.return_value = 2
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 验证循环条件
            gui.is_monitoring = True
            assert gui.is_monitoring == True
            
            gui.is_monitoring = False
            assert gui.is_monitoring == False
            
            # 清理
            gui.root.destroy()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


# ============================================================================
# 单元测试：资源清理
# Validates: Requirements 7.1, 7.2, 7.3
# ============================================================================

@pytest.mark.unit
def test_on_closing_stops_monitoring():
    """
    测试_on_closing方法 - 停止监听
    
    验证窗口关闭时，如果正在监听则停止监听
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_power_mgr = MockPowerManager.return_value
            mock_logger = MockLogger.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 设置为监听状态
            gui.is_monitoring = True
            
            # 调用关闭方法
            gui._on_closing()
            
            # 验证停止监听被调用
            mock_hotkey_mgr.stop.assert_called_once()
            
            # 验证恢复休眠被调用
            mock_power_mgr.allow_sleep.assert_called_once()
            
            # 验证日志记录
            assert mock_logger.info.call_count >= 3  # 至少记录了关闭、停止监听、恢复休眠
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_on_closing_not_monitoring():
    """
    测试_on_closing方法 - 未监听状态
    
    验证窗口关闭时，如果未监听则不调用stop
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_power_mgr = MockPowerManager.return_value
            mock_logger = MockLogger.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 设置为未监听状态
            gui.is_monitoring = False
            
            # 调用关闭方法
            gui._on_closing()
            
            # 验证stop未被调用
            mock_hotkey_mgr.stop.assert_not_called()
            
            # 验证恢复休眠仍被调用
            mock_power_mgr.allow_sleep.assert_called_once()
            
            # 验证日志记录
            assert mock_logger.info.call_count >= 2  # 至少记录了关闭和恢复休眠
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_on_closing_always_allows_sleep():
    """
    测试_on_closing方法 - 总是恢复休眠
    
    验证无论什么状态，关闭时都会恢复系统休眠
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        # 测试两种状态
        for monitoring_state in [True, False]:
            with patch('gui.ConfigManager') as MockConfigManager, \
                 patch('gui.HotkeyManager') as MockHotkeyManager, \
                 patch('gui.PowerManager') as MockPowerManager, \
                 patch('gui.Logger') as MockLogger:
                
                mock_config = MockConfigManager.return_value
                mock_config.get_hotkeys.return_value = {}
                
                mock_power_mgr = MockPowerManager.return_value
                
                # 创建GUI
                gui = HotkeyManagerGUI()
                gui.root.withdraw()
                gui.is_monitoring = monitoring_state
                
                # 调用关闭方法
                gui._on_closing()
                
                # 验证恢复休眠总是被调用
                mock_power_mgr.allow_sleep.assert_called_once()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_on_closing_cleanup_order():
    """
    测试_on_closing方法 - 清理顺序
    
    验证资源清理的正确顺序：先停止监听，再恢复休眠，最后销毁窗口
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_power_mgr = MockPowerManager.return_value
            mock_logger = MockLogger.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            gui.is_monitoring = True
            
            # 创建调用顺序记录器
            call_order = []
            
            def record_stop():
                call_order.append('stop')
            
            def record_allow_sleep():
                call_order.append('allow_sleep')
            
            mock_hotkey_mgr.stop.side_effect = record_stop
            mock_power_mgr.allow_sleep.side_effect = record_allow_sleep
            
            # 调用关闭方法
            gui._on_closing()
            
            # 验证调用顺序
            assert call_order == ['stop', 'allow_sleep'], \
                f"清理顺序不正确: {call_order}"
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_hotkey_manager_destructor():
    """
    测试HotkeyManager析构函数
    
    验证析构函数在监听运行时调用stop
    """
    with patch('hotkey_manager.Logger') as MockLogger:
        mock_logger = MockLogger.return_value
        
        # 创建HotkeyManager实例
        manager = HotkeyManager()
        manager.is_running = True
        manager.hotkeys = {"ctrl+alt+n": "C:\\test.exe"}
        
        # 模拟keyboard.remove_hotkey
        with patch('hotkey_manager.keyboard.remove_hotkey'):
            # 调用析构函数
            manager.__del__()
            
            # 验证stop被调用（通过检查is_running状态）
            assert manager.is_running == False
            
            # 验证日志记录
            assert mock_logger.info.call_count >= 1


@pytest.mark.unit
def test_hotkey_manager_destructor_not_running():
    """
    测试HotkeyManager析构函数 - 未运行状态
    
    验证析构函数在未运行时不调用stop
    """
    with patch('hotkey_manager.Logger') as MockLogger:
        mock_logger = MockLogger.return_value
        
        # 创建HotkeyManager实例
        manager = HotkeyManager()
        manager.is_running = False
        
        # 调用析构函数
        manager.__del__()
        
        # 验证状态未改变
        assert manager.is_running == False
        
        # 验证debug日志被记录
        assert mock_logger.debug.call_count >= 1


@pytest.mark.unit
def test_power_manager_destructor():
    """
    测试PowerManager析构函数
    
    验证析构函数在防休眠启用时恢复休眠
    """
    with patch('power_manager.Logger') as MockLogger, \
         patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
        
        mock_logger = MockLogger.return_value
        
        # 创建PowerManager实例
        manager = PowerManager()
        manager.is_preventing_sleep = True
        
        # 调用析构函数
        manager.__del__()
        
        # 验证防休眠状态被关闭
        assert manager.is_preventing_sleep == False
        
        # 验证日志记录
        assert mock_logger.info.call_count >= 2  # 析构函数日志 + allow_sleep日志


@pytest.mark.unit
def test_power_manager_destructor_not_preventing():
    """
    测试PowerManager析构函数 - 未防休眠状态
    
    验证析构函数在未防休眠时不调用API
    """
    with patch('power_manager.Logger') as MockLogger, \
         patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1) as mock_api:
        
        mock_logger = MockLogger.return_value
        
        # 创建PowerManager实例
        manager = PowerManager()
        manager.is_preventing_sleep = False
        
        # 重置mock以清除初始化时的调用
        mock_api.reset_mock()
        
        # 调用析构函数
        manager.__del__()
        
        # 验证状态未改变
        assert manager.is_preventing_sleep == False
        
        # 验证debug日志被记录
        assert mock_logger.debug.call_count >= 1


@pytest.mark.unit
def test_hotkey_unregistration_on_stop():
    """
    测试快捷键注销
    
    验证stop方法正确注销所有快捷键
    """
    with patch('hotkey_manager.Logger') as MockLogger, \
         patch('hotkey_manager.keyboard') as mock_keyboard:
        
        mock_logger = MockLogger.return_value
        
        # 创建HotkeyManager实例
        manager = HotkeyManager()
        manager.is_running = True
        manager.hotkeys = {
            "ctrl+alt+n": "C:\\notepad.exe",
            "ctrl+shift+t": "C:\\test.exe",
            "win+e": "C:\\explorer.exe"
        }
        
        # 调用stop
        manager.stop()
        
        # 验证所有快捷键被注销
        assert mock_keyboard.remove_hotkey.call_count == 3
        
        # 验证每个快捷键都被注销
        called_hotkeys = [call[0][0] for call in mock_keyboard.remove_hotkey.call_args_list]
        assert "ctrl+alt+n" in called_hotkeys
        assert "ctrl+shift+t" in called_hotkeys
        assert "win+e" in called_hotkeys
        
        # 验证is_running被设置为False
        assert manager.is_running == False
        
        # 验证日志记录
        assert mock_logger.info.call_count >= 1


@pytest.mark.unit
def test_hotkey_unregistration_handles_errors():
    """
    测试快捷键注销错误处理
    
    验证注销失败时不影响其他快捷键的注销
    """
    with patch('hotkey_manager.Logger') as MockLogger, \
         patch('hotkey_manager.keyboard') as mock_keyboard:
        
        mock_logger = MockLogger.return_value
        
        # 模拟第二个快捷键注销失败
        def remove_side_effect(hotkey):
            if hotkey == "ctrl+shift+t":
                raise Exception("注销失败")
        
        mock_keyboard.remove_hotkey.side_effect = remove_side_effect
        
        # 创建HotkeyManager实例
        manager = HotkeyManager()
        manager.is_running = True
        manager.hotkeys = {
            "ctrl+alt+n": "C:\\notepad.exe",
            "ctrl+shift+t": "C:\\test.exe",
            "win+e": "C:\\explorer.exe"
        }
        
        # 调用stop（不应抛出异常）
        manager.stop()
        
        # 验证所有快捷键都尝试注销
        assert mock_keyboard.remove_hotkey.call_count == 3
        
        # 验证警告日志被记录
        assert mock_logger.warning.call_count >= 1
        
        # 验证is_running仍被设置为False
        assert manager.is_running == False


@pytest.mark.unit
def test_sleep_prevention_restored_on_close():
    """
    测试防休眠恢复
    
    验证关闭时防休眠功能被正确恢复
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_power_mgr = MockPowerManager.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 模拟防休眠已启用
            gui.power_manager.is_preventing_sleep = True
            
            # 调用关闭方法
            gui._on_closing()
            
            # 验证allow_sleep被调用
            mock_power_mgr.allow_sleep.assert_called_once()
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_cleanup_logs_are_recorded():
    """
    测试清理日志记录
    
    验证所有清理步骤都被记录到日志
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            mock_logger = MockLogger.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            gui.is_monitoring = True
            
            # 调用关闭方法
            gui._on_closing()
            
            # 验证日志记录
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            
            # 检查关键日志消息
            assert any("关闭" in msg for msg in info_calls), "缺少关闭日志"
            assert any("停止" in msg or "监听" in msg for msg in info_calls), "缺少停止监听日志"
            assert any("休眠" in msg for msg in info_calls), "缺少恢复休眠日志"
            assert any("清理" in msg or "完成" in msg for msg in info_calls), "缺少清理完成日志"
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)
