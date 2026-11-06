#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = ["playwright==1.58.0"]
# ///
"""正方教务课表抓取与快照比较，可直接通过 uv run 执行。

首次使用（交互输入账号密码，自动准备依赖与无头浏览器）：
  uv run --python 3.13.9 cli/zf_schedule_monitor_uv.py --install-browser --login --base-url https://jwxt.gxnzd.com.cn/jwglxt/

配置文件登录：添加 --config cli/config.json。
手动浏览器登录：添加 --manual，此时 --install-browser 会安装完整 Chromium。
离线验证：添加 --from-json 路径，无需访问学校。
默认数据目录：脚本所在目录下的 data/zf_schedule/。
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import getpass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.parse import urljoin

DEFAULT_ENDPOINT = "kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151"
# 保持原版快照字段不变，以便兼容旧 snapshot；不保存可能仅用于排版的 jcor。
FIELDS = (
    "kch_id", "kcmc", "jxbmc", "xqj", "jc", "jcs", "zcd",
    "cdmc", "xqmc", "xm", "khfsmc", "xkbz", "skfsmc",
)


def load_credentials(config_path: Path | None) -> tuple[str, str] | None:
    """从配置文件加载凭据，如果没有配置文件则返回 None。"""
    if config_path is None:
        return None

    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在：{config_path}")

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        username = config.get("username", "").strip()
        password = config.get("password", "").strip()

        if not username or not password:
            raise ValueError("配置文件必须包含 username 和 password 字段")

        return username, password
    except json.JSONDecodeError as exc:
        raise ValueError(f"配置文件格式错误：{exc}") from exc


def prompt_credentials() -> tuple[str, str]:
    """从命令行交互式获取凭据。"""
    print("请输入登录凭据：")
    username = input("学号: ").strip()
    password = getpass.getpass("密码: ").strip()

    if not username or not password:
        raise ValueError("学号和密码不能为空")

    return username, password


def auto_login(page, login_url: str, username: str, password: str) -> None:
    """自动登录正方教务系统。"""
    print(f"正在访问登录页面：{login_url}")
    page.goto(login_url, wait_until="domcontentloaded", timeout=45000)

    # 等待登录表单加载
    time.sleep(2)

    # 尝试多种常见的用户名和密码字段选择器
    username_selectors = [
        "input#yhm",
        "input[name='yhm']",
        "input#username",
        "input[name='username']",
        "input[type='text']",
    ]

    password_selectors = [
        "input#mm",
        "input[name='mm']",
        "input#password",
        "input[name='password']",
        "input[type='password']",
    ]

    # 填写用户名
    username_filled = False
    for selector in username_selectors:
        try:
            if page.locator(selector).count() > 0:
                page.fill(selector, username)
                print(f"已填写用户名（选择器：{selector}）")
                username_filled = True
                break
        except Exception:
            continue

    if not username_filled:
        raise RuntimeError("无法找到用户名输入框，请检查网页结构")

    # 填写密码
    password_filled = False
    for selector in password_selectors:
        try:
            if page.locator(selector).count() > 0:
                page.fill(selector, password)
                print(f"已填写密码（选择器：{selector}）")
                password_filled = True
                break
        except Exception:
            continue

    if not password_filled:
        raise RuntimeError("无法找到密码输入框，请检查网页结构")

    # 尝试点击登录按钮
    login_button_selectors = [
        "button#dl",
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('登录')",
        "input[value='登录']",
        "a:has-text('登录')",
    ]

    login_clicked = False
    for selector in login_button_selectors:
        try:
            if page.locator(selector).count() > 0:
                page.click(selector)
                print(f"已点击登录按钮（选择器：{selector}）")
                login_clicked = True
                break
        except Exception:
            continue

    if not login_clicked:
        raise RuntimeError("无法找到登录按钮，请检查网页结构")

    # auth_loginSuccess.html 是中间跳转，等待进入实际教务页面再继续请求。
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

    print("等待登录完成...")
    try:
        page.wait_for_url(
            lambda url: all(marker not in url.lower() for marker in ("login_slogin", "loginsuccess")),
            wait_until="domcontentloaded", timeout=15000,
        )
        login_failed = False
    except PlaywrightTimeoutError:
        login_failed = True

    if login_failed:
        # 检查是否有错误提示
        error_messages = []
        error_selectors = [
            "#tips",
            ".alert-danger",
            ".error",
            "[id*='error']",
            "[class*='error']",
        ]
        for selector in error_selectors:
            try:
                if page.locator(selector).count() > 0:
                    error_text = page.locator(selector).inner_text()
                    if error_text.strip():
                        error_messages.append(error_text.strip())
            except Exception:
                continue

        if error_messages:
            raise RuntimeError(f"登录失败：{'; '.join(error_messages)}")
        else:
            raise RuntimeError("登录可能失败（仍在登录页面），请检查账号密码或使用 --manual 手动登录")

    print("登录成功！")


def locate_project_root() -> Path:
    """单文件运行时始终以脚本目录为基准，不依赖外层 uv 项目。"""
    return Path(__file__).resolve().parent


def resolve_data_dir(project_root: Path, override: str | None) -> Path:
    if not override:
        return project_root / "data" / "zf_schedule"
    path = Path(override).expanduser()
    # 相对路径相对于调用方传入的模块目录，而不是当前工作目录
    return (path if path.is_absolute() else project_root / path).resolve()


def ensure_private_data_dir(data_dir: Path) -> None:
    """默认阻止浏览器 Cookie、学生信息与课程快照被 git 意外提交。"""
    data_dir.mkdir(parents=True, exist_ok=True)
    ignore_path = data_dir / ".gitignore"
    if not ignore_path.exists():
        ignore_path.write_text("*\n!.gitignore\n", encoding="utf-8")


def unwrap_response(data: object) -> tuple[dict, str | None]:
    """兼容接口原始 JSON 和本脚本生成的 {fetched_at, response} JSON。"""
    if not isinstance(data, dict):
        raise ValueError("JSON 顶层必须是对象")
    if "response" in data:
        raw = data["response"]
        if not isinstance(raw, dict):
            raise ValueError("response 必须是对象，文件可能不是课表快照")
        return raw, data.get("fetched_at")
    return data, None


def normalize(raw: dict, *, allow_empty: bool = False) -> dict:
    rows = raw.get("kbList")
    if not isinstance(rows, list):
        raise ValueError("响应缺少 kbList 数组，可能登录失效或接口不匹配")
    if not rows and not allow_empty:
        raise ValueError("kbList 为空；为防止误判全部课程取消，本次不覆盖旧快照")

    courses = []
    for index, item in enumerate(rows, 1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index} 条课程不是对象")
        required = ("kcmc", "xqj", "jcs", "zcd")
        missing = [key for key in required if not str(item.get(key) or "").strip()]
        if missing:
            raise ValueError(f"第 {index} 条课程缺少关键字段：{', '.join(missing)}")
        courses.append({key: str(item.get(key) or "").strip() for key in FIELDS})
    courses.sort(key=lambda row: json.dumps(row, sort_keys=True, ensure_ascii=False))

    sjk_list = raw.get("sjkList", [])
    if not isinstance(sjk_list, list):
        raise ValueError("sjkList 不是数组")
    other = sorted(str(item["qtkcgs"]).strip() for item in sjk_list
                   if isinstance(item, dict) and item.get("qtkcgs"))
    return {"courses": courses, "other_courses": other}


def verify_semester(raw: dict, year: str, term: str) -> None:
    """阻止其他学期的数据写入指定学期的文件。"""
    student = raw.get("xsxx")
    if isinstance(student, dict):
        if student.get("XNM") and str(student["XNM"]) != year:
            raise ValueError(f"JSON 学年 {student['XNM']} 与 --year {year} 不一致")
        if student.get("XQM") and str(student["XQM"]) != term:
            raise ValueError(f"JSON 学期 {student['XQM']} 与 --term {term} 不一致")


def course_desc(row: dict) -> str:
    section = row.get("jcs") or row.get("jc", "?").removesuffix("节")
    return (f"{row.get('kcmc') or '未命名'} | 星期{row.get('xqj') or '?'} "
            f"第{section}节 | {row.get('zcd') or '?'} | "
            f"{row.get('cdmc') or '地点未知'} | {row.get('xm') or '教师未知'}")


def _as_count(rows: list[dict]) -> Counter:
    return Counter(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows)


def atomic_write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp",
                                         delete=False) as handle:
            temp_path = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def report_and_save(raw: dict, year: str, term: str, data_dir: Path,
                    fetched_at: str | None = None) -> int:
    verify_semester(raw, year, term)
    new = normalize(raw)  # 验证通过才开始操作磁盘
    ensure_private_data_dir(data_dir)
    snapshot = data_dir / f"snapshot_{year}_{term}.json"
    latest = data_dir / f"latest_raw_{year}_{term}.json"
    changed = False
    if snapshot.exists():
        old = json.loads(snapshot.read_text(encoding="utf-8-sig"))
        if not isinstance(old, dict) or not isinstance(old.get("courses"), list):
            raise ValueError("旧快照格式无效，请人工检查（未覆盖）")
        removed = _as_count(old["courses"]) - _as_count(new["courses"])
        added = _as_count(new["courses"]) - _as_count(old["courses"])
        old_other = Counter(old.get("other_courses", []))
        new_other = Counter(new["other_courses"])
        changed = bool(removed or added or old_other != new_other)
        if not changed:
            print("课表无变化（已核对完整课程记录及其他课程）")
        else:
            print(f"课表有变化：删除/修改前 {sum(removed.values())} 条；新增/修改后 {sum(added.values())} 条")
            for encoded, count in removed.items():
                for _ in range(count):
                    print("  -", course_desc(json.loads(encoded)))
            for encoded, count in added.items():
                for _ in range(count):
                    print("  +", course_desc(json.loads(encoded)))
            if old_other != new_other:
                print("  其他课程变化：", new["other_courses"])
            # 留存变动前的快照，便于回溯被调走的课
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            history = data_dir / "history" / f"snapshot_{year}_{term}_{stamp}.json"
            history.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(snapshot, history)
            print("已备份变更前快照：", history)
    else:
        print(f"已建立首次课表基线：{len(new['courses'])} 条记录，"
              f"{len({item['kcmc'] for item in new['courses']})} 种课程，"
              f"另有 {len(new['other_courses'])} 条其他课程")
        for row in new["courses"][:8]:
            print("  ", course_desc(row))

    # 先写原始响应、最后提交快照：任何失败都不应令快照指向未保存的数据
    atomic_write_json(latest, {
        "fetched_at": fetched_at or datetime.now(timezone.utc).isoformat(),
        "response": raw,
    })
    atomic_write_json(snapshot, new)
    print("课表数据目录：", data_dir)
    print("原始响应：", latest.name)
    print("标准化快照：", snapshot.name)
    return 0


def fetch_from_school(args: argparse.Namespace, data_dir: Path,
                      credentials: tuple[str, str] | None = None) -> dict:
    # 只在抓取网络时需要 Playwright，离线验证 JSON 无需安装依赖
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("缺少 playwright，请通过 uv run 执行本脚本以安装声明的依赖") from exc

    base = args.base_url.rstrip("/") + "/"
    endpoint = args.endpoint
    endpoint_url = endpoint if endpoint.startswith(("https://", "http://")) else urljoin(base, endpoint.lstrip("/"))
    login_url = args.login_url or urljoin(base, "xtgl/login_slogin.html")
    ensure_private_data_dir(data_dir)
    profile = data_dir / "browser-profile"

    # API 可直接传入凭据；原有 CLI 仍使用配置文件或交互输入。
    if args.login and credentials is None:
        if args.manual:
            # 手动登录模式（原方式）
            credentials = None
        elif args.config:
            # 从配置文件读取
            credentials = load_credentials(args.config)
            print(f"已从配置文件加载凭据：{args.config}")
        else:
            # 命令行交互式输入
            credentials = prompt_credentials()

    with sync_playwright() as playwright:
        # 根据登录方式决定是否使用无头模式
        headless = not args.manual if args.login else True

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile), headless=headless,
        )
        try:
            if args.login:
                page = context.new_page()
                if args.manual:
                    # 手动登录模式
                    page.goto(login_url, wait_until="domcontentloaded", timeout=45000)
                    print("请在浏览器里完成你本人账号的登录。")
                    input("成功进入教务系统后，在终端按 Enter 查询课程... ")
                elif credentials:
                    # 自动登录模式
                    username, password = credentials
                    auto_login(page, login_url, username, password)
                else:
                    raise RuntimeError("未提供登录凭据")

            payload = {"xnm": args.year, "xqm": args.term}
            if "cxXsgrkb" in endpoint_url:
                payload["kzlx"] = "ck"
            response = context.request.post(
                endpoint_url,
                form=payload,
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": urljoin(base, "kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N2151"),
                },
                timeout=30000,
            )
            if not response.ok:
                raise RuntimeError(f"接口 HTTP {response.status}；请检查登录与 --endpoint")
            try:
                result = response.json()
            except Exception as exc:
                raise RuntimeError("接口未返回 JSON，登录可能过期；尝试 --login，或检查接口路径") from exc
            if not isinstance(result, dict):
                raise ValueError("接口返回的 JSON 顶层不是对象")
            return result
        finally:
            context.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="正方教务个人课表抓取、验证和变化检测（单文件 uv run）")
    parser.add_argument("--base-url", help="教务系统基础地址，例如 https://jwxt.gxnzd.com.cn/")
    parser.add_argument("--login", action="store_true", help="执行登录操作（需配合 --config、--manual 或交互式输入）")
    parser.add_argument("--install-browser", action="store_true", help="抓取前安装 Chromium（首次运行使用）")
    parser.add_argument("--manual", action="store_true", help="手动浏览器登录（需配合 --login）")
    parser.add_argument("--config", type=Path, help="从 JSON 配置文件读取账号密码（推荐服务器使用）")
    parser.add_argument("--login-url", help="自定义学校统一身份认证入口")
    parser.add_argument("--year", default="2026", help="学年起始年，例如 2026 对应 2026-2027")
    parser.add_argument("--term", choices=("3", "12"), default="3", help="3=第一学期，12=第二学期")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="课程 API 相对路径或完整 URL")
    parser.add_argument("--from-json", type=Path, help="离线导入原始接口响应或本脚本生成的包装 JSON")
    parser.add_argument("--data-dir", help="可选保存位置；相对路径以脚本目录为基准")
    args = parser.parse_args()
    if args.from_json is None and not args.base_url:
        parser.error("必须提供 --base-url 或 --from-json")
    if args.manual and not args.login:
        parser.error("--manual 必须配合 --login 使用")
    if args.config and not args.login:
        parser.error("--config 必须配合 --login 使用")
    if args.config and args.manual:
        parser.error("--config 和 --manual 不能同时使用")
    if args.login and args.from_json is not None:
        parser.error("--login 与 --from-json 不能同时使用")
    project_root = locate_project_root()
    data_dir = resolve_data_dir(project_root, args.data_dir)
    print("识别到的项目根目录：", project_root)
    try:
        if args.from_json is not None:
            src = json.loads(args.from_json.read_text(encoding="utf-8-sig"))
            raw, fetched_at = unwrap_response(src)
        else:
            if args.install_browser:
                command = [sys.executable, "-m", "playwright", "install"]
                if not args.manual:
                    command.append("--only-shell")
                subprocess.run([*command, "chromium"], check=True)
            raw, fetched_at = fetch_from_school(args, data_dir), None
        return report_and_save(raw, args.year, args.term, data_dir, fetched_at)
    except Exception as exc:
        print(f"未更新课表快照：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
