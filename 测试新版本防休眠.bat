@echo off
chcp 65001 >nul
echo ========================================
echo 测试新版本防休眠功能
echo ========================================
echo.

if not exist "dist\pyQuickStart.exe" (
    echo [错误] 未找到 dist\pyQuickStart.exe
    echo 请先运行 打包程序.bat 或 强制关闭并打包.bat
    pause
    exit /b 1
)

echo 新版本改进：
echo ✓ 四重防护机制
echo   1. 鼠标事件触发（mouse_event 0移动）
echo   2. 重置空闲计时器（SetThreadExecutionState）
echo   3. 模拟按键（Shift键）
echo   4. 恢复持续状态
echo.
echo ✓ 刷新间隔：从55秒缩短到30秒
echo.
echo ========================================
echo 测试步骤
echo ========================================
echo.
echo 1. 即将启动新版本程序
echo 2. 请在程序中开启防休眠功能
echo 3. 观察日志文件（logs\hotkey_YYYYMMDD.log）
echo 4. 应该每30秒看到一次"防休眠刷新完成"
echo 5. 等待至少5分钟，观察电脑是否休眠
echo.
echo 按任意键启动程序...
pause >nul

echo.
echo 正在启动 dist\pyQuickStart.exe...
start "" "dist\pyQuickStart.exe"

echo.
echo 程序已启动！
echo.
echo 请执行以下操作：
echo 1. 在程序界面点击"开启防休眠"
echo 2. 最小化程序窗口
echo 3. 等待5-10分钟
echo 4. 观察电脑是否进入休眠/锁屏
echo.
echo 查看日志：
echo   notepad logs\hotkey_%date:~0,4%%date:~5,2%%date:~8,2%.log
echo.
echo 如果仍然休眠，请运行：
echo   检查电源设置.bat
echo.
pause
