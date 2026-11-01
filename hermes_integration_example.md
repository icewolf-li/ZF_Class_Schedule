# Hermes Agent 集成示例

本文档展示如何将正方教务课表插件集成到 Hermes Agent 中。

## 1. 插件注册

在 Hermes Agent 的插件目录中注册此插件：

```json
{
  "plugins": [
    {
      "name": "zf_schedule",
      "path": "/path/to/ZF_Class_Schedule",
      "enabled": true
    }
  ]
}
```

## 2. 用户交互流程

### 2.1 首次配置

当用户第一次使用时，Agent 应该引导用户配置：

**用户：** "帮我查看我的课表"

**Agent：** "好的，我需要先配置您的教务系统账号。请提供以下信息：
1. 您的学号
2. 您的密码
3. 教务系统 URL（例如：https://jwxt.gxnzd.com.cn/）
4. 当前学年（例如：2026）
5. 当前学期（3=第一学期，12=第二学期）
6. 本学期开始日期（例如：2026-09-01）"

**用户：** "学号：20230001，密码：mypass123，URL：https://jwxt.gxnzd.com.cn/，学年：2026，学期：3，开始日期：2026-09-01"

**Agent 执行：**
```bash
cd /path/to/ZF_Class_Schedule
uv run python hermes_plugin.py setup \
  --username 20230001 \
  --password mypass123 \
  --base-url https://jwxt.gxnzd.com.cn/ \
  --year 2026 \
  --term 3 \
  --start-date 2026-09-01
```

**Agent：** "✓ 配置完成！现在为您查询课表..."

### 2.2 查询课表

**用户：** "我今天有什么课？"

**Agent 执行：**
```bash
cd /path/to/ZF_Class_Schedule
uv run python hermes_plugin.py get --format table
```

**Agent 返回：**
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

【下午 5-6节】
------------------------------------------------------------
周四:
  📖 计算机网络
  📍 教学楼D102
  👨‍🏫 赵老师

============================================================

您本周共有 4 门课程。今天是周一，有以下课程：
- 上午 1-2 节：高等数学（教学楼A101）
```

### 2.3 检查变化

设置定时任务，每天自动检查课表变化：

**Cron 任务（每天早上 7 点）：**
```bash
0 7 * * * cd /path/to/ZF_Class_Schedule && uv run python hermes_plugin.py check
```

如果有变化，Agent 主动推送通知：

**Agent：** "⚠️ 课表有变化！
- 新增/修改：2 条
- 删除/修改前：1 条

请使用 '查看课表' 命令查看最新课表。"

## 3. 多平台适配

### 3.1 微信

表格视图已经优化为适合微信展示的纯文本格式，可以直接发送。

### 3.2 QQ

同微信，直接发送表格视图。

### 3.3 钉钉

可以使用 Markdown 卡片格式：

```markdown
## 📅 本周课表（第 5 周）

### 周一
- **上午 1-2 节**：高等数学
  - 📍 教学楼A101
  - 👨‍🏫 张老师

### 周二
- **下午 5-6 节**：数据结构
  - 📍 实验楼C301
  - 👨‍🏫 王老师
```

### 3.4 Telegram

可以使用 HTML 格式：

```html
<b>📅 第 5 周课表</b>

<b>周一</b>
上午 1-2 节：<i>高等数学</i>
📍 教学楼A101
👨‍🏫 张老师

<b>周二</b>
下午 5-6 节：<i>数据结构</i>
📍 实验楼C301
👨‍🏫 王老师
```

## 4. API 集成

如果需要程序化调用，可以使用 Python API：

```python
from hermes_plugin import HermesPlugin

# 初始化插件
plugin = HermesPlugin()

# 配置
plugin.setup(
    username="20230001",
    password="mypass123",
    base_url="https://jwxt.gxnzd.com.cn/",
    year="2026",
    term="3",
    semester_start_date="2026-09-01"
)

# 获取课表
result = plugin.get_schedule(format="table")
if result["status"] == "success":
    print(result["formatted_output"])
    print(f"当前第 {result['current_week']} 周")
    print(f"共 {result['total_courses']} 门课程")

# 检查变化
changes = plugin.check_changes()
if changes["status"] == "changed":
    print(f"课表有变化：{changes['message']}")
```

## 5. 错误处理

### 5.1 登录失败

**错误信息：** "登录失败：用户名或密码错误"

**Agent 响应：** "登录失败，请检查您的学号和密码是否正确。您可以使用以下命令重新配置：
```
重新配置账号
```"

### 5.2 Cookie 过期

**错误信息：** "接口未返回 JSON，登录可能过期"

**Agent 自动处理：** 自动使用 `--force-login` 重新登录

**Agent 响应：** "检测到登录已过期，正在重新登录..."

### 5.3 网络错误

**错误信息：** "获取课表失败: timeout"

**Agent 响应：** "网络连接超时，请稍后再试。您也可以检查：
1. 教务系统是否正常访问
2. 网络连接是否正常"

## 6. 高级功能

### 6.1 课程提醒

Agent 可以在上课前提醒用户：

**定时任务（每小时检查）：**
```python
from datetime import datetime
from hermes_plugin import HermesPlugin

plugin = HermesPlugin()
result = plugin.get_schedule()

# 解析当前时间和课表
now = datetime.now()
current_hour = now.hour
current_weekday = now.isoweekday()

# 检查接下来的课程
# ... 实现提醒逻辑
```

**Agent 推送：** "⏰ 提醒：30分钟后有课！
- 课程：高等数学
- 时间：上午 1-2 节（8:00-9:40）
- 地点：教学楼A101
- 教师：张老师"

### 6.2 作业提醒

如果教务系统包含作业信息，可以扩展插件功能：

```python
# 在 hermes_plugin.py 中添加
def get_assignments(self):
    """获取作业列表"""
    # ... 实现
```

### 6.3 考试提醒

同样可以添加考试查询功能：

```python
def get_exams(self):
    """获取考试安排"""
    # ... 实现
```

## 7. 部署建议

### 7.1 服务器部署

推荐使用 Docker 容器部署：

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装 uv
RUN pip install uv

# 复制项目文件
COPY . /app

# 安装依赖
RUN uv add playwright
RUN uv run playwright install chromium --with-deps

# 运行插件
CMD ["uv", "run", "python", "hermes_plugin.py", "get", "--format", "table"]
```

### 7.2 定时任务

使用 cron 或系统计划任务定期检查课表变化：

```bash
# Linux/Mac crontab
0 7 * * * cd /path/to/ZF_Class_Schedule && uv run python hermes_plugin.py check
```

```powershell
# Windows 计划任务
$action = New-ScheduledTaskAction -Execute "C:\Users\<user>\.local\bin\uv.exe" `
  -Argument "run python D:\path\to\ZF_Class_Schedule\hermes_plugin.py check" `
  -WorkingDirectory "D:\path\to\ZF_Class_Schedule"

$trigger = New-ScheduledTaskTrigger -Daily -At "07:00"

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ZF_Schedule_Check"
```

## 8. 安全建议

1. **配置文件加密**：对 `hermes_config.json` 进行加密存储
2. **权限控制**：限制配置文件的读写权限
3. **定期更换密码**：建议每学期更换一次密码
4. **日志审计**：记录所有操作日志
5. **数据备份**：定期备份课表数据

## 9. 常见问题

**Q: 如何更新配置？**
A: 重新运行 setup 命令即可覆盖旧配置。

**Q: 支持多账号吗？**
A: 当前版本不支持，每个插件实例只能配置一个账号。如需多账号，可以部署多个插件实例。

**Q: 如何查看历史课表？**
A: 历史数据保存在 `data/zf_schedule/history/` 目录。

**Q: 可以导出课表到日历吗？**
A: 当前版本不支持，但可以扩展功能生成 iCal 格式。

## 10. 贡献指南

欢迎提交 PR 或 Issue：
- 仓库地址：https://github.com/yourusername/ZF_Class_Schedule
- 讨论区：https://github.com/yourusername/ZF_Class_Schedule/discussions
