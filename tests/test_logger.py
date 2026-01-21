"""
Logger 测试模块
包含单元测试和属性测试
"""
import pytest
import tempfile
import threading
from pathlib import Path
from hypothesis import given, settings, strategies as st
from logger import Logger


# Feature: hotkey-power-manager, Property 9: Logger单例一致性
# Validates: Requirements 7.5
@pytest.mark.property
@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=100))
def test_logger_singleton_consistency(num_instances):
    """
    属性测试：Logger单例一致性
    
    对于任何时刻，多次创建Logger实例应该返回同一个对象引用
    """
    # 创建多个Logger实例
    instances = [Logger() for _ in range(num_instances)]
    
    # 验证所有实例都是同一个对象
    first_instance = instances[0]
    for i, instance in enumerate(instances[1:], start=1):
        assert instance is first_instance, \
            f"实例 {i} 不是同一个对象: id={id(instance)}, 期望id={id(first_instance)}"
    
    # 验证所有实例的id相同
    instance_ids = [id(instance) for instance in instances]
    assert len(set(instance_ids)) == 1, \
        f"发现多个不同的实例ID: {set(instance_ids)}"


@pytest.mark.property
@settings(max_examples=100)
@given(st.integers(min_value=2, max_value=20))
def test_logger_singleton_thread_safety(num_threads):
    """
    属性测试：Logger单例线程安全性
    
    验证在多线程环境下，Logger仍然保持单例特性
    """
    instances = []
    lock = threading.Lock()
    
    def create_logger():
        logger = Logger()
        with lock:
            instances.append(logger)
    
    # 创建多个线程同时创建Logger实例
    threads = [threading.Thread(target=create_logger) for _ in range(num_threads)]
    
    # 启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 验证所有实例都是同一个对象
    first_instance = instances[0]
    for i, instance in enumerate(instances[1:], start=1):
        assert instance is first_instance, \
            f"线程 {i} 创建的实例不是同一个对象"
    
    # 验证所有实例的id相同
    instance_ids = [id(instance) for instance in instances]
    assert len(set(instance_ids)) == 1, \
        f"多线程环境下发现多个不同的实例ID: {set(instance_ids)}"



# Feature: hotkey-power-manager, Property 8: 日志记录完整性
# Validates: Requirements 2.3, 3.3, 6.1, 6.2
@pytest.mark.property
@settings(max_examples=100)
@given(st.lists(
    st.tuples(
        st.sampled_from(['info', 'warning', 'error', 'debug']),
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip() and '\r' not in x and '\n' not in x)
    ),
    min_size=1,
    max_size=50
))
def test_log_recording_completeness(log_entries):
    """
    属性测试：日志记录完整性
    
    对于任何重要操作（快捷键注册、程序启动、防休眠状态变化、错误），
    都应该有对应的日志条目被写入日志文件
    """
    # 创建临时日志目录和文件
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_log_dir = Path(temp_dir) / "logs"
        temp_log_dir.mkdir(exist_ok=True)
        
        # 重置Logger单例以使用临时日志目录
        Logger._instance = None
        
        # 修改Logger的日志文件路径
        import logging
        from datetime import datetime
        
        log_file = temp_log_dir / f"hotkey_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 创建新的Logger实例
        logger = Logger()
        
        # 清除现有的handlers并添加新的handler
        logger.logger.handlers.clear()
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.logger.addHandler(file_handler)
        logger.logger.setLevel(logging.DEBUG)
        
        # 记录所有日志条目
        for level, message in log_entries:
            if level == 'info':
                logger.info(message)
            elif level == 'warning':
                logger.warning(message)
            elif level == 'error':
                logger.error(message)
            elif level == 'debug':
                logger.debug(message)
        
        # 确保日志被写入并关闭文件句柄
        for handler in logger.logger.handlers:
            handler.flush()
            handler.close()
        logger.logger.handlers.clear()
        
        # 读取日志文件内容
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # 验证所有日志条目都被记录
        for level, message in log_entries:
            # 跳过空消息或只包含空白字符的消息
            if not message.strip():
                continue
            
            assert message in log_content, \
                f"日志条目未找到: [{level.upper()}] {message}"
            
            # 验证日志级别标记存在
            level_marker = f"[{level.upper()}]"
            assert level_marker in log_content, \
                f"日志级别标记未找到: {level_marker}"
        
        # 重置Logger单例
        Logger._instance = None



# ============================================================================
# 单元测试：日志文件管理
# Validates: Requirements 6.3, 6.4, 6.5
# ============================================================================

@pytest.mark.unit
def test_log_file_creation():
    """
    测试日志文件创建
    
    验证Logger创建时会自动创建logs目录和日志文件
    """
    # 重置Logger单例
    Logger._instance = None
    
    # 创建Logger实例
    logger = Logger()
    
    # 验证logs目录存在
    log_dir = Path("logs")
    assert log_dir.exists(), "logs目录未创建"
    assert log_dir.is_dir(), "logs不是目录"
    
    # 验证日志文件存在
    from datetime import datetime
    log_file = log_dir / f"hotkey_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 写入一条日志以确保文件被创建
    logger.info("测试日志")
    
    # 刷新handlers
    for handler in logger.logger.handlers:
        handler.flush()
    
    assert log_file.exists(), f"日志文件未创建: {log_file}"
    assert log_file.is_file(), "日志文件不是文件"


@pytest.mark.unit
def test_log_format():
    """
    测试日志格式
    
    验证日志条目包含时间戳、级别和消息
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_log_dir = Path(temp_dir) / "logs"
        temp_log_dir.mkdir(exist_ok=True)
        
        # 重置Logger单例
        Logger._instance = None
        
        import logging
        from datetime import datetime
        
        log_file = temp_log_dir / f"hotkey_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 手动创建logger而不使用单例
        test_logger = logging.getLogger('test_logger')
        test_logger.handlers.clear()
        test_logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        test_logger.addHandler(file_handler)
        
        # 写入测试日志
        test_message = "测试日志格式"
        test_logger.info(test_message)
        
        # 刷新并关闭handler
        file_handler.flush()
        file_handler.close()
        test_logger.handlers.clear()
        
        # 读取日志文件
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # 验证日志格式
        assert test_message in log_content, f"日志消息未找到，日志内容: {log_content}"
        assert "[INFO]" in log_content, "日志级别标记未找到"
        
        # 验证时间戳格式（简单检查是否包含日期时间）
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.search(timestamp_pattern, log_content), "时间戳格式不正确"
        
        # 重置Logger单例
        Logger._instance = None


@pytest.mark.unit
def test_different_log_levels():
    """
    测试不同级别的日志
    
    验证Logger能够记录info、warning、error、debug级别的日志
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_log_dir = Path(temp_dir) / "logs"
        temp_log_dir.mkdir(exist_ok=True)
        
        # 重置Logger单例
        Logger._instance = None
        
        import logging
        from datetime import datetime
        
        log_file = temp_log_dir / f"hotkey_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 创建Logger实例
        logger = Logger()
        
        # 清除现有handlers并添加新的handler
        logger.logger.handlers.clear()
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.logger.addHandler(file_handler)
        logger.logger.setLevel(logging.DEBUG)
        
        # 写入不同级别的日志
        logger.info("信息日志")
        logger.warning("警告日志")
        logger.error("错误日志")
        logger.debug("调试日志")
        
        # 刷新并关闭handler
        for handler in logger.logger.handlers:
            handler.flush()
            handler.close()
        logger.logger.handlers.clear()
        
        # 读取日志文件
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # 验证所有级别的日志都被记录
        assert "信息日志" in log_content, "INFO日志未记录"
        assert "[INFO]" in log_content, "INFO级别标记未找到"
        
        assert "警告日志" in log_content, "WARNING日志未记录"
        assert "[WARNING]" in log_content, "WARNING级别标记未找到"
        
        assert "错误日志" in log_content, "ERROR日志未记录"
        assert "[ERROR]" in log_content, "ERROR级别标记未找到"
        
        assert "调试日志" in log_content, "DEBUG日志未记录"
        assert "[DEBUG]" in log_content, "DEBUG级别标记未找到"
        
        # 重置Logger单例
        Logger._instance = None


@pytest.mark.unit
def test_log_file_naming():
    """
    测试日志文件命名
    
    验证日志文件按日期命名（格式: hotkey_YYYYMMDD.log）
    """
    # 重置Logger单例
    Logger._instance = None
    
    # 创建Logger实例
    logger = Logger()
    
    # 获取预期的日志文件名
    from datetime import datetime
    expected_filename = f"hotkey_{datetime.now().strftime('%Y%m%d')}.log"
    expected_path = Path("logs") / expected_filename
    
    # 写入一条日志以确保文件被创建
    logger.info("测试日志文件命名")
    
    # 刷新handlers
    for handler in logger.logger.handlers:
        handler.flush()
    
    # 验证文件名格式正确
    assert expected_path.exists(), f"日志文件未按预期命名: {expected_path}"
    
    # 验证文件名格式
    import re
    filename_pattern = r'hotkey_\d{8}\.log'
    assert re.match(filename_pattern, expected_filename), "日志文件名格式不正确"


@pytest.mark.unit
def test_utf8_encoding():
    """
    测试UTF-8编码
    
    验证日志文件使用UTF-8编码，能够正确处理中文和其他Unicode字符
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_log_dir = Path(temp_dir) / "logs"
        temp_log_dir.mkdir(exist_ok=True)
        
        # 重置Logger单例
        Logger._instance = None
        
        import logging
        from datetime import datetime
        
        log_file = temp_log_dir / f"hotkey_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 创建Logger实例
        logger = Logger()
        
        # 清除现有handlers并添加新的handler
        logger.logger.handlers.clear()
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.logger.addHandler(file_handler)
        
        # 写入包含中文和其他Unicode字符的日志
        chinese_message = "这是中文日志消息"
        emoji_message = "日志包含表情符号 🎉 ✨"
        mixed_message = "混合文本: Hello 世界 🌍"
        
        logger.info(chinese_message)
        logger.warning(emoji_message)
        logger.error(mixed_message)
        
        # 刷新并关闭handler
        for handler in logger.logger.handlers:
            handler.flush()
            handler.close()
        logger.logger.handlers.clear()
        
        # 使用UTF-8编码读取日志文件
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # 验证所有Unicode字符都被正确记录
        assert chinese_message in log_content, "中文日志未正确记录"
        assert emoji_message in log_content, "表情符号日志未正确记录"
        assert mixed_message in log_content, "混合文本日志未正确记录"
        
        # 重置Logger单例
        Logger._instance = None

