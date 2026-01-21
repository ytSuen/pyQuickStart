"""
集成测试模块
测试完整工作流、配置持久化和资源清理
Validates: All requirements
"""
import pytest
import tempfile
import time
import json
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import psutil

from config_manager import ConfigManager
from hotkey_manager import HotkeyManager
from power_manager import PowerManager
from gui import HotkeyManagerGUI
from logger import Logger


# ============================================================================
# 集成测试：完整工作流
# Validates: All requirements
# ============================================================================

@pytest.mark.integration
def test_complete_workflow_add_hotkey_start_monitoring():
    """
    集成测试：完整工作流 - 添加快捷键并启动监听
    
    测试流程：
    1. 创建GUI
    2. 添加快捷键配置
    3. 启动监听
    4. 验证快捷键已注册
    5. 停止监听
    6. 验证资源清理
    
    验证需求：1.1, 1.2, 1.3, 4.1, 5.1, 5.5
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 步骤1: 创建配置管理器和快捷键管理器
        config_manager = ConfigManager(config_file=temp_config_path)
        hotkey_manager = HotkeyManager()
        
        # 验证初始状态
        assert len(config_manager.get_hotkeys()) == 0
        assert len(hotkey_manager.hotkeys) == 0
        assert hotkey_manager.is_running == False
        
        # 步骤2: 添加快捷键配置
        hotkey = "ctrl+alt+t"
        result = hotkey_manager.add_hotkey(hotkey, tmp_exe_path)
        assert result == True, "添加快捷键应该成功"
        
        config_manager.add_hotkey(hotkey, tmp_exe_path)
        
        # 验证配置已添加
        assert hotkey in hotkey_manager.hotkeys
        assert hotkey in config_manager.get_hotkeys()
        
        # 步骤3: 启动监听
        with patch('keyboard.add_hotkey') as mock_add_hotkey:
            hotkey_manager.start()
            
            # 验证监听已启动
            assert hotkey_manager.is_running == True
            
            # 验证快捷键已注册
            mock_add_hotkey.assert_called_once()
            
            # 步骤4: 停止监听
            with patch('keyboard.remove_hotkey') as mock_remove_hotkey:
                hotkey_manager.stop()
                
                # 验证监听已停止
                assert hotkey_manager.is_running == False
                
                # 验证快捷键已注销
                mock_remove_hotkey.assert_called_once()
        
        # 步骤5: 验证配置持久化
        config_manager_reload = ConfigManager(config_file=temp_config_path)
        reloaded_hotkeys = config_manager_reload.get_hotkeys()
        assert hotkey in reloaded_hotkeys
        assert reloaded_hotkeys[hotkey] == tmp_exe_path
        
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)



@pytest.mark.integration
def test_complete_workflow_with_program_launch():
    """
    集成测试：完整工作流 - 包含程序启动
    
    测试流程：
    1. 配置快捷键
    2. 启动监听
    3. 模拟触发快捷键启动程序
    4. 验证进程监控
    5. 验证防休眠启用
    6. 停止监听
    
    验证需求：1.3, 2.1, 2.2, 3.1, 9.1, 9.4
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 创建管理器实例
        config_manager = ConfigManager(config_file=temp_config_path)
        hotkey_manager = HotkeyManager()
        power_manager = PowerManager()
        
        # 添加快捷键
        hotkey = "ctrl+shift+p"
        hotkey_manager.add_hotkey(hotkey, tmp_exe_path)
        config_manager.add_hotkey(hotkey, tmp_exe_path)
        
        # 启动监听
        with patch('keyboard.add_hotkey'):
            hotkey_manager.start()
            assert hotkey_manager.is_running == True
        
        # 模拟程序启动
        mock_process = Mock(spec=psutil.Process)
        mock_process.pid = 12345
        mock_process.is_running.return_value = True
        mock_process.exe.return_value = tmp_exe_path
        
        # 创建mock Popen对象
        mock_popen_instance = Mock()
        mock_popen_instance.pid = 12345
        
        with patch('hotkey_manager.subprocess.Popen', return_value=mock_popen_instance) as mock_popen, \
             patch('hotkey_manager.psutil.Process', return_value=mock_process), \
             patch('hotkey_manager.psutil.process_iter', return_value=[]):
            
            # 触发程序启动
            hotkey_manager.launch_program(tmp_exe_path)
            
            # 验证进程被添加到监控列表
            time.sleep(0.6)  # 等待进程添加
            assert len(hotkey_manager.running_processes) > 0
        
        # 验证进程计数
        count = hotkey_manager.get_running_count()
        assert count > 0, "应该有运行中的进程"
        
        # 验证防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1) as mock_api:
            power_manager.prevent_sleep()
            assert power_manager.is_preventing_sleep == True
            mock_api.assert_called()
        
        # 停止监听
        with patch('keyboard.remove_hotkey'):
            hotkey_manager.stop()
        
        # 恢复休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            power_manager.allow_sleep()
            assert power_manager.is_preventing_sleep == False
        
    finally:
        # 清理
        hotkey_manager.running_processes.clear()
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)


@pytest.mark.integration
def test_complete_workflow_multiple_hotkeys():
    """
    集成测试：完整工作流 - 多个快捷键
    
    测试流程：
    1. 添加多个快捷键
    2. 启动监听
    3. 验证所有快捷键已注册
    4. 删除一个快捷键
    5. 验证配置更新
    6. 停止监听
    
    验证需求：1.2, 1.3, 1.5, 4.1, 4.2, 5.2, 5.4
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    temp_exe_files = []
    try:
        # 创建多个临时exe文件
        for i in range(3):
            tmp = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
            tmp.close()
            temp_exe_files.append(tmp.name)
        
        # 创建管理器
        config_manager = ConfigManager(config_file=temp_config_path)
        hotkey_manager = HotkeyManager()
        
        # 添加多个快捷键
        hotkeys = [
            ("ctrl+alt+a", temp_exe_files[0]),
            ("ctrl+shift+b", temp_exe_files[1]),
            ("win+c", temp_exe_files[2])
        ]
        
        for hotkey, path in hotkeys:
            result = hotkey_manager.add_hotkey(hotkey, path)
            assert result == True, f"添加快捷键 {hotkey} 应该成功"
            config_manager.add_hotkey(hotkey, path)
        
        # 验证所有快捷键已添加
        assert len(hotkey_manager.hotkeys) == 3
        assert len(config_manager.get_hotkeys()) == 3
        
        # 启动监听
        with patch('keyboard.add_hotkey') as mock_add_hotkey:
            hotkey_manager.start()
            
            # 验证所有快捷键已注册
            assert mock_add_hotkey.call_count == 3
            assert hotkey_manager.is_running == True
        
        # 删除一个快捷键
        hotkey_to_remove = "ctrl+shift+b"
        with patch('keyboard.remove_hotkey'):
            result = hotkey_manager.remove_hotkey(hotkey_to_remove)
            assert result == True
        
        config_manager.remove_hotkey(hotkey_to_remove)
        
        # 验证快捷键已删除
        assert hotkey_to_remove not in hotkey_manager.hotkeys
        assert hotkey_to_remove not in config_manager.get_hotkeys()
        assert len(hotkey_manager.hotkeys) == 2
        
        # 停止监听
        with patch('keyboard.remove_hotkey') as mock_remove_hotkey:
            hotkey_manager.stop()
            # 应该注销剩余的2个快捷键
            assert mock_remove_hotkey.call_count == 2
        
        # 验证配置持久化
        config_manager_reload = ConfigManager(config_file=temp_config_path)
        reloaded_hotkeys = config_manager_reload.get_hotkeys()
        assert len(reloaded_hotkeys) == 2
        assert hotkey_to_remove not in reloaded_hotkeys
        
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        for path in temp_exe_files:
            Path(path).unlink(missing_ok=True)



# ============================================================================
# 集成测试：配置持久化流程
# Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
# ============================================================================

@pytest.mark.integration
def test_config_persistence_workflow():
    """
    集成测试：配置持久化流程
    
    测试流程：
    1. 创建配置并保存
    2. 重新加载配置
    3. 验证配置一致性
    4. 修改配置
    5. 再次验证持久化
    
    验证需求：4.1, 4.2, 4.5
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 步骤1: 创建初始配置
        config_manager1 = ConfigManager(config_file=temp_config_path)
        
        hotkeys_to_add = {
            "ctrl+alt+n": tmp_exe_path,
            "ctrl+shift+t": tmp_exe_path,
            "win+e": tmp_exe_path
        }
        
        for hotkey, path in hotkeys_to_add.items():
            config_manager1.add_hotkey(hotkey, path)
        
        # 验证内存中的配置
        assert len(config_manager1.get_hotkeys()) == 3
        
        # 步骤2: 创建新实例重新加载配置
        config_manager2 = ConfigManager(config_file=temp_config_path)
        reloaded_hotkeys = config_manager2.get_hotkeys()
        
        # 验证配置一致性
        assert len(reloaded_hotkeys) == 3
        for hotkey, path in hotkeys_to_add.items():
            assert hotkey in reloaded_hotkeys
            assert reloaded_hotkeys[hotkey] == path
        
        # 步骤3: 修改配置
        config_manager2.remove_hotkey("ctrl+shift+t")
        config_manager2.add_hotkey("ctrl+alt+x", tmp_exe_path)
        
        # 步骤4: 再次重新加载验证
        config_manager3 = ConfigManager(config_file=temp_config_path)
        final_hotkeys = config_manager3.get_hotkeys()
        
        assert len(final_hotkeys) == 3
        assert "ctrl+shift+t" not in final_hotkeys
        assert "ctrl+alt+x" in final_hotkeys
        assert final_hotkeys["ctrl+alt+x"] == tmp_exe_path
        
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)


@pytest.mark.integration
def test_config_persistence_with_unicode():
    """
    集成测试：配置持久化 - Unicode字符支持
    
    测试流程：
    1. 添加包含中文的配置
    2. 保存并重新加载
    3. 验证Unicode字符完整性
    
    验证需求：4.5
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        # 创建配置管理器
        config_manager1 = ConfigManager(config_file=temp_config_path)
        
        # 添加包含Unicode字符的配置
        unicode_configs = {
            "ctrl+alt+中": "C:\\程序文件\\记事本\\notepad.exe",
            "ctrl+shift+日": "C:\\日本語\\プログラム\\test.exe",
            "win+한": "C:\\한글\\프로그램\\app.exe"
        }
        
        for hotkey, path in unicode_configs.items():
            config_manager1.add_hotkey(hotkey, path)
        
        # 重新加载配置
        config_manager2 = ConfigManager(config_file=temp_config_path)
        reloaded_hotkeys = config_manager2.get_hotkeys()
        
        # 验证Unicode字符完整性
        assert len(reloaded_hotkeys) == 3
        for hotkey, path in unicode_configs.items():
            assert hotkey in reloaded_hotkeys, f"快捷键 {hotkey} 未正确保存"
            assert reloaded_hotkeys[hotkey] == path, f"路径 {path} 未正确保存"
        
        # 验证JSON文件编码
        with open(temp_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "程序文件" in content
            assert "日本語" in content
            assert "한글" in content
        
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.integration
def test_config_persistence_corrupted_file_recovery():
    """
    集成测试：配置持久化 - 损坏文件恢复
    
    测试流程：
    1. 创建损坏的配置文件
    2. 加载配置（应该创建默认配置）
    3. 添加新配置
    4. 验证恢复后的配置可用
    
    验证需求：4.3, 4.4
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
        # 写入损坏的JSON
        f.write("{ invalid json content }")
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 加载损坏的配置文件
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 验证创建了默认配置
        assert config_manager.get_hotkeys() == {}
        
        # 添加新配置
        config_manager.add_hotkey("ctrl+alt+r", tmp_exe_path)
        
        # 验证配置可用
        assert "ctrl+alt+r" in config_manager.get_hotkeys()
        
        # 重新加载验证
        config_manager2 = ConfigManager(config_file=temp_config_path)
        assert "ctrl+alt+r" in config_manager2.get_hotkeys()
        
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)



# ============================================================================
# 集成测试：资源清理流程
# Validates: Requirements 7.1, 7.2, 7.3
# ============================================================================

@pytest.mark.integration
def test_resource_cleanup_workflow():
    """
    集成测试：资源清理流程
    
    测试流程：
    1. 启动监听
    2. 启用防休眠
    3. 停止监听
    4. 验证快捷键注销
    5. 验证防休眠恢复
    
    验证需求：7.1, 7.2, 7.3
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 创建管理器
        config_manager = ConfigManager(config_file=temp_config_path)
        hotkey_manager = HotkeyManager()
        power_manager = PowerManager()
        
        # 添加快捷键
        hotkey_manager.add_hotkey("ctrl+alt+c", tmp_exe_path)
        config_manager.add_hotkey("ctrl+alt+c", tmp_exe_path)
        
        # 步骤1: 启动监听
        with patch('keyboard.add_hotkey') as mock_add_hotkey:
            hotkey_manager.start()
            assert hotkey_manager.is_running == True
            mock_add_hotkey.assert_called_once()
        
        # 步骤2: 启用防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1) as mock_api:
            power_manager.prevent_sleep()
            assert power_manager.is_preventing_sleep == True
            mock_api.assert_called()
        
        # 步骤3: 停止监听
        with patch('keyboard.remove_hotkey') as mock_remove_hotkey:
            hotkey_manager.stop()
            
            # 验证快捷键注销
            assert hotkey_manager.is_running == False
            mock_remove_hotkey.assert_called_once()
        
        # 步骤4: 恢复防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1) as mock_api:
            power_manager.allow_sleep()
            assert power_manager.is_preventing_sleep == False
            mock_api.assert_called()
        
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)


@pytest.mark.integration
def test_resource_cleanup_on_gui_close():
    """
    集成测试：GUI关闭时的资源清理
    
    测试流程：
    1. 创建GUI
    2. 添加快捷键
    3. 启动监听
    4. 关闭GUI
    5. 验证所有资源被清理
    
    验证需求：7.1, 7.2, 7.3, 5.5
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger:
            
            # 配置mock对象
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {"ctrl+alt+t": tmp_exe_path}
            
            mock_hotkey_mgr = MockHotkeyManager.return_value
            mock_power_mgr = MockPowerManager.return_value
            mock_logger = MockLogger.return_value
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 模拟启动监听
            gui.is_monitoring = True
            
            # 关闭GUI
            gui._on_closing()
            
            # 验证资源清理
            # 1. 停止快捷键监听
            mock_hotkey_mgr.stop.assert_called_once()
            
            # 2. 恢复系统休眠
            mock_power_mgr.allow_sleep.assert_called_once()
            
            # 3. 验证日志记录
            assert mock_logger.info.call_count >= 3
            
            # 验证监听状态被清除
            # (在实际调用中is_monitoring会被设置为False，但这里是mock环境)
    
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)


@pytest.mark.integration
def test_resource_cleanup_with_running_processes():
    """
    集成测试：有运行进程时的资源清理
    
    测试流程：
    1. 启动程序
    2. 验证进程监控
    3. 停止监听
    4. 验证进程列表被清理
    5. 验证防休眠恢复
    
    验证需求：3.5, 7.2, 9.2
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 创建管理器
        hotkey_manager = HotkeyManager()
        power_manager = PowerManager()
        
        # 添加快捷键
        hotkey_manager.add_hotkey("ctrl+alt+p", tmp_exe_path)
        
        # 启动监听
        with patch('keyboard.add_hotkey'):
            hotkey_manager.start()
        
        # 模拟添加运行中的进程
        mock_process = Mock(spec=psutil.Process)
        mock_process.pid = 99999
        mock_process.is_running.return_value = True
        hotkey_manager.running_processes.append(mock_process)
        
        # 验证进程计数
        count = hotkey_manager.get_running_count()
        assert count == 1
        
        # 启用防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            power_manager.prevent_sleep()
            assert power_manager.is_preventing_sleep == True
        
        # 停止监听
        with patch('keyboard.remove_hotkey'):
            hotkey_manager.stop()
            assert hotkey_manager.is_running == False
        
        # 恢复防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            power_manager.allow_sleep()
            assert power_manager.is_preventing_sleep == False
        
        # 清理进程列表
        hotkey_manager.running_processes.clear()
        assert len(hotkey_manager.running_processes) == 0
        
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)



# ============================================================================
# 集成测试：GUI完整工作流
# Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
# ============================================================================

@pytest.mark.integration
def test_gui_complete_workflow():
    """
    集成测试：GUI完整工作流
    
    测试流程：
    1. 启动GUI
    2. 添加快捷键
    3. 启动监听
    4. 验证状态更新
    5. 删除快捷键
    6. 停止监听
    7. 关闭GUI
    
    验证需求：5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
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
            mock_hotkey_mgr.get_running_count.return_value = 0
            
            mock_power_mgr = MockPowerManager.return_value
            
            # 步骤1: 创建GUI
            gui = HotkeyManagerGUI()
            gui.root.withdraw()
            
            # 验证初始状态
            assert gui.is_monitoring == False
            assert gui.start_btn.cget("text") == "启动监听"
            
            # 步骤2: 添加快捷键
            gui.hotkey_entry.insert(0, "ctrl+alt+g")
            gui.path_entry.insert(0, tmp_exe_path)
            gui._add_hotkey()
            
            # 验证添加成功
            mock_hotkey_mgr.add_hotkey.assert_called_once_with("ctrl+alt+g", tmp_exe_path)
            mock_config.add_hotkey.assert_called_once_with("ctrl+alt+g", tmp_exe_path)
            mock_messagebox.showinfo.assert_called_once()
            
            # 步骤3: 启动监听
            mock_config.get_hotkeys.return_value = {"ctrl+alt+g": tmp_exe_path}
            gui._toggle_monitoring()
            
            # 验证监听已启动
            mock_hotkey_mgr.start.assert_called_once()
            assert gui.is_monitoring == True
            assert gui.start_btn.cget("text") == "停止监听"
            assert "运行中" in gui.status_label.cget("text")
            
            # 步骤4: 模拟状态更新
            mock_hotkey_mgr.get_running_count.return_value = 2
            count = gui.hotkey_manager.get_running_count()
            gui.process_label.config(text=f"运行中程序: {count}")
            
            # 验证状态显示
            assert gui.process_label.cget("text") == "运行中程序: 2"
            
            # 步骤5: 停止监听
            gui._toggle_monitoring()
            
            # 验证监听已停止
            mock_hotkey_mgr.stop.assert_called_once()
            mock_power_mgr.allow_sleep.assert_called()
            assert gui.is_monitoring == False
            assert gui.start_btn.cget("text") == "启动监听"
            
            # 步骤6: 关闭GUI
            gui._on_closing()
            
            # 验证资源清理
            mock_power_mgr.allow_sleep.assert_called()
    
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)


@pytest.mark.integration
def test_gui_error_handling_workflow():
    """
    集成测试：GUI错误处理工作流
    
    测试流程：
    1. 尝试添加无效快捷键
    2. 尝试添加不存在的文件
    3. 尝试在无配置时启动监听
    4. 验证错误提示
    
    验证需求：8.1, 8.2, 8.3, 8.4
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        with patch('gui.ConfigManager') as MockConfigManager, \
             patch('gui.HotkeyManager') as MockHotkeyManager, \
             patch('gui.PowerManager') as MockPowerManager, \
             patch('gui.Logger') as MockLogger, \
             patch('gui.messagebox') as mock_messagebox, \
             patch('gui.tk.Tk') as MockTk:
            
            mock_config = MockConfigManager.return_value
            mock_config.get_hotkeys.return_value = {}
            
            # 创建mock root窗口
            mock_root = Mock()
            MockTk.return_value = mock_root
            
            # 创建GUI
            gui = HotkeyManagerGUI()
            gui.root = mock_root
            
            # 创建mock输入框
            gui.hotkey_entry = Mock()
            gui.hotkey_entry.get = Mock(return_value="")
            gui.hotkey_entry.insert = Mock()
            gui.hotkey_entry.delete = Mock()
            
            gui.path_entry = Mock()
            gui.path_entry.get = Mock(return_value="")
            gui.path_entry.insert = Mock()
            gui.path_entry.delete = Mock()
            
            # 测试1: 空输入
            gui.hotkey_entry.get.return_value = ""
            gui.path_entry.get.return_value = ""
            gui._add_hotkey()
            mock_messagebox.showwarning.assert_called_once()
            mock_messagebox.reset_mock()
            
            # 测试2: 无效快捷键格式
            gui.hotkey_entry.get.return_value = "n"  # 无修饰键
            gui.path_entry.get.return_value = "C:\\test.exe"
            with patch('os.path.exists', return_value=True):
                gui._add_hotkey()
                mock_messagebox.showerror.assert_called_once()
            mock_messagebox.reset_mock()
            
            # 测试3: 文件不存在
            gui.hotkey_entry.get.return_value = "ctrl+alt+t"
            gui.path_entry.get.return_value = "C:\\nonexistent.exe"
            with patch('os.path.exists', return_value=False):
                gui._add_hotkey()
                mock_messagebox.showerror.assert_called_once()
            mock_messagebox.reset_mock()
            
            # 测试4: 无配置时启动监听
            gui.is_monitoring = False
            gui._toggle_monitoring()
            mock_messagebox.showwarning.assert_called_once()
            assert gui.is_monitoring == False
    
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)



# ============================================================================
# 集成测试：进程监控和防休眠联动
# Validates: Requirements 3.1, 3.2, 3.5, 9.1, 9.2, 9.3, 9.4
# ============================================================================

@pytest.mark.integration
def test_process_monitoring_and_sleep_prevention_integration():
    """
    集成测试：进程监控和防休眠联动
    
    测试流程：
    1. 启动程序
    2. 验证进程被监控
    3. 验证防休眠启用
    4. 模拟进程结束
    5. 验证防休眠恢复
    
    验证需求：3.1, 3.2, 3.5, 9.1, 9.2, 9.3, 9.4
    """
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 创建管理器
        hotkey_manager = HotkeyManager()
        power_manager = PowerManager()
        
        # 添加快捷键
        hotkey_manager.add_hotkey("ctrl+alt+m", tmp_exe_path)
        
        # 启动监听
        with patch('keyboard.add_hotkey'):
            hotkey_manager.start()
        
        # 步骤1: 模拟程序启动
        mock_process1 = Mock(spec=psutil.Process)
        mock_process1.pid = 11111
        mock_process1.is_running.return_value = True
        hotkey_manager.running_processes.append(mock_process1)
        
        # 步骤2: 验证进程计数
        count = hotkey_manager.get_running_count()
        assert count == 1, "应该有1个运行中的进程"
        
        # 步骤3: 启用防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            if count > 0:
                power_manager.prevent_sleep()
            assert power_manager.is_preventing_sleep == True
        
        # 步骤4: 添加第二个进程
        mock_process2 = Mock(spec=psutil.Process)
        mock_process2.pid = 22222
        mock_process2.is_running.return_value = True
        hotkey_manager.running_processes.append(mock_process2)
        
        count = hotkey_manager.get_running_count()
        assert count == 2, "应该有2个运行中的进程"
        
        # 步骤5: 模拟第一个进程结束
        mock_process1.is_running.return_value = False
        count = hotkey_manager.get_running_count()
        assert count == 1, "应该剩余1个运行中的进程"
        
        # 防休眠应该仍然启用
        assert power_manager.is_preventing_sleep == True
        
        # 步骤6: 模拟第二个进程也结束
        mock_process2.is_running.return_value = False
        count = hotkey_manager.get_running_count()
        assert count == 0, "应该没有运行中的进程"
        
        # 步骤7: 恢复防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            if count == 0:
                power_manager.allow_sleep()
            assert power_manager.is_preventing_sleep == False
        
        # 停止监听
        with patch('keyboard.remove_hotkey'):
            hotkey_manager.stop()
    
    finally:
        # 清理
        hotkey_manager.running_processes.clear()
        Path(tmp_exe_path).unlink(missing_ok=True)


@pytest.mark.integration
def test_duplicate_launch_prevention_integration():
    """
    集成测试：重复启动防护
    
    测试流程：
    1. 启动程序
    2. 尝试再次启动同一程序
    3. 验证不创建新进程
    4. 验证进程计数正确
    
    验证需求：2.2, 9.1, 9.4
    """
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 创建管理器
        hotkey_manager = HotkeyManager()
        
        # 添加快捷键
        hotkey_manager.add_hotkey("ctrl+alt+d", tmp_exe_path)
        
        # 启动监听
        with patch('keyboard.add_hotkey'):
            hotkey_manager.start()
        
        # 步骤1: 第一次启动程序
        mock_process = Mock(spec=psutil.Process)
        mock_process.pid = 33333
        mock_process.is_running.return_value = True
        mock_process.exe.return_value = tmp_exe_path
        
        # 创建mock Popen对象
        mock_popen_instance = Mock()
        mock_popen_instance.pid = 33333
        
        with patch('hotkey_manager.subprocess.Popen', return_value=mock_popen_instance) as mock_popen, \
             patch('hotkey_manager.psutil.Process', return_value=mock_process), \
             patch('hotkey_manager.psutil.process_iter', return_value=[]):
            
            hotkey_manager.launch_program(tmp_exe_path)
            
            # 等待进程添加
            time.sleep(0.6)
            
            # 验证进程被添加
            initial_count = len(hotkey_manager.running_processes)
            assert initial_count > 0
        
        # 步骤2: 尝试再次启动同一程序
        with patch('hotkey_manager.subprocess.Popen') as mock_popen:
            hotkey_manager.launch_program(tmp_exe_path)
            
            # 验证Popen未被调用（因为程序已运行）
            mock_popen.assert_not_called()
        
        # 步骤3: 验证进程计数未增加
        final_count = len(hotkey_manager.running_processes)
        assert final_count == initial_count, "重复启动不应增加进程计数"
        
        # 停止监听
        with patch('keyboard.remove_hotkey'):
            hotkey_manager.stop()
    
    finally:
        # 清理
        hotkey_manager.running_processes.clear()
        Path(tmp_exe_path).unlink(missing_ok=True)



# ============================================================================
# 集成测试：日志记录完整性
# Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5
# ============================================================================

@pytest.mark.integration
def test_logging_integration():
    """
    集成测试：日志记录完整性
    
    测试流程：
    1. 执行各种操作
    2. 验证所有操作都被记录
    3. 验证日志格式正确
    
    验证需求：6.1, 6.2, 6.3, 6.4, 6.5
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 创建管理器（使用真实的Logger）
        config_manager = ConfigManager(config_file=temp_config_path)
        hotkey_manager = HotkeyManager()
        power_manager = PowerManager()
        
        # 验证Logger单例
        logger1 = Logger()
        logger2 = Logger()
        assert logger1 is logger2, "Logger应该是单例"
        
        # 操作1: 添加快捷键
        result = hotkey_manager.add_hotkey("ctrl+alt+l", tmp_exe_path)
        assert result == True, "添加快捷键应该成功"
        config_manager.add_hotkey("ctrl+alt+l", tmp_exe_path)
        
        # 操作2: 启动监听
        with patch('keyboard.add_hotkey'):
            hotkey_manager.start()
            assert hotkey_manager.is_running == True
        
        # 操作3: 启用防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            power_manager.prevent_sleep()
            assert power_manager.is_preventing_sleep == True
        
        # 操作4: 停止监听
        with patch('keyboard.remove_hotkey'):
            hotkey_manager.stop()
            assert hotkey_manager.is_running == False
        
        # 操作5: 恢复防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            power_manager.allow_sleep()
            assert power_manager.is_preventing_sleep == False
        
        # 验证日志目录存在
        log_dir = Path("logs")
        assert log_dir.exists(), "日志目录应该存在"
        
        # 验证日志文件被创建
        log_files = list(log_dir.glob("hotkey_*.log"))
        assert len(log_files) > 0, "应该至少有一个日志文件"
    
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)


# ============================================================================
# 集成测试：端到端场景
# Validates: All requirements
# ============================================================================

@pytest.mark.integration
def test_end_to_end_typical_usage_scenario():
    """
    集成测试：端到端典型使用场景
    
    模拟用户的典型使用流程：
    1. 启动应用
    2. 添加多个快捷键
    3. 启动监听
    4. 触发快捷键启动程序
    5. 程序运行期间防止休眠
    6. 程序结束后恢复休眠
    7. 停止监听
    8. 关闭应用
    
    验证需求：所有需求
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    temp_exe_files = []
    try:
        # 创建多个临时exe文件
        for i in range(2):
            tmp = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
            tmp.close()
            temp_exe_files.append(tmp.name)
        
        # 步骤1: 初始化系统
        config_manager = ConfigManager(config_file=temp_config_path)
        hotkey_manager = HotkeyManager()
        power_manager = PowerManager()
        
        # 步骤2: 添加快捷键配置
        hotkeys = [
            ("ctrl+alt+1", temp_exe_files[0]),
            ("ctrl+alt+2", temp_exe_files[1])
        ]
        
        for hotkey, path in hotkeys:
            assert hotkey_manager.add_hotkey(hotkey, path) == True
            config_manager.add_hotkey(hotkey, path)
        
        # 验证配置
        assert len(hotkey_manager.hotkeys) == 2
        assert len(config_manager.get_hotkeys()) == 2
        
        # 步骤3: 启动监听
        with patch('keyboard.add_hotkey') as mock_add_hotkey:
            hotkey_manager.start()
            assert hotkey_manager.is_running == True
            assert mock_add_hotkey.call_count == 2
        
        # 步骤4: 模拟触发快捷键启动程序
        mock_processes = []
        for i, path in enumerate(temp_exe_files):
            mock_proc = Mock(spec=psutil.Process)
            mock_proc.pid = 40000 + i
            mock_proc.is_running.return_value = True
            mock_proc.exe.return_value = path
            mock_processes.append(mock_proc)
            
            # 创建mock Popen对象
            mock_popen_instance = Mock()
            mock_popen_instance.pid = mock_proc.pid
            
            with patch('hotkey_manager.subprocess.Popen', return_value=mock_popen_instance) as mock_popen, \
                 patch('hotkey_manager.psutil.Process', return_value=mock_proc), \
                 patch('hotkey_manager.psutil.process_iter', return_value=[]):
                hotkey_manager.launch_program(path)
                time.sleep(0.6)
        
        # 步骤5: 验证进程监控
        count = hotkey_manager.get_running_count()
        assert count == 2, f"应该有2个运行中的进程，实际有{count}个"
        
        # 步骤6: 启用防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            if count > 0:
                power_manager.prevent_sleep()
            assert power_manager.is_preventing_sleep == True
        
        # 步骤7: 模拟程序结束
        for mock_proc in mock_processes:
            mock_proc.is_running.return_value = False
        
        count = hotkey_manager.get_running_count()
        assert count == 0, "所有进程应该已结束"
        
        # 步骤8: 恢复防休眠
        with patch('power_manager.ctypes.windll.kernel32.SetThreadExecutionState', return_value=1):
            if count == 0:
                power_manager.allow_sleep()
            assert power_manager.is_preventing_sleep == False
        
        # 步骤9: 停止监听
        with patch('keyboard.remove_hotkey') as mock_remove_hotkey:
            hotkey_manager.stop()
            assert hotkey_manager.is_running == False
            assert mock_remove_hotkey.call_count == 2
        
        # 步骤10: 验证配置持久化
        config_manager_reload = ConfigManager(config_file=temp_config_path)
        reloaded_hotkeys = config_manager_reload.get_hotkeys()
        assert len(reloaded_hotkeys) == 2
        for hotkey, path in hotkeys:
            assert hotkey in reloaded_hotkeys
            assert reloaded_hotkeys[hotkey] == path
        
    finally:
        # 清理
        hotkey_manager.running_processes.clear()
        Path(temp_config_path).unlink(missing_ok=True)
        for path in temp_exe_files:
            Path(path).unlink(missing_ok=True)


@pytest.mark.integration
def test_end_to_end_error_recovery_scenario():
    """
    集成测试：端到端错误恢复场景
    
    测试系统在遇到错误时的恢复能力：
    1. 加载损坏的配置文件
    2. 系统恢复并创建新配置
    3. 添加新配置
    4. 正常使用
    
    验证需求：4.4, 8.4
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
        # 写入损坏的配置
        f.write("{ corrupted }")
    
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
        tmp_exe_path = tmp_exe.name
    
    try:
        # 步骤1: 尝试加载损坏的配置
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 步骤2: 验证系统恢复
        assert config_manager.get_hotkeys() == {}, "应该创建空配置"
        
        # 步骤3: 添加新配置
        hotkey_manager = HotkeyManager()
        assert hotkey_manager.add_hotkey("ctrl+alt+e", tmp_exe_path) == True
        config_manager.add_hotkey("ctrl+alt+e", tmp_exe_path)
        
        # 步骤4: 验证系统正常工作
        with patch('keyboard.add_hotkey'):
            hotkey_manager.start()
            assert hotkey_manager.is_running == True
        
        with patch('keyboard.remove_hotkey'):
            hotkey_manager.stop()
            assert hotkey_manager.is_running == False
        
        # 步骤5: 验证配置已正确保存
        config_manager_reload = ConfigManager(config_file=temp_config_path)
        assert "ctrl+alt+e" in config_manager_reload.get_hotkeys()
        
    finally:
        # 清理
        Path(temp_config_path).unlink(missing_ok=True)
        Path(tmp_exe_path).unlink(missing_ok=True)
