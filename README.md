# 快捷键启动工具

一个 Windows 桌面工具，支持自定义全局快捷键快速启动程序、打开网页、访问文件夹，并提供独立的防休眠功能。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## 📸 界面预览

现代化的浅色商务风格界面，简洁易用：
- 实时统计卡片（配置快捷键数、运行中程序数、防休眠状态）
- 快捷键录制输入框（点击后直接按下快捷键组合）
- 独立的防休眠控制按钮
- 清晰的快捷键列表管理

## ✨ 功能特性

- 🎯 **全局快捷键监听**（支持 Ctrl+Alt+Shift+Win 组合键）
- 🚀 **多种目标类型**：程序、网页、文件夹、文件
- 💤 **独立防休眠控制**（可独立开启/关闭，不受程序关闭影响）
- 🔄 **进程监控**（避免重复启动，实时显示运行中程序数量）
- 🎨 **现代化界面**（PyQt5 浅色商务风格设计）
- 🛡️ **冲突检测**（自动检测系统保留快捷键冲突）
- 💾 **配置自动保存**
- 📝 **完整日志记录**
- 📊 **实时统计**（配置快捷键数、运行中程序数、防休眠状态）
- 🔄 **自动更新**（启动时自动检查更新，一键下载安装新版本）

## 📋 系统要求

- Windows 10/11
- Python 3.8+
- 管理员权限（用于全局快捷键）

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**核心依赖**:
- `keyboard` - 全局快捷键监听
- `psutil` - 进程管理
- `PyQt5` - 现代化桌面界面

### 2. 启动程序

**⚠️ 重要：必须以管理员权限运行！**

**方式一（推荐）**：
```bash
# 右键点击 "启动.bat"，选择 "以管理员身份运行"
启动.bat
```

**方式二**：
```bash
# 右键点击 "main.py"，选择 "以管理员身份运行"
python main.py
```

**提示**: 
- 首次运行会自动创建配置文件
- 不以管理员权限运行将无法监听全局快捷键

### 3. 添加快捷键

1. 点击快捷键输入框，按下你想要的快捷键组合（如：Ctrl+Alt+N）
2. 输入目标路径或点击"浏览文件"/"浏览文件夹"按钮
3. 点击"添加快捷键"保存

### 4. 启动监听

点击"启动监听"按钮，然后使用快捷键测试！

### 5. 防休眠功能（可选）

- 点击"开启防休眠"按钮可独立控制防休眠功能
- 防休眠状态会持续保持，即使关闭程序也不会自动关闭
- 需要手动点击"关闭防休眠"才会停止

## 📝 快捷键格式

**格式**: `修饰键+修饰键+按键`

**修饰键**: `ctrl`, `alt`, `shift`, `win`

**示例**:
```
ctrl+alt+n      # Ctrl + Alt + N
ctrl+shift+t    # Ctrl + Shift + T
win+e           # Windows + E
```

## 🎯 支持的目标类型

| 类型 | 示例 |
|------|------|
| 程序 | `C:\Windows\notepad.exe` |
| 网页 | `https://www.google.com` |
| 文件夹 | `C:\Users\YourName\Documents` |
| 文件 | `D:\path\to\file.pdf` |

## 💡 配置示例

```
快捷键          目标
-----------------------------------------
ctrl+alt+n     C:\Windows\notepad.exe
ctrl+alt+g     https://www.google.com
ctrl+alt+d     C:\Users\YourName\Documents
ctrl+alt+v     C:\Program Files\VS Code\Code.exe
ctrl+alt+c     C:\Program Files\Google\Chrome\chrome.exe
```

## ⚠️ 注意事项

1. ⚠️ **必须以管理员权限运行**（否则快捷键无法生效）
2. ⚠️ **避免使用系统保留快捷键**（如 Ctrl+Alt+Del、Win+L 等）
3. ✅ 程序会自动检测快捷键冲突并提示
4. ✅ 配置文件：`config.json`
5. ✅ 日志文件：`logs/hotkey_YYYYMMDD.log`
6. ✅ 快捷键录制：点击输入框后直接按下快捷键组合
7. ✅ 防休眠功能独立运行，关闭程序不会自动关闭防休眠
8. ✅ 实时显示运行中程序数量和防休眠状态

### 系统保留快捷键（请避免使用）
- `Ctrl+Alt+Delete` - 任务管理器
- `Ctrl+Shift+Esc` - 任务管理器
- `Win+L` - 锁屏
- `Win+D` - 显示桌面
- `Win+E` - 文件资源管理器
- `Alt+Tab` - 切换窗口
- `Alt+F4` - 关闭窗口

## 📁 项目结构

```
├── main.py               # 主入口（自动请求管理员权限）
├── gui_qt.py             # PyQt5 界面实现（浅色商务风格）
├── hotkey_manager.py     # 快捷键管理（含冲突检测）
├── power_manager.py      # 电源管理（防休眠）
├── config_manager.py     # 配置管理（JSON）
├── logger.py             # 日志记录
├── 启动.bat              # 管理员权限启动脚本
├── requirements.txt      # 依赖列表
├── resources/            # 资源文件
│   └── SYT.png          # 程序图标
├── logs/                 # 日志目录
└── tests/                # 测试目录
```

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_hotkey_manager.py

# 查看覆盖率
pytest --cov=. --cov-report=html
```

## 🐛 故障排除

| 问题 | 解决方案 |
|------|----------|
| 快捷键不响应 | 1. 确保以管理员身份运行<br>2. 检查状态是否显示"运行中"<br>3. 查看日志文件 |
| 提示需要管理员权限 | 右键点击 `启动.bat`，选择"以管理员身份运行" |
| 快捷键冲突警告 | 更换其他快捷键组合，避免系统保留快捷键 |
| PyQt5 无法启动 | `pip install PyQt5` |
| 目标无法打开 | 检查路径是否正确且文件存在 |
| 配置文件损坏 | 删除 `config.json` 重新生成 |
| 程序已运行不再启动 | 这是防重复启动功能，先关闭已运行的程序 |
| 防休眠无法关闭 | 重新打开程序，点击"关闭防休眠"按钮 |
| 运行中程序数量为0 | 这是正常的，只有通过快捷键启动的程序才会被监控 |

## 📦 打包发布

使用 PyInstaller 打包成独立可执行文件：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包成单文件（带窗口）
pyinstaller --onefile --windowed --icon=resources/SYT.png --name="快捷键启动工具" main.py

# 打包后的文件在 dist/ 目录下
```

**注意**：打包后的 exe 文件仍需要以管理员权限运行。

## 🔄 自动更新

程序内置自动更新功能，无需手动下载新版本：

### 用户使用
1. **自动检查**：程序启动后 3 秒自动检查更新
2. **手动检查**：点击界面右上角 "🔄 检查更新" 按钮
3. **一键更新**：发现新版本时，点击确认即可自动下载安装
4. **自动重启**：更新完成后程序自动重启到新版本

### 开发者发布新版本
详细步骤请参考 [自动更新使用指南.md](./自动更新使用指南.md)

快速发布：
```bash
# 使用发布助手（推荐）
发布新版本.bat

# 或手动执行
1. 编辑 version.json 更新版本号
2. 运行 打包程序.bat
3. 在 Gitee 创建 Release 并上传 exe
4. 提交代码到仓库
```

版本号规则：
- 主版本号（X.0.0）：重大功能变更
- 次版本号（1.X.0）：新增功能
- 修订号（1.0.X）：Bug 修复

## 🔧 开发相关

### 代码结构

- `main.py` - 程序入口，自动请求管理员权限
- `gui_qt.py` - PyQt5 界面，包含所有 UI 组件和交互逻辑
- `hotkey_manager.py` - 快捷键管理，使用 keyboard 库监听全局快捷键
- `power_manager.py` - 电源管理，使用 ctypes 调用 Windows API 防止休眠
- `config_manager.py` - 配置管理，JSON 格式存储
- `logger.py` - 日志记录，按日期分文件

### 技术栈

- **GUI**: PyQt5
- **快捷键**: keyboard
- **进程管理**: psutil
- **电源管理**: ctypes (Windows API)
- **测试**: pytest

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 更新日志

### v1.0.0 (2026-01-22)
- ✅ 实现全局快捷键监听
- ✅ 支持多种目标类型（程序、网页、文件夹）
- ✅ 独立防休眠控制
- ✅ 进程监控和防重复启动
- ✅ 快捷键冲突检测
- ✅ 现代化 PyQt5 界面
- ✅ 自动请求管理员权限

## 📄 许可证

MIT License
