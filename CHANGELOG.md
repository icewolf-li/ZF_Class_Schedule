# 更新日志

## v2.0.0 - Hermes Agent 插件支持

### 🎉 重大更新

#### Hermes Agent 插件
- 全新的 `hermes_plugin.py` 插件主文件
- 完整的插件清单文件 `plugin.json`
- 快速启动脚本 `hermes_quickstart.ps1`
- 详细的集成文档 `hermes_integration_example.md`

#### 表格视图生成
- 📅 美观的当前周课表表格视图
- 适配微信、QQ、钉钉、Telegram 等多平台
- 支持三种格式：table（表格）、simple（简化）、json（原始数据）
- 自动计算当前周次
- 智能解析周次范围（支持单双周）

#### 周次计算
- 根据学期开始日期自动计算当前周次
- 支持单双周课程过滤
- 智能节次范围解析

#### API 集成
- Python API 接口，方便程序化调用
- 配置管理功能
- 课表变化检测
- 错误处理和状态返回

### 新增功能

#### 插件命令
```bash
# 配置账号
hermes_plugin.py setup --username <学号> --password <密码> --base-url <URL>

# 获取课表
hermes_plugin.py get --format table

# 检查变化
hermes_plugin.py check
```

#### 配置文件
- `hermes_config.json` - 插件配置
- `hermes_config.example.json` - 配置示例

#### 文档
- Agent 提示词（README.md 顶部）
- Hermes Agent 集成示例
- 多平台适配指南
- API 使用说明

### 改进

- 更智能的登录状态管理
- 更友好的错误提示
- 更完善的测试用例
- 更详细的文档说明

---

## v1.0.0 - 支持服务器无头模式

### 支持服务器无头模式

现在支持三种登录方式，可以在没有图形界面的服务器上运行：

1. **配置文件模式**（推荐）
   - 从 JSON 文件读取账号密码
   - 无需交互，适合定时任务
   - 示例：`--login --config config.json`

2. **交互式输入模式**
   - 在命令行中输入账号密码
   - 密码输入隐藏显示
   - 示例：`--login`（会提示输入）

3. **手动浏览器模式**（原方式）
   - 打开浏览器窗口手动登录
   - 适合自动登录失败的情况
   - 示例：`--login --manual`

### 自动登录功能

- 自动填写用户名和密码
- 自动点击登录按钮
- 支持多种常见的表单元素选择器
- 自动检测登录结果和错误信息

### 安全改进

- 新增 `.gitignore` 防止敏感信息提交
- 配置文件示例（`config.example.json`）
- 密码输入使用 `getpass` 模块隐藏显示

### 易用性提升

- 新增详细的 `README.md` 使用文档
- 新增 `setup.ps1` 一键初始化脚本
- 改进的命令行参数说明
- 更友好的错误提示

## 使用变化

### 原命令（需要手动登录）
```bash
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login
```
现在默认会提示输入账号密码，如果要使用原来的手动模式，需要添加 `--manual`：
```bash
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login --manual
```

### 推荐使用方式（配置文件）
```bash
# 首次登录
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/ --login --config config.json

# 后续查询
uv run python zf_schedule_monitor_uv.py --base-url https://jwxt.gxnzd.com.cn/
```

## 兼容性

- 向后兼容原有功能
- 已保存的登录状态和数据格式不变
- 旧的命令添加 `--manual` 参数即可使用原方式
