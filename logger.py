"""
日志记录模块
"""
import logging
import threading
from pathlib import Path
from datetime import datetime


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

        log_file = log_dir / f"hotkey_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def info(self, message: str, exc_info=False):
        self.logger.info(message, exc_info=exc_info)

    def warning(self, message: str, exc_info=False):
        self.logger.warning(message, exc_info=exc_info)

    def error(self, message: str, exc_info=False):
        self.logger.error(message, exc_info=exc_info)

    def debug(self, message: str, exc_info=False):
        self.logger.debug(message, exc_info=exc_info)

    def critical(self, message: str, exc_info=False):
        self.logger.critical(message, exc_info=exc_info)

