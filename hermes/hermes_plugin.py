#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = ["playwright==1.58.0"]
# ///
"""正方教务课表 Hermes Agent 插件

这是一个 Hermes Agent 插件，用于查询正方教务系统的个人课程表。
支持自动登录、课表变化检测、表格视图生成等功能。

插件功能：
1. 配置账号密码和教务系统 URL
2. 自动登录并获取课表
3. 生成当前周的表格视图（适配微信、QQ 等平台）
4. 检测课表变化并通知
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import re

MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR.parent / "cli"))


def get_current_week(start_date: str) -> int:
    """计算当前是第几周（从学期开始日期算起）"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        today = datetime.now()
        delta = today - start
        week = (delta.days // 7) + 1
        return max(1, week)
    except Exception:
        return 1


def parse_week_range(zcd: str) -> List[int]:
    """解析周次字符串，例如 '1-16周' 或 '1,3,5,7-9周(单)' """
    weeks = []
    if not zcd:
        return weeks

    # 移除 '周' 字
    zcd = zcd.replace('周', '')

    # 检查是否有单双周标记
    is_odd = '单' in zcd
    is_even = '双' in zcd
    zcd = zcd.replace('(单)', '').replace('(双)', '').replace('（单）', '').replace('（双）', '')

    # 分割逗号
    parts = zcd.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            # 范围，例如 '1-16'
            try:
                start, end = part.split('-')
                for w in range(int(start), int(end) + 1):
                    if is_odd and w % 2 == 0:
                        continue
                    if is_even and w % 2 == 1:
                        continue
                    weeks.append(w)
            except ValueError:
                continue
        else:
            # 单个周次
            try:
                w = int(part)
                if is_odd and w % 2 == 0:
                    continue
                if is_even and w % 2 == 1:
                    continue
                weeks.append(w)
            except ValueError:
                continue

    return sorted(set(weeks))


def parse_section_range(jcs: str) -> List[int]:
    """解析节次字符串，例如 '1-2' 或 '3' """
    sections = []
    if not jcs:
        return sections

    if '-' in jcs:
        try:
            start, end = jcs.split('-')
            sections = list(range(int(start), int(end) + 1))
        except ValueError:
            pass
    else:
        try:
            sections = [int(jcs)]
        except ValueError:
            pass

    return sections


def generate_week_table(courses: List[Dict[str, Any]], current_week: int) -> str:
    """生成当前周的课表（文本表格格式，适合微信/QQ展示）"""
    # 初始化课表网格 [节次][星期几]
    # 节次：1-12（每天最多12节课）
    # 星期：1-7
    grid = [[None for _ in range(8)] for _ in range(13)]  # 0索引不使用，1-12节，1-7星期

    # 填充课表
    for course in courses:
        try:
            xqj = int(course.get('xqj', 0))  # 星期几
            if xqj < 1 or xqj > 7:
                continue

            # 检查这门课是否在当前周
            zcd = course.get('zcd', '')
            weeks = parse_week_range(zcd)
            if current_week not in weeks:
                continue

            # 获取节次
            jcs = course.get('jcs', course.get('jc', ''))
            sections = parse_section_range(jcs)

            # 课程信息
            course_info = {
                'name': course.get('kcmc', '未命名'),
                'location': course.get('cdmc', ''),
                'teacher': course.get('xm', ''),
                'weeks': zcd,
                'sections': jcs
            }

            # 填入网格（多节次的课程会占用多行）
            for section in sections:
                if 1 <= section <= 12:
                    if grid[section][xqj] is None:
                        grid[section][xqj] = course_info
        except Exception:
            continue

    # 生成文本表格
    lines = []
    lines.append("=" * 60)
    lines.append(f"📅 第 {current_week} 周课表")
    lines.append("=" * 60)
    lines.append("")

    weekdays = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']

    # 按节次分组显示（更紧凑）
    section_groups = [
        (1, 2, "上午 1-2节"),
        (3, 4, "上午 3-4节"),
        (5, 6, "下午 5-6节"),
        (7, 8, "下午 7-8节"),
        (9, 10, "晚上 9-10节"),
        (11, 12, "晚上 11-12节")
    ]

    for start_section, end_section, label in section_groups:
        has_course = False
        section_courses = {}

        # 收集这个时间段的所有课程
        for day in range(1, 8):
            for section in range(start_section, end_section + 1):
                if grid[section][day] is not None:
                    if day not in section_courses:
                        section_courses[day] = grid[section][day]
                    has_course = True
                    break  # 只取第一节（多节连上的课）

        if has_course:
            lines.append(f"\n【{label}】")
            lines.append("-" * 60)
            for day in range(1, 8):
                if day in section_courses:
                    info = section_courses[day]
                    lines.append(f"{weekdays[day]}:")
                    lines.append(f"  📖 {info['name']}")
                    if info['location']:
                        lines.append(f"  📍 {info['location']}")
                    if info['teacher']:
                        lines.append(f"  👨‍🏫 {info['teacher']}")

    if not any(any(cell for cell in row) for row in grid):
        lines.append("\n🎉 本周没有课程安排")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


def generate_simple_table(courses: List[Dict[str, Any]], current_week: int) -> str:
    """生成简化版课表（列表格式）"""
    lines = []
    lines.append(f"📅 第 {current_week} 周课表\n")

    # 按星期分组
    weekdays = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
    schedule_by_day = {i: [] for i in range(1, 8)}

    for course in courses:
        try:
            xqj = int(course.get('xqj', 0))
            if xqj < 1 or xqj > 7:
                continue

            # 检查周次
            zcd = course.get('zcd', '')
            weeks = parse_week_range(zcd)
            if current_week not in weeks:
                continue

            schedule_by_day[xqj].append(course)
        except Exception:
            continue

    for day in range(1, 8):
        if schedule_by_day[day]:
            lines.append(f"\n{weekdays[day]}:")
            lines.append("-" * 40)

            # 按节次排序
            schedule_by_day[day].sort(key=lambda c: int(c.get('jcs', c.get('jc', '99')).split('-')[0]))

            for course in schedule_by_day[day]:
                jcs = course.get('jcs', course.get('jc', ''))
                name = course.get('kcmc', '未命名')
                location = course.get('cdmc', '')
                teacher = course.get('xm', '')

                lines.append(f"  第{jcs}节 | {name}")
                if location:
                    lines.append(f"         📍 {location}")
                if teacher:
                    lines.append(f"         👨‍🏫 {teacher}")

    return "\n".join(lines)


class HermesPlugin:
    """Hermes Agent 插件主类"""

    def __init__(self, config_path: str | None = None):
        self.config_path = Path(config_path) if config_path else MODULE_DIR / "hermes_config.json"
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载插件配置"""
        if not self.config_path.exists():
            return {
                "username": "",
                "password": "",
                "base_url": "https://jwxt.gxnzd.com.cn/jwglxt/",
                "year": "2026",
                "term": "3",
                "semester_start_date": "2026-09-01"
            }

        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"加载配置失败: {e}", file=sys.stderr)
            return {}

    def save_config(self) -> None:
        """保存插件配置"""
        try:
            self.config_path.write_text(
                json.dumps(self.config, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"保存配置失败: {e}", file=sys.stderr)

    def setup(self, username: str, password: str, base_url: str,
              year: str = "2026", term: str = "3",
              semester_start_date: str = "2026-09-01") -> Dict[str, Any]:
        """配置插件"""
        self.config.update({
            "username": username,
            "password": password,
            "base_url": base_url.rstrip("/") + "/",
            "year": year,
            "term": term,
            "semester_start_date": semester_start_date
        })
        self.save_config()
        return {"status": "success", "message": "配置已保存"}

    def get_schedule(self, force_login: bool = False, format: str = "table") -> Dict[str, Any]:
        """获取课表

        Args:
            force_login: 是否强制重新登录
            format: 返回格式，'table' 表格视图, 'simple' 简化列表, 'json' 原始数据

        Returns:
            包含课表数据和格式化视图的字典
        """
        if not self.config.get("username") or not self.config.get("password"):
            return {
                "status": "error",
                "message": "请先配置账号密码：使用 setup 命令"
            }

        try:
            # 直接复用抓取函数，不再生成含密码的临时配置文件。
            credentials = (self.config["username"], self.config["password"])

            # 模拟命令行参数
            class Args:
                def __init__(self, config):
                    self.base_url = config["base_url"]
                    self.login = force_login
                    self.manual = False
                    self.config = None
                    self.year = config.get("year", "2026")
                    self.term = config.get("term", "3")
                    self.endpoint = "kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151"
                    self.login_url = None
                    self.from_json = None
                    self.data_dir = None

            args = Args(self.config)

            # 调用主脚本功能
            from zf_schedule_monitor_uv import fetch_from_school, normalize, atomic_write_json

            data_dir = MODULE_DIR / "data" / "zf_schedule"

            # 如果不是强制登录，先尝试使用已有 cookie
            if not force_login:
                # 检查是否有最新的快照
                latest_file = data_dir / f"latest_raw_{args.year}_{args.term}.json"
                if latest_file.exists():
                    try:
                        # 尝试用现有 cookie 获取（不登录）
                        args.login = False
                        raw = fetch_from_school(args, data_dir, credentials=credentials)
                    except Exception:
                        # Cookie 可能过期，重新登录
                        args.login = True
                        raw = fetch_from_school(args, data_dir, credentials=credentials)
                else:
                    # 首次使用，需要登录
                    args.login = True
                    raw = fetch_from_school(args, data_dir, credentials=credentials)
            else:
                raw = fetch_from_school(args, data_dir, credentials=credentials)

            # 保存前后两次标准化结果，供 check 比较变化。
            normalized = normalize(raw)
            latest_file = data_dir / f"latest_raw_{args.year}_{args.term}.json"
            snapshot_file = data_dir / f"snapshot_{args.year}_{args.term}.json"
            if latest_file.exists():
                previous = json.loads(latest_file.read_text(encoding="utf-8"))
                atomic_write_json(snapshot_file, previous)
            elif not snapshot_file.exists():
                atomic_write_json(snapshot_file, normalized)
            atomic_write_json(latest_file, normalized)
            courses = normalized["courses"]

            # 计算当前周
            current_week = get_current_week(self.config.get("semester_start_date", "2026-09-01"))

            # 生成格式化输出
            if format == "table":
                formatted_output = generate_week_table(courses, current_week)
            elif format == "simple":
                formatted_output = generate_simple_table(courses, current_week)
            else:
                formatted_output = json.dumps(normalized, ensure_ascii=False, indent=2)

            return {
                "status": "success",
                "current_week": current_week,
                "total_courses": len(courses),
                "formatted_output": formatted_output,
                "raw_data": normalized
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取课表失败: {str(e)}"
            }

    def check_changes(self) -> Dict[str, Any]:
        """检查课表变化"""
        try:
            data_dir = MODULE_DIR / "data" / "zf_schedule"

            year = self.config.get("year", "2026")
            term = self.config.get("term", "3")

            snapshot = data_dir / f"snapshot_{year}_{term}.json"
            latest = data_dir / f"latest_raw_{year}_{term}.json"

            if not snapshot.exists() or not latest.exists():
                return {
                    "status": "no_data",
                    "message": "暂无课表数据，请先获取课表"
                }

            # 读取快照
            old_data = json.loads(snapshot.read_text(encoding="utf-8"))
            latest_data = json.loads(latest.read_text(encoding="utf-8"))

            # 简单比较（实际可以更详细）
            old_courses = set(json.dumps(c, sort_keys=True) for c in old_data.get("courses", []))
            new_courses = set(json.dumps(c, sort_keys=True) for c in latest_data.get("courses", []))

            if old_courses == new_courses:
                return {
                    "status": "no_change",
                    "message": "课表无变化"
                }
            else:
                added = len(new_courses - old_courses)
                removed = len(old_courses - new_courses)
                return {
                    "status": "changed",
                    "message": f"课表有变化：新增/修改 {added} 条，删除/修改前 {removed} 条",
                    "changes": {
                        "added": added,
                        "removed": removed
                    }
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"检查变化失败: {str(e)}"
            }


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description="正方教务课表 Hermes Agent 插件")
    parser.add_argument("command", choices=["setup", "get", "check"],
                       help="命令：setup=配置, get=获取课表, check=比较最近两次抓取")
    parser.add_argument("--username", help="学号")
    parser.add_argument("--password", help="密码")
    parser.add_argument("--base-url", help="教务系统URL")
    parser.add_argument("--year", default="2026", help="学年")
    parser.add_argument("--term", default="3", choices=["3", "12"], help="学期")
    parser.add_argument("--start-date", default="2026-09-01", help="学期开始日期")
    parser.add_argument("--force-login", action="store_true", help="强制重新登录")
    parser.add_argument("--format", default="table", choices=["table", "simple", "json"],
                       help="输出格式")

    args = parser.parse_args()

    plugin = HermesPlugin()

    if args.command == "setup":
        if not args.username or not args.password or not args.base_url:
            print("错误：setup 命令需要 --username, --password, --base-url 参数", file=sys.stderr)
            sys.exit(1)

        result = plugin.setup(
            args.username, args.password, args.base_url,
            args.year, args.term, args.start_date
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "get":
        result = plugin.get_schedule(args.force_login, args.format)
        if result["status"] == "success":
            print(result["formatted_output"])
            print(f"\n状态：成功 | 当前第 {result['current_week']} 周 | 共 {result['total_courses']} 门课程")
        else:
            print(f"错误：{result['message']}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "check":
        result = plugin.check_changes()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

