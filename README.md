# 快捷键启动工具

一个 Windows 桌面工具，支持自定义全局快捷键快速启动程序、打开网页、访问文件夹，并在程序运行期间自动防止系统休眠。

## ✨ 功能特性

- 🎯 全局快捷键监听（支持 Ctrl+Alt+Shift+Win 组合键）
- 🚀 支持多种目标类型：程序、网页、文件夹、文件
- 💤 智能防休眠（仅在程序运行时）
- 🔄 进程监控（避免重复启动）
- 🎨 双界面支持：Web UI（现代化）/ Tkinter UI（传统）
- 💾 配置自动保存
- 📝 完整日志记录

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

**可选依赖** (Web UI):
```bash
pip install pywebview
```

### 2. 启动程序

```bash
# 推荐：使用启动脚本选择界面
python start.py

# 或直接启动 Web UI
python web_gui.py

# 或使用传统 Tkinter UI
python main.py
```

### 3. 添加快捷键

1. 输入快捷键组合（如：`ctrl+alt+n`）
2. 输入目标路径或点击浏览按钮
3. 点击"添加"保存

### 4. 启动监听

点击"启动监听"按钮，然后使用快捷键测试！

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

1. ✅ 需要以管理员权限运行
2. ✅ 避免使用系统保留快捷键（如 Ctrl+Alt+Del）
3. ✅ 配置文件：`config.json`
4. ✅ 日志文件：`logs/hotkey_YYYYMMDD.log`
5. ✅ Web UI 需要：`pip install pywebview`

## 📁 项目结构

```
├── start.py              # 启动脚本
├── main.py               # Tkinter UI 入口
├── web_gui.py            # Web UI 入口
├── gui.py                # Tkinter 界面
├── hotkey_manager.py     # 快捷键管理
├── power_manager.py      # 电源管理
├── config_manager.py     # 配置管理
├── logger.py             # 日志记录
├── requirements.txt      # 依赖列表
├── ui/                   # Web UI 文件
│   ├── index-interactive.html
│   └── QUICKSTART.md
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
| 快捷键不响应 | 以管理员身份运行 |
| Web UI 无法启动 | `pip install pywebview` |
| 目标无法打开 | 检查路径是否正确 |
| 配置文件损坏 | 删除 `config.json` 重新生成 |

## 📦 打包发布

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="快捷键工具" start.py
```

## 📄 许可证

MIT License
