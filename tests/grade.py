#!/usr/bin/env python3
"""Lab 3 local grader; uses only the Python standard library."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PROGRAM = BUILD / "lab03"
IMPLEMENTATION = ROOT / "src" / "lab03.c"
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


def matches(actual, expected):
    return actual == expected or actual == expected + "\n"


def run_program_cases(cases):
    compiled, detail = compile_executable(PROGRAM, [MAIN_SOURCE, IMPLEMENTATION])
    if not compiled:
        return False, detail
    for program_input, expected in cases:
        passed, run_detail, output = run_command(
            [str(PROGRAM)], program_input=program_input, timeout=2
        )
        if not passed:
            return False, "程序测试失败：" + run_detail
        if not matches(output, expected):
            actual = output.replace("\n", "\\n")
            return False, (
                f"输入 {program_input!r}，期望 {expected!r}，实际 {actual!r}"
            )
    return True, ""


def run_task(task_id, harness, cases):
    passed, detail = run_harness(task_id, harness)
    if not passed:
        return False, detail
    return run_program_cases(cases)


SWAP_HARNESS = r'''
#include "lab03.h"

#include <stdio.h>

int main(void) {
    int health = 80;
    int attack = 35;
    int same = 42;
    int aliased = 17;

    swap_stats(&health, &attack);
    if (health != 35 || attack != 80) {
        fprintf(stderr, "普通交换失败\n");
        return 1;
    }
    swap_stats(&same, &same);
    if (same != 42) {
        fprintf(stderr, "相同地址不应改变值\n");
        return 1;
    }
    swap_stats(&aliased, &aliased);
    if (aliased != 17) {
        fprintf(stderr, "别名指针处理失败\n");
        return 1;
    }
    return 0;
}
'''


INITIALIZE_HARNESS = r'''
#include "lab03.h"

#include <stdio.h>

static int check(int id, int health, int attack) {
    Adventurer adventurer = {-1, -1, -1};

    initialize_adventurer(&adventurer, id, health, attack);
    if (adventurer.id != id || adventurer.health != health ||
        adventurer.attack != attack) {
        fprintf(stderr, "初始化结果错误\n");
        return 0;
    }
    return 1;
}

int main(void) {
    return check(101, 80, 35) && check(1, 0, 0) &&
           check(9999, 100, 100) ? 0 : 1;
}
'''


POWER_HARNESS = r'''
#include "lab03.h"

#include <stdio.h>

static int check(Adventurer adventurer, int expected) {
    Adventurer before = adventurer;
    int actual = combat_power(&adventurer);

    if (actual != expected) {
        fprintf(stderr, "id=%d，期望战力 %d，实际 %d\n",
                adventurer.id, expected, actual);
        return 0;
    }
    if (adventurer.id != before.id || adventurer.health != before.health ||
        adventurer.attack != before.attack) {
        fprintf(stderr, "计算战力时修改了结构体\n");
        return 0;
    }
    return 1;
}

int main(void) {
    Adventurer first = {101, 80, 35};
    Adventurer minimum = {1, 0, 0};
    Adventurer maximum = {9999, 100, 100};

    return check(first, 150) && check(minimum, 0) && check(maximum, 300)
        ? 0 : 1;
}
'''


FIND_HARNESS = r'''
#include "lab03.h"

#include <stdio.h>

int main(void) {
    Adventurer team[] = {
        {101, 80, 35}, {202, 60, 50}, {303, 100, 20}, {202, 1, 1}
    };

    if (find_adventurer(team, 4, 101) != &team[0] ||
        find_adventurer(team, 4, 202) != &team[1] ||
        find_adventurer(team, 4, 303) != &team[2]) {
        fprintf(stderr, "没有返回原数组中的首个匹配元素\n");
        return 1;
    }
    if (find_adventurer(team, 4, 999) != NULL ||
        find_adventurer(team, 0, 101) != NULL) {
        fprintf(stderr, "未找到时应返回 NULL\n");
        return 1;
    }
    return 0;
}
'''


RANK_HARNESS = r'''
#include "lab03.h"

#include <stdio.h>

static int same_record(const Adventurer *actual, const Adventurer *expected) {
    return actual->id == expected->id && actual->health == expected->health &&
           actual->attack == expected->attack;
}

int main(void) {
    Adventurer team[] = {
        {3, 60, 40},
        {1, 80, 30},
        {4, 100, 0},
        {2, 10, 100}
    };
    Adventurer expected[] = {
        {2, 10, 100},
        {1, 80, 30},
        {3, 60, 40},
        {4, 100, 0}
    };
    Adventurer single = {9, 12, 34};
    size_t index;

    rank_team(NULL, 0);
    rank_team(&single, 1);
    if (single.id != 9 || single.health != 12 || single.attack != 34) {
        fprintf(stderr, "单元素数组被错误修改\n");
        return 1;
    }
    rank_team(team, 4);
    for (index = 0; index < 4; index++) {
        if (!same_record(&team[index], &expected[index])) {
            fprintf(stderr, "排名或完整记录移动错误，位置 %zu\n", index);
            return 1;
        }
    }
    rank_team(team, 4);
    for (index = 0; index < 4; index++) {
        if (!same_record(&team[index], &expected[index])) {
            fprintf(stderr, "已排序数组再次排序后发生变化\n");
            return 1;
        }
    }
    return 0;
}
'''


def main():
    tasks = [
        (
            "swap_stats", "交换属性", 15,
            lambda: run_task("swap_stats", SWAP_HARNESS, [
                ("1 80 35\n", "Swapped stats: 35 80"),
                ("1 0 100\n", "Swapped stats: 100 0"),
                ("1 101 20\n", "Error: invalid input"),
                ("1 80 35 extra\n", "Error: invalid input"),
            ]),
        ),
        (
            "initialize_adventurer", "初始化冒险者", 15,
            lambda: run_task("initialize_adventurer", INITIALIZE_HARNESS, [
                ("2 101 80 35\n", "Adventurer: id=101 health=80 attack=35"),
                ("2 9999 0 100\n", "Adventurer: id=9999 health=0 attack=100"),
                ("2 0 80 35\n", "Error: invalid input"),
                ("2 101 -1 35\n", "Error: invalid input"),
            ]),
        ),
        (
            "combat_power", "计算战力", 15,
            lambda: run_task("combat_power", POWER_HARNESS, [
                ("3 101 80 35\n", "Combat power: 150"),
                ("3 1 0 0\n", "Combat power: 0"),
                ("3 9999 100 100\n", "Combat power: 300"),
                ("3 101 80 35 1\n", "Error: invalid input"),
            ]),
        ),
        (
            "find_adventurer", "查找队员", 20,
            lambda: run_task("find_adventurer", FIND_HARNESS, [
                (
                    "4 3 202 101 80 35 202 60 50 303 100 20\n",
                    "Found adventurer: id=202 health=60 attack=50",
                ),
                (
                    "4 2 999 101 80 35 202 60 50\n",
                    "Adventurer not found",
                ),
                (
                    "4 2 101 101 80 35 101 60 50\n",
                    "Error: invalid input",
                ),
                ("4 0 101\n", "Error: invalid input"),
            ]),
        ),
        (
            "rank_team", "阵容排名", 35,
            lambda: run_task("rank_team", RANK_HARNESS, [
                (
                    "5 3 101 80 35 202 60 50 303 100 20\n",
                    "Ranked IDs: 202 101 303",
                ),
                (
                    "5 4 3 60 40 1 80 30 4 100 0 2 10 100\n",
                    "Ranked IDs: 2 1 3 4",
                ),
                ("5 1 77 0 0\n", "Ranked IDs: 77"),
                ("5 2 1 10 10 1 20 20\n", "Error: invalid input"),
                ("6 1 1 10 10\n", "Error: invalid input"),
            ]),
        ),
    ]
    results = []
    for task_id, name, max_score, check in tasks:
        passed, detail = check()
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
        "lab": "lab03",
        "tasks": results,
        "total": total,
        "max_total": 100,
    }
    BUILD.mkdir(exist_ok=True)
    (BUILD / "grade.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("Lab 3：冒险者队伍管理器")
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
