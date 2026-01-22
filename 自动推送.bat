@echo off
chcp 65001 >nul
echo ========================================
echo   自动推送到 Gitee
echo ========================================
echo.

cd /d "%~dp0"

echo 1. 设置 Git 编辑器为记事本...
git config core.editor notepad

echo 2. 拉取并自动合并...
git pull origin main --no-rebase --no-edit

if errorlevel 1 (
    echo.
    echo 合并失败，尝试重置并强制推送...
    echo.
    choice /c YN /m "是否强制推送（会覆盖远程更改）"
    
    if errorlevel 2 goto end
    if errorlevel 1 (
        git push origin main --force
        goto success
    )
)

echo.
echo 3. 推送到 Gitee...
git push origin main

if errorlevel 1 (
    echo.
    echo 推送失败！尝试强制推送...
    choice /c YN /m "是否强制推送"
    
    if errorlevel 2 goto end
    if errorlevel 1 (
        git push origin main --force
    )
)

:success
echo.
echo ========================================
echo   推送成功！
echo ========================================
echo.
echo 查看仓库：https://gitee.com/sytao_2020/pyQuickStart
echo.

:end
pause
