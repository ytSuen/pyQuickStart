@echo off
chcp 65001 >nul
echo ========================================
echo 强制关闭程序并重新打包
echo ========================================
echo.

echo [1/5] 强制关闭所有 pyQuickStart 进程...
tasklist | find /i "pyQuickStart.exe" >nul
if %errorlevel%==0 (
    echo 发现运行中的进程，正在关闭...
    taskkill /F /IM pyQuickStart.exe /T 2>nul
    timeout /t 2 /nobreak >nul
) else (
    echo 没有运行中的进程
)
echo.

echo [2/5] 删除旧的 dist 文件...
if exist "dist\pyQuickStart.exe" (
    del /f /q "dist\pyQuickStart.exe" 2>nul
    if exist "dist\pyQuickStart.exe" (
        echo [警告] 无法删除旧文件，可能被占用
        echo 请手动删除 dist\pyQuickStart.exe 后重试
        pause
        exit /b 1
    )
    echo ✓ 旧文件已删除
) else (
    echo 没有旧文件需要删除
)
echo.

echo [3/5] 激活虚拟环境...
if not exist ".venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
echo.

echo [4/5] 清理构建缓存...
if exist "build" rmdir /s /q build 2>nul
echo ✓ 缓存已清理
echo.

echo [5/5] 开始打包...
pyinstaller pyQuickStart.spec --clean
if errorlevel 1 (
    echo.
    echo [错误] 打包失败
    echo 请检查上面的错误信息
    pause
    exit /b 1
)
echo.

echo ========================================
echo 打包完成！
echo ========================================
echo.

if exist "dist\pyQuickStart.exe" (
    echo ✓ 文件位置: dist\pyQuickStart.exe
    for %%A in ("dist\pyQuickStart.exe") do (
        set /a sizeMB=%%~zA/1024/1024
    )
    echo ✓ 文件大小: %sizeMB% MB
    echo.
    echo 可以运行测试:
    echo   dist\pyQuickStart.exe
) else (
    echo [错误] 未找到生成的 exe 文件
)
echo.
pause
