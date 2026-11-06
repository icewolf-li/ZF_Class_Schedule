# 正方教务课表工具

自动登录本人账号的正方教务系统，获取课程表。按使用方式分为三个模块，使用 Git sparse checkout 可以只检出需要的文件。

| 使用场景 | 入口 | 需要的文件 |
| --- | --- | --- |
| Windows 本地查询、保存快照 | `cli/` | 一个独立 Python 脚本 |
| Hermes Agent 调用 | `hermes/` | 插件适配器、配置示例和 CLI 抓取脚本 |
| 云服务器或本机 Docker API | `docker/` | Docker 模块和 CLI 抓取脚本 |

```text
cli/
  zf_schedule_monitor_uv.py   独立入口，也是其他模块复用的抓取逻辑
  config.example.json       CLI 账号配置示例
hermes/
  hermes_plugin.py           Hermes 命令行适配器
  hermes_config.example.json
  plugin.json               命令描述
  HERMES_AGENT_PROMPT.md     可直接发送给 Agent 的完整安装提示词
docker/
  compose.yaml
  Dockerfile
  Dockerfile.dockerignore
  pyproject.toml
  uv.lock
  config.example.json       API 账号、入学年份、缓存及校历配置示例
  schedule_api.py
  schedule_calendar.py
```

账号配置、浏览器 profile 和课表数据不进入 Git，也不会打包进 Docker 镜像。所有示例中的学期日期均需按学校实际情况填写。学校要求验证码、校园网络或统一身份认证时，自动登录可能受到限制。

## 1. Windows：只下载脚本，直接 uv run

前提：已安装 Git 和 [uv](https://docs.astral.sh/uv/)。在 PowerShell 7 中复制执行下面这一行；目录名 `ZF-Schedule-CLI` 需要尚不存在。

```powershell
git clone --depth 1 --filter=blob:none --sparse https://github.com/icewolf-li/ZF_Class_Schedule.git ZF-Schedule-CLI; git -C ZF-Schedule-CLI sparse-checkout set --no-cone '/cli/zf_schedule_monitor_uv.py' '/.gitignore'; uv run --python 3.13.9 ZF-Schedule-CLI/cli/zf_schedule_monitor_uv.py --install-browser --login --base-url https://jwxt.gxnzd.com.cn/jwglxt/ --year 2026 --term 3
```

先把 `--base-url` 换成学校教务系统的完整应用地址，学年、学期也按实际填写。程序会交互询问学号和密码，密码不回显。

- uv 根据脚本内的依赖声明准备 Python 和 Playwright，无需 `uv init` 或 `uv add`。
- `--install-browser` 安装 Chromium headless shell；之后可省略该参数。
- `--year 2026` 表示 **2026–2027 学年**；`--term 3` 表示第一学期，`--term 12` 表示第二学期。
- CLI 输出完整课表记录和变化摘要，不提供 API 的按日/按周筛选。
- 默认数据保存在 `ZF-Schedule-CLI/cli/data/zf_schedule/`，含最新响应、快照、变更历史和浏览器 profile。

再次抓取时建议仍带 `--login`，确保 session cookie 过期后能够登录：

```powershell
uv run --python 3.13.9 ZF-Schedule-CLI/cli/zf_schedule_monitor_uv.py --login --base-url https://jwxt.gxnzd.com.cn/jwglxt/ --year 2026 --term 3
```

需要保存账号配置时，将以下 UTF-8 JSON 保存为 `ZF-Schedule-CLI/cli/config.json`：

```json
{
  "username": "你的学号",
  "password": "你的密码",
  "base_url": "https://jwxt.gxnzd.com.cn/jwglxt/"
}
```

然后执行；CLI 的 `--base-url` 仍需传入：

```powershell
uv run --python 3.13.9 ZF-Schedule-CLI/cli/zf_schedule_monitor_uv.py --login --config ZF-Schedule-CLI/cli/config.json --base-url https://jwxt.gxnzd.com.cn/jwglxt/ --year 2026 --term 3
```

其他用法：

```powershell
# 有验证码时，在本机打开完整浏览器手动登录
uv run --python 3.13.9 ZF-Schedule-CLI/cli/zf_schedule_monitor_uv.py --install-browser --login --manual --base-url https://jwxt.gxnzd.com.cn/jwglxt/

# 离线验证已有 JSON，不访问教务系统
uv run --python 3.13.9 ZF-Schedule-CLI/cli/zf_schedule_monitor_uv.py --from-json '你的课表响应.json' --year 2026 --term 3
```

## 2. Hermes Agent：复制提示词，由 Agent 安装配置

这是供 Hermes Agent 调用的命令行适配器。`plugin.json` 描述命令，实际执行入口是 `hermes_plugin.py`；Git 下载本身不代表已注册到某个 Hermes 平台。

把下面整段复制给 Hermes Agent：

```text
请帮我安装并配置正方教务课表 Hermes 适配器。

仓库：https://github.com/icewolf-li/ZF_Class_Schedule.git

1. 检查 Git、uv 是否可用。使用一个新的专用目录，不覆盖已有目录。
2. 用 Git sparse checkout 只拉取 hermes/、cli/zf_schedule_monitor_uv.py 和 .gitignore，
   不拉取 Docker 模块。命令参考：
   git clone --depth 1 --filter=blob:none --sparse https://github.com/icewolf-li/ZF_Class_Schedule.git ZF-Schedule-Hermes
   git -C ZF-Schedule-Hermes sparse-checkout set --no-cone /hermes/ /cli/zf_schedule_monitor_uv.py /.gitignore
3. 阅读 hermes/HERMES_AGENT_PROMPT.md，按其中步骤完成安装。
4. 向我确认学号、密码、完整教务系统应用 URL、学年、学期和实际教学第一周日期。
   不使用示例日期代替校历，不在日志或回答中复述密码。
5. 在 hermes/hermes_config.json 中保存 UTF-8 配置，安装 Playwright 浏览器。
6. 使用 uv run --python 3.13.9 hermes/hermes_plugin.py get --format table 验证。
   所有相对路径都以专用仓库目录为基准。
7. 根据当前 Hermes 实例支持的本地工具/技能机制接入这些命令；如果没有原生注册方式，
   直接调用脚本，不要虚构安装成功。后续帮我查询课表时使用这个适配器。

遇到验证码或登录错误时告诉我具体原因，不要连续重试登录。
```

完整提示词及配置说明见 [hermes/HERMES_AGENT_PROMPT.md](hermes/HERMES_AGENT_PROMPT.md)。

安装完成后，在 `ZF-Schedule-Hermes` 目录使用：

```powershell
uv run --python 3.13.9 hermes/hermes_plugin.py get --format table
uv run --python 3.13.9 hermes/hermes_plugin.py get --format simple
uv run --python 3.13.9 hermes/hermes_plugin.py get --format json
uv run --python 3.13.9 hermes/hermes_plugin.py get --force-login
uv run --python 3.13.9 hermes/hermes_plugin.py check
```

`check` 比较最近两次成功抓取，不会主动访问学校；先执行 `get` 更新。配置和数据固定保存在 `hermes/` 下，不受执行命令时所在目录影响。Hermes 模块使用显式学年、学期及学期开始日期，需要换学期时更新配置；自动学期功能属于下面的 Docker API。

## 3. Docker API：先下载，再填配置，最后启动

适用于本机 Docker Desktop 或安装了 Docker Engine + Compose plugin 的 Linux 云服务器。宿主机只需要 Git 和 Docker，不需要安装 Python、uv 或 Chromium。建议至少 2 GB 内存，并预留镜像和构建缓存空间。

### 第一步：只拉取 Docker 模块及共享抓取脚本

在准备部署的机器上执行以下命令。它们不包含 shell 拼接语法，可在 PowerShell 7 或常见 Linux 终端逐行运行：

```text
git clone --depth 1 --filter=blob:none --sparse https://github.com/icewolf-li/ZF_Class_Schedule.git ZF-Schedule-Docker
git -C ZF-Schedule-Docker sparse-checkout set --no-cone /docker/ /cli/zf_schedule_monitor_uv.py /.gitignore
```

### 第二步：创建配置，由你填写账号和密钥

Windows PowerShell：

```powershell
Copy-Item ZF-Schedule-Docker/docker/config.example.json ZF-Schedule-Docker/docker/config.json
```

Linux 服务器：

```text
cp ZF-Schedule-Docker/docker/config.example.json ZF-Schedule-Docker/docker/config.json
```

编辑新建的 `docker/config.json`，至少填写下面这些字段，保留示例中其他设置即可：

```json
{
  "username": "你的学号",
  "password": "你的密码",
  "base_url": "https://jwxt.gxnzd.com.cn/jwglxt/",
  "api_key": "请填写你生成的随机长密钥",
  "enrollment_year": 2025,
  "teaching_weeks": 20,
  "calendar": {},
  "cache_ttl": 3600,
  "host": "0.0.0.0",
  "port": 8000,
  "data_dir": "data/zf_schedule_api"
}
```

不要覆盖已有的真实配置。`base_url` 必须包含学校应用路径，例如 `/jwglxt/`。入学年份只需填写一次，不必随学期修改。

### 第三步：构建并启动

```text
docker compose -f ZF-Schedule-Docker/docker/compose.yaml up -d --build
docker compose -f ZF-Schedule-Docker/docker/compose.yaml ps
docker compose -f ZF-Schedule-Docker/docker/compose.yaml logs --tail 100
```

第一次会下载镜像、依赖和浏览器，可能较慢。容器启动后监听 `8000` 端口，以非 root 用户运行；配置文件只读挂载，浏览器数据由 named volume 保存。镜像使用 Chromium headless shell，浏览器和系统依赖仍占主要体积。

如果已经完整克隆本仓库，从仓库根目录使用 `docker compose -f docker/compose.yaml up -d --build` 即可。本仓库整理时迁移的本地配置位于 `docker/config.json`。

### 第四步：调用 API

本机 PowerShell 示例：

```powershell
$headers = @{ 'X-API-Key' = '与config.json相同的密钥' }
Invoke-RestMethod 'http://localhost:8000/schedule/today' -Headers $headers
Invoke-RestMethod 'http://localhost:8000/schedule/week' -Headers $headers
```

| 接口 | 功能 |
| --- | --- |
| `GET /schedule` | 当前整学期课程，使用缓存 |
| `GET /schedule/latest` | 强制重新抓取当前学期，并更新缓存 |
| `GET /schedule/today` | 今天的课程 |
| `GET /schedule/date?date=2026-11-06` | 指定日期的课程 |
| `GET /schedule/week` | 本周课程，周一至周日 |
| `GET /schedule/week?date=2026-11-06` | 指定日期所在周及教学周次 |
| `GET /schedule/week?week=5` | 当前学期第 5 个教学周 |

所有接口都要求 `X-API-Key`。日期使用 `YYYY-MM-DD`；`date` 与 `week` 不能同时传入。所有接口支持 `refresh=true` 强制刷新对应学期；`/schedule` 和 `/schedule/latest` 也支持用 `date` 选择整学期。

响应包含 `year`、`term`、`grade`、`semester_name`、`week`、`courses`、`fetched_at`、`cached`、`message`。周查询还包含 `start_date`、`end_date` 和七天的 `days` 数组，每天含日期、星期和课程。课程字段沿用教务系统，如 `kcmc` 为课程名、`xqj` 为星期、`jcs` 为节次、`zcd` 为教学周、`cdmc` 为地点、`xm` 为教师。

寒暑假、入学前、没有匹配课程或显式传入 `date=null` / `week=null` 时，返回 `200`、`message: "无课"` 和 `courses: []`；假期无当前教学学期，`week=N` 同样返回无课。周查询传入的日期处于假期时，该周按无课返回；显式 null 的周查询返回 `days: []`。

状态码：密钥无效 `401`，接口不存在 `404`，参数错误 `400`，学校登录或抓取失败 `502`。抓取失败不覆盖缓存。缓存按学期隔离，默认 3600 秒，`cache_ttl: 0` 禁用；只保存在内存里，重启容器后首次请求会重新抓取。

### 自动学期与真实校历

以 2025 年入学为例：2025 年秋季为大一上学期；2026 年春季为大一下学期；2026 年秋季为大二上学期。使用中国时间 UTC+08:00 判断今天，不受服务器时区影响。

**默认校历是估算：9 月、3 月的第一个周一开学，每学期 20 个教学周。** 入学年份不能确定学校真实开学日和假期，请按学校日历覆盖 `calendar`，下面仅为格式示例：

```json
"calendar": {
  "2025-3": {"start_date": "2025-09-08", "end_date": "2026-01-18"},
  "2025-12": {"start_date": "2026-03-02", "end_date": "2026-07-12"}
}
```

键为“学年起始年-学期代码”，`3` 是上学期，`12` 是下学期。起止日均包含在教学期内；第一教学周按开学日所在的周一至周日计算。不填结束日期时按 `teaching_weeks` 推算；设为 `null` 或 `start_date: null` 表示该学期无课。未覆盖的学期使用默认规则。

所有 API 配置支持 `ZF_` 前缀环境变量，如 `ZF_USERNAME`、`ZF_PASSWORD`、`ZF_BASE_URL`、`ZF_API_KEY`、`ZF_ENROLLMENT_YEAR`、`ZF_TEACHING_WEEKS`、`ZF_CACHE_TTL`、`ZF_CALENDAR`，优先于 JSON。`ZF_CALENDAR` 使用 JSON 字符串。Compose 固定监听地址、端口及数据目录；其他环境变量需自行加入 Compose 的 `environment`，宿主机变量不会自动全部传入容器。

### 云服务器访问与日常更新

服务器必须能访问学校教务系统；某些学校限制云服务器或要求校园网络。

先通过 SSH 隧道验证，无需向公网开放 8000。在本机 PowerShell 中保持以下命令运行，再访问 `http://localhost:18000`：

```powershell
ssh -N -L 18000:127.0.0.1:8000 用户名@服务器IP
```

长期对外调用建议使用域名和 HTTPS 反向代理。如果反向代理运行在服务器宿主机，将 `docker/compose.yaml` 的端口映射改为 `127.0.0.1:8000:8000`，公网只开放所需的 HTTPS 端口；不要在公网明文 HTTP 中传输密钥。

修改账号或校历配置后重启：

```text
docker compose -f ZF-Schedule-Docker/docker/compose.yaml restart
```

更新代码并重新构建：

```text
git -C ZF-Schedule-Docker pull --ff-only
docker compose -f ZF-Schedule-Docker/docker/compose.yaml up -d --build
```

停止容器：

```text
docker compose -f ZF-Schedule-Docker/docker/compose.yaml down
```

不要在日常更新时添加 `down -v`，它会删除持久化 volume。容器配置了 `restart: unless-stopped`；Docker 服务开机启动后，未被手动停止的容器会恢复运行。

本项目用于本人授权的课表查询。请妥善保管账号、密钥和课程数据，并遵守学校的使用规定。
