"""单账号课表 API：自动学期、按日/周查询、密钥鉴权及内存缓存。"""

import argparse
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from functools import partial
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import math
import os
from pathlib import Path
import sys
import threading
import time
from urllib.parse import parse_qs, urlsplit

# 源码目录中复用 cli；镜像内三个脚本位于同一目录。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cli"))

from schedule_calendar import AcademicCalendar, Semester, courses_on, monday, parse_date, today_in_china
from zf_schedule_monitor_uv import (
    DEFAULT_ENDPOINT, fetch_from_school, normalize, prompt_credentials,
    resolve_data_dir, verify_semester,
)

LOGGER = logging.getLogger(__name__)


def load_settings(config_path: Path, interactive: bool = False) -> dict:
    """环境变量优先于 JSON；服务运行期间不再要求终端输入。"""
    config = {}
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        if not isinstance(config, dict):
            raise ValueError("配置文件顶层必须是对象")
    defaults = {
        "username": "", "password": "", "base_url": "", "api_key": "",
        "enrollment_year": "", "teaching_weeks": 20, "calendar": {}, "cache_ttl": 3600,
        "host": "0.0.0.0", "port": 8000, "data_dir": "data/zf_schedule_api",
    }
    settings = {key: os.environ.get(f"ZF_{key.upper()}", config.get(key, default))
                for key, default in defaults.items()}
    for key in ("username", "password", "base_url", "api_key", "host", "data_dir"):
        settings[key] = str(settings[key]) if settings[key] is not None else ""
    if interactive:
        settings["username"], settings["password"] = prompt_credentials()
    for key in ("username", "password", "base_url", "api_key", "host", "data_dir", "enrollment_year"):
        if not str(settings[key] or "").strip():
            raise ValueError(f"缺少配置 {key}，请设置 ZF_{key.upper()} 或配置文件；API 已改为通过入学年份自动判断学期")
    if urlsplit(settings["base_url"]).scheme not in ("http", "https") or not urlsplit(settings["base_url"]).hostname:
        raise ValueError("base_url 必须是完整的 HTTP/HTTPS 地址，包含学校应用路径")
    if isinstance(settings["calendar"], str):
        settings["calendar"] = json.loads(settings["calendar"])
    try:
        for key in ("enrollment_year", "teaching_weeks", "port"):
            if not str(settings[key]).isascii() or not str(settings[key]).isdigit():
                raise ValueError(f"{key} 必须是整数")
            settings[key] = int(settings[key])
        settings["cache_ttl"] = float(settings["cache_ttl"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"数值配置无效：{exc}") from exc
    if not math.isfinite(settings["cache_ttl"]) or settings["cache_ttl"] < 0:
        raise ValueError("cache_ttl 必须是大于等于 0 的有限秒数")
    if not 1 <= settings["port"] <= 65535:
        raise ValueError("port 必须在 1 到 65535 之间")
    AcademicCalendar(settings)  # 校历在启动时校验，避免请求期间才发现错误。
    return settings


def fetch_schedule(settings: dict, year: str, term: str) -> dict:
    """每次刷新均无头登录，避免依赖可能过期的 session cookie。"""
    args = argparse.Namespace(
        base_url=settings["base_url"], year=year, term=term,
        endpoint=DEFAULT_ENDPOINT, login_url=None, login=True, manual=False, config=None,
    )
    return fetch_from_school(
        args, resolve_data_dir(Path(__file__).resolve().parent, settings["data_dir"]),
        credentials=(settings["username"], settings["password"]),
    )


class ScheduleCache:
    def __init__(self, settings: dict, fetcher=None, clock=time.monotonic):
        self.settings = settings
        self.fetcher = fetcher or partial(fetch_schedule, settings)
        self.clock = clock
        self.lock = threading.Lock()
        self.entries = OrderedDict()

    def get(self, semester: Semester, force: bool = False) -> dict:
        key = (str(semester.year), semester.term)
        # 所有学期共用抓取锁：persistent profile 不能并发打开。
        with self.lock:
            entry = self.entries.get(key)
            if not force and entry is not None and self.clock() < entry[1]:
                self.entries.move_to_end(key)
                return {**entry[0], "cached": True}
            raw = self.fetcher(*key)
            verify_semester(raw, *key)
            result = normalize(raw, allow_empty=True)
            value = {"year": key[0], "term": key[1],
                     "fetched_at": datetime.now(timezone.utc).isoformat(), **result}
            # 只有抓取与验证成功才替换对应学期缓存。
            self.entries[key] = (value, self.clock() + self.settings["cache_ttl"])
            self.entries.move_to_end(key)
            while len(self.entries) > 8:
                self.entries.popitem(last=False)
            return {**value, "cached": False}


class ScheduleService:
    ROUTES = {"/schedule", "/schedule/latest", "/schedule/today", "/schedule/date", "/schedule/week"}

    def __init__(self, cache: ScheduleCache, today=today_in_china):
        self.cache = cache
        self.calendar = AcademicCalendar(cache.settings)
        self.today = today

    def query(self, path: str, params: dict[str, list[str]]) -> dict:
        allowed = {"refresh"}
        if path in ("/schedule", "/schedule/latest", "/schedule/date", "/schedule/week"):
            allowed.add("date")
        if path == "/schedule/week":
            allowed.add("week")
        if set(params) - allowed or any(len(values) != 1 for values in params.values()):
            raise QueryError("查询参数无效或重复")
        if "date" in params and "week" in params:
            raise QueryError("date 和 week 不能同时指定")
        if path == "/schedule/date" and "date" not in params:
            raise QueryError("请传入 date=YYYY-MM-DD；date=null 表示无课")
        refresh = params.get("refresh", ["false"])[0].lower()
        if refresh not in ("true", "false", "1", "0"):
            raise QueryError("refresh 必须为 true/false 或 1/0")
        force = path == "/schedule/latest" or refresh in ("true", "1")
        value = self.today()
        if "date" in params:
            text = params["date"][0]
            try:
                value = None if text.lower() in ("null", "") else parse_date(text)
            except ValueError as exc:
                raise QueryError(str(exc)) from exc
        week = None
        if "week" in params:
            text = params["week"][0]
            if text.lower() not in ("null", ""):
                if not text.isascii() or not text.isdigit() or not 1 <= int(text) <= 53:
                    raise QueryError("week 必须是 1 到 53 的整数，表示本学期教学周")
                week = int(text)
            else:
                value = None
        semester = self.calendar.semester_for(value)
        is_week = path == "/schedule/week"
        is_day = path in ("/schedule/today", "/schedule/date")
        result = {
            "year": None, "term": None, "grade": None, "semester_index": None,
            "semester_name": None, "semester_start": None, "semester_end": None,
            "week": None, "date": value.isoformat() if value else None,
            "courses": [], "other_courses": [], "fetched_at": None, "cached": False,
            "message": "无课",
        }
        if is_week:
            result.update(start_date=None, end_date=None, days=[])
        if semester is None:
            if is_week and value is not None:
                start = monday(value)
                result.update(start_date=start.isoformat(), end_date=(start + timedelta(days=6)).isoformat(),
                              days=[self.empty_day(start + timedelta(days=i)) for i in range(7)])
            return result
        result.update(semester.metadata())
        target_week = week if week is not None else semester.week_for(value)
        result["week"] = target_week
        if is_week:
            start = semester.week_start + timedelta(weeks=target_week - 1)
            result.update(start_date=start.isoformat(), end_date=(start + timedelta(days=6)).isoformat())
            if target_week > semester.weeks:
                result["days"] = [self.empty_day(start + timedelta(days=i)) for i in range(7)]
                return result
        raw = self.cache.get(semester, force=force)
        result.update(raw)
        if is_day:
            result["courses"] = courses_on(raw["courses"], semester, value)
            result["other_courses"] = []  # 没有明确日期的实践课不能算入某一天。
        elif is_week:
            days = []
            for offset in range(7):
                current = start + timedelta(days=offset)
                courses = courses_on(raw["courses"], semester, current)
                day = self.empty_day(current)
                day.update(courses=courses, message="有课" if courses else "无课")
                days.append(day)
            result["days"] = days
            result["courses"] = [row for day in days for row in day["courses"]]
            result["other_courses"] = []
        result["message"] = "有课" if result["courses"] or result["other_courses"] else "无课"
        return result

    @staticmethod
    def empty_day(value):
        return {"date": value.isoformat(), "weekday": value.isoweekday(), "courses": [], "message": "无课"}


class ScheduleHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, service: ScheduleService, **kwargs):
        self.service = service
        super().__init__(*args, **kwargs)

    def send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        supplied = self.headers.get_all("X-API-Key", [])
        expected = self.service.cache.settings["api_key"].encode("utf-8")
        if len(supplied) != 1 or not hmac.compare_digest(supplied[0].encode("utf-8"), expected):
            self.send_json(401, {"error": "API 密钥无效"})
            return
        path = urlsplit(self.path)
        if path.path not in self.service.ROUTES:
            self.send_json(404, {"error": "接口不存在"})
            return
        try:
            try:
                params = parse_qs(path.query, keep_blank_values=True, max_num_fields=8)
            except ValueError as exc:
                raise QueryError("查询参数数量过多") from exc
            # 参数错误属于 400；教务返回数据验证错误仍属于 502。
            result = self.service.query(path.path, params)
        except QueryError as exc:
            self.send_json(400, {"error": str(exc)})
            return
        except Exception:
            LOGGER.exception("课表抓取失败")
            self.send_json(502, {"error": "课表抓取失败，请检查服务日志、账号及教务系统状态"})
            return
        self.send_json(200, result)

    def log_message(self, format, *args):
        LOGGER.info("客户端 %s 请求完成", self.client_address[0])


class QueryError(ValueError):
    """与教务系统无关的请求参数错误。"""


def create_server(settings: dict, cache: ScheduleCache | None = None) -> ThreadingHTTPServer:
    handler = partial(ScheduleHandler, service=ScheduleService(cache or ScheduleCache(settings)))
    return ThreadingHTTPServer((settings["host"], settings["port"]), handler)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"), help="JSON 配置文件，默认脚本同目录的 config.json")
    parser.add_argument("--interactive", action="store_true", help="启动时交互输入账号密码")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        settings = load_settings(args.config, args.interactive)
        server = create_server(settings)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    LOGGER.info("课表 API 启动：%s:%s，入学年份 %s，缓存 %s 秒", settings["host"], settings["port"],
                settings["enrollment_year"], settings["cache_ttl"])
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
