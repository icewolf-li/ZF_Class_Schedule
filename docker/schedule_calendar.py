"""学期校历和课程周次解析；不依赖宿主系统的时区或第三方库。"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import re

CHINA_TIME = timezone(timedelta(hours=8))


def today_in_china() -> date:
    return datetime.now(CHINA_TIME).date()


def parse_date(value: str) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("日期必须使用 YYYY-MM-DD 格式")
    try:
        result = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("日期不存在，请检查月份与日期") from exc
    if not 1901 <= result.year <= 9997:
        raise ValueError("日期年份必须在 1901 到 9997 之间")
    return result


def monday(value: date) -> date:
    return value - timedelta(days=value.weekday())


@dataclass(frozen=True)
class Semester:
    year: int
    term: str
    start: date
    end: date
    enrollment_year: int

    @property
    def week_start(self) -> date:
        return monday(self.start)

    @property
    def weeks(self) -> int:
        return (self.end - self.week_start).days // 7 + 1

    def week_for(self, value: date) -> int | None:
        if self.start <= value <= self.end:
            return (value - self.week_start).days // 7 + 1
        return None

    def metadata(self) -> dict:
        grade = self.year - self.enrollment_year + 1
        grade_name = {1: "大一", 2: "大二", 3: "大三", 4: "大四"}.get(grade, f"{grade}年级")
        return {
            "year": str(self.year), "term": self.term, "grade": grade,
            "semester_index": (grade - 1) * 2 + (1 if self.term == "3" else 2),
            "semester_name": grade_name + ("上学期" if self.term == "3" else "下学期"),
            "semester_start": self.start.isoformat(), "semester_end": self.end.isoformat(),
        }


class AcademicCalendar:
    def __init__(self, settings: dict):
        self.enrollment_year = int(settings["enrollment_year"])
        self.teaching_weeks = int(settings.get("teaching_weeks", 20))
        if not 1901 <= self.enrollment_year <= 9996:
            raise ValueError("enrollment_year 必须在 1901 到 9996 之间")
        if not 1 <= self.teaching_weeks <= 25:
            raise ValueError("teaching_weeks 必须在 1 到 25 之间，避免默认春秋学期重叠")
        overrides = settings.get("calendar", {})
        if not isinstance(overrides, dict):
            raise ValueError("calendar 必须是对象，使用 YYYY-3 或 YYYY-12 作为键")
        self.overrides = {}
        for key, value in overrides.items():
            match = re.fullmatch(r"(\d{4})-(3|12)", key)
            if not match or not 1901 <= int(match[1]) <= 9996:
                raise ValueError(f"calendar 学期键无效：{key}")
            year, term = int(match[1]), match[2]
            if value is None:
                self.overrides[year, term] = None
                continue
            if not isinstance(value, dict) or "start_date" not in value:
                raise ValueError(f"calendar.{key} 必须包含 start_date，或设置为 null")
            if value["start_date"] is None:
                self.overrides[year, term] = None
                continue
            start = parse_date(str(value["start_date"]))
            end = (parse_date(str(value["end_date"])) if value.get("end_date") is not None
                   else monday(start) + timedelta(weeks=self.teaching_weeks, days=-1))
            expected_year = year if term == "3" else year + 1
            if start.year != expected_year or end < start or (end - monday(start)).days >= 26 * 7:
                raise ValueError(f"calendar.{key} 起止日期无效或超过 26 个教学周")
            self.overrides[year, term] = Semester(year, term, start, end, self.enrollment_year)
        # 覆盖后的日期不能跨学期重叠，否则同一天的学期归属不确定。
        affected = {year + delta for year, _ in self.overrides for delta in (-1, 0, 1)}
        terms = sorted((semester for year in affected if 1901 <= year <= 9996
                        for term in ("3", "12")
                        if (semester := self.semester(year, term)) is not None), key=lambda item: item.start)
        if any(left.end >= right.start for left, right in zip(terms, terms[1:])):
            raise ValueError("calendar 学期日期不能重叠")

    def semester(self, year: int, term: str) -> Semester | None:
        if year < self.enrollment_year or not 1901 <= year <= 9996:
            return None
        if (year, term) in self.overrides:
            return self.overrides[year, term]
        start = date(year if term == "3" else year + 1, 9 if term == "3" else 3, 1)
        start += timedelta(days=(-start.weekday()) % 7)
        end = start + timedelta(weeks=self.teaching_weeks, days=-1)
        return Semester(year, term, start, end, self.enrollment_year)

    def semester_for(self, value: date | None) -> Semester | None:
        if value is None:
            return None
        # 显式校历可能跨到下一个公历年，不能仅按查询年份枚举默认学期。
        for semester in self.overrides.values():
            if semester is not None and semester.year >= self.enrollment_year and semester.week_for(value) is not None:
                return semester
        for year in (value.year - 1, value.year):
            for term in ("3", "12"):
                semester = self.semester(year, term)
                if semester is not None and semester.week_for(value) is not None:
                    return semester
        return None


def course_weeks(text: str) -> set[int]:
    """按段解析单双周，避免 6-8周(双),9周 中的第 9 周被过滤。"""
    weeks = set()
    for part in re.split(r"[,，、;；]", text or ""):
        match = re.fullmatch(r"\s*(\d+)(?:\s*[-~～—]\s*(\d+))?\s*周?\s*(?:[（(]?\s*([单双])\s*周?\s*[）)]?)?\s*", part)
        if not match:
            continue
        start, end = int(match[1]), int(match[2] or match[1])
        for week in range(max(1, start), min(53, end) + 1):
            if match[3] == "单" and week % 2 == 0:
                continue
            if match[3] == "双" and week % 2 == 1:
                continue
            weeks.add(week)
    return weeks


def courses_on(courses: list[dict], semester: Semester, value: date) -> list[dict]:
    week = semester.week_for(value)
    if week is None:
        return []
    result = [row for row in courses if str(row.get("xqj")) == str(value.isoweekday())
              and week in course_weeks(row.get("zcd", ""))]
    return sorted(result, key=lambda row: (int(re.search(r"\d+", row.get("jcs", "0"))[0])
                                         if re.search(r"\d+", row.get("jcs", "0")) else 0,
                                         row.get("kcmc", "")))
