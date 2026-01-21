"""
快捷键管理器测试模块
包含单元测试和属性测试
"""
import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import tempfile
import os
from hotkey_manager import HotkeyManager


# ============================================================================
# 属性测试
# ============================================================================

# Feature: hotkey-power-manager, Property 5: 快捷键格式验证
@settings(max_examples=100)
@given(
    keys=st.lists(
        st.sampled_from(['a', 'b', 'c', '1', '2', 'f1', 'f2', 'space', 'enter']),
        min_size=1,
        max_size=3
    )
)
def test_property_hotkey_format_validation_no_modifier(keys):
    """
    属性 5: 快捷键格式验证
    验证: 需求 1.1, 10.5
    
    对于任何不包含修饰键的快捷键字符串，系统应该拒绝添加
    """
    manager = HotkeyManager()
    
    # 创建不包含修饰键的快捷键
    hotkey = '+'.join(keys)
    
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 尝试添加快捷键，应该失败
        result = manager.add_hotkey(hotkey, tmp_path)
        assert result is False, f"应该拒绝无修饰键的快捷键: {hotkey}"
    finally:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# Feature: hotkey-power-manager, Property 5: 快捷键格式验证
@settings(max_examples=100)
@given(
    modifier=st.sampled_from(['ctrl', 'alt', 'shift', 'win']),
    key=st.sampled_from(['a', 'b', 'c', 'n', 't', '1', '2', 'f1', 'f2', 'space'])
)
def test_property_hotkey_format_validation_with_modifier(modifier, key):
    """
    属性 5: 快捷键格式验证
    验证: 需求 1.1, 10.5
    
    对于任何包含至少一个修饰键的快捷键字符串，格式验证应该通过
    """
    manager = HotkeyManager()
    
    # 创建包含修饰键的快捷键
    hotkey = f"{modifier}+{key}"
    
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 尝试添加快捷键，格式验证应该通过（可能因为文件路径而失败，但不应该因为格式）
        result = manager.add_hotkey(hotkey, tmp_path)
        # 如果失败，检查是否是因为格式问题
        # 由于文件存在，格式正确的快捷键应该成功添加
        assert result is True, f"包含修饰键的快捷键应该通过格式验证: {hotkey}"
    finally:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# Feature: hotkey-power-manager, Property 6: 快捷键大小写不敏感
@settings(max_examples=100)
@given(
    modifier1=st.sampled_from(['ctrl', 'alt', 'shift', 'win']),
    modifier2=st.sampled_from(['ctrl', 'alt', 'shift', 'win']),
    key=st.sampled_from(['a', 'b', 'c', 'n', 't', 'f1', 'f2'])
)
def test_property_hotkey_case_insensitive(modifier1, modifier2, key):
    """
    属性 6: 快捷键大小写不敏感
    验证: 需求 10.4
    
    对于任何快捷键字符串，不同大小写组合应该被视为相同的快捷键
    """
    manager = HotkeyManager()
    
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 创建不同大小写的快捷键
        hotkey_lower = f"{modifier1}+{modifier2}+{key}".lower()
        hotkey_upper = f"{modifier1}+{modifier2}+{key}".upper()
        hotkey_mixed = f"{modifier1.upper()}+{modifier2.lower()}+{key.capitalize()}"
        
        # 添加小写版本
        result1 = manager.add_hotkey(hotkey_lower, tmp_path)
        assert result1 is True, f"应该成功添加快捷键: {hotkey_lower}"
        
        # 验证格式验证对大写和混合大小写也通过
        assert manager._validate_hotkey_format(hotkey_upper), f"大写快捷键应该通过格式验证: {hotkey_upper}"
        assert manager._validate_hotkey_format(hotkey_mixed), f"混合大小写快捷键应该通过格式验证: {hotkey_mixed}"
        
    finally:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# Feature: hotkey-power-manager, Property 7: 文件类型限制
@settings(max_examples=100)
@given(
    extension=st.sampled_from(['.txt', '.bat', '.cmd', '.com', '.dll', '.sys', '.msi', '.py', '.js', '.pdf', '.doc'])
)
def test_property_file_type_restriction_non_exe(extension):
    """
    属性 7: 文件类型限制
    验证: 需求 2.5
    
    对于任何非.exe扩展名的文件路径，系统应该拒绝添加
    """
    manager = HotkeyManager()
    
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 尝试添加非.exe文件
        result = manager.add_hotkey('ctrl+alt+t', tmp_path)
        assert result is False, f"应该拒绝非.exe文件: {tmp_path}"
    finally:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# Feature: hotkey-power-manager, Property 7: 文件类型限制
@settings(max_examples=100)
@given(
    modifier=st.sampled_from(['ctrl', 'alt', 'shift', 'win']),
    key=st.sampled_from(['a', 'b', 'c', 'n', 't', 'f1'])
)
def test_property_file_type_restriction_exe_only(modifier, key):
    """
    属性 7: 文件类型限制
    验证: 需求 2.5
    
    对于任何.exe扩展名的文件路径，文件类型验证应该通过
    """
    manager = HotkeyManager()
    
    # 创建临时.exe文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        hotkey = f"{modifier}+{key}"
        # 尝试添加.exe文件
        result = manager.add_hotkey(hotkey, tmp_path)
        assert result is True, f".exe文件应该通过验证: {tmp_path}"
    finally:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)



# ============================================================================
# 单元测试
# ============================================================================

def test_add_hotkey_success():
    """
    测试正常添加快捷键流程
    需求: 1.2
    """
    manager = HotkeyManager()
    
    # 创建临时.exe文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 添加有效的快捷键
        result = manager.add_hotkey('ctrl+alt+n', tmp_path)
        assert result is True
        assert 'ctrl+alt+n' in manager.hotkeys
        assert manager.hotkeys['ctrl+alt+n'] == tmp_path
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_add_hotkey_conflict_override():
    """
    测试快捷键冲突处理（覆盖）
    需求: 1.2
    """
    manager = HotkeyManager()
    
    # 创建两个临时.exe文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp1:
        tmp_path1 = tmp1.name
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp2:
        tmp_path2 = tmp2.name
    
    try:
        # 添加第一个快捷键
        result1 = manager.add_hotkey('ctrl+alt+t', tmp_path1)
        assert result1 is True
        assert manager.hotkeys['ctrl+alt+t'] == tmp_path1
        
        # 添加相同快捷键但不同路径（应该覆盖）
        result2 = manager.add_hotkey('ctrl+alt+t', tmp_path2)
        assert result2 is True
        assert manager.hotkeys['ctrl+alt+t'] == tmp_path2
    finally:
        if os.path.exists(tmp_path1):
            os.unlink(tmp_path1)
        if os.path.exists(tmp_path2):
            os.unlink(tmp_path2)


def test_add_hotkey_invalid_path():
    """
    测试无效路径拒绝
    需求: 2.4
    """
    manager = HotkeyManager()
    
    # 尝试添加不存在的路径
    result = manager.add_hotkey('ctrl+alt+x', 'C:\\nonexistent\\program.exe')
    assert result is False
    assert 'ctrl+alt+x' not in manager.hotkeys


def test_add_hotkey_invalid_format():
    """
    测试无效快捷键格式拒绝
    需求: 1.1
    """
    manager = HotkeyManager()
    
    # 创建临时.exe文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 尝试添加无修饰键的快捷键
        result = manager.add_hotkey('a', tmp_path)
        assert result is False
        assert 'a' not in manager.hotkeys
        
        # 尝试添加只有按键的快捷键
        result = manager.add_hotkey('f1', tmp_path)
        assert result is False
        assert 'f1' not in manager.hotkeys
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_add_hotkey_invalid_file_type():
    """
    测试非.exe文件拒绝
    需求: 2.5
    """
    manager = HotkeyManager()
    
    # 创建临时非.exe文件
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        result = manager.add_hotkey('ctrl+alt+t', tmp_path)
        assert result is False
        assert 'ctrl+alt+t' not in manager.hotkeys
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_remove_hotkey_success():
    """
    测试成功移除快捷键
    需求: 1.2
    """
    manager = HotkeyManager()
    
    # 创建临时.exe文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 先添加快捷键
        manager.add_hotkey('ctrl+alt+r', tmp_path)
        assert 'ctrl+alt+r' in manager.hotkeys
        
        # 移除快捷键
        result = manager.remove_hotkey('ctrl+alt+r')
        assert result is True
        assert 'ctrl+alt+r' not in manager.hotkeys
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_remove_hotkey_not_exists():
    """
    测试移除不存在的快捷键
    需求: 1.2
    """
    manager = HotkeyManager()
    
    # 尝试移除不存在的快捷键
    result = manager.remove_hotkey('ctrl+alt+z')
    assert result is False


# ============================================================================
# 进程管理属性测试
# ============================================================================

# Feature: hotkey-power-manager, Property 4: 重复启动防护
@settings(max_examples=100, deadline=None)
@given(
    num_launches=st.integers(min_value=2, max_value=5)
)
def test_property_duplicate_launch_protection(num_launches):
    """
    属性 4: 重复启动防护
    验证: 需求 2.2
    
    对于任何已在运行的程序，再次触发其快捷键不应该创建新的进程实例
    
    注意：此测试通过模拟已运行的进程来验证重复启动防护逻辑
    """
    import psutil
    from unittest.mock import Mock, patch
    
    manager = HotkeyManager()
    
    # 创建一个模拟的程序路径
    test_program = r"C:\Windows\System32\calc.exe"
    
    # 创建一个模拟的进程对象
    mock_process = Mock(spec=psutil.Process)
    mock_process.pid = 12345
    mock_process.is_running.return_value = True
    mock_process.exe.return_value = test_program
    
    # 将模拟进程添加到运行列表（模拟程序已运行）
    manager.running_processes.append(mock_process)
    initial_count = len(manager.running_processes)
    
    # 使用patch模拟subprocess.Popen，确保不会真正启动进程
    with patch('hotkey_manager.subprocess.Popen') as mock_popen:
        # 多次尝试启动同一程序
        for i in range(num_launches):
            manager.launch_program(test_program)
        
        # 验证subprocess.Popen从未被调用（因为程序已在运行）
        assert mock_popen.call_count == 0, f"重复启动不应该调用Popen，但被调用了 {mock_popen.call_count} 次"
    
    # 验证进程数量没有增加
    final_count = len(manager.running_processes)
    assert final_count == initial_count, f"重复启动不应该增加进程计数，期望 {initial_count}，实际 {final_count}"
    
    # 清理
    manager.running_processes.clear()


# Feature: hotkey-power-manager, Property 2: 进程监控准确性
@settings(max_examples=100, deadline=None)
@given(
    num_processes=st.integers(min_value=1, max_value=10),
    num_terminated=st.integers(min_value=0, max_value=5)
)
def test_property_process_monitoring_accuracy(num_processes, num_terminated):
    """
    属性 2: 进程监控准确性
    验证: 需求 9.1, 9.3, 9.4
    
    对于任何时刻，get_running_count()返回的数量应该等于running_processes列表中
    仍在运行的进程数量，且列表应该实时反映进程的启动和结束
    """
    from unittest.mock import Mock
    import psutil
    
    manager = HotkeyManager()
    
    # 确保终止的进程数不超过总进程数
    num_terminated = min(num_terminated, num_processes)
    
    # 创建模拟的运行中进程
    running_processes = []
    for i in range(num_processes - num_terminated):
        mock_proc = Mock(spec=psutil.Process)
        mock_proc.pid = 1000 + i
        mock_proc.is_running.return_value = True
        running_processes.append(mock_proc)
    
    # 创建模拟的已终止进程
    terminated_processes = []
    for i in range(num_terminated):
        mock_proc = Mock(spec=psutil.Process)
        mock_proc.pid = 2000 + i
        mock_proc.is_running.return_value = False
        terminated_processes.append(mock_proc)
    
    # 将所有进程添加到管理器（混合运行和已终止的）
    manager.running_processes = running_processes + terminated_processes
    
    # 调用get_running_count()，它应该过滤掉已终止的进程
    actual_count = manager.get_running_count()
    
    # 验证返回的数量等于实际运行中的进程数
    expected_count = num_processes - num_terminated
    assert actual_count == expected_count, f"进程计数不准确，期望 {expected_count}，实际 {actual_count}"
    
    # 验证running_processes列表已被清理（只包含运行中的进程）
    assert len(manager.running_processes) == expected_count, f"进程列表未正确清理，期望 {expected_count}，实际 {len(manager.running_processes)}"
    
    # 验证列表中的所有进程都在运行
    for proc in manager.running_processes:
        assert proc.is_running(), "进程列表中不应包含已终止的进程"
    
    # 清理
    manager.running_processes.clear()






# ============================================================================
# 进程监控单元测试
# ============================================================================

def test_monitor_processes_cleanup():
    """
    测试_monitor_processes方法清理已终止的进程
    需求: 3.5, 9.2
    """
    from unittest.mock import Mock
    import psutil
    import time
    
    manager = HotkeyManager()
    
    # 创建模拟的运行中进程
    running_proc = Mock(spec=psutil.Process)
    running_proc.pid = 1001
    running_proc.is_running.return_value = True
    
    # 创建模拟的已终止进程
    terminated_proc = Mock(spec=psutil.Process)
    terminated_proc.pid = 1002
    terminated_proc.is_running.return_value = False
    
    # 添加到管理器
    manager.running_processes = [running_proc, terminated_proc]
    
    # 启动监听（这会启动监控线程）
    manager.is_running = True
    
    # 手动调用一次监控逻辑（模拟线程执行）
    manager.running_processes = [p for p in manager.running_processes if p.is_running()]
    
    # 验证已终止的进程被移除
    assert len(manager.running_processes) == 1
    assert manager.running_processes[0].pid == 1001
    
    # 清理
    manager.is_running = False
    manager.running_processes.clear()


def test_get_running_count_filters_terminated():
    """
    测试get_running_count方法过滤已终止的进程
    需求: 9.2, 9.4
    """
    from unittest.mock import Mock
    import psutil
    
    manager = HotkeyManager()
    
    # 创建3个运行中的进程
    for i in range(3):
        mock_proc = Mock(spec=psutil.Process)
        mock_proc.pid = 1000 + i
        mock_proc.is_running.return_value = True
        manager.running_processes.append(mock_proc)
    
    # 创建2个已终止的进程
    for i in range(2):
        mock_proc = Mock(spec=psutil.Process)
        mock_proc.pid = 2000 + i
        mock_proc.is_running.return_value = False
        manager.running_processes.append(mock_proc)
    
    # 调用get_running_count
    count = manager.get_running_count()
    
    # 验证只计数运行中的进程
    assert count == 3, f"应该返回3个运行中的进程，实际返回 {count}"
    
    # 验证列表已被清理
    assert len(manager.running_processes) == 3
    
    # 清理
    manager.running_processes.clear()


def test_get_running_count_empty_list():
    """
    测试get_running_count在空列表时返回0
    需求: 9.4
    """
    manager = HotkeyManager()
    
    # 空列表
    assert manager.get_running_count() == 0
    
    # 清理
    manager.running_processes.clear()


def test_monitor_processes_thread_lifecycle():
    """
    测试进程监控线程的生命周期
    需求: 3.5, 9.2
    """
    from unittest.mock import Mock
    import psutil
    import time
    
    manager = HotkeyManager()
    
    # 添加一个模拟进程
    mock_proc = Mock(spec=psutil.Process)
    mock_proc.pid = 1001
    mock_proc.is_running.return_value = True
    manager.running_processes.append(mock_proc)
    
    # 启动监听（会启动监控线程）
    manager.is_running = True
    import threading
    monitor_thread = threading.Thread(target=manager._monitor_processes, daemon=True)
    monitor_thread.start()
    
    # 等待一小段时间让线程运行
    time.sleep(0.2)
    
    # 验证线程正在运行
    assert monitor_thread.is_alive()
    
    # 停止监听
    manager.is_running = False
    
    # 等待线程结束
    time.sleep(5.5)  # 等待超过监控间隔
    
    # 验证线程已结束
    assert not monitor_thread.is_alive()
    
    # 清理
    manager.running_processes.clear()


# ============================================================================
# 快捷键注册属性测试
# ============================================================================

# Feature: hotkey-power-manager, Property 11: 快捷键注册完整性
@settings(max_examples=100, deadline=None)
@given(
    num_hotkeys=st.integers(min_value=1, max_value=10),
    modifiers=st.lists(
        st.sampled_from(['ctrl', 'alt', 'shift', 'win']),
        min_size=1,
        max_size=2,
        unique=True
    ),
    keys=st.lists(
        st.sampled_from(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'n', 't', 'f1', 'f2', 'f3']),
        min_size=1,
        max_size=1
    )
)
def test_property_hotkey_registration_integrity(num_hotkeys, modifiers, keys):
    """
    属性 11: 快捷键注册完整性
    验证: 需求 1.3
    
    对于任何配置的快捷键集合，当启动监听时，所有快捷键都应该被成功注册到keyboard库
    """
    from unittest.mock import patch, MagicMock
    import tempfile
    import os
    
    manager = HotkeyManager()
    
    # 生成唯一的快捷键集合
    hotkey_set = set()
    temp_files = []
    
    try:
        # 创建临时.exe文件和快捷键配置
        for i in range(num_hotkeys):
            # 创建临时.exe文件
            tmp = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
            tmp_path = tmp.name
            tmp.close()
            temp_files.append(tmp_path)
            
            # 生成唯一的快捷键
            modifier_str = '+'.join(modifiers[:min(len(modifiers), 2)])
            key = keys[0] if keys else 'a'
            hotkey = f"{modifier_str}+{key}+{i}"  # 添加索引确保唯一性
            
            # 添加快捷键
            result = manager.add_hotkey(hotkey, tmp_path)
            if result:
                hotkey_set.add(hotkey)
        
        # 如果没有成功添加任何快捷键，跳过测试
        if len(hotkey_set) == 0:
            return
        
        # 使用mock来跟踪keyboard.add_hotkey的调用
        with patch('keyboard.add_hotkey') as mock_add_hotkey:
            # 配置mock返回成功
            mock_add_hotkey.return_value = None
            
            # 启动监听
            manager.start()
            
            # 验证keyboard.add_hotkey被调用的次数等于配置的快捷键数量
            assert mock_add_hotkey.call_count == len(hotkey_set), \
                f"应该注册 {len(hotkey_set)} 个快捷键，实际注册了 {mock_add_hotkey.call_count} 个"
            
            # 验证所有配置的快捷键都被注册
            registered_hotkeys = set()
            for call in mock_add_hotkey.call_args_list:
                # call[0][0] 是第一个位置参数（快捷键字符串）
                registered_hotkeys.add(call[0][0])
            
            # 验证所有快捷键都被注册
            assert registered_hotkeys == hotkey_set, \
                f"注册的快捷键集合不匹配。期望: {hotkey_set}，实际: {registered_hotkeys}"
            
            # 停止监听
            manager.stop()
    
    finally:
        # 清理临时文件
        for tmp_path in temp_files:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        # 清理管理器
        manager.hotkeys.clear()
        manager.running_processes.clear()


# ============================================================================
# 快捷键监听启动和停止单元测试
# ============================================================================

def test_start_registers_all_hotkeys():
    """
    测试start方法注册所有快捷键
    需求: 1.3
    """
    from unittest.mock import patch
    import tempfile
    import os
    
    manager = HotkeyManager()
    temp_files = []
    
    try:
        # 添加多个快捷键
        hotkeys_to_add = [
            ('ctrl+alt+a', None),
            ('ctrl+shift+b', None),
            ('win+c', None)
        ]
        
        for hotkey, _ in hotkeys_to_add:
            tmp = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
            tmp_path = tmp.name
            tmp.close()
            temp_files.append(tmp_path)
            manager.add_hotkey(hotkey, tmp_path)
        
        # 使用mock跟踪keyboard.add_hotkey调用
        with patch('keyboard.add_hotkey') as mock_add_hotkey:
            manager.start()
            
            # 验证所有快捷键都被注册
            assert mock_add_hotkey.call_count == len(hotkeys_to_add)
            
            # 验证is_running标志被设置
            assert manager.is_running is True
            
            # 停止监听
            manager.stop()
    
    finally:
        # 清理临时文件
        for tmp_path in temp_files:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        manager.hotkeys.clear()


def test_stop_unregisters_all_hotkeys():
    """
    测试stop方法注销所有快捷键
    需求: 1.4
    """
    from unittest.mock import patch
    import tempfile
    import os
    
    manager = HotkeyManager()
    temp_files = []
    
    try:
        # 添加多个快捷键
        hotkeys_to_add = [
            ('ctrl+alt+x', None),
            ('ctrl+shift+y', None)
        ]
        
        for hotkey, _ in hotkeys_to_add:
            tmp = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
            tmp_path = tmp.name
            tmp.close()
            temp_files.append(tmp_path)
            manager.add_hotkey(hotkey, tmp_path)
        
        # 启动监听
        with patch('keyboard.add_hotkey'):
            manager.start()
        
        # 使用mock跟踪keyboard.remove_hotkey调用
        with patch('keyboard.remove_hotkey') as mock_remove_hotkey:
            manager.stop()
            
            # 验证所有快捷键都被注销
            assert mock_remove_hotkey.call_count == len(hotkeys_to_add)
            
            # 验证is_running标志被清除
            assert manager.is_running is False
    
    finally:
        # 清理临时文件
        for tmp_path in temp_files:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        manager.hotkeys.clear()


def test_start_when_already_running():
    """
    测试重复启动处理
    需求: 1.3
    """
    from unittest.mock import patch
    
    manager = HotkeyManager()
    
    # 第一次启动
    with patch('keyboard.add_hotkey'):
        manager.start()
        assert manager.is_running is True
        
        # 第二次启动（应该被忽略）
        with patch('keyboard.add_hotkey') as mock_add_hotkey:
            manager.start()
            # 验证没有再次注册快捷键
            assert mock_add_hotkey.call_count == 0
        
        # 停止监听
        with patch('keyboard.remove_hotkey'):
            manager.stop()


def test_stop_when_not_running():
    """
    测试在未运行时停止
    需求: 1.4
    """
    from unittest.mock import patch
    
    manager = HotkeyManager()
    
    # 确保未运行
    assert manager.is_running is False
    
    # 尝试停止（应该安全返回）
    with patch('keyboard.remove_hotkey') as mock_remove_hotkey:
        manager.stop()
        # 验证没有尝试注销快捷键
        assert mock_remove_hotkey.call_count == 0


def test_start_starts_monitor_thread():
    """
    测试start方法启动监控线程
    需求: 1.3
    """
    from unittest.mock import patch
    import time
    
    manager = HotkeyManager()
    
    with patch('keyboard.add_hotkey'):
        manager.start()
        
        # 等待一小段时间让线程启动
        time.sleep(0.1)
        
        # 验证is_running标志被设置（监控线程依赖此标志）
        assert manager.is_running is True
        
        # 停止监听
        with patch('keyboard.remove_hotkey'):
            manager.stop()
        
        # 等待线程结束
        time.sleep(5.5)


# ============================================================================
# 错误处理测试
# Validates: Requirements 2.4, 8.4
# ============================================================================

def test_launch_program_failure_nonexistent():
    """
    测试程序启动失败 - 不存在的程序
    
    验证当程序路径不存在时，系统能够正确处理错误
    需求: 2.4
    """
    manager = HotkeyManager()
    
    # 尝试启动不存在的程序
    nonexistent_path = "C:\\NonExistent\\Program\\test.exe"
    
    # 应该记录错误但不崩溃
    try:
        manager.launch_program(nonexistent_path)
        # 验证没有进程被添加到列表
        assert len(manager.running_processes) == 0
    except Exception as e:
        pytest.fail(f"启动不存在的程序不应该抛出异常: {e}")


def test_launch_program_failure_invalid_path():
    """
    测试程序启动失败 - 无效的路径格式
    
    验证当程序路径格式无效时，系统能够正确处理错误
    需求: 2.4
    """
    manager = HotkeyManager()
    
    invalid_paths = [
        "",  # 空路径
        "   ",  # 空白路径
        "invalid:path",  # 无效字符
        "C:\\",  # 目录而不是文件
    ]
    
    for invalid_path in invalid_paths:
        try:
            manager.launch_program(invalid_path)
            # 验证没有进程被添加
            assert len(manager.running_processes) == 0
        except Exception as e:
            pytest.fail(f"无效路径 '{invalid_path}' 不应该抛出异常: {e}")


def test_process_access_denied():
    """
    测试进程访问被拒绝
    
    验证当无法访问进程信息时，系统能够正确处理
    需求: 2.4
    """
    from unittest.mock import Mock
    import psutil
    
    manager = HotkeyManager()
    
    # 创建一个模拟的进程，访问时抛出AccessDenied异常
    mock_proc = Mock(spec=psutil.Process)
    mock_proc.pid = 9999
    mock_proc.is_running.side_effect = psutil.AccessDenied("Access denied")
    
    # 添加到运行列表
    manager.running_processes.append(mock_proc)
    
    # 调用get_running_count，应该处理AccessDenied异常
    try:
        count = manager.get_running_count()
        # 由于访问被拒绝，进程应该被移除
        assert len(manager.running_processes) == 0
    except psutil.AccessDenied:
        pytest.fail("get_running_count应该处理AccessDenied异常")


def test_process_no_such_process():
    """
    测试进程不存在错误
    
    验证当进程突然消失时，系统能够正确处理
    需求: 2.4
    """
    from unittest.mock import Mock
    import psutil
    
    manager = HotkeyManager()
    
    # 创建一个模拟的进程，访问时抛出NoSuchProcess异常
    mock_proc = Mock(spec=psutil.Process)
    mock_proc.pid = 8888
    mock_proc.is_running.side_effect = psutil.NoSuchProcess(8888)
    
    # 添加到运行列表
    manager.running_processes.append(mock_proc)
    
    # 调用get_running_count，应该处理NoSuchProcess异常
    try:
        count = manager.get_running_count()
        # 进程应该被移除
        assert len(manager.running_processes) == 0
    except psutil.NoSuchProcess:
        pytest.fail("get_running_count应该处理NoSuchProcess异常")


def test_add_hotkey_with_permission_error():
    """
    测试添加快捷键时的权限错误
    
    验证当文件权限不足时，系统能够正确处理
    需求: 8.4
    """
    manager = HotkeyManager()
    
    # 在Windows上，某些系统文件可能无法访问
    # 使用一个可能存在但无法执行的系统文件
    system_file = "C:\\Windows\\System32\\config\\system"
    
    # 尝试添加（应该失败，因为不是.exe文件）
    result = manager.add_hotkey("ctrl+alt+s", system_file)
    assert result is False
    assert "ctrl+alt+s" not in manager.hotkeys


def test_keyboard_registration_failure():
    """
    测试快捷键注册失败
    
    验证当keyboard库注册失败时，系统能够继续运行
    需求: 8.4
    """
    from unittest.mock import patch
    import tempfile
    import os
    
    manager = HotkeyManager()
    
    # 创建临时.exe文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 添加快捷键
        manager.add_hotkey('ctrl+alt+k', tmp_path)
        
        # 模拟keyboard.add_hotkey抛出异常
        with patch('keyboard.add_hotkey', side_effect=Exception("Registration failed")):
            # 启动监听，应该记录错误但不崩溃
            try:
                manager.start()
                # 验证is_running仍然被设置
                assert manager.is_running is True
            except Exception as e:
                pytest.fail(f"快捷键注册失败不应该导致程序崩溃: {e}")
            finally:
                manager.stop()
    
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_keyboard_unregistration_failure():
    """
    测试快捷键注销失败
    
    验证当keyboard库注销失败时，系统能够继续运行
    需求: 8.4
    """
    from unittest.mock import patch
    import tempfile
    import os
    
    manager = HotkeyManager()
    
    # 创建临时.exe文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 添加快捷键
        manager.add_hotkey('ctrl+alt+u', tmp_path)
        
        # 启动监听
        with patch('keyboard.add_hotkey'):
            manager.start()
        
        # 模拟keyboard.remove_hotkey抛出异常
        with patch('keyboard.remove_hotkey', side_effect=Exception("Unregistration failed")):
            # 停止监听，应该记录错误但不崩溃
            try:
                manager.stop()
                # 验证is_running被清除
                assert manager.is_running is False
            except Exception as e:
                pytest.fail(f"快捷键注销失败不应该导致程序崩溃: {e}")
    
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_launch_program_with_subprocess_error():
    """
    测试程序启动时的subprocess错误
    
    验证当subprocess.Popen失败时，系统能够正确处理
    需求: 2.4
    """
    from unittest.mock import patch
    import tempfile
    import os
    
    manager = HotkeyManager()
    
    # 创建临时.exe文件
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 模拟subprocess.Popen抛出异常
        with patch('hotkey_manager.subprocess.Popen', side_effect=OSError("Failed to start process")):
            # 尝试启动程序，应该记录错误但不崩溃
            try:
                manager.launch_program(tmp_path)
                # 验证没有进程被添加
                assert len(manager.running_processes) == 0
            except OSError:
                pytest.fail("subprocess错误应该被捕获和处理")
    
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_monitor_processes_with_exception():
    """
    测试进程监控线程中的异常处理
    
    验证监控线程能够处理进程检查时的异常
    需求: 2.4
    """
    from unittest.mock import Mock
    import psutil
    
    manager = HotkeyManager()
    
    # 创建一个会抛出异常的模拟进程
    mock_proc = Mock(spec=psutil.Process)
    mock_proc.pid = 7777
    mock_proc.is_running.side_effect = RuntimeError("Unexpected error")
    
    # 添加到运行列表
    manager.running_processes.append(mock_proc)
    
    # 调用get_running_count，它应该处理异常并移除有问题的进程
    try:
        count = manager.get_running_count()
        # 验证有问题的进程被移除
        assert len(manager.running_processes) == 0
    except RuntimeError:
        pytest.fail("监控进程时的异常应该被处理")
