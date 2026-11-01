# 项目结构说明

```
ZF_Class_Schedule/
├── 📄 README.md                          # 主文档（包含 Agent 提示词）
├── 📄 HERMES_AGENT_PROMPT.md             # 完整的 Agent 提示词（可单独复制）
├── 📄 CHANGELOG.md                       # 更新日志
├── 📄 PROJECT_STRUCTURE.md               # 本文件：项目结构说明
│
├── 🔧 核心文件
│   ├── zf_schedule_monitor_uv.py         # 主爬虫脚本（原始功能）
│   ├── hermes_plugin.py                  # Hermes Agent 插件主文件
│   └── plugin.json                       # 插件清单（描述插件信息和命令）
│
├── 📋 配置文件
│   ├── config.example.json               # 原始脚本配置示例
│   └── hermes_config.example.json        # Hermes 插件配置示例
│
├── 🚀 启动脚本
│   ├── setup.ps1                         # 原始脚本初始化（Windows）
│   └── hermes_quickstart.ps1             # Hermes 插件快速启动（Windows）
│
├── 🧪 测试文件
│   └── test_plugin.py                    # 插件功能测试
│
├── 📚 文档
│   └── hermes_integration_example.md     # Hermes Agent 集成详细指南
│
├── 📁 数据目录（运行时生成，已加入 .gitignore）
│   └── data/
│       └── zf_schedule/
│           ├── browser-profile/          # 浏览器登录状态
│           ├── snapshot_<year>_<term>.json        # 课表快照
│           ├── latest_raw_<year>_<term>.json      # 最新原始数据
│           └── history/                  # 历史变更记录
│
└── 🔒 .gitignore                         # Git 忽略规则

生成的配置文件（不提交到 git）：
├── config.json                            # 原始脚本配置（敏感信息）
├── hermes_config.json                     # Hermes 插件配置（敏感信息）
└── temp_hermes_config.json               # 临时配置（自动清理）
```

## 文件说明

### 📄 文档类

#### README.md
- **用途**：项目主文档
- **包含**：
  - 🤖 Agent 提示词（顶部）
  - 功能特点说明
  - 安装使用指南
  - 原始脚本使用方法
  - Hermes 插件使用方法
  - 常见问题

#### HERMES_AGENT_PROMPT.md
- **用途**：完整的 Agent 提示词
- **特点**：可独立使用，直接复制粘贴给任何 AI Agent
- **包含**：
  - 详细的安装步骤
  - 配置流程说明
  - 使用示例
  - 错误处理指南
  - 智能问答示例

#### CHANGELOG.md
- **用途**：记录版本更新历史
- **内容**：
  - v2.0.0: Hermes Agent 插件支持
  - v1.0.0: 服务器无头模式支持

#### PROJECT_STRUCTURE.md
- **用途**：项目结构说明
- **内容**：本文件

#### hermes_integration_example.md
- **用途**：Hermes Agent 详细集成指南
- **包含**：
  - 插件注册方法
  - 用户交互流程
  - 多平台适配（微信/QQ/钉钉/Telegram）
  - API 集成示例
  - 错误处理
  - 高级功能（课程提醒、作业提醒等）
  - 部署建议
  - 安全建议

### 🔧 核心脚本

#### zf_schedule_monitor_uv.py
- **用途**：原始课表爬虫脚本
- **功能**：
  - 登录正方教务系统
  - 获取课表数据
  - 检测课表变化
  - 保存快照和历史
- **使用方式**：
  ```bash
  # 配置文件方式
  uv run python zf_schedule_monitor_uv.py --base-url <URL> --login --config config.json
  
  # 交互式输入
  uv run python zf_schedule_monitor_uv.py --base-url <URL> --login
  
  # 手动浏览器
  uv run python zf_schedule_monitor_uv.py --base-url <URL> --login --manual
  ```

#### hermes_plugin.py
- **用途**：Hermes Agent 插件主文件
- **功能**：
  - 配置管理（setup）
  - 课表查询（get）
  - 变化检测（check）
  - 表格视图生成
  - 周次计算
- **核心函数**：
  - `HermesPlugin` 类：插件主类
  - `generate_week_table()`: 生成表格视图
  - `generate_simple_table()`: 生成简化列表
  - `parse_week_range()`: 解析周次范围
  - `parse_section_range()`: 解析节次范围
  - `get_current_week()`: 计算当前周次
- **使用方式**：
  ```bash
  # 配置
  uv run python hermes_plugin.py setup --username <学号> --password <密码> --base-url <URL>
  
  # 查询
  uv run python hermes_plugin.py get --format table
  
  # 检查
  uv run python hermes_plugin.py check
  ```

#### plugin.json
- **用途**：插件清单文件
- **格式**：JSON
- **内容**：
  - 插件元信息（名称、版本、描述）
  - 命令定义
  - 参数说明
  - 使用示例
  - 依赖列表
  - 安装步骤

### 📋 配置文件

#### config.example.json
- **用途**：原始脚本配置模板
- **字段**：
  - `username`: 学号
  - `password`: 密码
  - `base_url`: 教务系统 URL

#### hermes_config.example.json
- **用途**：Hermes 插件配置模板
- **字段**：
  - `username`: 学号
  - `password`: 密码
  - `base_url`: 教务系统 URL
  - `year`: 学年
  - `term`: 学期
  - `semester_start_date`: 学期开始日期

### 🚀 启动脚本

#### setup.ps1
- **用途**：原始脚本初始化向导（Windows PowerShell）
- **功能**：
  - 检查依赖（uv、playwright）
  - 安装依赖
  - 创建配置文件
  - 首次登录测试
  - 显示使用说明

#### hermes_quickstart.ps1
- **用途**：Hermes 插件快速启动（Windows PowerShell）
- **功能**：
  - 检查环境
  - 安装依赖
  - 配置插件
  - 测试查询
  - 显示使用说明

### 🧪 测试文件

#### test_plugin.py
- **用途**：插件功能单元测试
- **测试项**：
  - 周次解析（`test_parse_week_range()`）
  - 节次解析（`test_parse_section_range()`）
  - 当前周计算（`test_get_current_week()`）
  - 表格生成（`test_table_generation()`）
- **使用方式**：
  ```bash
  python test_plugin.py
  ```

### 🔒 安全文件

#### .gitignore
- **用途**：防止敏感信息提交到 git
- **忽略内容**：
  - 配置文件（含密码）
  - 数据目录
  - Python 缓存
  - IDE 配置
  - 日志文件

## 使用流程

### 方式 1：原始脚本

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/ZF_Class_Schedule.git
cd ZF_Class_Schedule

# 2. 运行初始化脚本（Windows）
.\setup.ps1

# 或手动配置（Linux/Mac）
uv add playwright
uv run playwright install chromium
cp config.example.json config.json
# 编辑 config.json

# 3. 首次登录
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login --config config.json

# 4. 后续查询
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/
```

### 方式 2：Hermes Agent 插件

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/ZF_Class_Schedule.git
cd ZF_Class_Schedule

# 2. 运行快速启动脚本（Windows）
.\hermes_quickstart.ps1

# 或手动配置（Linux/Mac）
uv add playwright
uv run playwright install chromium
uv run python hermes_plugin.py setup --username <学号> --password <密码> --base-url <URL>

# 3. 查询课表
uv run python hermes_plugin.py get --format table

# 4. 检查变化
uv run python hermes_plugin.py check
```

### 方式 3：通过 AI Agent

直接将 `HERMES_AGENT_PROMPT.md` 的内容复制粘贴给任何 AI Agent（ChatGPT、Claude、Hermes Agent 等），Agent 会自动帮你完成安装、配置和使用。

## 输出格式

### 表格视图（--format table）
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
...
```

### 简化列表（--format simple）
```
📅 第 5 周课表

周一:
----------------------------------------
  第1-2节 | 高等数学
         📍 教学楼A101
         👨‍🏫 张老师
...
```

### JSON 数据（--format json）
```json
{
  "courses": [
    {
      "kch_id": "...",
      "kcmc": "高等数学",
      "xqj": "1",
      "jcs": "1-2",
      "zcd": "1-16周",
      "cdmc": "教学楼A101",
      "xm": "张老师",
      ...
    }
  ],
  "other_courses": []
}
```

## 数据存储

### 目录结构
```
data/zf_schedule/
├── browser-profile/              # Chromium 浏览器配置和 Cookie
│   ├── Default/
│   └── ...
├── snapshot_2026_3.json          # 2026 学年第一学期快照
├── latest_raw_2026_3.json        # 最新原始数据
└── history/                      # 历史变更记录
    ├── snapshot_2026_3_20261101T120000000000Z.json
    └── ...
```

### 数据文件说明

#### snapshot_<year>_<term>.json
- **格式**：标准化的课表快照
- **结构**：
  ```json
  {
    "courses": [...],      // 课程列表
    "other_courses": [...]  // 其他课程
  }
  ```
- **用途**：用于变化检测

#### latest_raw_<year>_<term>.json
- **格式**：包装的原始 API 响应
- **结构**：
  ```json
  {
    "fetched_at": "2026-11-01T12:00:00Z",
    "response": {
      "kbList": [...],
      "sjkList": [...],
      "xsxx": {...}
    }
  }
  ```
- **用途**：保留完整数据，便于调试

#### history/snapshot_<year>_<term>_<timestamp>.json
- **格式**：历史快照
- **命名**：时间戳采用 ISO 8601 格式（UTC）
- **用途**：追溯课表变更历史

## 依赖管理

### Python 包
- `playwright>=1.40.0`: 浏览器自动化
- `python>=3.13`: Python 运行时

### 系统依赖
- `uv`: Python 包管理器
- `chromium`: 浏览器（通过 playwright 安装）

### 安装命令
```bash
# 安装 uv（如果没有）
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 Python 包
uv add playwright

# 安装浏览器
uv run playwright install chromium
```

## 开发指南

### 添加新功能

1. 在 `hermes_plugin.py` 中添加新方法
2. 在 `plugin.json` 中注册新命令
3. 更新 `README.md` 文档
4. 添加测试用例到 `test_plugin.py`
5. 更新 `CHANGELOG.md`

### 测试流程

```bash
# 1. 语法检查
python -m py_compile hermes_plugin.py

# 2. 单元测试
python test_plugin.py

# 3. 集成测试
python hermes_plugin.py test

# 4. 完整流程测试
.\hermes_quickstart.ps1
```

### 提交代码

```bash
# 1. 确保敏感信息不被提交
git status
# 检查是否有 config.json、hermes_config.json 等文件

# 2. 添加改动
git add .

# 3. 提交（使用中文 commit 信息）
git commit -m "添加新功能：xxx"

# 4. 推送
git push origin main
```

## 常见问题

### 问：为什么有两个脚本？
答：`zf_schedule_monitor_uv.py` 是原始功能脚本，适合直接使用；`hermes_plugin.py` 是为 Hermes Agent 设计的插件接口，提供更友好的 API 和表格视图。

### 问：配置文件的区别？
答：`config.json` 给原始脚本用，只包含基本登录信息；`hermes_config.json` 给插件用，包含额外的学期信息用于计算周次。

### 问：数据保存在哪里？
答：默认保存在 `data/zf_schedule/` 目录，该目录已加入 `.gitignore`，不会被提交到 git。

### 问：如何备份数据？
答：直接复制 `data/` 目录即可。

### 问：支持多账号吗？
答：当前不支持。如需多账号，可以部署多个项目副本。

### 问：如何贡献代码？
答：欢迎提交 Pull Request 到 GitHub 仓库。

## 许可证

MIT License - 详见仓库中的 LICENSE 文件

## 联系方式

- GitHub Issues: https://github.com/yourusername/ZF_Class_Schedule/issues
- Discussions: https://github.com/yourusername/ZF_Class_Schedule/discussions
