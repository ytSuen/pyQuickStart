"""
电源管理模块
防止系统休眠
"""
import ctypes
from logger import Logger

# Windows电源管理常量
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


class PowerManager:
    def __init__(self):
        self.logger = Logger()
        self.is_preventing_sleep = False

    def prevent_sleep(self):
        """防止系统休眠"""
        if self.is_preventing_sleep:
            self.logger.debug("防休眠模式已经启用，跳过")
            return

        try:
            # 调用Windows API防止休眠
            result = ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            )
            self.is_preventing_sleep = True
            self.logger.info(f"已启用防休眠模式 (API返回值: {result})")
        except Exception as e:
            self.logger.error(f"启用防休眠失败: {e}")

    def allow_sleep(self):
        """允许系统休眠"""
        if not self.is_preventing_sleep:
            self.logger.debug("防休眠模式未启用，跳过")
            return

        try:
            # 恢复系统默认电源管理
            result = ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            self.is_preventing_sleep = False
            self.logger.info(f"已关闭防休眠模式 (API返回值: {result})")
        except Exception as e:
            self.logger.error(f"关闭防休眠失败: {e}")

    def __del__(self):
        """析构函数，确保恢复系统休眠功能"""
        if self.is_preventing_sleep:
            self.logger.info("PowerManager析构函数被调用：检测到防休眠模式仍启用")
            self.logger.info("PowerManager析构函数：恢复系统休眠功能")
            self.allow_sleep()
        else:
            self.logger.debug("PowerManager析构函数被调用：防休眠模式未启用，无需清理")
