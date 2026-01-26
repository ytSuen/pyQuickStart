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

echo [1/6] 激活虚拟环境...
call .venv\Scripts\activate.bat
echo.

echo [2/6] 安装/更新依赖...
pip install -r requirements-prod.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo ✓ 依赖已安装
echo.

echo [3/6] 检查并转换图标...
if not exist "resources\SYT.ico" (
    echo 正在安装Pillow...
    pip install Pillow -q
    if errorlevel 1 (
        echo [警告] Pillow安装失败，将使用默认图标
    ) else (
        echo 正在转换PNG图标为ICO格式...
        python -c "from PIL import Image; img = Image.open('resources/SYT.png'); img.save('resources/SYT.ico', format='ICO', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]); print('✓ 图标转换成功')"
        if errorlevel 1 (
            echo [警告] 图标转换失败，将使用默认图标
        )
    )
) else (
    echo ✓ 图标文件已存在
)
echo.

echo [4/6] 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo ✓ 清理完成
echo.

echo [5/6] 开始打包...
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
    if exist "resources\SYT.ico" (
        echo ✓ 图标已应用: resources\SYT.ico
    )
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
