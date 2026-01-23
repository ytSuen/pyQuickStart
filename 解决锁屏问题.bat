@echo off
chcp 65001 >nul
echo ========================================
echo 解决 Windows 自动锁屏问题
echo ========================================
echo.
echo 重要说明：
echo 防休眠功能可以阻止电脑休眠，但无法阻止自动锁屏！
echo 锁屏和休眠是两个不同的功能。
echo.
echo ========================================
echo 方案1：关闭自动锁屏（推荐）
echo ========================================
echo.
echo 1. 打开 Windows 设置
echo 2. 账户 ^> 登录选项
echo 3. 找到"需要登录"
echo 4. 设置为"从不"
echo.
echo 或者运行以下命令（需要管理员权限）：
echo.
echo reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v InactivityTimeoutSecs /t REG_DWORD /d 0 /f
echo.
pause
echo.
echo 是否立即执行？(Y/N)
set /p choice=
if /i "%choice%"=="Y" (
    echo.
    echo 正在设置...
    reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v InactivityTimeoutSecs /t REG_DWORD /d 0 /f
    if errorlevel 1 (
        echo [错误] 需要管理员权限
        echo 请右键此文件，选择"以管理员身份运行"
    ) else (
        echo ✓ 设置成功！
    )
)
echo.

echo ========================================
echo 方案2：关闭屏幕保护程序
echo ========================================
echo.
echo 1. 右键桌面 ^> 个性化
echo 2. 锁屏界面 ^> 屏幕保护程序设置
echo 3. 选择"无"
echo 4. 取消勾选"在恢复时显示登录屏幕"
echo.
pause
echo.

echo ========================================
echo 方案3：修改电源计划
echo ========================================
echo.
echo 当前电源设置：
echo.
powercfg /query SCHEME_CURRENT SUB_VIDEO VIDEOIDLE | findstr /C:"当前交流电源设置索引" /C:"当前直流电源设置索引"
echo.
echo 设置显示器从不关闭：
powercfg /change monitor-timeout-ac 0
powercfg /change monitor-timeout-dc 0
echo ✓ 已设置显示器从不关闭
echo.
pause

echo ========================================
echo 方案4：检查组策略（企业环境）
echo ========================================
echo.
echo 如果以上方法无效，可能是组策略限制
echo.
echo 1. Win+R 输入 gpedit.msc
echo 2. 计算机配置 ^> 管理模板 ^> 系统 ^> 电源管理
echo 3. 检查是否有强制锁屏策略
echo.
echo 如果是企业环境，请联系IT管理员
echo.
pause

echo ========================================
echo 总结
echo ========================================
echo.
echo 防休眠功能的作用：
echo ✓ 阻止电脑进入休眠状态（硬盘停转、内存保存）
echo ✓ 阻止显示器自动关闭
echo ✗ 无法阻止自动锁屏（这是安全策略）
echo.
echo 如果你遇到的是"屏幕变黑需要输入密码"：
echo → 这是自动锁屏，不是休眠
echo → 需要使用上述方案关闭自动锁屏
echo.
echo 如果你遇到的是"电脑完全关闭，需要按电源键"：
echo → 这才是休眠，防休眠功能可以阻止
echo.
pause
