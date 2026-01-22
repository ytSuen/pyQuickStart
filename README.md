# 快捷键启动工具 (pyQuickStart)

一个 Windows 桌面工具，支持自定义全局快捷键快速启动程序、打开网页、访问文件夹，并提供**智能防休眠**功能（三重防护机制 + 无感键盘模拟）。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Version](https://img.shields.io/badge/version-1.1.0-green.svg)

## 📸 界面预览

现代化的浅色商务风格界面，简洁易用：
- 实时统计卡片（配置快捷键数、运行中程序数、防休眠状态）
- 快捷键录制输入框（点击后直接按下快捷键组合）
- 独立的防休眠控制按钮
- 清晰的快捷键列表管理

## ✨ 功能特性

### 核心功能
- 🎯 **全局快捷键监听**（支持 Ctrl+Alt+Shift+Win 组合键）
- 🚀 **多种目标类型**：程序、网页、文件夹、文件
- 🔄 **进程监控**（避免重复启动，实时显示运行中程序数量）
- 🎨 **现代化界面**（PyQt5 浅色商务风格设计）
- 🛡️ **冲突检测**（自动检测系统保留快捷键冲突）
- 💾 **配置自动保存**
- 📝 **完整日志记录**
- 📊 **实时统计**（配置快捷键数、运行中程序数、防休眠状态）

### 🌟 智能防休眠（新增）
- 💤 **独立防休眠控制**（可独立开启/关闭，不受程序关闭影响）
- 🛡️ **三重防护机制**：
  - Windows API 调用（SetThreadExecutionState + PowerRequest）
  - 定时刷新系统状态（每 30 秒）
  - **无感键盘模拟**（每 60 秒模拟 F15 键）
- 🎯 **完全无感操作**：
  - 使用 F15 功能键（极少使用，不干扰操作）
  - 按键持续仅 10 毫秒
  - 用户几乎感觉不到

### 📦 打包版本
- ✅ 提供独立 exe 文件（无需安装 Python）
- ✅ 单文件模式（约 37 MB）
- ✅ 包含所有依赖库
- ✅ 双击即可运行

## 📋 系统要求

### 使用打包版本（推荐）
- Windows 10/11
- 管理员权限（用于全局快捷键）
- 无需安装 Python

### 从源码运行
- Windows 10/11
- Python 3.8+
- 管理员权限（用于全局快捷键）

## 🚀 快速开始

### 方式一：使用打包版本（推荐）

1. **下载程序**
   - 从 `dist` 目录获取 `pyQuickStart.exe`
   - 或运行 `打包程序.bat` 自行打包

2. **启动程序**
   ```bash
   # 方式1：双击启动脚本
   启动程序.bat
   
   # 方式2：右键 exe 文件，选择"以管理员身份运行"
   dist\pyQuickStart.exe
   ```

3. **首次运行**
   - 可能被杀毒软件拦截，请添加信任
   - 会自动创建配置文件 `config.json`

### 方式二：从源码运行

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

   **核心依赖**:
   - `keyboard` - 全局快捷键监听
   - `psutil` - 进程管理
   - `PyQt5` - 现代化桌面界面
   - `pynput` - 键盘模拟（防休眠功能）

2. **启动程序**
   ```bash
   # 方式1：使用启动脚本
   启动程序.bat
   
   # 方式2：直接运行
   python main.py
   ```

**⚠️ 重要提示**：
- 必须以管理员权限运行（否则快捷键无法生效）
- 首次运行会自动创建配置文件
- 不以管理员权限运行将无法监听全局快捷键

### 3. 添加快捷键

1. 点击快捷键输入框，按下你想要的快捷键组合（如：Ctrl+Alt+N）
2. 输入目标路径或点击"浏览文件"/"浏览文件夹"按钮
3. 点击"添加快捷键"保存

### 4. 启动监听

点击"启动监听"按钮，然后使用快捷键测试！

### 5. 智能防休眠功能（可选）

**开启防休眠**：
- 点击"开启防休眠"按钮
- 状态卡片显示"开启"
- 程序会自动：
  - 调用 Windows API 防止休眠
  - 每 30 秒刷新一次系统状态
  - 每 60 秒模拟一次 F15 按键（完全无感）

**关闭防休眠**：
- 点击"关闭防休眠"按钮
- 状态卡片显示"关闭"

**特点**：
- ✅ 独立控制，不随快捷键启动/停止而变化
- ✅ 三重防护机制，确保不休眠
- ✅ 无感操作，不影响正常使用

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
├── dist/                     # 打包输出目录
│   └── pyQuickStart.exe     # 独立可执行文件（37 MB）
├── main.py                   # 主入口（自动请求管理员权限）
├── gui_qt.py                 # PyQt5 界面实现（浅色商务风格）
├── hotkey_manager.py         # 快捷键管理（含冲突检测）
├── power_manager.py          # 电源管理（防休眠 + 键盘模拟）
├── config_manager.py         # 配置管理（JSON）
├── logger.py                 # 日志记录
├── 启动程序.bat              # 启动脚本（打包版）
├── 打包程序.bat              # 重新打包脚本
├── 测试程序.bat              # 功能测试脚本
├── 清理无用文件.bat          # 清理缓存脚本
├── pyQuickStart.spec         # PyInstaller 配置
├── requirements.txt          # 依赖列表（完整）
├── requirements-prod.txt     # 生产依赖
├── requirements-dev.txt      # 开发依赖
├── 使用说明.md               # 详细使用文档
├── 快速开始.txt              # 快速入门指南
├── 打包完成报告.md           # 打包说明
├── 清理报告.txt              # 清理记录
├── resources/                # 资源文件
│   └── SYT.png              # 程序图标
├── logs/                     # 日志目录
├── tests/                    # 测试目录
└── .venv/                    # 虚拟环境
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
| exe 被杀毒软件拦截 | 添加到白名单/信任列表，这是 PyInstaller 打包程序的常见误报 |
| 打包失败 | 1. 确保虚拟环境已创建<br>2. 运行 `打包程序.bat`<br>3. 查看错误信息 |

## 📦 打包发布

### 自动打包（推荐）

```bash
# 双击运行打包脚本
打包程序.bat
```

脚本会自动：
1. 检查虚拟环境
2. 安装 PyInstaller（如果未安装）
3. 使用 `pyQuickStart.spec` 配置打包
4. 生成 `dist\pyQuickStart.exe`

### 手动打包

```bash
# 1. 激活虚拟环境
.venv\Scripts\activate

# 2. 安装 PyInstaller
pip install pyinstaller

# 3. 使用 spec 文件打包
pyinstaller pyQuickStart.spec --clean

# 4. 或使用命令行打包
pyinstaller --onefile --windowed --icon=resources/SYT.png --name=pyQuickStart main.py
```

### 打包配置

- **打包工具**: PyInstaller 6.18.0
- **Python 版本**: 3.14.2
- **打包模式**: 单文件（--onefile）
- **窗口模式**: 无控制台（--windowed）
- **文件大小**: 约 37.4 MB
- **包含资源**: resources\SYT.png

### 分发说明

**最小分发包**：
- `dist\pyQuickStart.exe`

**完整分发包**：
- `dist\pyQuickStart.exe`
- `resources\SYT.png`（如需自定义图标）
- `使用说明.md`（用户文档）
- `快速开始.txt`（快速指南）

**注意事项**：
- ✅ 接收者无需安装 Python 环境
- ⚠️ 首次运行可能被杀毒软件拦截，需添加信任
- ⚠️ 仍需要以管理员权限运行
- ✅ 建议创建快捷方式并设置"以管理员身份运行"

## 🔧 开发相关

### 代码结构

- `main.py` - 程序入口，自动请求管理员权限
- `gui_qt.py` - PyQt5 界面，包含所有 UI 组件和交互逻辑
- `hotkey_manager.py` - 快捷键管理，使用 keyboard 库监听全局快捷键
- `power_manager.py` - 电源管理，使用 ctypes 调用 Windows API 防止休眠
- `config_manager.py` - 配置管理，JSON 格式存储
- `logger.py` - 日志记录，按日期分文件

### 技术栈

- **GUI**: PyQt5 5.15.11
- **快捷键**: keyboard 0.13.5
- **进程管理**: psutil 7.2.1
- **键盘模拟**: pynput 1.8.1（防休眠功能）
- **电源管理**: ctypes (Windows API)
- **打包工具**: PyInstaller 6.18.0
- **测试**: pytest 7.4.0+

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 更新日志

### v1.1.0 (2026-01-22)
- 🌟 **新增智能防休眠功能**
  - 三重防护机制（API + 定时刷新 + 键盘模拟）
  - 无感键盘模拟（每 60 秒模拟 F15 键）
  - 完全不干扰用户操作
- 📦 **新增打包功能**
  - 提供独立 exe 文件（37.4 MB）
  - 无需安装 Python 环境
  - 单文件模式，双击即用
- 🛠️ **新增辅助脚本**
  - 启动程序.bat（快速启动）
  - 打包程序.bat（自动打包）
  - 测试程序.bat（功能测试）
  - 清理无用文件.bat（清理缓存）
- 📚 **完善文档**
  - 使用说明.md（详细文档）
  - 快速开始.txt（快速指南）
  - 打包完成报告.md（打包说明）
  - 清理报告.txt（清理记录）
- 🔧 **优化依赖管理**
  - 添加 pynput 依赖（键盘模拟）
  - 分离生产和开发依赖
  - 更新所有依赖到最新版本

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
