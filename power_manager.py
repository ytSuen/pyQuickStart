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

# 鼠标事件常量
MOUSEEVENTF_MOVE = 0x0001


class _ReasonContextReason(ctypes.Union):
    _fields_ = [("SimpleReasonString", ctypes.c_wchar_p)]


class _ReasonContext(ctypes.Structure):
    _fields_ = [
        ("Version", ctypes.c_uint32),
        ("Flags", ctypes.c_uint32),
        ("Reason", _ReasonContextReason),
    ]


class PowerManager:
    # 防护强度枚举
    class ProtectionLevel:
        LIGHT = "light"      # 轻度：60秒，20像素
        MEDIUM = "medium"    # 中度：30秒，50像素
        HEAVY = "heavy"      # 重度：15秒，100像素
        CUSTOM = "custom"    # 自定义：120秒，100像素（默认）
    
    def __init__(self, protection_level="custom"):
        self.logger = Logger()
        self.is_preventing_sleep = False
        self._keepalive_timer = None
        self._keepalive_interval_seconds = 30
        self._power_request_handle = None
        self._keyboard = Controller()
        self._keyboard_simulation_timer = None
        self._keyboard_simulation_interval = 120  # 默认120秒
        self.protection_level = protection_level
        self._mouse_movement_pixels = 100  # 默认100像素
        self._update_protection_settings()
        # 锁屏检测相关
        self._lock_count = 0
        self._last_lock_time = None
        # 错误跟踪
        self._last_critical_error = None

    def _update_protection_settings(self):
        """根据防护强度更新设置"""
        settings = {
            "light": (60, 20),
            "medium": (30, 50),
            "heavy": (15, 100),
            "custom": (120, 100)  # 自定义默认设置
        }
        interval, pixels = settings.get(self.protection_level, (120, 100))
        self._keyboard_simulation_interval = interval
        self._mouse_movement_pixels = pixels
        self.logger.debug(f"防护设置已更新: 强度={self.protection_level}, 间隔={interval}秒, 像素={pixels}px")
    
    def set_protection_level(self, level):
        """设置防护强度"""
        if level not in ["light", "medium", "heavy", "custom"]:
            self.logger.warning(f"无效的防护强度: {level}，保持当前设置")
            return False
        
        self.protection_level = level
        self._update_protection_settings()
        self.logger.info(f"防护强度已更改为: {level}")
        
        # 如果防护已启用，重新调度定时器
        if self.is_preventing_sleep:
            self._schedule_keyboard_simulation()
            self.logger.info("防护已启用，重新调度定时器以应用新设置")
        
        return True

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

    def _move_mouse(self, pixels):
        """执行鼠标移动 - 使用绝对坐标确保精确回到原位"""
        try:
            if not hasattr(ctypes, "windll"):
                error_msg = "鼠标移动失败: ctypes.windll不可用 (非Windows平台或ctypes未正确加载)"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            try:
                # 定义POINT结构体用于获取鼠标位置
                class POINT(ctypes.Structure):
                    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
                
                # 获取当前鼠标位置
                point = POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
                original_x, original_y = point.x, point.y
                self.logger.debug(f"鼠标原始位置: ({original_x}, {original_y})")
                
                # 向右移动
                ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, pixels, 0, 0, 0)
                self.logger.debug(f"鼠标向右移动: {pixels}px")
                time.sleep(0.15)  # 增加到150毫秒，让系统有足够时间识别为用户活动
                
                # 向左移动回原位（使用相对移动而不是绝对定位）
                ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, -pixels, 0, 0, 0)
                self.logger.debug(f"鼠标向左移动回原位: {pixels}px")
                time.sleep(0.05)
                
                self.logger.debug(f"鼠标移动完成: {pixels}px往返，已回到原位")
            except (OSError, AttributeError, ctypes.ArgumentError) as e:
                # 捕获ctypes特定异常
                error_msg = f"鼠标移动失败 (像素: {pixels}px): ctypes API调用错误 - {type(e).__name__}: {e}"
                self.logger.error(error_msg, exc_info=True)
                raise RuntimeError(error_msg) from e
        except RuntimeError:
            # 重新抛出RuntimeError以触发降级
            raise
        except Exception as e:
            # 捕获其他未预期的异常
            error_msg = f"鼠标移动失败 (像素: {pixels}px): 未预期的错误 - {type(e).__name__}: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    def _reset_idle_timer(self):
        """重置空闲计时器"""
        func = self._get_set_thread_execution_state()
        if func is not None:
            result = func(ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
            self.logger.debug(f"重置空闲计时器: SetThreadExecutionState API返回值={hex(result) if result else '0 (失败)'}")
            return result
        else:
            self.logger.debug("重置空闲计时器: SetThreadExecutionState API不可用")
            return None
    
    def _simulate_keyboard(self):
        """模拟按键 - 使用F15键（不会影响用户操作）"""
        try:
            # F15键通常不会被应用程序使用，是防止休眠的理想选择
            self._keyboard.press(Key.f15)
            time.sleep(0.05)  # 增加按键持续时间到50毫秒
            self._keyboard.release(Key.f15)
            self.logger.debug("模拟按键完成: F15")
        except Exception as e:
            # 如果F15失败，降级使用Shift
            self.logger.warning(f"F15按键失败，降级使用Shift: {e}")
            self._keyboard.press(Key.shift)
            time.sleep(0.05)
            self._keyboard.release(Key.shift)
            self.logger.debug("模拟按键完成: Shift (降级)")
    
    def _restore_continuous_state(self):
        """恢复持续状态"""
        func = self._get_set_thread_execution_state()
        if func is not None:
            result = func(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
            self.logger.debug(f"恢复持续状态: SetThreadExecutionState API返回值={hex(result) if result else '0 (失败)'}")
            return result
        else:
            self.logger.debug("恢复持续状态: SetThreadExecutionState API不可用")
            return None

    def _simulate_key_press(self):
        """模拟鼠标小范围移动 - 规避锁屏"""
        # 记录防护强度和移动像素数
        self.logger.debug(f"开始防护刷新 - 强度: {self.protection_level}, 移动像素: {self._mouse_movement_pixels}px, 间隔: {self._keyboard_simulation_interval}秒")
        
        # 跟踪各个方法的成功状态
        methods_success = {
            "mouse_movement": False,
            "reset_idle_timer": False,
            "simulate_keyboard": False,
            "restore_continuous_state": False
        }
        
        try:
            # 方法1：模拟按键（优先级提高，因为按键更可靠）
            self.logger.debug(f"步骤1: 模拟按键")
            try:
                self._simulate_keyboard()
                methods_success["simulate_keyboard"] = True
            except Exception as e:
                self.logger.warning(f"步骤1: 模拟按键失败: {e}")
            
            # 方法2：使用 mouse_event 移动鼠标（增大移动范围，规避锁屏）
            pixels = self._mouse_movement_pixels
            self.logger.debug(f"步骤2: 执行鼠标移动 ({pixels}px)")
            try:
                self._move_mouse(pixels)
                self.logger.debug(f"步骤2: 鼠标移动成功")
                methods_success["mouse_movement"] = True
            except Exception as e:
                self.logger.warning(f"步骤2: 鼠标移动失败，降级到其他方法: {e}")
            
            # 方法3：使用 SetThreadExecutionState 重置空闲计时器
            self.logger.debug(f"步骤3: 重置空闲计时器")
            try:
                result = self._reset_idle_timer()
                if result:
                    methods_success["reset_idle_timer"] = True
            except Exception as e:
                self.logger.warning(f"步骤3: 重置空闲计时器失败: {e}")
            
            # 方法4：恢复持续状态
            self.logger.debug(f"步骤4: 恢复持续状态")
            try:
                result = self._restore_continuous_state()
                if result:
                    methods_success["restore_continuous_state"] = True
            except Exception as e:
                self.logger.warning(f"步骤4: 恢复持续状态失败: {e}")
            
            # 检查是否所有方法都失败
            if not any(methods_success.values()):
                # 所有方法都失败
                error_msg = (
                    f"严重错误: 所有防护方法都失败！\n"
                    f"防护强度: {self.protection_level}\n"
                    f"失败的方法: 鼠标移动, 重置空闲计时器, 模拟按键, 恢复持续状态\n"
                    f"故障排除建议:\n"
                    f"1. 检查是否在虚拟机或远程桌面环境中运行\n"
                    f"2. 确认程序具有足够的系统权限\n"
                    f"3. 检查Windows版本兼容性\n"
                    f"4. 查看日志文件获取详细错误信息\n"
                    f"5. 尝试以管理员身份运行程序"
                )
                self.logger.critical(error_msg)
                # 存储错误信息供GUI显示
                self._last_critical_error = error_msg
            else:
                # 至少有一个方法成功
                success_methods = [k for k, v in methods_success.items() if v]
                self.logger.info(f"防锁屏刷新完成 (强度: {self.protection_level}, 成功方法: {', '.join(success_methods)})")
                # 清除之前的错误信息
                self._last_critical_error = None
                
        except Exception as e:
            # 捕获整个过程中的未预期异常
            error_msg = f"防锁屏刷新过程发生严重错误: {type(e).__name__}: {e}"
            self.logger.critical(error_msg, exc_info=True)
            self._last_critical_error = error_msg
    
    def get_last_critical_error(self):
        """获取最后一次严重错误信息（供GUI显示）"""
        return getattr(self, '_last_critical_error', None)

    def check_lock_state(self):
        """检测系统是否锁屏"""
        try:
            if hasattr(ctypes, "windll"):
                # 使用GetForegroundWindow检测
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd == 0:
                    # 可能处于锁屏状态
                    if self._last_lock_time is None:
                        self._last_lock_time = time.time()
                        self._lock_count += 1
                        self.logger.warning(f"检测到可能的锁屏事件 (第{self._lock_count}次)")
                    return True
                else:
                    if self._last_lock_time is not None:
                        duration = time.time() - self._last_lock_time
                        self.logger.info(f"从锁屏恢复，持续时间: {duration:.1f}秒")
                        self._last_lock_time = None
                    return False
        except Exception as e:
            self.logger.error(f"检测锁屏状态失败: {e}", exc_info=True)
        return False
    
    def get_lock_statistics(self):
        """获取锁屏统计信息"""
        return {
            "lock_count": self._lock_count,
            "currently_locked": self._last_lock_time is not None
        }

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
            self.logger.error(f"启用防休眠失败 (防护强度: {self.protection_level}): {e}", exc_info=True)
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
            self.logger.error(f"关闭防休眠失败 (防护强度: {self.protection_level}): {e}", exc_info=True)
            return False

    def __del__(self):
        """析构函数，确保恢复系统休眠功能"""
        if self.is_preventing_sleep:
            self.logger.info("PowerManager析构函数被调用：检测到防休眠模式仍启用")
            self.logger.info("PowerManager析构函数：恢复系统休眠功能")
            self.allow_sleep()
        else:
            self.logger.debug("PowerManager析构函数被调用：防休眠模式未启用，无需清理")
