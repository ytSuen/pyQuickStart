@echo off
chcp 65001 >nul
echo ========================================
echo pyQuickStart 版本发布助手
echo ========================================
echo.

REM 检查虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先创建虚拟环境
    pause
    exit /b 1
)

REM 读取当前版本
echo [1/6] 读取当前版本...
for /f "tokens=2 delims=:, " %%a in ('findstr /C:"\"version\"" version.json') do (
    set CURRENT_VERSION=%%~a
)
echo 当前版本: %CURRENT_VERSION%
echo.

REM 询问新版本号
set /p NEW_VERSION="请输入新版本号 (例如: 1.1.0): "
if "%NEW_VERSION%"=="" (
    echo [错误] 版本号不能为空
    pause
    exit /b 1
)
echo.

REM 询问更新说明
set /p CHANGELOG="请输入更新说明 (简短描述): "
if "%CHANGELOG%"=="" (
    set CHANGELOG=版本更新
)
echo.

REM 获取当前日期
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (
    set BUILD_DATE=%%a-%%b-%%c
)

echo [2/6] 更新 version.json...
(
echo {
echo   "version": "%NEW_VERSION%",
echo   "build_date": "%BUILD_DATE%",
echo   "description": "%CHANGELOG%",
echo   "changelog": "%CHANGELOG%",
echo   "download_url": "https://gitee.com/sytao_2020/pyQuickStart/releases/download/v%NEW_VERSION%/pyQuickStart.exe"
echo }
) > version.json
echo ✓ version.json 已更新
echo.

echo [3/6] 激活虚拟环境...
call .venv\Scripts\activate.bat
echo.

echo [4/6] 安装依赖...
pip install -r requirements-prod.txt -q
echo ✓ 依赖已安装
echo.

echo [5/6] 打包程序...
pyinstaller pyQuickStart.spec --clean
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)
echo ✓ 打包完成
echo.

echo [6/6] 检查打包结果...
if exist "dist\pyQuickStart.exe" (
    echo ✓ pyQuickStart.exe 已生成
    for %%A in ("dist\pyQuickStart.exe") do echo   文件大小: %%~zA 字节
) else (
    echo [错误] 未找到 pyQuickStart.exe
    pause
    exit /b 1
)
echo.

echo ========================================
echo 发布准备完成！
echo ========================================
echo.
echo 版本号: v%NEW_VERSION%
echo 更新说明: %CHANGELOG%
echo 构建日期: %BUILD_DATE%
echo.
echo 接下来的步骤：
echo 1. 测试 dist\pyQuickStart.exe 是否正常工作
echo 2. 在 Gitee 创建 Release (标签: v%NEW_VERSION%)
echo 3. 上传 dist\pyQuickStart.exe 到 Release
echo 4. 提交代码: git add . ^&^& git commit -m "release: v%NEW_VERSION%" ^&^& git push
echo.
echo 详细步骤请参考: 自动更新使用指南.md
echo.
pause
