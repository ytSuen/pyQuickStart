"""
自动更新模块
检查并下载新版本
"""
import os
import sys
import json
import requests
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, Optional
from logger import Logger


class Updater:
    """自动更新器"""
    
    # Gitee 仓库配置
    REPO_OWNER = "sytao_2020"
    REPO_NAME = "pyQuickStart"
    
    # 版本信息URL（使用Gitee Raw文件）
    VERSION_URL = f"https://gitee.com/{REPO_OWNER}/{REPO_NAME}/raw/main/version.json"
    
    # 下载URL模板
    DOWNLOAD_URL_TEMPLATE = f"https://gitee.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{{tag}}/pyQuickStart.exe"
    
    def __init__(self):
        self.logger = Logger()
        self.current_version = self._load_local_version()
        
    def _load_local_version(self) -> str:
        """加载本地版本号"""
        try:
            version_file = self._get_version_file_path()
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', '1.0.0')
        except Exception as e:
            self.logger.error(f"读取本地版本失败: {e}")
        return "1.0.0"
    
    def _get_version_file_path(self) -> Path:
        """获取版本文件路径"""
        if getattr(sys, 'frozen', False):
            # 打包后，version.json 在 _MEIPASS 临时目录中
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            return Path(base_path) / 'version.json'
        else:
            # 开发环境
            return Path(__file__).parent / 'version.json'
    
    def check_update(self) -> Tuple[bool, Optional[dict]]:
        """
        检查是否有新版本
        
        Returns:
            (has_update, version_info)
            has_update: 是否有更新
            version_info: 版本信息字典，包含 version, download_url, changelog 等
        """
        try:
            self.logger.info(f"检查更新: 当前版本 {self.current_version}")
            
            # 请求版本信息
            response = requests.get(self.VERSION_URL, timeout=10)
            response.raise_for_status()
            
            remote_info = response.json()
            remote_version = remote_info.get('version', '1.0.0')
            
            self.logger.info(f"远程版本: {remote_version}")
            
            # 比较版本号
            if self._compare_version(remote_version, self.current_version) > 0:
                # 构建下载URL
                download_url = remote_info.get('download_url')
                if not download_url:
                    # 如果没有指定下载URL，使用默认模板
                    tag = f"v{remote_version}"
                    download_url = self.DOWNLOAD_URL_TEMPLATE.format(tag=tag)
                
                version_info = {
                    'version': remote_version,
                    'download_url': download_url,
                    'changelog': remote_info.get('changelog', ''),
                    'build_date': remote_info.get('build_date', ''),
                    'description': remote_info.get('description', '')
                }
                
                self.logger.info(f"发现新版本: {remote_version}")
                return True, version_info
            else:
                self.logger.info("当前已是最新版本")
                return False, None
                
        except requests.RequestException as e:
            self.logger.error(f"检查更新失败（网络错误）: {e}")
            return False, None
        except Exception as e:
            self.logger.error(f"检查更新失败: {e}")
            return False, None
    
    def _compare_version(self, v1: str, v2: str) -> int:
        """
        比较版本号
        
        Returns:
            1: v1 > v2
            0: v1 == v2
            -1: v1 < v2
        """
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            
            # 补齐长度
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))
            
            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            return 0
        except Exception as e:
            self.logger.error(f"版本比较失败: {e}")
            return 0
    
    def download_update(self, version_info: dict, progress_callback=None) -> Tuple[bool, str]:
        """
        下载更新
        
        Args:
            version_info: 版本信息
            progress_callback: 进度回调函数 callback(downloaded, total)
            
        Returns:
            (success, message/file_path)
        """
        download_url = version_info.get('download_url')
        if not download_url:
            return False, "下载URL不存在"
        
        try:
            self.logger.info(f"开始下载: {download_url}")
            
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, 'pyQuickStart_new.exe')
            
            # 下载文件
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            self.logger.info(f"下载完成: {temp_file}")
            return True, temp_file
            
        except Exception as e:
            self.logger.error(f"下载失败: {e}")
            return False, str(e)
    
    def apply_update(self, new_exe_path: str) -> Tuple[bool, str]:
        """
        应用更新（替换当前exe）
        
        Args:
            new_exe_path: 新exe文件路径
            
        Returns:
            (success, message)
        """
        try:
            if not getattr(sys, 'frozen', False):
                return False, "仅支持打包后的exe更新"
            
            current_exe = sys.executable
            backup_exe = current_exe + '.old'
            
            self.logger.info(f"准备更新: {current_exe}")
            
            # 创建更新脚本
            update_script = self._create_update_script(
                new_exe_path, 
                current_exe, 
                backup_exe
            )
            
            self.logger.info("启动更新脚本")
            
            # 启动更新脚本并退出当前程序
            if sys.platform == 'win32':
                subprocess.Popen(
                    ['cmd', '/c', update_script],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                subprocess.Popen(['sh', update_script])
            
            return True, "更新脚本已启动，程序即将重启"
            
        except Exception as e:
            self.logger.error(f"应用更新失败: {e}")
            return False, str(e)
    
    def _create_update_script(self, new_exe: str, current_exe: str, backup_exe: str) -> str:
        """创建更新脚本"""
        if sys.platform == 'win32':
            script_path = os.path.join(tempfile.gettempdir(), 'update_pyqs.bat')
            script_content = f'''@echo off
chcp 65001 >nul
echo 正在更新程序...
timeout /t 2 /nobreak >nul

REM 备份当前版本
if exist "{current_exe}" (
    echo 备份当前版本...
    move /y "{current_exe}" "{backup_exe}"
)

REM 复制新版本
echo 安装新版本...
move /y "{new_exe}" "{current_exe}"

REM 启动新版本
echo 启动程序...
start "" "{current_exe}"

REM 删除备份（可选）
timeout /t 2 /nobreak >nul
if exist "{backup_exe}" (
    del /f /q "{backup_exe}"
)

REM 删除脚本自身
del /f /q "%~f0"
'''
        else:
            script_path = os.path.join(tempfile.gettempdir(), 'update_pyqs.sh')
            script_content = f'''#!/bin/bash
echo "正在更新程序..."
sleep 2

# 备份当前版本
if [ -f "{current_exe}" ]; then
    echo "备份当前版本..."
    mv "{current_exe}" "{backup_exe}"
fi

# 复制新版本
echo "安装新版本..."
mv "{new_exe}" "{current_exe}"
chmod +x "{current_exe}"

# 启动新版本
echo "启动程序..."
"{current_exe}" &

# 删除备份
sleep 2
if [ -f "{backup_exe}" ]; then
    rm -f "{backup_exe}"
fi

# 删除脚本自身
rm -f "$0"
'''
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return script_path
    
    def get_current_version(self) -> str:
        """获取当前版本号"""
        return self.current_version
