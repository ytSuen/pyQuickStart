@echo off
chcp 65001 >nul
echo 正在清理 Git 状态...

REM 强制关闭所有编辑器
taskkill /F /IM vim.exe 2>nul
taskkill /F /IM gvim.exe 2>nul
taskkill /F /IM nvim.exe 2>nul
taskkill /F /IM notepad.exe 2>nul

timeout /t 2 /nobreak >nul

REM 删除交换文件
if exist ".git\.MERGE_MSG.swp" del /F /Q ".git\.MERGE_MSG.swp"
if exist ".git\index.lock" del /F /Q ".git\index.lock"

REM 中止合并
git merge --abort 2>nul

REM 配置编辑器为 notepad
git config core.editor "notepad"

echo 清理完成！
echo.
git status
pause
