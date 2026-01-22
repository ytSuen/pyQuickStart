@echo off
chcp 65001 >nul
echo ========================================
echo   推送到 Gitee
echo ========================================
echo.

cd /d "%~dp0"

echo 1. 关闭可能占用文件的进程...
taskkill /F /IM pyQuickStart.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo 2. 取消之前的 rebase（如果有）...
git rebase --abort >nul 2>&1

echo 3. 重置工作区...
git reset --hard HEAD

echo 4. 拉取远程更改...
git pull origin main --rebase

if errorlevel 1 (
    echo.
    echo 拉取失败，尝试使用 merge 方式...
    git pull origin main --no-rebase
)

echo.
echo 5. 推送到 Gitee...
git push origin main

if errorlevel 1 (
    echo.
    echo 推送失败！
    echo 请检查网络连接或手动推送
    pause
    exit /b 1
)

echo.
echo ========================================
echo   推送成功！
echo ========================================
echo.
echo 查看仓库：https://gitee.com/sytao_2020/pyQuickStart
echo.
pause
