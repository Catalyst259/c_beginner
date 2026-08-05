#!/usr/bin/env python3
"""Lab 5 本地评分器；只使用 Python 标准库。"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PROGRAM = BUILD / "lab05"
IMPLEMENTATION = ROOT / "src" / "lab05.c"
MAIN_SOURCE = ROOT / "src" / "main.c"
INCLUDE = ROOT / "include"
STRICT_FLAGS = [
    "-std=c17", "-Wall", "-Wextra", "-Werror", "-pedantic", f"-I{INCLUDE}"
]
SANITIZER_FLAGS = [
    "-fsanitize=address,undefined", "-fno-omit-frame-pointer"
]
RUN_ENV = os.environ.copy()
RUN_ENV["ASAN_OPTIONS"] = "detect_leaks=1:halt_on_error=1"
RUN_ENV["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
UNCHANGED_VALUE = 123456789


def run_command(command, *, program_input=None, timeout=10):
    def execute(environment):
        return subprocess.run(
            command,
            input=program_input,
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            timeout=timeout,
        )

    try:
        result = execute(RUN_ENV)
        diagnostic = result.stderr or result.stdout
        if (result.returncode != 0 and
                "LeakSanitizer has encountered a fatal error" in diagnostic):
            fallback_env = RUN_ENV.copy()
            fallback_env["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
            result = execute(fallback_env)
    except subprocess.TimeoutExpired:
        return False, "运行超时", ""
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).strip()
        return False, diagnostic or "程序以非零状态结束", result.stdout
    return True, "", result.stdout


def compile_executable(output, sources):
    command = [
        "gcc", *STRICT_FLAGS, *SANITIZER_FLAGS, *map(str, sources),
        "-o", str(output),
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


def c_integer(value):
    if value == -(2 ** 63):
        return "LLONG_MIN"
    return f"{value}LL"


def make_harness(cases):
    rows = []
    for expression, status, expected in cases:
        expected_value = UNCHANGED_VALUE if expected is None else expected
        rows.append(
            "    {" + json.dumps(expression) + ", " + status + ", " +
            c_integer(expected_value) + "},"
        )
    return r'''
#include "lab05.h"

#include <limits.h>
#include <stdio.h>

typedef struct {
    const char *expression;
    CalculatorStatus status;
    long long expected;
} Case;

int main(void) {
    const Case cases[] = {
''' + "\n".join(rows) + r'''
    };
    size_t index;

    for (index = 0; index < sizeof(cases) / sizeof(cases[0]); index++) {
        long long result = 123456789LL;
        CalculatorStatus actual = evaluate_expression(
            cases[index].expression, &result
        );

        if (actual != cases[index].status) {
            fprintf(stderr,
                    "表达式 %s 状态错误：期望 %d，实际 %d\n",
                    cases[index].expression, cases[index].status, actual);
            return 1;
        }
        if (actual == CALCULATOR_OK && result != cases[index].expected) {
            fprintf(stderr,
                    "表达式 %s 结果错误：期望 %lld，实际 %lld\n",
                    cases[index].expression, cases[index].expected, result);
            return 1;
        }
        if (actual != CALCULATOR_OK && result != 123456789LL) {
            fprintf(stderr, "表达式 %s 失败时修改了 result\n",
                    cases[index].expression);
            return 1;
        }
    }
    return 0;
}
'''


def write_and_run_harness(task_id, cases):
    BUILD.mkdir(exist_ok=True)
    harness = BUILD / f"{task_id}_harness.c"
    executable = BUILD / f"{task_id}_harness"
    harness.write_text(make_harness(cases), encoding="utf-8")
    compiled, detail = compile_executable(
        executable, [harness, IMPLEMENTATION]
    )
    if not compiled:
        return False, detail
    passed, detail, _ = run_command([str(executable)], timeout=2)
    if not passed:
        return False, "函数测试失败：" + detail
    return True, ""


def matches(actual, expected):
    return actual == expected or actual == expected + "\n"


def run_program_cases(cases):
    compiled, detail = compile_executable(
        PROGRAM, [MAIN_SOURCE, IMPLEMENTATION]
    )
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


def run_task(task_id, function_cases, program_cases):
    passed, detail = write_and_run_harness(task_id, function_cases)
    if not passed:
        return False, detail
    return run_program_cases(program_cases)


NUMBER_CASES = [
    ("0", "CALCULATOR_OK", 0),
    ("  00042\t\n", "CALCULATOR_OK", 42),
    ("9223372036854775807", "CALCULATOR_OK", 2 ** 63 - 1),
    ("", "CALCULATOR_INVALID_EXPRESSION", None),
    ("  \n\t", "CALCULATOR_INVALID_EXPRESSION", None),
    ("9223372036854775808", "CALCULATOR_OVERFLOW", None),
]

ARITHMETIC_CASES = [
    ("2 + 3 * 4", "CALCULATOR_OK", 14),
    ("20-3-2", "CALCULATOR_OK", 15),
    ("20/3", "CALCULATOR_OK", 6),
    ("18/5*2", "CALCULATOR_OK", 6),
    ("8 + 12 / 3 - 2 * 5", "CALCULATOR_OK", 2),
    ("2-5", "CALCULATOR_OK", -3),
    ("1 / 0", "CALCULATOR_DIVISION_BY_ZERO", None),
]

POWER_CASES = [
    ("2^10", "CALCULATOR_OK", 1024),
    ("2^3^2", "CALCULATOR_OK", 512),
    ("2*3^2+1", "CALCULATOR_OK", 19),
    ("0^0", "CALCULATOR_OK", 1),
    ("10^18", "CALCULATOR_OK", 10 ** 18),
    ("2^63", "CALCULATOR_OVERFLOW", None),
]

PARENTHESES_CASES = [
    ("(2+3)*4", "CALCULATOR_OK", 20),
    ("2 + 3 * (4 - 1)^2", "CALCULATOR_OK", 29),
    ("(((7)))", "CALCULATOR_OK", 7),
    ("2^(1+2)", "CALCULATOR_OK", 8),
    ("()", "CALCULATOR_INVALID_EXPRESSION", None),
    ("(1+2", "CALCULATOR_INVALID_EXPRESSION", None),
    ("1+2)", "CALCULATOR_INVALID_EXPRESSION", None),
    ("2(3)", "CALCULATOR_INVALID_EXPRESSION", None),
]

COMPLETE_CASES = [
    ("-2", "CALCULATOR_OK", -2),
    ("2*-3", "CALCULATOR_OK", -6),
    ("-(1+2)", "CALCULATOR_OK", -3),
    ("--2 + +3", "CALCULATOR_OK", 5),
    ("-2^2", "CALCULATOR_OK", -4),
    ("(-2)^2", "CALCULATOR_OK", 4),
    ("2^-1", "CALCULATOR_NEGATIVE_EXPONENT", None),
    ("2+", "CALCULATOR_INVALID_EXPRESSION", None),
    ("*2", "CALCULATOR_INVALID_EXPRESSION", None),
    ("2**3", "CALCULATOR_INVALID_EXPRESSION", None),
    ("answer", "CALCULATOR_INVALID_EXPRESSION", None),
    ("1 2", "CALCULATOR_INVALID_EXPRESSION", None),
    ("9223372036854775807+1", "CALCULATOR_OVERFLOW", None),
    ("3037000500*3037000500", "CALCULATOR_OVERFLOW", None),
    ("(-9223372036854775807-1)/-1", "CALCULATOR_OVERFLOW", None),
    ("-(-9223372036854775807-1)", "CALCULATOR_OVERFLOW", None),
]


def main():
    tasks = [
        (
            "parse_number", "读取整数与移动游标", 15,
            lambda: run_task(
                "parse_number", NUMBER_CASES,
                [
                    ("42\n", "Result: 42"),
                    ("  0007  \n", "Result: 7"),
                    ("9223372036854775808\n", "Error: arithmetic overflow"),
                    ("\n", "Error: invalid expression"),
                ],
            ),
        ),
        (
            "arithmetic", "四则多步运算", 25,
            lambda: run_task(
                "arithmetic", ARITHMETIC_CASES,
                [
                    ("2 + 3 * 4\n", "Result: 14"),
                    ("20-3-2\n", "Result: 15"),
                    ("20/3\n", "Result: 6"),
                    ("1/0\n", "Error: division by zero"),
                ],
            ),
        ),
        (
            "power", "乘方与右结合", 20,
            lambda: run_task(
                "power", POWER_CASES,
                [
                    ("2^3^2\n", "Result: 512"),
                    ("2*3^2+1\n", "Result: 19"),
                    ("2^63\n", "Error: arithmetic overflow"),
                ],
            ),
        ),
        (
            "parentheses", "括号与递归", 20,
            lambda: run_task(
                "parentheses", PARENTHESES_CASES,
                [
                    ("2 + 3 * (4 - 1)^2\n", "Result: 29"),
                    ("(((7)))\n", "Result: 7"),
                    ("()\n", "Error: invalid expression"),
                    ("2(3)\n", "Error: invalid expression"),
                ],
            ),
        ),
        (
            "complete_expression", "一元符号与完整表达式", 20,
            lambda: run_task(
                "complete_expression", COMPLETE_CASES,
                [
                    ("-2^2\n", "Result: -4"),
                    ("(-2)^2\n", "Result: 4"),
                    ("2*-3\n", "Result: -6"),
                    ("2^-1\n", "Error: negative exponent"),
                    ("2+\n", "Error: invalid expression"),
                    (
                        "3037000500*3037000500\n",
                        "Error: arithmetic overflow",
                    ),
                ],
            ),
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
        "lab": "lab05",
        "tasks": results,
        "total": total,
        "max_total": 100,
    }
    BUILD.mkdir(exist_ok=True)
    (BUILD / "grade.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Lab 5：中缀表达式计算器")
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
