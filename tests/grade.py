#!/usr/bin/env python3
"""Lab 0 的本地评分器；只使用 Python 标准库。"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PROGRAM = BUILD / "lab00"
SOURCE = ROOT / "src" / "main.c"


def compile_program():
    BUILD.mkdir(exist_ok=True)
    command = [
        "gcc", "-std=c17", "-Wall", "-Wextra", "-Werror", "-pedantic",
        str(SOURCE), "-o", str(PROGRAM),
    ]
    try:
        result = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, timeout=10
        )
    except subprocess.TimeoutExpired:
        return False, "编译超时"
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).strip()
        return False, "编译失败：" + (diagnostic or "GCC 未返回诊断")
    return True, ""


def matches(program_output, expected):
    return program_output == expected or program_output == expected + "\n"


def run_case(program_input, expected):
    try:
        result = subprocess.run(
            [str(PROGRAM)], input=program_input, cwd=ROOT, text=True,
            capture_output=True, timeout=2
        )
    except subprocess.TimeoutExpired:
        return False, "运行超时"
    if result.returncode != 0:
        return False, "程序以非零状态结束"
    if matches(result.stdout, expected):
        return True, ""
    actual = result.stdout.replace("\n", "\\n")
    return False, f"输入 {program_input!r}，期望 {expected!r}，实际 {actual!r}"


def all_cases(cases):
    for program_input, expected in cases:
        passed, detail = run_case(program_input, expected)
        if not passed:
            return False, detail
    return True, ""


def main():
    tasks = [
        ("combined_budget", "合并预算 (+)", 15,
         [(" 120 +\t30 ", "Combined budget: 150.00")]),
        ("remaining_budget", "剩余预算 (-)", 15,
         [("20 - 50", "Remaining budget: -30.00")]),
        ("total_cost", "总费用 (*)", 15,
         [("12 * 3", "Total cost: 36.00")]),
        ("per_person_cost", "人均费用 (/)", 15,
         [("45 / 3", "Per-person cost: 15.00")]),
        ("division_by_zero", "除零处理", 10,
         [("5 / 0", "Error: division by zero")]),
        ("invalid_input", "非法输入处理", 10,
         [
             ("", "Error: invalid input"),
             ("10 +", "Error: invalid input"),
             ("-1 + 2", "Error: invalid input"),
             ("2 ^ 3", "Error: invalid input"),
             ("two + 3", "Error: invalid input"),
             ("1 / 0 extra", "Error: invalid input"),
         ]),
        ("floating_point", "浮点兼容", 20,
         [
             ("1.25 + 2.5", "Combined budget: 3.75"),
             ("9.5 - 12.25", "Remaining budget: -2.75"),
             ("2.5 * 4.2", "Total cost: 10.50"),
             ("7.5 / 2.5", "Per-person cost: 3.00"),
         ]),
    ]

    compiled, compile_detail = compile_program()
    results = []
    for task_id, name, max_score, cases in tasks:
        if compiled:
            passed, detail = all_cases(cases)
        else:
            passed, detail = False, compile_detail
        score = max_score if passed else 0
        results.append({
            "id": task_id,
            "name": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "detail": detail,
        })

    total = sum(task["score"] for task in results)
    report = {
        "lab": "lab00",
        "tasks": results,
        "total": total,
        "max_total": 100,
    }
    BUILD.mkdir(exist_ok=True)
    (BUILD / "grade.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("Lab 0：社团活动经费速算器")
    for task in results:
        state = "通过" if task["passed"] else "未通过"
        print(f"[{state}] {task['name']}: {task['score']}/{task['max_score']}")
        if task["detail"]:
            print("  " + task["detail"])
    print(f"总分：{total}/100")
    print("详细结果已写入 build/grade.json")
    return 0 if total == 100 else 1


if __name__ == "__main__":
    sys.exit(main())
