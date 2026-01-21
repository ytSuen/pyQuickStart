"""
配置管理模块
负责保存和加载快捷键配置
"""
import json
from pathlib import Path
from typing import Dict
from logger import Logger


class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.logger = Logger()
        self.config: Dict = {}
        self.load()

    def load(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info(f"配置已加载: {len(self.config.get('hotkeys', {}))} 个快捷键")
            else:
                self.config = {"hotkeys": {}}
                self.logger.info("创建新配置文件")
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            self.config = {"hotkeys": {}}

    def save(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            self.logger.info("配置已保存")
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")

    def get_hotkeys(self) -> Dict[str, str]:
        """获取所有快捷键配置"""
        hotkeys = self.config.get("hotkeys", {})
        # 确保返回的是字典类型
        if not isinstance(hotkeys, dict):
            self.logger.warning(f"配置中的hotkeys不是字典类型: {type(hotkeys)}，返回空字典")
            return {}
        return hotkeys

    def add_hotkey(self, hotkey: str, program_path: str):
        """添加快捷键"""
        if "hotkeys" not in self.config or not isinstance(self.config.get("hotkeys"), dict):
            self.config["hotkeys"] = {}
        self.config["hotkeys"][hotkey] = program_path
        self.save()

    def remove_hotkey(self, hotkey: str):
        """移除快捷键"""
        if "hotkeys" in self.config and hotkey in self.config["hotkeys"]:
            del self.config["hotkeys"][hotkey]
            self.save()
