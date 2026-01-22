# 快捷键启动工具

一个 Windows 桌面工具，支持自定义全局快捷键快速启动程序、打开网页、访问文件夹，并提供独立的防休眠功能。

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

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="快捷键工具" main.py
```

## 📄 许可证

MIT License
