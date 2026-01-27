"""
日志记录模块
"""
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta


class Logger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking pattern for thread safety
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化日志系统"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 清理7天前的日志
        self._cleanup_old_logs(log_dir, days=7)

        # 使用新的命名格式: pyQuickStart_yyyymmdd.log
        log_file = log_dir / f"pyQuickStart_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.current_date = datetime.now().date()
        self.log_file = log_file

    def _cleanup_old_logs(self, log_dir: Path, days: int = 7):
        """清理指定天数之前的日志文件"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 查找所有日志文件（支持旧格式和新格式）
            log_patterns = ["hotkey_*.log", "pyQuickStart_*.log"]
            
            for pattern in log_patterns:
                for log_file in log_dir.glob(pattern):
                    try:
                        # 从文件名中提取日期
                        # hotkey_20260126.log 或 pyQuickStart_20260126.log
                        date_str = log_file.stem.split('_')[-1]
                        file_date = datetime.strptime(date_str, '%Y%m%d')
                        
                        # 如果文件日期早于截止日期，删除它
                        if file_date < cutoff_date:
                            log_file.unlink()
                            self.logger.info(f"已删除过期日志: {log_file.name}")
                    except (ValueError, IndexError):
                        # 文件名格式不正确，跳过
                        continue
            
        except Exception as e:
            # 清理失败不应该影响程序运行
            print(f"清理日志文件时出错: {e}")

    def _check_date_change(self):
        """检查日期是否变化，如果变化则切换到新的日志文件"""
        current_date = datetime.now().date()
        
        if current_date != self.current_date:
            # 日期已变化，需要切换日志文件
            log_dir = Path("logs")
            new_log_file = log_dir / f"pyQuickStart_{current_date.strftime('%Y%m%d')}.log"
            
            # 移除旧的文件处理器
            for handler in self.logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    self.logger.removeHandler(handler)
            
            # 添加新的文件处理器
            new_handler = logging.FileHandler(new_log_file, encoding='utf-8')
            new_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
            self.logger.addHandler(new_handler)
            
            self.current_date = current_date
            self.log_file = new_log_file
            self.logger.info(f"日志文件已切换到: {new_log_file.name}")
            
            # 清理旧日志
            self._cleanup_old_logs(log_dir, days=7)

    def info(self, message: str, exc_info=False):
        self._check_date_change()
        self.logger.info(message, exc_info=exc_info)

    def warning(self, message: str, exc_info=False):
        self._check_date_change()
        self.logger.warning(message, exc_info=exc_info)

    def error(self, message: str, exc_info=False):
        self._check_date_change()
        self.logger.error(message, exc_info=exc_info)

    def debug(self, message: str, exc_info=False):
        self._check_date_change()
        self.logger.debug(message, exc_info=exc_info)

    def critical(self, message: str, exc_info=False):
        self._check_date_change()
        self.logger.critical(message, exc_info=exc_info)

