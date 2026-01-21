"""
ConfigManager 测试模块
包含单元测试和属性测试
"""
import json
import pytest
import tempfile
from pathlib import Path
from hypothesis import given, settings, strategies as st
from config_manager import ConfigManager


# Feature: hotkey-power-manager, Property 1: 配置持久化往返一致性
# Validates: Requirements 4.1, 4.2, 4.5
@pytest.mark.property
@settings(max_examples=100)
@given(st.dictionaries(
    keys=st.text(min_size=1, max_size=50),
    values=st.text(min_size=1, max_size=200),
    min_size=0,
    max_size=20
))
def test_config_roundtrip_consistency(hotkeys_dict):
    """
    属性测试：配置持久化往返一致性
    
    对于任何有效的快捷键配置字典（包含Unicode字符如中文路径），
    保存到JSON文件后再加载应该得到等价的配置数据，且所有字符保持完整性
    """
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        # 创建ConfigManager实例并设置配置
        config_manager = ConfigManager(config_file=temp_config_path)
        config_manager.config = {"hotkeys": hotkeys_dict}
        
        # 保存配置
        config_manager.save()
        
        # 创建新的ConfigManager实例加载配置
        config_manager_loaded = ConfigManager(config_file=temp_config_path)
        loaded_hotkeys = config_manager_loaded.get_hotkeys()
        
        # 验证往返一致性
        assert loaded_hotkeys == hotkeys_dict, \
            f"配置往返不一致: 原始={hotkeys_dict}, 加载={loaded_hotkeys}"
        
        # 验证所有键值对都保持完整
        for key, value in hotkeys_dict.items():
            assert key in loaded_hotkeys, f"键 '{key}' 在加载后丢失"
            assert loaded_hotkeys[key] == value, \
                f"键 '{key}' 的值不一致: 原始='{value}', 加载='{loaded_hotkeys[key]}'"
    
    finally:
        # 清理临时文件
        Path(temp_config_path).unlink(missing_ok=True)



# ============================================================================
# 单元测试：ConfigManager基础功能
# Validates: Requirements 4.3, 4.4
# ============================================================================

@pytest.mark.unit
def test_config_file_creation():
    """
    测试配置文件创建
    
    验证当配置文件不存在时，ConfigManager会创建默认的空配置
    """
    with tempfile.NamedTemporaryFile(suffix='.json', delete=True) as f:
        temp_config_path = f.name
    
    # 确保文件不存在
    assert not Path(temp_config_path).exists()
    
    # 创建ConfigManager
    config_manager = ConfigManager(config_file=temp_config_path)
    
    # 验证创建了默认配置
    assert config_manager.config == {"hotkeys": {}}
    assert config_manager.get_hotkeys() == {}


@pytest.mark.unit
def test_add_hotkey():
    """
    测试add_hotkey方法
    
    验证添加快捷键后配置正确更新并保存
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 添加快捷键
        config_manager.add_hotkey("ctrl+alt+n", "C:\\notepad.exe")
        
        # 验证内存中的配置
        assert "ctrl+alt+n" in config_manager.get_hotkeys()
        assert config_manager.get_hotkeys()["ctrl+alt+n"] == "C:\\notepad.exe"
        
        # 验证文件已保存
        with open(temp_config_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        assert "ctrl+alt+n" in saved_config["hotkeys"]
        assert saved_config["hotkeys"]["ctrl+alt+n"] == "C:\\notepad.exe"
        
        # 添加第二个快捷键
        config_manager.add_hotkey("ctrl+shift+t", "C:\\terminal.exe")
        assert len(config_manager.get_hotkeys()) == 2
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_remove_hotkey():
    """
    测试remove_hotkey方法
    
    验证移除快捷键后配置正确更新并保存
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 添加两个快捷键
        config_manager.add_hotkey("ctrl+alt+n", "C:\\notepad.exe")
        config_manager.add_hotkey("ctrl+shift+t", "C:\\terminal.exe")
        assert len(config_manager.get_hotkeys()) == 2
        
        # 移除一个快捷键
        config_manager.remove_hotkey("ctrl+alt+n")
        
        # 验证内存中的配置
        assert "ctrl+alt+n" not in config_manager.get_hotkeys()
        assert "ctrl+shift+t" in config_manager.get_hotkeys()
        assert len(config_manager.get_hotkeys()) == 1
        
        # 验证文件已保存
        with open(temp_config_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        assert "ctrl+alt+n" not in saved_config["hotkeys"]
        assert "ctrl+shift+t" in saved_config["hotkeys"]
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_remove_nonexistent_hotkey():
    """
    测试移除不存在的快捷键
    
    验证移除不存在的快捷键不会引发错误
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        config_manager.add_hotkey("ctrl+alt+n", "C:\\notepad.exe")
        
        # 移除不存在的快捷键
        config_manager.remove_hotkey("ctrl+alt+x")
        
        # 验证原有配置未受影响
        assert "ctrl+alt+n" in config_manager.get_hotkeys()
        assert len(config_manager.get_hotkeys()) == 1
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_corrupted_file_handling():
    """
    测试损坏文件处理
    
    验证当配置文件损坏时，系统能够创建新的空配置
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
        # 写入无效的JSON
        f.write("{ invalid json content }")
    
    try:
        # 创建ConfigManager，应该处理损坏的文件
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 验证创建了默认配置
        assert config_manager.config == {"hotkeys": {}}
        assert config_manager.get_hotkeys() == {}
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_unicode_support():
    """
    测试Unicode字符支持
    
    验证配置文件正确处理中文路径和Unicode字符
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 添加包含中文的路径
        chinese_path = "C:\\程序文件\\记事本\\notepad.exe"
        config_manager.add_hotkey("ctrl+alt+中", chinese_path)
        
        # 验证保存和加载
        config_manager_loaded = ConfigManager(config_file=temp_config_path)
        loaded_hotkeys = config_manager_loaded.get_hotkeys()
        
        assert "ctrl+alt+中" in loaded_hotkeys
        assert loaded_hotkeys["ctrl+alt+中"] == chinese_path
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


# ============================================================================
# 边界条件测试
# Validates: Requirements 1.5, 4.3, 4.4
# ============================================================================

@pytest.mark.unit
def test_max_hotkeys_limit():
    """
    测试50个快捷键限制
    
    验证系统能够处理最多50个快捷键配置
    需求: 1.5
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 添加50个快捷键
        for i in range(50):
            hotkey = f"ctrl+alt+f{i % 12 + 1}"  # 使用F1-F12循环
            if i >= 12:
                hotkey = f"ctrl+shift+f{i % 12 + 1}"
            if i >= 24:
                hotkey = f"alt+shift+f{i % 12 + 1}"
            if i >= 36:
                hotkey = f"ctrl+alt+{chr(97 + (i - 36))}"  # a-n
            
            program_path = f"C:\\Program{i}\\test.exe"
            config_manager.add_hotkey(hotkey, program_path)
        
        # 验证所有快捷键都被保存
        hotkeys = config_manager.get_hotkeys()
        assert len(hotkeys) == 50, f"应该有50个快捷键，实际有 {len(hotkeys)} 个"
        
        # 验证可以重新加载
        config_manager_loaded = ConfigManager(config_file=temp_config_path)
        loaded_hotkeys = config_manager_loaded.get_hotkeys()
        assert len(loaded_hotkeys) == 50, f"加载后应该有50个快捷键，实际有 {len(loaded_hotkeys)} 个"
        
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_empty_config_file():
    """
    测试空配置文件
    
    验证系统能够处理空的配置文件
    需求: 4.3
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
        # 写入空的JSON对象
        f.write("{}")
    
    try:
        # 加载空配置
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 验证返回空的快捷键字典
        hotkeys = config_manager.get_hotkeys()
        assert hotkeys == {}, f"空配置应该返回空字典，实际返回 {hotkeys}"
        
        # 验证可以添加新的快捷键
        config_manager.add_hotkey("ctrl+alt+n", "C:\\test.exe")
        assert len(config_manager.get_hotkeys()) == 1
        
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_empty_hotkeys_section():
    """
    测试空的hotkeys部分
    
    验证系统能够处理包含空hotkeys部分的配置文件
    需求: 4.3
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
        # 写入包含空hotkeys的JSON
        f.write('{"hotkeys": {}}')
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 验证返回空的快捷键字典
        hotkeys = config_manager.get_hotkeys()
        assert hotkeys == {}
        
        # 验证可以添加新的快捷键
        config_manager.add_hotkey("ctrl+alt+t", "C:\\test.exe")
        assert len(config_manager.get_hotkeys()) == 1
        
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_corrupted_json_various_formats():
    """
    测试各种损坏的JSON文件格式
    
    验证系统能够处理各种格式错误的JSON文件
    需求: 4.4
    """
    corrupted_contents = [
        ("{ invalid json }", True),  # 无效的JSON语法 - 应该创建默认配置
        ("{", True),  # 不完整的JSON - 应该创建默认配置
        ('{"hotkeys": [}', True),  # 语法错误 - 应该创建默认配置
        ('{"hotkeys": "not a dict"}', False),  # 类型错误 - JSON有效但hotkeys不是字典
        ("", True),  # 空文件 - 应该创建默认配置
        ("null", True),  # null值 - 应该创建默认配置
        ("[]", True),  # 数组而不是对象 - 应该创建默认配置
    ]
    
    for i, (content, should_reset) in enumerate(corrupted_contents):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_config_path = f.name
            f.write(content)
        
        try:
            # 创建ConfigManager，应该处理损坏的文件
            config_manager = ConfigManager(config_file=temp_config_path)
            
            if should_reset:
                # 对于无效的JSON，应该创建默认配置
                assert config_manager.config == {"hotkeys": {}}, \
                    f"损坏的JSON #{i} 应该创建默认配置，实际: {config_manager.config}"
            
            # 无论如何，get_hotkeys()应该返回空字典或有效字典
            hotkeys = config_manager.get_hotkeys()
            assert isinstance(hotkeys, dict), \
                f"get_hotkeys() 应该返回字典，实际返回: {type(hotkeys)}"
            
        finally:
            Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_invalid_unicode_characters():
    """
    测试无效的Unicode字符处理
    
    验证系统能够处理包含特殊Unicode字符的配置
    需求: 4.5
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 测试各种特殊Unicode字符
        special_chars = [
            ("ctrl+alt+😀", "C:\\emoji\\test.exe"),  # Emoji
            ("ctrl+alt+\u200b", "C:\\zero-width\\test.exe"),  # 零宽字符
            ("ctrl+alt+\n", "C:\\newline\\test.exe"),  # 换行符
            ("ctrl+alt+\t", "C:\\tab\\test.exe"),  # 制表符
            ("ctrl+alt+日本語", "C:\\japanese\\test.exe"),  # 日文
            ("ctrl+alt+한글", "C:\\korean\\test.exe"),  # 韩文
            ("ctrl+alt+العربية", "C:\\arabic\\test.exe"),  # 阿拉伯文
        ]
        
        for hotkey, path in special_chars:
            config_manager.add_hotkey(hotkey, path)
        
        # 验证所有配置都被保存
        hotkeys = config_manager.get_hotkeys()
        assert len(hotkeys) == len(special_chars)
        
        # 验证可以重新加载
        config_manager_loaded = ConfigManager(config_file=temp_config_path)
        loaded_hotkeys = config_manager_loaded.get_hotkeys()
        
        # 验证所有特殊字符都被正确保存和加载
        for hotkey, path in special_chars:
            assert hotkey in loaded_hotkeys, f"快捷键 {repr(hotkey)} 未被正确保存"
            assert loaded_hotkeys[hotkey] == path, f"路径不匹配: {loaded_hotkeys[hotkey]} != {path}"
        
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_very_long_paths():
    """
    测试非常长的文件路径
    
    验证系统能够处理超长的文件路径
    需求: 4.5
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 创建一个非常长的路径（接近Windows MAX_PATH限制）
        long_path = "C:\\" + "\\".join(["folder" + str(i) for i in range(50)]) + "\\program.exe"
        
        config_manager.add_hotkey("ctrl+alt+l", long_path)
        
        # 验证保存和加载
        config_manager_loaded = ConfigManager(config_file=temp_config_path)
        loaded_hotkeys = config_manager_loaded.get_hotkeys()
        
        assert "ctrl+alt+l" in loaded_hotkeys
        assert loaded_hotkeys["ctrl+alt+l"] == long_path
        
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_duplicate_hotkeys():
    """
    测试重复的快捷键
    
    验证系统正确处理重复的快捷键（应该覆盖）
    需求: 1.2
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 添加第一个快捷键
        config_manager.add_hotkey("ctrl+alt+d", "C:\\first.exe")
        assert config_manager.get_hotkeys()["ctrl+alt+d"] == "C:\\first.exe"
        
        # 添加相同的快捷键但不同的路径（应该覆盖）
        config_manager.add_hotkey("ctrl+alt+d", "C:\\second.exe")
        assert config_manager.get_hotkeys()["ctrl+alt+d"] == "C:\\second.exe"
        
        # 验证只有一个快捷键
        assert len(config_manager.get_hotkeys()) == 1
        
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


# ============================================================================
# 文件系统错误处理测试
# Validates: Requirements 8.4
# ============================================================================

@pytest.mark.unit
def test_save_to_readonly_directory():
    """
    测试保存到只读目录
    
    验证当无法写入配置文件时，系统能够正确处理错误
    需求: 8.4
    """
    import os
    
    # 使用一个不存在的深层目录路径
    readonly_path = "C:\\NonExistent\\DeepPath\\ReadOnly\\config.json"
    
    config_manager = ConfigManager(config_file=readonly_path)
    
    # 尝试添加快捷键并保存
    try:
        config_manager.add_hotkey("ctrl+alt+r", "C:\\test.exe")
        # 应该记录错误但不崩溃
        # 验证内存中的配置仍然被更新
        assert "ctrl+alt+r" in config_manager.get_hotkeys()
    except Exception as e:
        pytest.fail(f"文件系统错误不应该导致程序崩溃: {e}")


@pytest.mark.unit
def test_load_from_inaccessible_file():
    """
    测试从无法访问的文件加载
    
    验证当配置文件无法读取时，系统能够创建默认配置
    需求: 8.4
    """
    # 使用一个不存在的路径
    inaccessible_path = "C:\\System\\Protected\\config.json"
    
    try:
        config_manager = ConfigManager(config_file=inaccessible_path)
        
        # 应该创建默认配置
        assert config_manager.config == {"hotkeys": {}}
        assert config_manager.get_hotkeys() == {}
    except Exception as e:
        pytest.fail(f"无法访问文件不应该导致程序崩溃: {e}")


@pytest.mark.unit
def test_save_with_disk_full():
    """
    测试磁盘空间不足时的保存操作
    
    验证当磁盘空间不足时，系统能够正确处理错误
    需求: 8.4
    """
    from unittest.mock import patch, mock_open
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        config_manager.add_hotkey("ctrl+alt+t", "C:\\test.exe")
        
        # 模拟磁盘空间不足
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            # 尝试保存，应该记录错误但不崩溃
            try:
                config_manager.save()
            except OSError:
                pytest.fail("磁盘空间不足错误应该被捕获和处理")
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_load_with_encoding_error():
    """
    测试加载包含编码错误的文件
    
    验证当文件编码错误时，系统能够正确处理
    需求: 8.4
    """
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as f:
        temp_config_path = f.name
        # 写入无效的UTF-8字节序列
        f.write(b'{"hotkeys": {"ctrl+alt+n": "\xff\xfe"}}')
    
    try:
        # 尝试加载，应该处理编码错误
        config_manager = ConfigManager(config_file=temp_config_path)
        
        # 应该创建默认配置
        assert config_manager.config == {"hotkeys": {}}
    except Exception as e:
        pytest.fail(f"编码错误不应该导致程序崩溃: {e}")
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_concurrent_file_access():
    """
    测试并发文件访问
    
    验证当多个进程同时访问配置文件时，系统能够正确处理
    需求: 8.4
    """
    import threading
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        
        errors = []
        
        def add_hotkeys(start_index):
            try:
                for i in range(start_index, start_index + 5):
                    config_manager.add_hotkey(f"ctrl+alt+{i}", f"C:\\test{i}.exe")
            except Exception as e:
                errors.append(e)
        
        # 创建多个线程同时添加快捷键
        threads = []
        for i in range(3):
            t = threading.Thread(target=add_hotkeys, args=(i * 5,))
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 验证没有异常
        assert len(errors) == 0, f"并发访问导致错误: {errors}"
        
        # 验证至少有一些快捷键被添加
        assert len(config_manager.get_hotkeys()) > 0
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_file_deleted_during_operation():
    """
    测试操作过程中文件被删除
    
    验证当配置文件在操作过程中被删除时，系统能够正确处理
    需求: 8.4
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        config_manager.add_hotkey("ctrl+alt+t", "C:\\test.exe")
        
        # 删除配置文件
        Path(temp_config_path).unlink()
        
        # 尝试保存，应该能够重新创建文件
        try:
            config_manager.save()
            # 验证文件被重新创建
            assert Path(temp_config_path).exists()
        except Exception as e:
            pytest.fail(f"文件被删除后的保存操作不应该崩溃: {e}")
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_json_dump_failure():
    """
    测试JSON序列化失败
    
    验证当JSON序列化失败时，系统能够正确处理
    需求: 8.4
    """
    from unittest.mock import patch
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_config_path = f.name
    
    try:
        config_manager = ConfigManager(config_file=temp_config_path)
        config_manager.add_hotkey("ctrl+alt+t", "C:\\test.exe")
        
        # 模拟json.dump失败
        with patch('json.dump', side_effect=TypeError("Object not serializable")):
            # 尝试保存，应该记录错误但不崩溃
            try:
                config_manager.save()
            except TypeError:
                pytest.fail("JSON序列化错误应该被捕获和处理")
    
    finally:
        Path(temp_config_path).unlink(missing_ok=True)
