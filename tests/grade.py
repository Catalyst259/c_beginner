#!/usr/bin/env python3
"""Lab 2 本地评分器；只使用 Python 标准库。"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PROGRAM = BUILD / "lab02"
IMPLEMENTATION = ROOT / "src" / "lab02.c"
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


LENGTH_HARNESS = r'''
#include "lab02.h"

#include <stdio.h>

int main(void) {
    char maximum[LAB02_TEXT_CAPACITY];
    size_t index;

    for (index = 0; index < LAB02_TEXT_CAPACITY - 1; index++) {
        maximum[index] = 'x';
    }
    maximum[LAB02_TEXT_CAPACITY - 1] = '\0';

    if (text_length("") != 0 ||
        text_length("a") != 1 ||
        text_length("  pointer text  ") != 16 ||
        text_length(maximum) != LAB02_TEXT_CAPACITY - 1) {
        fprintf(stderr, "字符串长度计算错误\n");
        return 1;
    }
    return 0;
}
'''


FIND_HARNESS = r'''
#include "lab02.h"

#include <stdio.h>

static int check(const char *text, char target, int expected) {
    const char *found = find_first_character(text, target);

    if (expected < 0) {
        if (found != NULL) {
            fprintf(stderr, "字符不存在时应返回 NULL\n");
            return 0;
        }
    } else if (found != text + expected) {
        fprintf(stderr, "字符 '%c' 期望下标 %d\n", target, expected);
        return 0;
    }
    return 1;
}

int main(void) {
    return check("banana", 'b', 0) &&
           check("banana", 'n', 2) &&
           check("banana", 'a', 1) &&
           check("pointer", 'r', 6) &&
           check("a b", ' ', 1) &&
           check("banana", 'x', -1) &&
           check("", 'x', -1) ? 0 : 1;
}
'''


REVERSE_HARNESS = r'''
#include "lab02.h"

#include <stdio.h>
#include <string.h>

static int check(char text[], const char *expected) {
    reverse_text(text);
    if (strcmp(text, expected) != 0) {
        fprintf(stderr, "期望 \"%s\"，实际 \"%s\"\n", expected, text);
        return 0;
    }
    return 1;
}

int main(void) {
    char empty[] = "";
    char one[] = "x";
    char even[] = "abcd";
    char odd[] = "abcde";
    char spaces[] = "a b c";
    char palindrome[] = "level";

    return check(empty, "") &&
           check(one, "x") &&
           check(even, "dcba") &&
           check(odd, "edcba") &&
           check(spaces, "c b a") &&
           check(palindrome, "level") ? 0 : 1;
}
'''


COPY_HARNESS = r'''
#include "lab02.h"

#include <stdio.h>
#include <string.h>

int main(void) {
    char destination[LAB02_TEXT_CAPACITY] = "sentinel";

    if (!copy_text(destination, 6, "hello") ||
        strcmp(destination, "hello") != 0) {
        fprintf(stderr, "恰好容纳字符串时复制失败\n");
        return 1;
    }
    strcpy(destination, "sentinel");
    if (copy_text(destination, 5, "hello") != 0 ||
        strcmp(destination, "sentinel") != 0) {
        fprintf(stderr, "容量不足时必须失败并保持目标不变\n");
        return 1;
    }
    if (!copy_text(destination, LAB02_TEXT_CAPACITY, "pointer text") ||
        strcmp(destination, "pointer text") != 0) {
        fprintf(stderr, "普通字符串复制失败\n");
        return 1;
    }
    strcpy(destination, "sentinel");
    if (!copy_text(destination, 1, "") || destination[0] != '\0') {
        fprintf(stderr, "容量 1 应能复制空字符串\n");
        return 1;
    }
    return 0;
}
'''


REPLACE_HARNESS = r'''
#include "lab02.h"

#include <stdio.h>
#include <string.h>

static int check(const char *input, size_t capacity,
                 const char *target, const char *replacement,
                 int expected_count, const char *expected_text) {
    char text[LAB02_TEXT_CAPACITY];
    int actual_count;

    strcpy(text, input);
    actual_count = replace_all(text, capacity, target, replacement);
    if (actual_count != expected_count || strcmp(text, expected_text) != 0) {
        fprintf(stderr,
                "\"%s\" 中替换 \"%s\"：期望 %d 和 \"%s\"，"
                "实际 %d 和 \"%s\"\n",
                input, target, expected_count, expected_text,
                actual_count, text);
        return 0;
    }
    return 1;
}

int main(void) {
    return check("cat cat", 16, "cat", "dog", 2, "dog dog") &&
           check("aaaa", 16, "aa", "b", 2, "bb") &&
           check("aaa", 16, "aa", "X", 1, "Xa") &&
           check("aaaa", 16, "aa", "aaa", 2, "aaaaaa") &&
           check("banana", 16, "na", "", 2, "ba") &&
           check("abc", 16, "x", "yy", 0, "abc") &&
           check("a", 3, "a", "aa", 1, "aa") &&
           check("a", 2, "a", "aa", -1, "a") &&
           check("a", 8, "a", "aa", 1, "aa") &&
           check("", 1, "a", "", 0, "") ? 0 : 1;
}
'''


TASK_CASES = {
    "text_length": [
        ("1\nhello world\n", "Text length: 11\n"),
        ("1\n\n", "Text length: 0\n"),
        ("1\n  a  \n", "Text length: 5\n"),
        ("9\n", "Error: invalid input\n"),
    ],
    "find_character": [
        ("2\na\nbanana\n", "First occurrence: 1\n"),
        ("2\n \na b\n", "First occurrence: 1\n"),
        ("2\nx\nbanana\n", "First occurrence: none\n"),
        ("2\nab\ntext\n", "Error: invalid input\n"),
    ],
    "reverse_text": [
        ("3\nabcde\n", "Reversed text: edcba\n"),
        ("3\na b c\n", "Reversed text: c b a\n"),
        ("3\n\n", "Reversed text: \n"),
        ("3\nabc\nextra\n", "Error: invalid input\n"),
    ],
    "copy_text": [
        ("4\n6\nhello\n", "Copied text: hello\n"),
        ("4\n5\nhello\n", "Error: insufficient capacity\n"),
        ("4\n1\n\n", "Copied text: \n"),
        ("4\n129\nhello\n", "Error: invalid input\n"),
        ("4\nsix\nhello\n", "Error: invalid input\n"),
    ],
    "replace_all": [
        ("5\ncat\ndog\ncat cat\n", "Replacements: 2; Text: dog dog\n"),
        ("5\naa\nX\naaa\n", "Replacements: 1; Text: Xa\n"),
        ("5\nna\n\nbanana\n", "Replacements: 2; Text: ba\n"),
        ("5\nx\nyy\nabc\n", "Replacements: 0; Text: abc\n"),
        (
            "5\na\naa\n" + "a" * 64 + "\n",
            "Error: insufficient capacity\n",
        ),
        ("5\n\nx\ntext\n", "Error: invalid input\n"),
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
        ("text_length", "消息长度", 15, LENGTH_HARNESS),
        ("find_character", "查找字符", 15, FIND_HARNESS),
        ("reverse_text", "反转消息", 20, REVERSE_HARNESS),
        ("copy_text", "安全复制", 20, COPY_HARNESS),
        ("replace_all", "批量子串替换", 30, REPLACE_HARNESS),
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
        "lab": "lab02",
        "tasks": results,
        "total": total,
        "max_total": 100,
    }
    BUILD.mkdir(exist_ok=True)
    (BUILD / "grade.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("Lab 2：社团消息编辑器")
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
