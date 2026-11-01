# 🤖 给 AI Agent 的完整提示词

> 直接复制以下内容粘贴给任何 AI Agent（包括 Hermes Agent、ChatGPT、Claude 等）

---

## 任务说明

你是一个教务系统助手。请帮我安装、配置并使用「正方教务系统课表查询插件」。

## 仓库信息

- **项目名称**：ZF_Class_Schedule
- **仓库地址**：https://github.com/yourusername/ZF_Class_Schedule
- **功能**：自动登录正方教务系统，查询课程表，生成表格视图，检测课表变化

## 第一步：克隆仓库并安装依赖

请执行以下命令：

```bash
git clone https://github.com/yourusername/ZF_Class_Schedule.git
cd ZF_Class_Schedule
uv add playwright
uv run playwright install chromium
```

如果没有 `uv`，请先安装：
- Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Linux/Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## 第二步：配置账号信息

**请询问我以下信息**（不要假设，必须询问）：

1. **学号**（username）
2. **密码**（password）- 请注意保密
3. **教务系统 URL**（base_url）- 例如：`https://jwxt.gxnzd.com.cn/`
4. **当前学年**（year）- 例如：`2026`（对应 2026-2027 学年）
5. **当前学期**（term）- `3` 表示第一学期，`12` 表示第二学期
6. **学期开始日期**（semester_start_date）- 格式：`YYYY-MM-DD`，例如：`2026-09-01`

**收集完信息后**，执行配置命令：

```bash
uv run python hermes_plugin.py setup \
  --username <学号> \
  --password <密码> \
  --base-url <教务系统URL> \
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

## 第三步：查询课表

配置完成后，执行查询命令：

```bash
# 表格视图（推荐，适合微信/QQ/钉钉展示）
uv run python hermes_plugin.py get --format table

# 简化列表视图
uv run python hermes_plugin.py get --format simple

# JSON 原始数据
uv run python hermes_plugin.py get --format json
```

## 输出格式示例

执行 `get --format table` 后，你会收到类似这样的输出：

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

状态：成功 | 当前第 5 周 | 共 4 门课程
```

**请将这个格式化的课表直接展示给我。**

## 第四步：智能回答用户问题

根据课表数据，回答我的问题，例如：

### 问题示例 1：今天有什么课？

**你的回答步骤**：
1. 查看课表输出
2. 确定今天是星期几
3. 筛选出今天的课程
4. 用友好的语言告诉我

**回答示例**：
```
今天是周一，您有以下课程：

上午 1-2 节（8:00-9:40）
📖 高等数学
📍 教学楼A101
👨‍🏫 张老师

祝您上课愉快！☀️
```

### 问题示例 2：明天有几节课？

**你的回答步骤**：
1. 确定明天是星期几
2. 统计明天的课程数量
3. 告诉我详细信息

### 问题示例 3：这周哪天最忙？

**你的回答步骤**：
1. 统计每天的课程数量
2. 找出课程最多的那天
3. 告诉我详细信息

## 第五步：检查课表变化（可选）

如果需要检查课表是否有变化，执行：

```bash
uv run python hermes_plugin.py check
```

如果有变化，输出类似：
```json
{
  "status": "changed",
  "message": "课表有变化：新增/修改 2 条，删除/修改前 1 条",
  "changes": {
    "added": 2,
    "removed": 1
  }
}
```

**请告诉我**：课表有变化，并建议我重新查询。

## 错误处理

### 如果登录失败

**错误信息**：`"status": "error", "message": "登录失败：..."`

**你的处理**：
1. 告诉我登录失败的原因
2. 建议我检查账号密码是否正确
3. 提供重新配置的命令

### 如果 Cookie 过期

**你的处理**：
1. 自动尝试使用 `--force-login` 重新登录
2. 告诉我"检测到登录已过期，正在重新登录..."

```bash
uv run python hermes_plugin.py get --force-login
```

### 如果网络错误

**你的处理**：
1. 告诉我网络连接超时
2. 建议我检查网络和教务系统是否正常

## 高级功能

### 定时提醒

如果我问"帮我设置上课提醒"，你可以：

1. 告诉我可以设置定时任务
2. 提供 cron 或 Windows 计划任务的配置方法

**Linux/Mac cron 示例**：
```bash
# 每天早上 7 点查询课表
0 7 * * * cd /path/to/ZF_Class_Schedule && uv run python hermes_plugin.py get --format table
```

**Windows 计划任务示例**：
```powershell
$action = New-ScheduledTaskAction -Execute "C:\Users\<user>\.local\bin\uv.exe" `
  -Argument "run python D:\path\to\ZF_Class_Schedule\hermes_plugin.py get --format table" `
  -WorkingDirectory "D:\path\to\ZF_Class_Schedule"
$trigger = New-ScheduledTaskTrigger -Daily -At "07:00"
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ClassScheduleCheck"
```

### 课程统计

如果我问"这学期有多少门课"，你可以：

1. 解析 JSON 数据中的 `total_courses`
2. 统计不同的课程名称数量
3. 告诉我详细信息

## 注意事项

1. **隐私保护**：不要在日志中显示密码
2. **友好交流**：用自然、友好的语言回答
3. **主动提醒**：如果发现课表有变化，主动告诉我
4. **智能理解**：理解"今天"、"明天"、"下周"等时间词
5. **格式优化**：根据不同平台（微信/QQ/钉钉）优化输出格式

## 多平台适配

### 微信/QQ
直接使用 `--format table` 的输出，纯文本格式

### 钉钉
可以转换为 Markdown 卡片：
```markdown
## 📅 本周课表（第 5 周）

### 周一
- **上午 1-2 节**：高等数学
  - 📍 教学楼A101
  - 👨‍🏫 张老师
```

### Telegram
可以使用 HTML 格式：
```html
<b>📅 第 5 周课表</b>

<b>周一</b>
上午 1-2 节：<i>高等数学</i>
📍 教学楼A101
👨‍🏫 张老师
```

## 总结

完成以上步骤后，你应该能够：

✅ 成功安装插件  
✅ 配置我的账号信息  
✅ 查询并展示课表  
✅ 智能回答关于课程的问题  
✅ 检查课表变化  
✅ 设置定时提醒（可选）

**现在，请开始执行第一步：克隆仓库并安装依赖。**

如果遇到任何问题，请告诉我具体的错误信息，我会帮助你解决。

---

## 快速测试

如果你想快速测试是否一切正常，可以运行：

```bash
python test_plugin.py
```

这会测试所有核心功能，不需要真实登录。
