# 正方教务系统课表爬虫

自动抓取正方教务系统的个人课程表，支持服务器无头模式运行。

## 功能特点

- 支持三种登录方式：配置文件、命令行交互、手动浏览器
- 支持无头模式，可在服务器上运行
- 自动检测课表变化
- 保存登录状态，后续无需重复登录
- 数据本地存储，支持历史记录

## 安装依赖

```bash
# 添加 playwright 依赖
uv add playwright

# 安装 Chromium 浏览器
uv run playwright install chromium
```

## 使用方法

### 方式 1：使用配置文件（推荐服务器使用）

1. 复制示例配置文件：
```bash
copy config.example.json config.json
```

2. 编辑 `config.json`，填入你的学号和密码：
```json
{
  "username": "你的学号",
  "password": "你的密码",
  "base_url": "https://jwxt.gxnzd.com.cn/"
}
```

3. 首次登录：
```bash
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login --config config.json
```

4. 后续查询（使用已保存的登录状态）：
```bash
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/
```

### 方式 2：命令行交互式输入

首次登录时交互式输入账号密码：
```bash
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login
```

程序会提示你输入学号和密码（密码输入时不会显示）。

### 方式 3：手动浏览器登录（原方式）

如果自动登录失败，可以使用手动模式：
```bash
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login --manual
```

程序会打开浏览器窗口，你可以手动输入账号密码，登录成功后在终端按 Enter 继续。

## 命令行参数

- `--base-url`: 教务系统基础地址（必填，除非使用 `--from-json`）
- `--login`: 执行登录操作
- `--manual`: 手动浏览器登录模式（需配合 `--login`）
- `--config`: 指定配置文件路径（需配合 `--login`）
- `--year`: 学年起始年，默认 2026
- `--term`: 学期代码，3=第一学期，12=第二学期，默认 3
- `--from-json`: 从本地 JSON 文件导入数据，用于离线验证
- `--data-dir`: 自定义数据保存目录

## 数据存储

默认数据保存在 `data/zf_schedule/` 目录：

- `browser-profile/`: 浏览器登录状态（Cookie）
- `snapshot_<year>_<term>.json`: 标准化的课表快照
- `latest_raw_<year>_<term>.json`: 最新的原始响应数据
- `history/`: 历史变更记录

## 定时任务

### Windows 计划任务

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：每天特定时间
4. 操作：启动程序
   - 程序：`C:\Users\<你的用户名>\.local\bin\uv.exe`
   - 参数：`run python D:\aaatemp\kechengbiao\zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/`
   - 起始于：`D:\aaatemp\kechengbiao`

### Linux/Mac Cron

```bash
# 编辑 crontab
crontab -e

# 每天早上 8 点检查课表
0 8 * * * cd /path/to/project && uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ >> /path/to/log.txt 2>&1
```

## 安全提示

1. `config.json` 包含敏感信息，请勿提交到 git
2. `data/` 目录包含个人信息和登录状态，请妥善保管
3. 建议定期更换密码，并重新登录
4. 在公共服务器上使用时，注意文件权限设置

## 常见问题

### 1. 登录失败

- 检查账号密码是否正确
- 尝试使用 `--manual` 模式手动登录
- 检查网络连接和教务系统是否可访问
- 某些学校可能有验证码，需要使用 `--manual` 模式

### 2. 接口返回错误

- 确认 `--base-url` 是否正确
- 尝试重新登录：`--login --config config.json`
- 检查学年和学期参数是否正确

### 3. 浏览器启动失败

确保已安装 Chromium：
```bash
uv run playwright install chromium
```

## 许可

本项目仅供学习交流使用，请勿用于商业用途。使用本工具时请遵守学校相关规定。
