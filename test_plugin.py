#!/usr/bin/env python3
"""测试插件功能"""

import json
from hermes_plugin import (
    parse_week_range,
    parse_section_range,
    get_current_week,
    generate_week_table,
    generate_simple_table
)


def test_parse_week_range():
    """测试周次解析"""
    print("测试周次解析...")

    test_cases = [
        ("1-16周", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        ("1-16周(单)", [1, 3, 5, 7, 9, 11, 13, 15]),
        ("1-16周(双)", [2, 4, 6, 8, 10, 12, 14, 16]),
        ("1,3,5周", [1, 3, 5]),
        ("1-4,7-9周", [1, 2, 3, 4, 7, 8, 9])
    ]

    for zcd, expected in test_cases:
        result = parse_week_range(zcd)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {zcd} -> {result}")


def test_parse_section_range():
    """测试节次解析"""
    print("\n测试节次解析...")

    test_cases = [
        ("1-2", [1, 2]),
        ("3-4", [3, 4]),
        ("5", [5]),
        ("9-10", [9, 10])
    ]

    for jcs, expected in test_cases:
        result = parse_section_range(jcs)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {jcs} -> {result}")


def test_get_current_week():
    """测试当前周计算"""
    print("\n测试当前周计算...")

    # 假设今天是学期开始后的第35天（第5周）
    week = get_current_week("2026-09-01")
    print(f"  当前是第 {week} 周（从 2026-09-01 开始计算）")


def test_table_generation():
    """测试表格生成"""
    print("\n测试表格生成...")

    # 模拟课程数据
    courses = [
        {
            "kcmc": "高等数学",
            "xqj": "1",
            "jcs": "1-2",
            "zcd": "1-16周",
            "cdmc": "教学楼A101",
            "xm": "张老师"
        },
        {
            "kcmc": "大学英语",
            "xqj": "3",
            "jcs": "3-4",
            "zcd": "1-16周",
            "cdmc": "教学楼B203",
            "xm": "李老师"
        },
        {
            "kcmc": "数据结构",
            "xqj": "2",
            "jcs": "5-6",
            "zcd": "1-16周(单)",
            "cdmc": "实验楼C301",
            "xm": "王老师"
        }
    ]

    print("\n表格视图:")
    print(generate_week_table(courses, 1))

    print("\n\n简化列表:")
    print(generate_simple_table(courses, 1))


if __name__ == "__main__":
    print("=" * 60)
    print("正方教务课表插件 - 功能测试")
    print("=" * 60)
    print()

    test_parse_week_range()
    test_parse_section_range()
    test_get_current_week()
    test_table_generation()

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
