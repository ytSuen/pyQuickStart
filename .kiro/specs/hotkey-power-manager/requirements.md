# 需求文档 - 快捷键启动与防休眠工具

## 简介

本系统是一个Windows桌面应用程序，允许用户通过自定义全局快捷键快速启动指定的可执行程序，并在程序运行期间自动防止系统进入休眠状态。该工具特别适用于企业环境中需要绕过自动休眠策略的场景。

## 术语表

- **System**: 快捷键启动与防休眠工具系统
- **Hotkey_Manager**: 快捷键管理器，负责全局快捷键监听和程序启动
- **Power_Manager**: 电源管理器，负责控制系统休眠状态
- **Config_Manager**: 配置管理器，负责持久化存储快捷键配置
- **GUI**: 图形用户界面
- **Global_Hotkey**: 全局快捷键，可在任何应用程序中触发
- **Target_Program**: 通过快捷键启动的目标可执行程序
- **Sleep_Prevention**: 防休眠机制，阻止系统进入睡眠或休眠状态

## 需求

### 需求 1: 全局快捷键注册与监听

**用户故事:** 作为用户，我希望能够注册全局快捷键，以便在任何应用程序中都能快速启动我常用的程序。

#### 验收标准

1. WHEN 用户添加一个快捷键配置 THEN THE System SHALL 验证快捷键格式是否符合规范（支持ctrl、alt、shift、win修饰键）
2. WHEN 用户注册的快捷键与现有快捷键冲突 THEN THE System SHALL 提示用户并允许覆盖或取消
3. WHEN 快捷键监听启动 THEN THE Hotkey_Manager SHALL 注册所有配置的全局快捷键到操作系统
4. WHEN 用户按下已注册的快捷键 THEN THE System SHALL 在任何应用程序中都能捕获该事件
5. THE System SHALL 支持最多50个快捷键配置

### 需求 2: 程序启动与进程管理

**用户故事:** 作为用户，我希望通过快捷键启动程序时能够避免重复启动，以便保持系统整洁。

#### 验收标准

1. WHEN 用户触发快捷键 THEN THE Hotkey_Manager SHALL 启动对应的目标程序
2. WHEN 目标程序已经在运行 THEN THE System SHALL 检测到并避免重复启动
3. WHEN 启动程序 THEN THE System SHALL 记录进程ID和启动时间到日志
4. WHEN 程序路径不存在或无效 THEN THE System SHALL 记录错误并提示用户
5. THE System SHALL 仅支持.exe格式的可执行文件

### 需求 3: 防休眠机制

**用户故事:** 作为企业用户，我希望在程序运行期间系统不会自动休眠，以便保持工作连续性。

#### 验收标准

1. WHEN 至少有一个通过快捷键启动的程序正在运行 THEN THE Power_Manager SHALL 调用Windows API防止系统休眠
2. WHEN 所有通过快捷键启动的程序都已关闭 THEN THE Power_Manager SHALL 恢复系统默认休眠行为
3. WHEN 防休眠状态改变 THEN THE System SHALL 记录状态变化到日志
4. WHEN System异常退出 THEN THE System SHALL 在析构函数中恢复系统休眠功能
5. THE System SHALL 每5秒检查一次运行中的进程状态

### 需求 4: 配置持久化

**用户故事:** 作为用户，我希望我的快捷键配置能够保存，以便下次启动程序时自动加载。

#### 验收标准

1. WHEN 用户添加或删除快捷键 THEN THE Config_Manager SHALL 立即保存配置到JSON文件
2. WHEN System启动 THEN THE Config_Manager SHALL 自动加载config.json中的所有快捷键配置
3. WHEN 配置文件不存在 THEN THE System SHALL 创建默认的空配置文件
4. WHEN 配置文件损坏或格式错误 THEN THE System SHALL 记录错误并创建新的空配置
5. THE System SHALL 使用UTF-8编码保存配置文件以支持中文路径

### 需求 5: 图形用户界面

**用户故事:** 作为用户，我希望有一个直观的图形界面来管理快捷键配置，以便轻松添加、删除和查看配置。

#### 验收标准

1. WHEN GUI启动 THEN THE System SHALL 显示所有已配置的快捷键列表
2. WHEN 用户点击"添加"按钮 THEN THE GUI SHALL 验证输入并添加新的快捷键配置
3. WHEN 用户点击"浏览"按钮 THEN THE GUI SHALL 打开文件选择对话框仅显示.exe文件
4. WHEN 用户选中快捷键并点击"删除" THEN THE GUI SHALL 移除该配置并更新显示
5. WHEN 用户点击"启动监听" THEN THE GUI SHALL 启动快捷键监听并更新状态显示
6. WHEN 用户点击"停止监听" THEN THE GUI SHALL 停止快捷键监听并恢复系统休眠
7. THE GUI SHALL 实时显示当前运行中的程序数量
8. THE GUI SHALL 实时显示监听状态（运行中/已停止）

### 需求 6: 日志记录

**用户故事:** 作为用户，我希望系统能够记录所有重要操作，以便在出现问题时进行排查。

#### 验收标准

1. WHEN 系统执行任何重要操作 THEN THE System SHALL 记录操作详情到日志文件
2. WHEN 发生错误 THEN THE System SHALL 记录错误信息和堆栈跟踪
3. THE System SHALL 按日期创建日志文件（格式: hotkey_YYYYMMDD.log）
4. THE System SHALL 将日志同时输出到文件和控制台
5. THE System SHALL 记录以下事件：快捷键注册、程序启动、防休眠状态变化、错误信息

### 需求 7: 安全性与资源管理

**用户故事:** 作为用户，我希望程序在退出时能够正确清理资源，以便不影响系统正常运行。

#### 验收标准

1. WHEN 用户关闭GUI窗口 THEN THE System SHALL 停止所有快捷键监听
2. WHEN System退出 THEN THE Power_Manager SHALL 恢复系统休眠功能
3. WHEN System退出 THEN THE System SHALL 释放所有注册的全局快捷键
4. THE System SHALL 不修改系统注册表或其他敏感设置
5. THE System SHALL 使用单例模式确保Logger只有一个实例

### 需求 8: 错误处理与用户反馈

**用户故事:** 作为用户，我希望在操作失败时能够收到清晰的错误提示，以便了解问题所在。

#### 验收标准

1. WHEN 添加快捷键失败 THEN THE GUI SHALL 显示错误对话框说明失败原因
2. WHEN 程序路径无效 THEN THE System SHALL 提示用户并拒绝添加
3. WHEN 快捷键格式错误 THEN THE System SHALL 提示用户正确的格式示例
4. WHEN 启动程序失败 THEN THE System SHALL 记录错误并继续运行
5. WHEN 操作成功 THEN THE GUI SHALL 显示成功提示信息

### 需求 9: 进程监控

**用户故事:** 作为系统，我需要持续监控已启动的程序状态，以便准确控制防休眠机制。

#### 验收标准

1. WHEN 程序通过快捷键启动 THEN THE Hotkey_Manager SHALL 将进程添加到监控列表
2. WHEN 监控线程运行 THEN THE System SHALL 每5秒检查一次进程列表
3. WHEN 进程已结束 THEN THE System SHALL 从监控列表中移除该进程
4. WHEN 查询运行中程序数量 THEN THE System SHALL 返回当前活跃进程的准确数量
5. THE System SHALL 使用psutil库进行跨平台进程管理

### 需求 10: 快捷键格式规范

**用户故事:** 作为用户，我希望了解支持的快捷键格式，以便正确配置快捷键。

#### 验收标准

1. THE System SHALL 支持以下修饰键：ctrl、alt、shift、win
2. THE System SHALL 支持修饰键与字母、数字、功能键的组合
3. THE System SHALL 使用加号(+)连接多个按键（例：ctrl+alt+n）
4. THE System SHALL 不区分快捷键中的大小写
5. THE System SHALL 拒绝不包含修饰键的单键快捷键（避免干扰正常输入）
