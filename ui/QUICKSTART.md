# 快速开始 - 5 分钟体验新 UI

## 🚀 立即预览 (无需安装)

### 步骤 1: 打开交互演示

**Windows**:
```cmd
start ui\index-interactive.html
```

**或者直接双击**: `ui/index-interactive.html`

### 步骤 2: 体验功能

在浏览器中尝试：

1. ✅ **添加快捷键**
   - 输入: `ctrl+alt+n`
   - 点击"浏览"按钮 (会自动填充示例路径)
   - 点击"添加快捷键"

2. ✅ **查看统计**
   - 观察"配置快捷键"数字变化
   - 查看卡片悬停效果

3. ✅ **启动监听**
   - 点击右上角"启动监听"按钮
   - 观察状态指示器变为绿色

4. ✅ **批量操作**
   - 勾选多个快捷键
   - 点击"删除选中"

5. ✅ **主题切换**
   - 打开 `ui/index-dark.html` 查看深色模式

## 📦 集成到现有项目 (10 分钟)

### 方案 A: 使用 pywebview (推荐)

#### 1. 安装依赖

```bash
pip install pywebview
```

#### 2. 创建 web_gui.py

复制以下代码到项目根目录的 `web_gui.py`:

```python
import webview
import os
from hotkey_manager import HotkeyManager
from config_manager import ConfigManager

class WebAPI:
    def __init__(self):
        self.hotkey_manager = HotkeyManager()
        self.config_manager = ConfigManager()
    
    def get_hotkeys(self):
        hotkeys = self.config_manager.get_hotkeys()
        return [{'hotkey': k, 'path': v} for k, v in hotkeys.items()]
    
    def add_hotkey(self, hotkey, path):
        if self.hotkey_manager.add_hotkey(hotkey, path):
            self.config_manager.add_hotkey(hotkey, path)
            return {'success': True}
        return {'success': False}

class WebGUI:
    def __init__(self):
        self.api = WebAPI()
    
    def run(self):
        html_path = os.path.join(os.path.dirname(__file__), 'ui', 'index-interactive.html')
        webview.create_window('快捷键启动工具', html_path, js_api=self.api, width=1200, height=800)
        webview.start(debug=True)

if __name__ == '__main__':
    app = WebGUI()
    app.run()
```

#### 3. 运行

```bash
python web_gui.py
```

### 方案 B: 保持 Tkinter，仅参考设计

如果暂时不想更换技术栈，可以：

1. 参考新 UI 的配色方案
2. 借鉴布局结构
3. 改进 Tkinter 界面的视觉设计

## 🎨 自定义设计

### 修改配色

在 HTML 文件中搜索并替换：

```html
<!-- 主色调: 蓝色 → 紫色 -->
bg-blue-600  →  bg-purple-600
text-blue-600  →  text-purple-600

<!-- 成功色: 绿色 → 青色 -->
bg-green-600  →  bg-cyan-600
text-green-600  →  text-cyan-600
```

### 修改 Logo

替换 `resources/SYT.png` 为你的 Logo 图片。

### 修改字体

在 `<head>` 中更改 Google Fonts 链接：

```html
<!-- 当前: Noto Sans SC -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<!-- 改为: Roboto -->
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
```

然后在 `<style>` 中修改：

```css
* {
    font-family: 'Roboto', sans-serif;
}
```

## 📚 文件说明

```
ui/
├── index.html              # 静态浅色模式
├── index-dark.html         # 静态深色模式
├── index-interactive.html  # 交互演示版 (推荐)
├── README.md              # 设计文档
├── PREVIEW.md             # 预览指南
├── IMPROVEMENTS.md        # 改进对比
├── INTEGRATION.md         # 集成指南 (详细)
└── QUICKSTART.md          # 本文件
```

## 🔧 常见问题

### Q1: 浏览器中看不到 Logo？

**原因**: 相对路径问题

**解决**:
```html
<!-- 修改前 -->
<img src="../resources/SYT.png">

<!-- 修改后 (使用绝对路径) -->
<img src="file:///完整路径/resources/SYT.png">
```

### Q2: pywebview 安装失败？

**Windows**:
```bash
# 确保安装了 Edge WebView2
# 通常 Windows 10/11 已预装
```

**Linux**:
```bash
sudo apt install python3-gi gir1.2-webkit2-4.0
```

**macOS**:
```bash
# 无需额外依赖，使用系统 WebKit
```

### Q3: 想要更多功能？

查看 `INTEGRATION.md` 了解：
- 文件选择对话框
- 系统托盘图标
- 自动更新
- 打包发布

## 🎯 下一步

### 初学者
1. ✅ 在浏览器中预览 `index-interactive.html`
2. ✅ 尝试修改颜色和文本
3. ✅ 阅读 `PREVIEW.md` 了解设计细节

### 开发者
1. ✅ 安装 pywebview
2. ✅ 创建 `web_gui.py`
3. ✅ 阅读 `INTEGRATION.md` 完整集成
4. ✅ 参考 `IMPROVEMENTS.md` 了解优势

### 设计师
1. ✅ 查看 `README.md` 了解设计系统
2. ✅ 修改配色和字体
3. ✅ 调整布局和间距
4. ✅ 添加自定义图标

## 📞 获取帮助

### 设计相关
- 查看 `README.md` - 完整设计文档
- 查看 `PREVIEW.md` - 界面预览指南
- 查看 `IMPROVEMENTS.md` - 改进对比

### 技术集成
- 查看 `INTEGRATION.md` - 详细集成指南
- 查看 pywebview 文档: https://pywebview.flowrl.com/
- 查看 Tailwind CSS 文档: https://tailwindcss.com/

### 在线资源
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Heroicons**: https://heroicons.com/
- **Google Fonts**: https://fonts.google.com/
- **Color Palette**: https://tailwindcss.com/docs/customizing-colors

## ✨ 设计亮点

### 1. 专业配色
- 基于生产力工具最佳实践
- 高对比度，易于阅读
- 支持浅色/深色双主题

### 2. 现代布局
- 卡片式设计
- 清晰的视觉层次
- 响应式网格系统

### 3. 流畅交互
- 200ms 过渡动画
- 悬停反馈
- 状态指示动画

### 4. 无障碍设计
- WCAG AA+ 对比度
- 键盘导航支持
- 动画偏好设置

### 5. 中文优化
- Noto Sans SC 字体
- 适合中文的行高和字距
- 清晰的中文显示

## 🎉 开始使用

**最快体验**:
```bash
start ui\index-interactive.html
```

**完整集成**:
```bash
pip install pywebview
python web_gui.py
```

**自定义设计**:
编辑 `ui/index-interactive.html`，修改 Tailwind 类名即可！

---

**设计完成**: 2026-01-21  
**预计学习时间**: 5-30 分钟  
**难度**: ⭐⭐ (简单到中等)

祝你使用愉快！🚀
