"""
Web UI 集成模块
使用 pywebview 将 HTML UI 与 Python 后端连接
"""
import webview
import os
import sys
from pathlib import Path
from hotkey_manager import HotkeyManager
from power_manager import PowerManager
from config_manager import ConfigManager
from logger import Logger


class WebAPI:
    """JavaScript 可调用的 Python API"""
    
    def __init__(self):
        self.hotkey_manager = HotkeyManager()
        self.power_manager = PowerManager()
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self.is_monitoring = False
        
        # 加载已保存的配置
        self._load_saved_hotkeys()
    
    def _load_saved_hotkeys(self):
        """加载已保存的快捷键配置"""
        hotkeys = self.config_manager.get_hotkeys()
        for hotkey, path in hotkeys.items():
            self.hotkey_manager.add_hotkey(hotkey, path)
        self.logger.info(f"已加载 {len(hotkeys)} 个快捷键配置")
    
    def get_hotkeys(self):
        """获取所有快捷键配置"""
        hotkeys = self.config_manager.get_hotkeys()
        return [
            {
                'hotkey': key,
                'path': path,
                'status': '已注册' if self.is_monitoring else '未注册'
            }
            for key, path in hotkeys.items()
        ]
    
    def add_hotkey(self, hotkey, path):
        """添加快捷键"""
        try:
            # 验证快捷键格式
            if not self._validate_hotkey(hotkey):
                return {'success': False, 'error': '快捷键格式不正确\n\n正确格式示例:\n• ctrl+alt+n\n• ctrl+shift+t\n• win+e\n\n必须包含至少一个修饰键（ctrl、alt、shift、win）'}
            
            # 验证目标路径
            if not path or not path.strip():
                return {'success': False, 'error': '请输入目标路径'}
            
            # 检查是否是 URL
            if not path.startswith(('http://', 'https://', 'www.')):
                # 检查文件或文件夹是否存在
                if not os.path.exists(path):
                    return {'success': False, 'error': f'目标不存在:\n{path}\n\n请检查路径是否正确'}
            
            # 添加快捷键
            if self.hotkey_manager.add_hotkey(hotkey, path):
                self.config_manager.add_hotkey(hotkey, path)
                self.logger.info(f"添加快捷键: {hotkey} -> {path}")
                
                # 如果正在监听，重新注册快捷键
                if self.is_monitoring:
                    self.hotkey_manager.stop()
                    self.hotkey_manager.start()
                
                return {'success': True}
            else:
                return {'success': False, 'error': '添加失败'}
        
        except Exception as e:
            self.logger.error(f"添加快捷键失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def remove_hotkey(self, hotkey):
        """删除快捷键"""
        try:
            self.hotkey_manager.remove_hotkey(hotkey)
            self.config_manager.remove_hotkey(hotkey)
            self.logger.info(f"删除快捷键: {hotkey}")
            return {'success': True}
        except Exception as e:
            self.logger.error(f"删除快捷键失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def toggle_monitoring(self):
        """切换监听状态"""
        try:
            if not self.is_monitoring:
                # 检查是否有配置
                if len(self.config_manager.get_hotkeys()) == 0:
                    return {
                        'success': False,
                        'error': '请先添加至少一个快捷键配置后再启动监听'
                    }
                
                self.hotkey_manager.start()
                self.is_monitoring = True
                self.logger.info("启动监听")
                return {'success': True, 'monitoring': True}
            else:
                self.hotkey_manager.stop()
                self.power_manager.allow_sleep()
                self.is_monitoring = False
                self.logger.info("停止监听")
                return {'success': True, 'monitoring': False}
        
        except Exception as e:
            self.logger.error(f"切换监听状态失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_status(self):
        """获取当前状态"""
        running_count = self.hotkey_manager.get_running_count()
        
        # 根据运行程序数量控制防休眠
        if running_count > 0:
            self.power_manager.prevent_sleep()
        else:
            self.power_manager.allow_sleep()
        
        return {
            'monitoring': self.is_monitoring,
            'hotkey_count': len(self.config_manager.get_hotkeys()),
            'running_count': running_count,
            'sleep_prevented': running_count > 0
        }
    
    def browse_file(self):
        """打开文件选择对话框"""
        try:
            result = webview.windows[0].create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=('所有文件 (*.*)', '可执行文件 (*.exe)', '批处理文件 (*.bat;*.cmd)')
            )
            if result and len(result) > 0:
                return {'success': True, 'path': result[0]}
            return {'success': False}
        except Exception as e:
            self.logger.error(f"文件选择失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def browse_folder(self):
        """打开文件夹选择对话框"""
        try:
            result = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG,
                allow_multiple=False
            )
            if result and len(result) > 0:
                return {'success': True, 'path': result[0]}
            return {'success': False}
        except Exception as e:
            self.logger.error(f"文件夹选择失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _validate_hotkey(self, hotkey):
        """验证快捷键格式"""
        if not hotkey or '+' not in hotkey:
            return False
        
        hotkey_lower = hotkey.lower()
        modifiers = ['ctrl', 'alt', 'shift', 'win']
        return any(mod in hotkey_lower for mod in modifiers)
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("开始清理资源")
        if self.is_monitoring:
            self.hotkey_manager.stop()
        self.power_manager.allow_sleep()
        self.logger.info("资源清理完成")


class WebGUI:
    """Web UI 主类"""
    
    def __init__(self):
        self.api = WebAPI()
        self.window = None
    
    def run(self):
        """启动 Web UI"""
        # 获取 HTML 文件路径
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            base_path = sys._MEIPASS
        else:
            # 开发环境路径
            base_path = os.path.dirname(__file__)
        
        html_path = os.path.join(base_path, 'ui', 'index-interactive.html')
        
        # 检查文件是否存在
        if not os.path.exists(html_path):
            self.api.logger.error(f"UI 文件不存在: {html_path}")
            print(f"错误: UI 文件不存在: {html_path}")
            print("请确保 ui/index-interactive.html 文件存在")
            return
        
        # 创建窗口
        self.window = webview.create_window(
            title='快捷键启动工具',
            url=html_path,
            js_api=self.api,
            width=1200,
            height=800,
            resizable=True,
            min_size=(800, 600)
        )
        
        # 注册关闭事件
        self.window.events.closing += self._on_closing
        
        # 启动
        self.api.logger.info("启动 Web UI")
        webview.start(debug=False)  # 设置 debug=True 可以打开开发者工具
    
    def _on_closing(self):
        """窗口关闭事件"""
        self.api.cleanup()


if __name__ == '__main__':
    try:
        app = WebGUI()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
