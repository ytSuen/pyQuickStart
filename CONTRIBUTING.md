# 贡献指南

感谢你对本项目的关注！欢迎提交 Issue 和 Pull Request。

## 开发环境设置

1. **克隆仓库**
```bash
git clone https://gitee.com/sytao_2020/pyQuickStart.git
cd pyQuickStart
```

2. **安装依赖**
```bash
# 生产环境依赖
pip install -r requirements.txt

# 开发环境依赖（包含代码质量工具）
pip install -r requirements-dev.txt
```

3. **运行测试**
```bash
pytest
```

## 代码规范

- 使用 Black 格式化代码：`black .`
- 使用 Flake8 检查代码：`flake8 .`
- 遵循 PEP 8 编码规范
- 为新功能添加单元测试
- 更新相关文档

## 提交 Pull Request

1. Fork 本仓库
2. 创建你的特性分支：`git checkout -b feature/AmazingFeature`
3. 提交你的更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 打开一个 Pull Request

## 报告 Bug

请在 Issue 中提供以下信息：
- 操作系统版本
- Python 版本
- 详细的错误信息和日志
- 复现步骤

## 功能建议

欢迎在 Issue 中提出新功能建议，请说明：
- 功能描述
- 使用场景
- 预期效果
