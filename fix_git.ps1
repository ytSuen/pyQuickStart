# 强制结束所有 Git 进程
Get-Process | Where-Object {$_.ProcessName -like "*git*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# 删除 Git 锁文件
Remove-Item ".git/index.lock" -Force -ErrorAction SilentlyContinue
Remove-Item ".git/HEAD.lock" -Force -ErrorAction SilentlyContinue
Remove-Item ".git/refs/heads/*.lock" -Force -ErrorAction SilentlyContinue

# 重置 rebase 状态
if (Test-Path ".git/rebase-merge") {
    Remove-Item ".git/rebase-merge" -Recurse -Force -ErrorAction SilentlyContinue
}
if (Test-Path ".git/rebase-apply") {
    Remove-Item ".git/rebase-apply" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Git 状态已清理"
Write-Host ""
Write-Host "现在可以重新执行 Git 命令"
