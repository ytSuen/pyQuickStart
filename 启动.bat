@echo off
chcp 65001 >nul
echo ========================================
echo   快捷键启动工具
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [√] 已获得管理员权限
    echo.
    echo 正在启动程序...
    python main.py
) else (
    echo [×] 需要管理员权限！
    echo.
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
)
