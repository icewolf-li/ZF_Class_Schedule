# 快速命令参考

## 🚀 快速开始

### Windows 一键启动
```powershell
.\hermes_quickstart.ps1
```

### Linux/Mac 手动启动
```bash
# 安装依赖
uv add playwright
uv run playwright install chromium

# 配置
uv run python hermes_plugin.py setup \
  --username 你的学号 \
  --password 你的密码 \
  --base-url https://jwxt.gxnzd.com.cn/

# 查询
uv run python hermes_plugin.py get --format table
```

---

## 📋 Hermes 插件命令

### 配置账号
```bash
uv run python hermes_plugin.py setup \
  --username <学号> \
  --password <密码> \
  --base-url <URL> \
  --year <学年> \
  --term <学期> \
  --start-date <开始日期>
```

**示例**：
```bash
uv run python hermes_plugin.py setup \
  --username 20230001 \
  --password mypass123 \
  --base-url https://jwxt.gxnzd.com.cn/ \
  --year 2026 \
  --term 3 \
  --start-date 2026-09-01
```

### 查询课表

**表格视图**（推荐，适合微信/QQ）：
```bash
uv run python hermes_plugin.py get --format table
```

**简化列表**：
```bash
uv run python hermes_plugin.py get --format simple
```

**JSON 数据**：
```bash
uv run python hermes_plugin.py get --format json
```

**强制重新登录**：
```bash
uv run python hermes_plugin.py get --force-login
```

### 检查变化
```bash
uv run python hermes_plugin.py check
```

### 测试插件
```bash
uv run python hermes_plugin.py test
```

---

## 🔧 原始脚本命令

### 配置文件方式（推荐服务器）
```bash
# 首次登录
uv run python zf_schedule_monitor_uv.py \
  --base-url https://jwxt.gxnzd.com.cn/ \
  --login \
  --config config.json

# 后续查询（使用已保存的登录状态）
uv run python zf_schedule_monitor_uv.py \
  --base-url https://jwxt.gxnzd.com.cn/
```

### 交互式输入
```bash
uv run python zf_schedule_monitor_uv.py \
  --base-url https://jwxt.gxnzd.com.cn/ \
  --login
```

### 手动浏览器登录
```bash
uv run python zf_schedule_monitor_uv.py \
  --base-url https://jwxt.gxnzd.com.cn/ \
  --login \
  --manual
```

### 离线验证 JSON
```bash
uv run python zf_schedule_monitor_uv.py \
  --from-json latest_raw_2026_3.json
```

---

## 🧪 测试命令

### 运行所有测试
```bash
python test_plugin.py
```

### 语法检查
```bash
python -m py_compile hermes_plugin.py
python -m py_compile zf_schedule_monitor_uv.py
```

---

## 📦 安装命令

### 安装 uv（如果没有）

**Windows**：
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac**：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 安装依赖
```bash
# Python 包
uv add playwright

# Chromium 浏览器
uv run playwright install chromium
```

---

## 🔄 Git 命令

### 初始化仓库
```bash
git init
git add .
git commit -m "初始提交：正方教务课表插件"
```

### 添加远程仓库
```bash
git remote add origin https://github.com/yourusername/ZF_Class_Schedule.git
git branch -M main
git push -u origin main
```

### 使用提交助手（Windows）
```powershell
.\git_commit.ps1
```

---

## ⏰ 定时任务

### Linux/Mac (cron)

编辑 crontab：
```bash
crontab -e
```

添加任务：
```bash
# 每天早上 7 点检查课表
0 7 * * * cd /path/to/ZF_Class_Schedule && uv run python hermes_plugin.py get --format table >> /var/log/schedule.log 2>&1

# 每小时检查变化
0 * * * * cd /path/to/ZF_Class_Schedule && uv run python hermes_plugin.py check >> /var/log/schedule_check.log 2>&1
```

### Windows (计划任务)

**PowerShell 命令**：
```powershell
# 创建每天早上 7 点的任务
$action = New-ScheduledTaskAction `
  -Execute "C:\Users\<username>\.local\bin\uv.exe" `
  -Argument "run python hermes_plugin.py get --format table" `
  -WorkingDirectory "D:\path\to\ZF_Class_Schedule"

$trigger = New-ScheduledTaskTrigger -Daily -At "07:00"

Register-ScheduledTask `
  -Action $action `
  -Trigger $trigger `
  -TaskName "ClassScheduleCheck" `
  -Description "每天早上检查课表"
```

**或使用任务计划程序 GUI**：
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（每天 7:00）
4. 操作：启动程序
   - 程序：`C:\Users\<username>\.local\bin\uv.exe`
   - 参数：`run python hermes_plugin.py get --format table`
   - 起始于：`D:\path\to\ZF_Class_Schedule`

---

## 🐳 Docker 部署

### 创建 Dockerfile
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装 uv
RUN pip install uv

# 复制项目
COPY . /app

# 安装依赖
RUN uv add playwright
RUN uv run playwright install chromium --with-deps

# 配置环境变量（或使用配置文件）
ENV ZF_USERNAME=""
ENV ZF_PASSWORD=""
ENV ZF_BASE_URL="https://jwxt.gxnzd.com.cn/"

# 运行
CMD ["uv", "run", "python", "hermes_plugin.py", "get", "--format", "table"]
```

### 构建和运行
```bash
# 构建镜像
docker build -t zf-schedule .

# 运行（使用配置文件）
docker run -v $(pwd)/hermes_config.json:/app/hermes_config.json zf-schedule

# 运行（使用环境变量）
docker run \
  -e ZF_USERNAME="20230001" \
  -e ZF_PASSWORD="mypass123" \
  -e ZF_BASE_URL="https://jwxt.gxnzd.com.cn/" \
  zf-schedule
```

---

## 🔍 常用查询

### 查看数据目录
```bash
ls -la data/zf_schedule/
```

### 查看最新快照
```bash
cat data/zf_schedule/snapshot_2026_3.json | python -m json.tool
```

### 查看历史记录
```bash
ls -la data/zf_schedule/history/
```

### 查看配置
```bash
cat hermes_config.json
```

---

## 🆘 故障排查

### 登录失败
```bash
# 重新配置
uv run python hermes_plugin.py setup \
  --username <学号> \
  --password <密码> \
  --base-url <URL>

# 强制重新登录
uv run python hermes_plugin.py get --force-login
```

### Cookie 过期
```bash
# 删除浏览器配置，重新登录
rm -rf data/zf_schedule/browser-profile/
uv run python hermes_plugin.py get --force-login
```

### 依赖问题
```bash
# 重新安装 playwright
uv remove playwright
uv add playwright
uv run playwright install chromium
```

### 查看日志
```bash
# 启用详细日志
uv run python hermes_plugin.py get --format table 2>&1 | tee debug.log
```

---

## 📱 AI Agent 使用

### 复制提示词给 Agent
```bash
# 方式1：复制 README.md 顶部的提示词
cat README.md

# 方式2：复制完整提示词
cat HERMES_AGENT_PROMPT.md
```

### Agent 命令示例

**配置**：
```
请帮我配置正方教务系统插件
学号：20230001
密码：mypass123
URL：https://jwxt.gxnzd.com.cn/
学年：2026
学期：3（第一学期）
开始日期：2026-09-01
```

**查询**：
```
查看我的课表
今天有什么课？
明天有几节课？
这周哪天最忙？
```

**检查**：
```
检查课表是否有变化
```

---

## 🔗 相关链接

- **项目文档**：README.md
- **Agent 提示词**：HERMES_AGENT_PROMPT.md
- **集成指南**：hermes_integration_example.md
- **项目结构**：PROJECT_STRUCTURE.md
- **更新日志**：CHANGELOG.md

---

## 💡 提示

1. 所有命令都在项目根目录执行
2. Windows 使用反引号 `` ` `` 或 `^` 进行换行
3. Linux/Mac 使用反斜杠 `\` 进行换行
4. 配置文件包含敏感信息，请勿提交到 git
5. 首次使用建议运行快速启动脚本

---

**最后更新**：2026-11-01
