# Git 提交助手脚本
# 使用方法：.\git_commit.ps1

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Git 提交助手" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# 检查是否在 git 仓库中
if (-not (Test-Path ".git")) {
    Write-Host "错误：当前目录不是 git 仓库" -ForegroundColor Red
    Write-Host "请先执行：git init" -ForegroundColor Yellow
    exit 1
}

# 检查状态
Write-Host "检查 Git 状态..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan

# 确认是否继续
Write-Host "是否继续提交？[Y/n]" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "n" -or $response -eq "N") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

# 添加所有文件（排除 .gitignore 中的）
Write-Host ""
Write-Host "添加文件..." -ForegroundColor Yellow
git add .

# 显示将要提交的内容
Write-Host ""
Write-Host "将要提交的文件：" -ForegroundColor Cyan
git diff --cached --name-status

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan

# 输入 commit 信息
Write-Host "请输入 commit 信息：" -ForegroundColor Yellow
$commitMessage = Read-Host

if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    Write-Host "错误：commit 信息不能为空" -ForegroundColor Red
    exit 1
}

# 提交
Write-Host ""
Write-Host "提交中..." -ForegroundColor Yellow
git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 提交成功" -ForegroundColor Green
} else {
    Write-Host "✗ 提交失败" -ForegroundColor Red
    exit 1
}

# 询问是否推送
Write-Host ""
Write-Host "是否推送到远程仓库？[Y/n]" -ForegroundColor Yellow
$response = Read-Host

if ($response -ne "n" -and $response -ne "N") {
    # 检查远程仓库
    $remotes = git remote
    if ([string]::IsNullOrWhiteSpace($remotes)) {
        Write-Host ""
        Write-Host "未配置远程仓库" -ForegroundColor Yellow
        Write-Host "请输入远程仓库 URL（例如：https://github.com/username/ZF_Class_Schedule.git）：" -ForegroundColor Cyan
        $remoteUrl = Read-Host

        if (-not [string]::IsNullOrWhiteSpace($remoteUrl)) {
            git remote add origin $remoteUrl
            Write-Host "✓ 已添加远程仓库" -ForegroundColor Green
        } else {
            Write-Host "跳过推送" -ForegroundColor Yellow
            exit 0
        }
    }

    Write-Host ""
    Write-Host "推送中..." -ForegroundColor Yellow

    # 获取当前分支
    $currentBranch = git branch --show-current

    git push -u origin $currentBranch

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 推送成功" -ForegroundColor Green
    } else {
        Write-Host "✗ 推送失败" -ForegroundColor Red
        Write-Host "如果是首次推送，可能需要设置上游分支" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "完成！" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
