@echo off
chcp 65001 >nul
echo ========================================
echo pyQuickStart 打包程序
echo ========================================
echo.

REM 检查虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在
    echo 请先创建虚拟环境: python -m venv .venv
    pause
    exit /b 1
)

echo [1/4] 激活虚拟环境...
call .venv\Scripts\activate.bat
echo.

echo [2/4] 安装/更新依赖...
pip install -r requirements-prod.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo ✓ 依赖已安装
echo.

echo [3/4] 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo ✓ 清理完成
echo.

echo [4/4] 开始打包...
pyinstaller pyQuickStart.spec --clean
if errorlevel 1 (
    echo [错误] 打包失败
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
        set size=%%~zA
        set /a sizeMB=%%~zA/1024/1024
    )
    echo ✓ 文件大小: %sizeMB% MB
    echo.
    echo 可以运行以下命令测试:
    echo   dist\pyQuickStart.exe
) else (
    echo [错误] 未找到生成的 exe 文件
    pause
    exit /b 1
)
echo.
pause
