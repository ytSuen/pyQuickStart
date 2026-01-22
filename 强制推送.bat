@echo off
chcp 65001 >nul
echo ========================================
echo   强制推送到 Gitee
echo ========================================
echo.
echo 警告：这将覆盖远程仓库的内容！
echo.
pause

cd /d "%~dp0"

echo.
echo 1. 结束所有 Git 进程...
taskkill /F /IM git.exe >nul 2>&1
taskkill /F /IM vim.exe >nul 2>&1
taskkill /F /IM nvim.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo 2. 清理 Git 状态...
del /f /q ".git\index.lock" >nul 2>&1
git merge --abort >nul 2>&1
git rebase --abort >nul 2>&1

echo 3. 查看当前状态...
git status

echo.
echo 4. 强制推送到 Gitee...
git push origin main --force

if errorlevel 1 (
    echo.
    echo ========================================
    echo   推送失败！
    echo ========================================
    echo.
    echo 请检查网络连接和 Gitee 权限
) else (
    echo.
    echo ========================================
    echo   推送成功！
    echo ========================================
    echo.
    echo 查看仓库：https://gitee.com/sytao_2020/pyQuickStart
)

echo.
pause
