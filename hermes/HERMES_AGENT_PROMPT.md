# Hermes Agent 安装与使用提示词

将下面整段发送给 Hermes Agent。此模块通过本地脚本提供课表工具；`plugin.json` 是命令描述，不保证任何特定 Hermes 版本会自动发现或注册。

```text
请帮我安装、配置并使用正方教务课表 Hermes 适配器。

仓库：https://github.com/icewolf-li/ZF_Class_Schedule.git

安装范围：只检出 hermes/、cli/zf_schedule_monitor_uv.py 和 .gitignore，不安装 Docker API。

一、准备
1. 检查 Git 和 uv；若缺失，告诉我安装方式，不擅自执行来源不明的安装脚本。
2. 使用新的专用目录。如果目录已存在，先检查当前配置和 Git 状态，避免覆盖。
3. 命令参考（逐行执行，并检查每一步是否成功）：
   git clone --depth 1 --filter=blob:none --sparse https://github.com/icewolf-li/ZF_Class_Schedule.git ZF-Schedule-Hermes
   git -C ZF-Schedule-Hermes sparse-checkout set --no-cone /hermes/ /cli/zf_schedule_monitor_uv.py /.gitignore
4. 后续命令均以 ZF-Schedule-Hermes 为工作目录，或使用相应的绝对路径。

二、配置
向我确认以下字段，不使用示例值代替实际信息：
- username：学号。
- password：密码；不要在日志、命令输出或回答中复述。
- base_url：完整的教务应用地址，必须包含学校实际应用路径，例如 /jwglxt/。
- year：当前学年起始年，例如 2026 对应 2026–2027 学年。
- term：3 为第一学期，12 为第二学期。
- semester_start_date：实际教学第一周的周一日期，格式 YYYY-MM-DD。

将信息写入 hermes/hermes_config.json，使用 UTF-8。参考 hermes_config.example.json，
不要把密码放进终端命令历史，也不要修改或提交 Git 中的示例配置来存储真实账号。
此适配器使用显式学期配置，换学期时需更新，不假设具备 Docker API 的自动学期能力。

三、依赖
两个 Python 入口都有 uv 脚本依赖声明，不需要 uv init 或 uv add。
安装浏览器：
uv run --python 3.13.9 --with playwright==1.58.0 python -m playwright install --only-shell chromium

Linux 如果缺少系统库，按 Playwright 官方方式安装依赖；可以在具备相应权限时使用
install --with-deps --only-shell chromium。不要反复尝试登录来解决系统库错误。

四、验证
uv run --python 3.13.9 hermes/hermes_plugin.py get --format table

如果失败，说明具体原因；遇到验证码、账号错误或网络限制时停止重试，告知我处理方式。
验证完成后，只反馈是否成功、课程数量和可用命令，不回显账号密码。

五、后续调用
- 表格：uv run --python 3.13.9 hermes/hermes_plugin.py get --format table
- 简化列表：uv run --python 3.13.9 hermes/hermes_plugin.py get --format simple
- JSON：uv run --python 3.13.9 hermes/hermes_plugin.py get --format json
- 重新登录：uv run --python 3.13.9 hermes/hermes_plugin.py get --force-login
- 比较最近两次成功抓取：uv run --python 3.13.9 hermes/hermes_plugin.py check

get 会保存抓取结果；check 只比较已经保存的前后两次结果，需先 get 更新。
配置和数据都在 hermes/ 下，查询课程时不要把 Docker 或 CLI 的数据目录当成 Hermes 数据。

根据当前 Hermes 实例支持的工具/技能机制接入上述命令。如果没有可用的原生注册机制，
直接通过命令执行工具调用脚本并说明此方式，不虚构插件已经注册。
```

配置示例见 [hermes_config.example.json](hermes_config.example.json)。本模块提供表格、简化列表和 JSON，不提供 ICS 输出。
