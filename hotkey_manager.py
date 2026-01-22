"""
快捷键管理模块
负责全局快捷键监听和程序启动
"""
import keyboard
import subprocess
import psutil
import threading
import time
import ctypes
from pathlib import Path
from typing import Dict, List, Set
from logger import Logger


class HotkeyManager:
    # 支持的修饰键
    MODIFIERS = {'ctrl', 'alt', 'shift', 'win'}

    def __init__(self):
        self.hotkeys: Dict[str, str] = {}  # 快捷键 -> 程序路径
        self.running_processes: List[psutil.Process] = []
        self.logger = Logger()
        self.is_running = False
        
        # 常见的系统保留快捷键
        self.system_hotkeys: Set[str] = {
            'ctrl+alt+delete', 'ctrl+alt+del',
            'ctrl+shift+esc',
            'win+l', 'win+d', 'win+e', 'win+r', 'win+tab',
            'win+i', 'win+s', 'win+a', 'win+x',
            'alt+tab', 'alt+f4',
            'ctrl+alt+tab',
        }

    def _validate_hotkey_format(self, hotkey: str) -> bool:
        """
        验证快捷键格式
        - 必须包含至少一个修饰键（ctrl/alt/shift/win）
        - 使用加号(+)连接
        """
        if not hotkey or not isinstance(hotkey, str):
            return False

        # 转换为小写进行验证
        hotkey_lower = hotkey.lower()
        keys = hotkey_lower.split('+')

        if len(keys) < 2:
            return False

        # 检查是否包含至少一个修饰键
        has_modifier = any(key in self.MODIFIERS for key in keys)
        return has_modifier

    def _validate_target(self, target_path: str) -> bool:
        """
        验证目标路径
        - 支持 .exe 文件
        - 支持网页 URL (http:// 或 https://)
        - 支持文件夹
        - 支持其他可执行文件
        """
        if not target_path or not isinstance(target_path, str):
            return False

        # 检查是否是 URL
        if target_path.startswith(('http://', 'https://', 'www.')):
            return True
        
        # 检查是否是文件或文件夹
        path = Path(target_path)
        return path.exists()  # 文件或文件夹存在即可

    def check_system_conflict(self, hotkey: str) -> tuple[bool, str]:
        """
        检查快捷键是否与系统快捷键冲突
        返回: (是否冲突, 冲突说明)
        """
        hotkey_lower = hotkey.lower()
        
        # 检查是否是系统保留快捷键
        if hotkey_lower in self.system_hotkeys:
            return True, f"'{hotkey}' 是系统保留快捷键，可能无法正常工作"
        
        # 检查是否与已有快捷键冲突
        if hotkey in self.hotkeys:
            return True, f"'{hotkey}' 已被绑定到: {self.hotkeys[hotkey]}"
        
        return False, ""
    
    def is_admin(self) -> bool:
        """检查是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def add_hotkey(self, hotkey: str, target_path: str) -> tuple[bool, str]:
        """
        添加快捷键绑定
        返回: (是否成功, 消息)
        """
        try:
            # 验证快捷键格式
            if not self._validate_hotkey_format(hotkey):
                msg = f"快捷键格式无效: {hotkey}，必须包含至少一个修饰键（ctrl/alt/shift/win）"
                self.logger.error(msg)
                return False, msg

            # 验证目标路径
            if not self._validate_target(target_path):
                msg = f"目标路径无效: {target_path}"
                self.logger.error(msg)
                return False, msg

            # 检查系统冲突
            has_conflict, conflict_msg = self.check_system_conflict(hotkey)
            if has_conflict:
                self.logger.warning(conflict_msg)
                # 如果是已存在的快捷键，允许覆盖
                if hotkey not in self.hotkeys:
                    return False, conflict_msg

            self.hotkeys[hotkey] = target_path
            self.logger.info(f"添加快捷键: {hotkey} -> {target_path}")
            return True, "添加成功"
        except Exception as e:
            msg = f"添加快捷键失败: {e}"
            self.logger.error(msg)
            return False, msg

    def remove_hotkey(self, hotkey: str) -> bool:
        """移除快捷键绑定"""
        if hotkey in self.hotkeys:
            del self.hotkeys[hotkey]
            # 只在监听运行时才从keyboard移除
            if self.is_running:
                try:
                    keyboard.remove_hotkey(hotkey)
                except KeyError:
                    pass  # 快捷键可能未注册
            self.logger.info(f"移除快捷键: {hotkey}")
            return True
        return False

    def launch_program(self, target_path: str):
        """启动程序、打开网页或文件夹"""
        try:
            # 检查是否是 URL
            if target_path.startswith(('http://', 'https://', 'www.')):
                # 打开网页
                import webbrowser
                webbrowser.open(target_path)
                self.logger.info(f"打开网页: {target_path}")
                return
            
            path = Path(target_path)
            
            # 检查是否是文件夹
            if path.is_dir():
                # 打开文件夹
                import os
                os.startfile(target_path)
                self.logger.info(f"打开文件夹: {target_path}")
                return
            
            # 检查是否是可执行文件
            if not path.is_file():
                self.logger.error(f"目标不存在: {target_path}")
                return
            
            # 规范化程序路径用于比较
            normalized_path = path.resolve()

            # 首先检查我们监控的进程列表
            for proc in self.running_processes:
                try:
                    if proc.is_running():
                        proc_exe = Path(proc.exe()).resolve()
                        if proc_exe == normalized_path:
                            self.logger.info(f"程序已在监控列表中运行: {normalized_path.name} (PID: {proc.pid})")
                            return
                except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                    continue

            # 检查系统中是否有相同路径的程序在运行
            for proc in psutil.process_iter(['exe']):
                try:
                    if proc.info['exe']:
                        proc_exe = Path(proc.info['exe']).resolve()
                        if proc_exe == normalized_path:
                            self.logger.info(f"程序已在系统中运行: {normalized_path.name} (PID: {proc.pid})")
                            # 将已存在的进程添加到监控列表
                            ps_process = psutil.Process(proc.pid)
                            if ps_process not in self.running_processes:
                                self.running_processes.append(ps_process)
                            return
                except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                    continue

            # 启动程序
            import os
            os.startfile(target_path)
            self.logger.info(f"启动程序: {target_path}")
            
            # 等待进程启动
            time.sleep(0.5)

        except Exception as e:
            self.logger.error(f"启动失败: {e}")

    def start(self) -> tuple[bool, str]:
        """
        启动快捷键监听
        返回: (是否成功, 消息)
        """
        if self.is_running:
            return True, "监听已在运行"

        # 检查管理员权限
        if not self.is_admin():
            msg = "需要管理员权限才能监听全局快捷键！\n请右键点击程序，选择"以管理员身份运行""
            self.logger.error(msg)
            return False, msg

        self.is_running = True
        failed_hotkeys = []

        # 注册所有快捷键
        for hotkey, program_path in self.hotkeys.items():
            try:
                keyboard.add_hotkey(hotkey, lambda p=program_path: self.launch_program(p))
                self.logger.info(f"注册快捷键: {hotkey}")
            except Exception as e:
                self.logger.error(f"注册快捷键失败 {hotkey}: {e}")
                failed_hotkeys.append(hotkey)

        # 启动进程监控线程
        monitor_thread = threading.Thread(target=self._monitor_processes, daemon=True)
        monitor_thread.start()

        self.logger.info("快捷键监听已启动")
        
        if failed_hotkeys:
            msg = f"部分快捷键注册失败: {', '.join(failed_hotkeys)}"
            return False, msg
        
        return True, "监听启动成功"

    def stop(self):
        """停止快捷键监听"""
        if not self.is_running:
            self.logger.debug("快捷键监听未运行，无需停止")
            return

        self.logger.info("开始停止快捷键监听")
        self.is_running = False

        # 移除所有快捷键
        removed_count = 0
        for hotkey in self.hotkeys.keys():
            try:
                keyboard.remove_hotkey(hotkey)
                removed_count += 1
                self.logger.debug(f"已注销快捷键: {hotkey}")
            except Exception as e:
                self.logger.warning(f"注销快捷键失败 {hotkey}: {e}")

        self.logger.info(f"快捷键监听已停止，共注销 {removed_count} 个快捷键")

    def _monitor_processes(self):
        """监控已启动的进程"""
        while self.is_running:
            # 清理已结束的进程，同时处理可能的异常
            filtered_processes = []
            for p in self.running_processes:
                try:
                    if p.is_running():
                        filtered_processes.append(p)
                except (psutil.NoSuchProcess, psutil.AccessDenied, OSError, Exception):
                    # 进程不存在、无法访问或其他异常，跳过
                    pass

            self.running_processes = filtered_processes
            time.sleep(5)

    def get_running_count(self) -> int:
        """获取正在运行的程序数量"""
        # 过滤掉已结束的进程，同时处理可能的异常
        filtered_processes = []
        for p in self.running_processes:
            try:
                if p.is_running():
                    filtered_processes.append(p)
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError, Exception):
                # 进程不存在、无法访问或其他异常，跳过
                self.logger.debug("检查进程状态时发生异常，跳过该进程")

        self.running_processes = filtered_processes
        return len(self.running_processes)

    def __del__(self):
        """析构函数，确保停止监听"""
        if self.is_running:
            self.logger.info("HotkeyManager析构函数被调用：检测到监听仍在运行")
            self.logger.info("HotkeyManager析构函数：停止快捷键监听")
            self.stop()
        else:
            self.logger.debug("HotkeyManager析构函数被调用：监听未运行，无需清理")
