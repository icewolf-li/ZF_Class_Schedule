# 正方教务课表爬虫 - 初始化脚本
# 使用方法：.\setup.ps1

Write-Host "正方教务课表爬虫 - 初始化向导" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 检查 uv 是否已安装
Write-Host "检查依赖..." -ForegroundColor Yellow
$uvPath = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvPath) {
    Write-Host "错误：未找到 uv 命令" -ForegroundColor Red
    Write-Host "请先安装 uv：https://github.com/astral-sh/uv" -ForegroundColor Red
    exit 1
}
Write-Host "✓ uv 已安装" -ForegroundColor Green

# 检查是否在 uv 项目中
if (-not (Test-Path "pyproject.toml")) {
    Write-Host ""
    Write-Host "未检测到 pyproject.toml，是否初始化 uv 项目？[Y/n]" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -ne "n" -and $response -ne "N") {
        Write-Host "初始化 uv 项目..." -ForegroundColor Yellow
        uv init --no-readme
        Write-Host "✓ 项目初始化完成" -ForegroundColor Green
    }
}

# 安装 playwright
Write-Host ""
Write-Host "安装 playwright..." -ForegroundColor Yellow
uv add playwright
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ playwright 已安装" -ForegroundColor Green
} else {
    Write-Host "✗ playwright 安装失败" -ForegroundColor Red
    exit 1
}

# 安装 Chromium 浏览器
Write-Host ""
Write-Host "安装 Chromium 浏览器..." -ForegroundColor Yellow
uv run playwright install chromium
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Chromium 已安装" -ForegroundColor Green
} else {
    Write-Host "✗ Chromium 安装失败" -ForegroundColor Red
    exit 1
}

# 创建配置文件
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "配置登录信息" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "config.json") {
    Write-Host "config.json 已存在，是否覆盖？[y/N]" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "跳过配置文件创建" -ForegroundColor Yellow
    } else {
        $createConfig = $true
    }
} else {
    $createConfig = $true
}

if ($createConfig) {
    Write-Host "请输入你的登录信息：" -ForegroundColor Yellow
    $username = Read-Host "学号"
    $password = Read-Host "密码" -AsSecureString
    $passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
    )
    $baseUrl = Read-Host "教务系统地址（默认: https://jwxt.gxnzd.com.cn/）"
    if ([string]::IsNullOrWhiteSpace($baseUrl)) {
        $baseUrl = "https://jwxt.gxnzd.com.cn/"
    }

    $config = @{
        username = $username
        password = $passwordPlain
        base_url = $baseUrl
    } | ConvertTo-Json -Depth 10

    [System.IO.File]::WriteAllText("$PWD\config.json", $config, [System.Text.Encoding]::UTF8)
    Write-Host "✓ 配置文件已创建：config.json" -ForegroundColor Green
}

# 首次登录测试
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "首次登录测试" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "是否立即测试登录？[Y/n]" -ForegroundColor Yellow
$response = Read-Host
if ($response -ne "n" -and $response -ne "N") {
    Write-Host ""
    Write-Host "开始登录测试..." -ForegroundColor Yellow

    if (Test-Path "config.json") {
        uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login --config config.json
    } else {
        uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ 登录测试成功！" -ForegroundColor Green
        Write-Host ""
        Write-Host "后续可以直接运行（无需再次登录）：" -ForegroundColor Cyan
        Write-Host "  uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "✗ 登录测试失败" -ForegroundColor Red
        Write-Host "可以尝试手动登录模式：" -ForegroundColor Yellow
        Write-Host "  uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login --manual" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "初始化完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "快速使用指南：" -ForegroundColor Cyan
Write-Host "  1. 查询课表（使用已保存登录状态）：" -ForegroundColor White
Write-Host "     uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 重新登录：" -ForegroundColor White
Write-Host "     uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login --config config.json" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. 查看帮助：" -ForegroundColor White
Write-Host "     uv run python zf_schedule_monitor_uv.py --help" -ForegroundColor Gray
Write-Host ""
Write-Host "详细文档请查看 README.md" -ForegroundColor Cyan
