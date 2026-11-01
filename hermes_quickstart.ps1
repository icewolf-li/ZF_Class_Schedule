# Hermes Agent 插件快速启动脚本
# 使用方法：.\hermes_quickstart.ps1

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "正方教务课表 - Hermes Agent 插件快速启动" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# 检查 Python 和 uv
Write-Host "检查环境..." -ForegroundColor Yellow
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
$uvPath = Get-Command uv -ErrorAction SilentlyContinue

if (-not $pythonPath) {
    Write-Host "✗ 未找到 Python" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python 已安装" -ForegroundColor Green

if (-not $uvPath) {
    Write-Host "✗ 未找到 uv" -ForegroundColor Red
    Write-Host "请先安装 uv：https://github.com/astral-sh/uv" -ForegroundColor Red
    exit 1
}
Write-Host "✓ uv 已安装" -ForegroundColor Green

# 检查 playwright
Write-Host ""
Write-Host "检查依赖..." -ForegroundColor Yellow
try {
    python -c "import playwright" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ playwright 已安装" -ForegroundColor Green
    } else {
        Write-Host "安装 playwright..." -ForegroundColor Yellow
        uv add playwright
        uv run playwright install chromium
        Write-Host "✓ playwright 已安装" -ForegroundColor Green
    }
} catch {
    Write-Host "安装 playwright..." -ForegroundColor Yellow
    uv add playwright
    uv run playwright install chromium
    Write-Host "✓ playwright 已安装" -ForegroundColor Green
}

# 检查配置
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "配置插件" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

if (Test-Path "hermes_config.json") {
    Write-Host "检测到已有配置文件" -ForegroundColor Green
    $config = Get-Content "hermes_config.json" -Encoding UTF8 | ConvertFrom-Json

    Write-Host "当前配置：" -ForegroundColor Yellow
    Write-Host "  学号：$($config.username)" -ForegroundColor White
    Write-Host "  URL：$($config.base_url)" -ForegroundColor White
    Write-Host "  学年：$($config.year)" -ForegroundColor White
    Write-Host "  学期：$($config.term)" -ForegroundColor White
    Write-Host ""

    Write-Host "是否重新配置？[y/N]" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -ne "y" -and $response -ne "Y") {
        $skipConfig = $true
    }
}

if (-not $skipConfig) {
    Write-Host ""
    Write-Host "请输入您的教务系统信息：" -ForegroundColor Cyan
    Write-Host ""

    $username = Read-Host "学号"
    $password = Read-Host "密码" -AsSecureString
    $passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
    )

    $baseUrl = Read-Host "教务系统 URL（直接回车使用默认：https://jwxt.gxnzd.com.cn/）"
    if ([string]::IsNullOrWhiteSpace($baseUrl)) {
        $baseUrl = "https://jwxt.gxnzd.com.cn/"
    }

    $year = Read-Host "学年（直接回车使用默认：2026）"
    if ([string]::IsNullOrWhiteSpace($year)) {
        $year = "2026"
    }

    $term = Read-Host "学期（3=第一学期，12=第二学期，直接回车使用默认：3）"
    if ([string]::IsNullOrWhiteSpace($term)) {
        $term = "3"
    }

    $startDate = Read-Host "学期开始日期（YYYY-MM-DD，直接回车使用默认：2026-09-01）"
    if ([string]::IsNullOrWhiteSpace($startDate)) {
        $startDate = "2026-09-01"
    }

    Write-Host ""
    Write-Host "正在配置插件..." -ForegroundColor Yellow

    uv run python hermes_plugin.py setup `
        --username $username `
        --password $passwordPlain `
        --base-url $baseUrl `
        --year $year `
        --term $term `
        --start-date $startDate

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 配置成功" -ForegroundColor Green
    } else {
        Write-Host "✗ 配置失败" -ForegroundColor Red
        exit 1
    }
}

# 测试查询
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "测试查询" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

Write-Host "是否立即查询课表？[Y/n]" -ForegroundColor Yellow
$response = Read-Host
if ($response -ne "n" -and $response -ne "N") {
    Write-Host ""
    Write-Host "正在查询课表..." -ForegroundColor Yellow
    Write-Host ""

    uv run python hermes_plugin.py get --format table

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ 查询成功！" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "✗ 查询失败" -ForegroundColor Red
        Write-Host "您可以尝试：" -ForegroundColor Yellow
        Write-Host "  1. 强制重新登录：uv run python hermes_plugin.py get --force-login" -ForegroundColor White
        Write-Host "  2. 检查账号密码是否正确" -ForegroundColor White
        Write-Host "  3. 检查网络连接" -ForegroundColor White
    }
}

# 显示使用说明
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "使用说明" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

Write-Host "常用命令：" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. 查询课表（表格视图）：" -ForegroundColor White
Write-Host "     uv run python hermes_plugin.py get --format table" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 查询课表（简化列表）：" -ForegroundColor White
Write-Host "     uv run python hermes_plugin.py get --format simple" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. 强制重新登录：" -ForegroundColor White
Write-Host "     uv run python hermes_plugin.py get --force-login" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. 检查课表变化：" -ForegroundColor White
Write-Host "     uv run python hermes_plugin.py check" -ForegroundColor Gray
Write-Host ""
Write-Host "  5. 重新配置：" -ForegroundColor White
Write-Host "     .\hermes_quickstart.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "详细文档：" -ForegroundColor Cyan
Write-Host "  - README.md：基本使用说明" -ForegroundColor White
Write-Host "  - hermes_integration_example.md：Hermes Agent 集成指南" -ForegroundColor White
Write-Host ""

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "启动完成！" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
