# 正方教务系统课表爬虫

---

## 🤖 Agent 提示词（复制粘贴给任何 AI Agent 使用）

```
你是一个课程表管理助手。请帮我安装和配置正方教务系统课表查询插件。

## 插件信息
- 仓库地址：https://github.com/yourusername/ZF_Class_Schedule
- 功能：自动登录正方教务系统，获取课程表，生成表格视图

## 安装步骤

1. 克隆仓库并安装依赖：
```bash
git clone https://github.com/yourusername/ZF_Class_Schedule.git
cd ZF_Class_Schedule
uv add playwright
uv run playwright install chromium
```

2. 配置我的账号信息（请询问我以下信息）：
   - 学号（username）
   - 密码（password）
   - 教务系统 URL（例如：https://jwxt.gxnzd.com.cn/）
   - 当前学年（例如：2026）
   - 当前学期（3=第一学期，12=第二学期）
   - 学期开始日期（例如：2026-09-01）

3. 配置插件：
```bash
uv run python hermes_plugin.py setup --username <学号> --password <密码> --base-url <URL> --year <学年> --term <学期> --start-date <开始日期>
```

4. 获取课表：
```bash
uv run python hermes_plugin.py get --format table
```

## 使用说明

### 查询课表
- 表格视图（推荐）：`uv run python hermes_plugin.py get --format table`
- 简化列表：`uv run python hermes_plugin.py get --format simple`
- 原始 JSON：`uv run python hermes_plugin.py get --format json`

### 重新登录
如果提示登录过期：`uv run python hermes_plugin.py get --force-login`

### 检查变化
检查课表是否有更新：`uv run python hermes_plugin.py check`

## 返回格式

插件会返回当前周的课表，格式为易读的文本表格，适合在微信、QQ、钉钉等平台展示：

```
============================================================
📅 第 5 周课表
============================================================

【上午 1-2节】
------------------------------------------------------------
周一:
  📖 高等数学
  📍 教学楼A101
  👨‍🏫 张老师

周三:
  📖 大学英语
  📍 教学楼B203
  👨‍🏫 李老师

【上午 3-4节】
------------------------------------------------------------
周二:
  📖 数据结构
  📍 实验楼C301
  👨‍🏫 王老师
...
```

## 定时任务

建议设置定时任务，每天自动检查课表变化并通知用户。

## 注意事项

1. 请妥善保管配置文件 `hermes_config.json`，其中包含敏感信息
2. 首次使用需要登录，之后会保存登录状态
3. 如果长时间未使用，可能需要重新登录
4. 支持无头模式，可在服务器上运行
```

---

## 📖 详细说明

自动抓取正方教务系统的个人课程表，支持服务器无头模式运行。

## 功能特点

- 支持三种登录方式：配置文件、命令行交互、手动浏览器
- 支持无头模式，可在服务器上运行
- 自动检测课表变化
- 保存登录状态，后续无需重复登录
- 数据本地存储，支持历史记录
- **🆕 Hermes Agent 插件支持**
- **🆕 生成表格视图，适配微信/QQ等平台**
- **🆕 自动计算当前周次**

## 安装依赖

```bash
# 添加 playwright 依赖
uv add playwright

# 安装 Chromium 浏览器
uv run playwright install chromium
```

## 使用方法

### 🆕 方式 0：作为 Hermes Agent 插件使用（推荐）

#### 安装插件
```bash
# 克隆仓库
git clone https://github.com/yourusername/ZF_Class_Schedule.git
cd ZF_Class_Schedule

# 安装依赖
uv add playwright
uv run playwright install chromium
```

#### 配置账号
```bash
uv run python hermes_plugin.py setup \
  --username 你的学号 \
  --password 你的密码 \
  --base-url https://jwxt.gxnzd.com.cn/ \
  --year 2026 \
  --term 3 \
  --start-date 2026-09-01
```

#### 获取课表
```bash
# 表格视图（适合微信/QQ展示）
uv run python hermes_plugin.py get --format table

# 简化列表
uv run python hermes_plugin.py get --format simple

# 原始 JSON 数据
uv run python hermes_plugin.py get --format json

# 强制重新登录
uv run python hermes_plugin.py get --force-login
```

#### 检查课表变化
```bash
uv run python hermes_plugin.py check
```

---

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
