@echo off
chcp 65001 >nul
echo ========================================
echo   修复 Git 并推送到 Gitee
echo ========================================
echo.

cd /d "%~dp0"

echo 1. 强制结束所有 Git 进程...
taskkill /F /IM git.exe >nul 2>&1
taskkill /F /IM git-remote-https.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo 2. 删除 Git 锁文件...
del /f /q ".git\index.lock" >nul 2>&1
del /f /q ".git\HEAD.lock" >nul 2>&1
del /f /q ".git\refs\heads\main.lock" >nul 2>&1
rmdir /s /q ".git\rebase-merge" >nul 2>&1
rmdir /s /q ".git\rebase-apply" >nul 2>&1
echo ✓ 锁文件已删除

echo.
echo 3. 检查 Git 状态...
git status

echo.
echo 4. 暂存所有更改...
git add -A

echo.
echo 5. 查看远程分支状态...
git fetch origin

echo.
echo 6. 拉取并合并远程更改...
git pull origin main --no-rebase --allow-unrelated-histories

if errorlevel 1 (
    echo.
    echo 拉取失败，尝试强制合并...
    git merge origin/main --allow-unrelated-histories -m "Merge remote changes"
)

echo.
echo 7. 推送到 Gitee...
git push origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo   推送失败！
    echo ========================================
    echo.
    echo 可能的原因：
    echo 1. 网络问题
    echo 2. 需要强制推送
    echo.
    echo 是否尝试强制推送？（会覆盖远程仓库）
    choice /c YN /m "强制推送"
    
    if errorlevel 2 goto end
    if errorlevel 1 (
        echo.
        echo 执行强制推送...
        git push origin main --force
        
        if errorlevel 1 (
            echo.
            echo 强制推送也失败了！
            echo 请检查：
            echo 1. 网络连接
            echo 2. Gitee 账号权限
            echo 3. 仓库地址是否正确
            goto end
        )
    )
)

echo.
echo ========================================
echo   推送成功！
echo ========================================
echo.
echo 查看仓库：https://gitee.com/sytao_2020/pyQuickStart
echo.

:end
pause
