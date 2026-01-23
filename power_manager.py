"""
电源管理模块
防止系统休眠
"""
import ctypes
import threading
import time
from pynput.keyboard import Controller, Key
from logger import Logger

# Windows电源管理常量
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

POWER_REQUEST_CONTEXT_VERSION = 0
POWER_REQUEST_CONTEXT_SIMPLE_STRING = 0x1

PowerRequestSystemRequired = 0
PowerRequestDisplayRequired = 1
PowerRequestAwayModeRequired = 2


class _ReasonContextReason(ctypes.Union):
    _fields_ = [("SimpleReasonString", ctypes.c_wchar_p)]


class _ReasonContext(ctypes.Structure):
    _fields_ = [
        ("Version", ctypes.c_uint32),
        ("Flags", ctypes.c_uint32),
        ("Reason", _ReasonContextReason),
    ]


class PowerManager:
    def __init__(self):
        self.logger = Logger()
        self.is_preventing_sleep = False
        self._keepalive_timer = None
        self._keepalive_interval_seconds = 30
        self._power_request_handle = None
        self._keyboard = Controller()
        self._keyboard_simulation_timer = None
        self._keyboard_simulation_interval = 55  # 每55秒模拟一次按键（比60秒更频繁）

    def _get_set_thread_execution_state(self):
        if not hasattr(ctypes, "windll"):
            return None
        try:
            func = ctypes.windll.kernel32.SetThreadExecutionState
            func.argtypes = [ctypes.c_uint]
            func.restype = ctypes.c_uint
            return func
        except Exception:
            return None

    def _get_power_request_apis(self):
        if not hasattr(ctypes, "windll"):
            return None
        try:
            kernel32 = ctypes.windll.kernel32
            power_create_request = kernel32.PowerCreateRequest
            power_create_request.argtypes = [ctypes.POINTER(_ReasonContext)]
            power_create_request.restype = ctypes.c_void_p

            power_set_request = kernel32.PowerSetRequest
            power_set_request.argtypes = [ctypes.c_void_p, ctypes.c_int]
            power_set_request.restype = ctypes.c_int

            power_clear_request = kernel32.PowerClearRequest
            power_clear_request.argtypes = [ctypes.c_void_p, ctypes.c_int]
            power_clear_request.restype = ctypes.c_int

            close_handle = kernel32.CloseHandle
            close_handle.argtypes = [ctypes.c_void_p]
            close_handle.restype = ctypes.c_int

            return power_create_request, power_set_request, power_clear_request, close_handle
        except Exception:
            return None

    def _ensure_power_request_handle(self):
        if self._power_request_handle is not None:
            return True

        apis = self._get_power_request_apis()
        if apis is None:
            return False

        power_create_request, _, _, _ = apis
        reason = _ReasonContext(
            Version=POWER_REQUEST_CONTEXT_VERSION,
            Flags=POWER_REQUEST_CONTEXT_SIMPLE_STRING,
            Reason=_ReasonContextReason(SimpleReasonString="pyQuickStart 防休眠"),
        )
        handle = power_create_request(ctypes.byref(reason))
        if not handle:
            self.logger.error("PowerCreateRequest 返回空句柄")
            return False
        self._power_request_handle = handle
        return True

    def _set_power_requests(self):
        apis = self._get_power_request_apis()
        if apis is None:
            return True
        power_create_request, power_set_request, _, _ = apis
        _ = power_create_request

        if not self._ensure_power_request_handle():
            self.logger.warning("PowerCreateRequest 失败，降级使用 SetThreadExecutionState")
            return False

        ok1 = bool(power_set_request(self._power_request_handle, PowerRequestSystemRequired))
        ok2 = bool(power_set_request(self._power_request_handle, PowerRequestDisplayRequired))
        if not ok1 or not ok2:
            self.logger.error("PowerSetRequest 失败")
            return False
        self.logger.info("PowerSetRequest 已启用 (SystemRequired/DisplayRequired)")
        return True

    def _clear_power_requests(self):
        apis = self._get_power_request_apis()
        if apis is None:
            return True
        _, _, power_clear_request, close_handle = apis

        handle = self._power_request_handle
        if handle is None:
            return True

        ok1 = bool(power_clear_request(handle, PowerRequestSystemRequired))
        ok2 = bool(power_clear_request(handle, PowerRequestDisplayRequired))
        _ = close_handle(handle)
        self._power_request_handle = None

        if not ok1 or not ok2:
            self.logger.error("PowerClearRequest 失败")
            return False
        self.logger.info("PowerClearRequest 已关闭 (SystemRequired/DisplayRequired)")
        return True

    def _cancel_keepalive(self):
        timer = self._keepalive_timer
        self._keepalive_timer = None
        if timer is not None:
            try:
                timer.cancel()
            except Exception:
                pass

    def _simulate_key_press(self):
        """模拟无感按键操作 - 使用 Shift 键（不会影响用户操作）"""
        try:
            # 使用 Shift 键，按下并立即释放，不会产生任何可见效果
            # 但足以让系统认为有用户活动
            self._keyboard.press(Key.shift)
            time.sleep(0.001)  # 1毫秒延迟
            self._keyboard.release(Key.shift)
            self.logger.info("模拟按键操作完成 (Shift)")
        except Exception as e:
            self.logger.error(f"模拟按键失败: {e}")

    def _cancel_keyboard_simulation(self):
        """取消键盘模拟定时器"""
        timer = self._keyboard_simulation_timer
        self._keyboard_simulation_timer = None
        if timer is not None:
            try:
                timer.cancel()
            except Exception:
                pass

    def _schedule_keyboard_simulation(self):
        """调度键盘模拟任务"""
        self._cancel_keyboard_simulation()
        if not self.is_preventing_sleep:
            return

        def _tick():
            if not self.is_preventing_sleep:
                return
            try:
                self._simulate_key_press()
            finally:
                self._schedule_keyboard_simulation()

        timer = threading.Timer(self._keyboard_simulation_interval, _tick)
        timer.daemon = True
        self._keyboard_simulation_timer = timer
        timer.start()

    def _schedule_keepalive(self):
        self._cancel_keepalive()
        if not self.is_preventing_sleep:
            return

        def _tick():
            if not self.is_preventing_sleep:
                return
            try:
                func = self._get_set_thread_execution_state()
                if func is not None:
                    func(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
            finally:
                self._schedule_keepalive()

        timer = threading.Timer(self._keepalive_interval_seconds, _tick)
        timer.daemon = True
        self._keepalive_timer = timer
        timer.start()

    def prevent_sleep(self):
        """防止系统休眠"""
        if self.is_preventing_sleep:
            self.logger.debug("防休眠模式已经启用，跳过")
            return True

        try:
            ok_power_request = self._set_power_requests()

            func = self._get_set_thread_execution_state()
            if func is None:
                self.logger.warning("启用防休眠失败: 当前平台不支持 SetThreadExecutionState")
                if ok_power_request:
                    self.is_preventing_sleep = True
                    self._schedule_keepalive()
                    return True
                return False

            result = func(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
            ok_set_thread = bool(result)
            if not ok_set_thread:
                self.logger.error("启用防休眠失败: SetThreadExecutionState 返回 0")
                if not ok_power_request:
                    return False

            self.is_preventing_sleep = True
            self._schedule_keepalive()
            self._schedule_keyboard_simulation()  # 启动键盘模拟
            self.logger.info(f"已启用防休眠模式 (API返回值: {result}，包含键盘模拟)")
            if not ok_power_request:
                self.logger.warning("PowerSetRequest 未生效/不可用，本次仅依赖 SetThreadExecutionState + 键盘模拟")
            return True
        except Exception as e:
            self.logger.error(f"启用防休眠失败: {e}")
            return False

    def allow_sleep(self):
        """允许系统休眠"""
        if not self.is_preventing_sleep:
            self.logger.debug("防休眠模式未启用，跳过")
            return True

        try:
            self._cancel_keepalive()
            self._cancel_keyboard_simulation()  # 取消键盘模拟

            ok_power_clear = self._clear_power_requests()

            func = self._get_set_thread_execution_state()
            if func is None:
                self.is_preventing_sleep = False
                self.logger.warning("关闭防休眠: 当前平台不支持 SetThreadExecutionState")
                return bool(ok_power_clear)

            result = func(ES_CONTINUOUS)
            ok_set_thread = bool(result)
            if not ok_set_thread:
                self.logger.error("关闭防休眠失败: SetThreadExecutionState 返回 0")
                return bool(ok_power_clear)
            self.is_preventing_sleep = False
            self.logger.info(f"已关闭防休眠模式 (API返回值: {result})")
            if not ok_power_clear:
                self.logger.warning("PowerClearRequest 失败/不可用，但 SetThreadExecutionState 已恢复")
            return True
        except Exception as e:
            self.logger.error(f"关闭防休眠失败: {e}")
            return False

    def __del__(self):
        """析构函数，确保恢复系统休眠功能"""
        if self.is_preventing_sleep:
            self.logger.info("PowerManager析构函数被调用：检测到防休眠模式仍启用")
            self.logger.info("PowerManager析构函数：恢复系统休眠功能")
            self.allow_sleep()
        else:
            self.logger.debug("PowerManager析构函数被调用：防休眠模式未启用，无需清理")
