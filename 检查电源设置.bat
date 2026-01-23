@echo off
chcp 65001 >nul
echo ========================================
echo 检查 Windows 电源设置
echo ========================================
echo.

echo [1] 当前电源计划：
powercfg /getactivescheme
echo.

echo [2] 显示器关闭时间：
powercfg /query SCHEME_CURRENT SUB_VIDEO VIDEOIDLE
echo.

echo [3] 系统休眠时间：
powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE
echo.

echo [4] 硬盘休眠时间：
powercfg /query SCHEME_CURRENT SUB_DISK DISKIDLE
echo.

echo [5] 锁屏时间（需要管理员权限）：
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v InactivityTimeoutSecs 2>nul
if errorlevel 1 (
    echo 未设置或需要管理员权限
)
echo.

echo ========================================
echo 建议设置（防止休眠）
echo ========================================
echo.
echo 如果要完全防止休眠，建议：
echo 1. 显示器关闭时间：设置为"从不"或较长时间
echo 2. 系统休眠时间：设置为"从不"或较长时间
echo 3. 使用命令：powercfg /change standby-timeout-ac 0
echo    （0 表示从不休眠，仅在接通电源时）
echo.
echo 当前程序使用的防休眠方法：
echo - SetThreadExecutionState API
echo - PowerSetRequest API
echo - 定时刷新（每30秒）
echo - 模拟鼠标/键盘事件（每30秒）
echo.

pause
