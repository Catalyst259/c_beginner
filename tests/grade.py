#!/usr/bin/env python3
"""Lab 1 本地评分器；只使用 Python 标准库。"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PROGRAM = BUILD / "lab01"
IMPLEMENTATION = ROOT / "src" / "lab01.c"
MAIN_SOURCE = ROOT / "src" / "main.c"
INCLUDE = ROOT / "include"
COMMON_FLAGS = [
    "-std=c17", "-Wall", "-Wextra", "-Werror", "-pedantic", f"-I{INCLUDE}"
]


def run_command(command, *, program_input=None, timeout=10):
    try:
        result = subprocess.run(
            command,
            input=program_input,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, "运行超时", ""
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).strip()
        return False, diagnostic or "程序以非零状态结束", result.stdout
    return True, "", result.stdout


def compile_executable(output, sources):
    command = ["gcc", *COMMON_FLAGS, *map(str, sources), "-o", str(output)]
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


def run_harness(task_id, source):
    BUILD.mkdir(exist_ok=True)
    harness = BUILD / f"{task_id}_harness.c"
    executable = BUILD / f"{task_id}_harness"
    harness.write_text(source, encoding="utf-8")
    compiled, detail = compile_executable(executable, [harness, IMPLEMENTATION])
    if not compiled:
        return False, detail
    passed, detail, _ = run_command([str(executable)], timeout=2)
    if not passed:
        return False, "函数测试失败：" + detail
    return True, ""


TOTAL_HARNESS = r'''
#include "lab01.h"

#include <stdio.h>

int main(void) {
    const int mixed[] = {20, 80, 50, 10, 90};
    const int one[] = {100};
    const int zeros[] = {0, 0, 0, 0};
    const int maximum[LAB01_MAX_ITEMS] = {
        100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
        100, 100, 100, 100, 100, 100, 100, 100, 100, 100
    };

    if (total_power(mixed, 5) != 250 || total_power(one, 1) != 100 ||
        total_power(zeros, 4) != 0 ||
        total_power(maximum, LAB01_MAX_ITEMS) != 2000) {
        fprintf(stderr, "总战力计算错误\n");
        return 1;
    }
    return 0;
}
'''


STRONGEST_HARNESS = r'''
#include "lab01.h"

#include <stdio.h>

static int check(const int items[], int count, int expected) {
    int actual = strongest_item_index(items, count);

    if (actual != expected) {
        fprintf(stderr, "期望最强下标 %d，实际 %d\n", expected, actual);
        return 0;
    }
    return 1;
}

int main(void) {
    const int first[] = {90, 20, 10};
    const int middle[] = {20, 90, 10};
    const int last[] = {20, 10, 90};
    const int tied[] = {20, 90, 50, 90, 10};
    const int one[] = {0};

    return check(first, 3, 0) && check(middle, 3, 1) &&
           check(last, 3, 2) && check(tied, 5, 1) && check(one, 1, 0)
               ? 0 : 1;
}
'''


FILTER_HARNESS = r'''
#include "lab01.h"

#include <stdio.h>

static int check(const int items[], int count, int minimum,
                 const int expected[], int expected_count) {
    int qualified[LAB01_MAX_ITEMS];
    int actual_count;
    int index;

    for (index = 0; index < LAB01_MAX_ITEMS; index++) {
        qualified[index] = -7;
    }
    actual_count = collect_qualified(items, count, minimum, qualified);
    if (actual_count != expected_count) {
        fprintf(stderr, "门槛 %d 期望 %d 件，实际 %d 件\n",
                minimum, expected_count, actual_count);
        return 0;
    }
    for (index = 0; index < expected_count; index++) {
        if (qualified[index] != expected[index]) {
            fprintf(stderr, "筛选结果的顺序或内容错误\n");
            return 0;
        }
    }
    return 1;
}

int main(void) {
    const int items[] = {20, 80, 50, 10, 90};
    const int some[] = {80, 50, 90};
    const int all[] = {20, 80, 50, 10, 90};
    const int none[] = {0};

    return check(items, 5, 50, some, 3) &&
           check(items, 5, 0, all, 5) &&
           check(items, 5, 100, none, 0) ? 0 : 1;
}
'''


SORT_HARNESS = r'''
#include "lab01.h"

#include <stdio.h>

static int check(int items[], int count, const int expected[]) {
    int index;

    sort_descending(items, count);
    for (index = 0; index < count; index++) {
        if (items[index] != expected[index]) {
            fprintf(stderr, "排序位置 %d 错误：期望 %d，实际 %d\n",
                    index, expected[index], items[index]);
            return 0;
        }
    }
    return 1;
}

int main(void) {
    int mixed[] = {20, 80, 50, 10, 90};
    const int mixed_expected[] = {90, 80, 50, 20, 10};
    int sorted[] = {100, 50, 50, 0};
    const int sorted_expected[] = {100, 50, 50, 0};
    int reverse[] = {0, 10, 20, 30};
    const int reverse_expected[] = {30, 20, 10, 0};
    int one[] = {7};
    const int one_expected[] = {7};

    return check(mixed, 5, mixed_expected) &&
           check(sorted, 4, sorted_expected) &&
           check(reverse, 4, reverse_expected) &&
           check(one, 1, one_expected) ? 0 : 1;
}
'''


PAIR_HARNESS = r'''
#include "lab01.h"

#include <stdio.h>

static int check(const int items[], int count, int limit, int expected) {
    int actual = best_pair_power(items, count, limit);

    if (actual != expected) {
        fprintf(stderr, "上限 %d 期望 %d，实际 %d\n",
                limit, expected, actual);
        return 0;
    }
    return 1;
}

int main(void) {
    const int mixed[] = {20, 80, 50, 10, 90};
    const int duplicate[] = {60, 60, 100};
    const int cannot_reuse[] = {70, 10};
    const int zeros[] = {0, 0};
    const int one[] = {100};

    return check(mixed, 5, 130, 130) &&
           check(mixed, 5, 100, 100) &&
           check(duplicate, 3, 120, 120) &&
           check(cannot_reuse, 2, 140, 80) &&
           check(zeros, 2, 0, 0) && check(one, 1, 200, -1) &&
           check(cannot_reuse, 2, 50, -1) ? 0 : 1;
}
'''


TASK_CASES = {
    "total_power": [
        ("1 5 20 80 50 10 90\n", "Total power: 250\n"),
        ("1 1 0\n", "Total power: 0\n"),
        ("1 2 10\n", "Error: invalid input\n"),
    ],
    "strongest_item": [
        ("2 5 20 90 50 90 10\n", "Strongest index: 1\n"),
        ("2 3 10 20 30 extra\n", "Error: invalid input\n"),
    ],
    "qualified_items": [
        ("3 5 50 20 80 50 10 90\n", "Qualified items: 80 50 90\n"),
        ("3 3 100 10 20 30\n", "Qualified items: none\n"),
        ("3 3 101 10 20 30\n", "Error: invalid input\n"),
    ],
    "sort_inventory": [
        ("4 5 20 80 50 10 90\n", "Sorted items: 90 80 50 20 10\n"),
        ("4 2 0 101\n", "Error: invalid input\n"),
    ],
    "best_pair": [
        ("5 5 130 20 80 50 10 90\n", "Best pair power: 130\n"),
        ("5 1 200 100\n", "Best pair power: none\n"),
        ("5 2 50 70 10\n", "Best pair power: none\n"),
        ("5 2 201 10 20\n", "Error: invalid input\n"),
        ("9 1 10\n", "Error: invalid input\n"),
    ],
}


def run_program_cases(task_id):
    compiled, detail = compile_executable(PROGRAM, [MAIN_SOURCE, IMPLEMENTATION])
    if not compiled:
        return False, detail
    for program_input, expected in TASK_CASES[task_id]:
        passed, run_detail, output = run_command(
            [str(PROGRAM)], program_input=program_input, timeout=2
        )
        if not passed:
            return False, "程序测试失败：" + run_detail
        if output != expected:
            actual = output.replace("\n", "\\n")
            return False, (
                f"输入 {program_input!r}，期望 {expected!r}，实际 {actual!r}"
            )
    return True, ""


def check_task(task_id, harness):
    passed, detail = run_harness(task_id, harness)
    if not passed:
        return False, detail
    return run_program_cases(task_id)


def main():
    tasks = [
        ("total_power", "总战力", 15, TOTAL_HARNESS),
        ("strongest_item", "最强物品", 15, STRONGEST_HARNESS),
        ("qualified_items", "门槛筛选", 20, FILTER_HARNESS),
        ("sort_inventory", "背包排序", 20, SORT_HARNESS),
        ("best_pair", "最佳双物品组合", 30, PAIR_HARNESS),
    ]
    results = []
    for task_id, name, max_score, harness in tasks:
        passed, detail = check_task(task_id, harness)
        results.append({
            "id": task_id,
            "name": name,
            "score": max_score if passed else 0,
            "max_score": max_score,
            "passed": passed,
            "detail": detail,
        })

    total = sum(task["score"] for task in results)
    report = {
        "lab": "lab01",
        "tasks": results,
        "total": total,
        "max_total": 100,
    }
    BUILD.mkdir(exist_ok=True)
    (BUILD / "grade.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("Lab 1：游戏背包整理器")
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
