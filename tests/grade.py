#!/usr/bin/env python3
"""Lab 7 本地评分器；只使用 Python 标准库。"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PROGRAM = BUILD / "lab07"
IMPLEMENTATION = ROOT / "src" / "lab07.c"
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


def run_command(command, *, cwd=ROOT, program_input=None, timeout=5):
    def execute(environment):
        return subprocess.run(
            command,
            input=program_input,
            cwd=cwd,
            env=environment,
            text=True,
            capture_output=True,
            timeout=timeout,
        )

    snapshot = None
    if Path(cwd) != ROOT:
        snapshot = Path(tempfile.mkdtemp(dir=BUILD))
        shutil.copytree(cwd, snapshot / "cwd")
    try:
        result = execute(RUN_ENV)
        diagnostic = result.stderr or result.stdout
        if (result.returncode != 0 and
                "LeakSanitizer has encountered a fatal error" in diagnostic):
            if snapshot is not None:
                shutil.rmtree(cwd)
                shutil.copytree(snapshot / "cwd", cwd)
            fallback_env = RUN_ENV.copy()
            fallback_env["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
            result = execute(fallback_env)
    except subprocess.TimeoutExpired:
        return False, "运行超时", ""
    finally:
        if snapshot is not None:
            shutil.rmtree(snapshot)
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


HARNESS_SOURCE = r'''
#include "lab07.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(condition, message) if (!(condition)) { fprintf(stderr, "%s (line %d)\n", message, __LINE__); return 1; }

static int seed_file(const char *path, const char *content) {
    FILE *file = fopen(path, "wb");
    size_t length = strlen(content);
    int ok;

    if (file == NULL) {
        return 0;
    }
    ok = (length == 0 || fwrite(content, 1, length, file) == length);
    return fclose(file) == 0 && ok;
}

static int seed_repeated(const char *path, size_t count, int character) {
    FILE *file = fopen(path, "wb");
    size_t index;
    int ok = 1;

    if (file == NULL) {
        return 0;
    }
    for (index = 0; index < count; index++) {
        if (fputc(character, file) == EOF) {
            ok = 0;
            break;
        }
    }
    return fclose(file) == 0 && ok;
}

static int file_equals(const char *path, const char *expected) {
    char actual[4096];
    FILE *file = fopen(path, "rb");
    size_t amount;
    size_t expected_length = strlen(expected);

    if (file == NULL) {
        return 0;
    }
    amount = fread(actual, 1, sizeof(actual), file);
    if (ferror(file) || fclose(file) != 0) {
        return 0;
    }
    return amount == expected_length &&
           memcmp(actual, expected, expected_length) == 0;
}

static int test_write(void) {
    CHECK(seed_file("write.txt", "old content"), "cannot seed write.txt");
    CHECK(write_text_file("write.txt", "alpha\nbeta") == FILE_STATUS_OK,
          "normal write status");
    CHECK(file_equals("write.txt", "alpha\nbeta"), "normal write content");
    CHECK(write_text_file("write.txt", "") == FILE_STATUS_OK,
          "empty write status");
    CHECK(file_equals("write.txt", ""), "empty write content");
    CHECK(write_text_file("missing/out.txt", "x") == FILE_STATUS_OPEN_ERROR,
          "open failure status");
    CHECK(write_text_file("/dev/full", "x") == FILE_STATUS_WRITE_ERROR,
          "close/write failure status");
    return 0;
}

static int test_append(void) {
    CHECK(seed_file("append.txt", "first\n"), "cannot seed append.txt");
    CHECK(append_text_line("append.txt", "second") == FILE_STATUS_OK,
          "normal append status");
    CHECK(file_equals("append.txt", "first\nsecond\n"),
          "normal append content");
    CHECK(append_text_line("new.txt", "") == FILE_STATUS_OK,
          "empty append status");
    CHECK(file_equals("new.txt", "\n"), "empty append content");
    CHECK(append_text_line("missing/out.txt", "x") == FILE_STATUS_OPEN_ERROR,
          "append open failure status");
    CHECK(append_text_line("/dev/full", "x") == FILE_STATUS_WRITE_ERROR,
          "append write failure status");
    return 0;
}

static int test_read(void) {
    char buffer[LAB07_TEXT_CAPACITY] = "unchanged";
    size_t length = 777;

    CHECK(seed_file("read.txt", "hello\nworld"), "cannot seed read.txt");
    CHECK(read_text_file("read.txt", buffer, sizeof(buffer), &length) ==
          FILE_STATUS_OK, "normal read status");
    CHECK(length == 11 && strcmp(buffer, "hello\nworld") == 0,
          "normal read result");

    strcpy(buffer, "sentinel");
    length = 777;
    CHECK(read_text_file("read.txt", buffer, 11, &length) ==
          FILE_STATUS_TOO_LARGE, "capacity boundary status");
    CHECK(strcmp(buffer, "sentinel") == 0 && length == 777,
          "capacity failure changed outputs");

    CHECK(seed_file("empty.txt", ""), "cannot seed empty.txt");
    CHECK(read_text_file("empty.txt", buffer, 1, &length) == FILE_STATUS_OK,
          "empty read status");
    CHECK(length == 0 && buffer[0] == '\0', "empty read result");

    strcpy(buffer, "sentinel");
    length = 777;
    CHECK(read_text_file("missing.txt", buffer, sizeof(buffer), &length) ==
          FILE_STATUS_OPEN_ERROR, "read open failure status");
    CHECK(strcmp(buffer, "sentinel") == 0 && length == 777,
          "open failure changed outputs");
    CHECK(read_text_file(".", buffer, sizeof(buffer), &length) ==
          FILE_STATUS_READ_ERROR, "read error status");
    CHECK(strcmp(buffer, "sentinel") == 0 && length == 777,
          "read error changed outputs");
    return 0;
}

static int same_stats(TextStats actual, size_t characters, size_t lines,
                      size_t words, size_t longest_line) {
    return actual.characters == characters && actual.lines == lines &&
           actual.words == words && actual.longest_line == longest_line;
}

static int test_stats(void) {
    TextStats stats = {99, 88, 77, 66};

    CHECK(seed_file("stats.txt", "one two\n\nthree\tfour"),
          "cannot seed stats.txt");
    CHECK(analyze_text_file("stats.txt", &stats) == FILE_STATUS_OK,
          "normal stats status");
    CHECK(same_stats(stats, 19, 3, 4, 10), "normal stats result");

    CHECK(seed_file("trailing.txt", "a\n"), "cannot seed trailing.txt");
    CHECK(analyze_text_file("trailing.txt", &stats) == FILE_STATUS_OK,
          "trailing newline status");
    CHECK(same_stats(stats, 2, 1, 1, 1), "trailing newline result");

    CHECK(seed_file("empty.txt", ""), "cannot seed empty stats");
    CHECK(analyze_text_file("empty.txt", &stats) == FILE_STATUS_OK,
          "empty stats status");
    CHECK(same_stats(stats, 0, 0, 0, 0), "empty stats result");

    stats = (TextStats){99, 88, 77, 66};
    CHECK(analyze_text_file("missing.txt", &stats) == FILE_STATUS_OPEN_ERROR,
          "stats open failure status");
    CHECK(same_stats(stats, 99, 88, 77, 66),
          "stats open failure changed output");
    CHECK(analyze_text_file(".", &stats) == FILE_STATUS_READ_ERROR,
          "stats read failure status");
    CHECK(same_stats(stats, 99, 88, 77, 66),
          "stats read failure changed output");
    return 0;
}

static int test_replace(void) {
    size_t count = 777;

    CHECK(seed_file("source.txt", "cat and cat\nscatter\n"),
          "cannot seed source");
    CHECK(replace_text_file("source.txt", "output.txt", "cat", "dog",
                            &count) == FILE_STATUS_OK,
          "normal replacement status");
    CHECK(count == 3, "normal replacement count");
    CHECK(file_equals("output.txt", "dog and dog\nsdogter\n"),
          "normal replacement content");

    CHECK(seed_file("source.txt", "aaaa"), "cannot seed overlap source");
    CHECK(replace_text_file("source.txt", "output.txt", "aa", "X", &count) ==
          FILE_STATUS_OK, "overlap replacement status");
    CHECK(count == 2 && file_equals("output.txt", "XX"),
          "overlap replacement result");

    CHECK(seed_file("source.txt", "banana"), "cannot seed deletion source");
    CHECK(replace_text_file("source.txt", "output.txt", "an", "", &count) ==
          FILE_STATUS_OK, "deletion status");
    CHECK(count == 2 && file_equals("output.txt", "ba"),
          "deletion result");

    CHECK(seed_file("source.txt", "plain"), "cannot seed no-match source");
    CHECK(replace_text_file("source.txt", "output.txt", "z", "xx", &count) ==
          FILE_STATUS_OK, "no-match status");
    CHECK(count == 0 && file_equals("output.txt", "plain"),
          "no-match result");

    CHECK(seed_repeated("source.txt", 600, 'a'), "cannot seed expansion");
    CHECK(seed_file("output.txt", "keep"), "cannot seed protected output");
    count = 777;
    CHECK(replace_text_file("source.txt", "output.txt", "a", "aa", &count) ==
          FILE_STATUS_TOO_LARGE, "expanded result status");
    CHECK(count == 777 && file_equals("output.txt", "keep"),
          "expanded result changed outputs");

    CHECK(seed_repeated("source.txt", LAB07_TEXT_CAPACITY, 'a'),
          "cannot seed oversized source");
    CHECK(replace_text_file("source.txt", "output.txt", "a", "b", &count) ==
          FILE_STATUS_TOO_LARGE, "oversized source status");
    CHECK(count == 777 && file_equals("output.txt", "keep"),
          "oversized source changed outputs");

    CHECK(replace_text_file("missing.txt", "output.txt", "a", "b", &count) ==
          FILE_STATUS_OPEN_ERROR, "missing source status");
    CHECK(count == 777 && file_equals("output.txt", "keep"),
          "missing source changed outputs");

    CHECK(seed_file("source.txt", "abc"), "cannot seed destination failure");
    CHECK(replace_text_file("source.txt", "missing/out.txt", "a", "b",
                            &count) == FILE_STATUS_OPEN_ERROR,
          "destination open failure status");
    CHECK(count == 777, "destination open failure changed count");
    CHECK(replace_text_file("source.txt", "/dev/full", "a", "b", &count) ==
          FILE_STATUS_WRITE_ERROR, "destination write failure status");
    CHECK(count == 777, "destination write failure changed count");
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        return 2;
    }
    if (strcmp(argv[1], "write") == 0) {
        return test_write();
    }
    if (strcmp(argv[1], "append") == 0) {
        return test_append();
    }
    if (strcmp(argv[1], "read") == 0) {
        return test_read();
    }
    if (strcmp(argv[1], "stats") == 0) {
        return test_stats();
    }
    if (strcmp(argv[1], "replace") == 0) {
        return test_replace();
    }
    return 2;
}
'''


def prepare_case_directory(task_id):
    case_dir = BUILD / f"{task_id}_files"
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True)
    return case_dir


def write_harness():
    BUILD.mkdir(exist_ok=True)
    harness = BUILD / "lab07_harness.c"
    harness.write_text(HARNESS_SOURCE, encoding="utf-8")
    return harness


def matches(actual, expected):
    return actual == expected or actual == expected + "\n"


def check_cli(task_id, case_dir):
    compiled, detail = compile_executable(
        PROGRAM, [MAIN_SOURCE, IMPLEMENTATION]
    )
    if not compiled:
        return False, detail

    if task_id == "write":
        (case_dir / "cli.txt").write_text("old", encoding="utf-8")
        program_input = "1\ncli.txt\nhello\nworld"
        expected = "Wrote bytes: 11"
        expected_file = ("cli.txt", "hello\nworld")
    elif task_id == "append":
        (case_dir / "cli.txt").write_text("first\n", encoding="utf-8")
        program_input = "2\ncli.txt\nsecond\n"
        expected = "Appended line"
        expected_file = ("cli.txt", "first\nsecond\n")
    elif task_id == "read":
        (case_dir / "cli.txt").write_text("hello\nworld", encoding="utf-8")
        program_input = "3\ncli.txt\n"
        expected = "File content (11 bytes):\nhello\nworld"
        expected_file = None
    elif task_id == "stats":
        (case_dir / "cli.txt").write_text("one two\nthree", encoding="utf-8")
        program_input = "4\ncli.txt\n"
        expected = (
            "Statistics: characters=13 lines=2 words=3 longest_line=7"
        )
        expected_file = None
    else:
        (case_dir / "source.txt").write_text(
            "cat and cat", encoding="utf-8"
        )
        program_input = "5\nsource.txt\noutput.txt\ncat\ndog\n"
        expected = "Replacements: 2"
        expected_file = ("output.txt", "dog and dog")

    passed, run_detail, output = run_command(
        [str(PROGRAM)], cwd=case_dir, program_input=program_input, timeout=2
    )
    if not passed:
        return False, "程序测试失败：" + run_detail
    if not matches(output, expected):
        actual = output.replace("\n", "\\n")
        return False, f"程序输出错误：期望 {expected!r}，实际 {actual!r}"
    if expected_file is not None:
        path, content = expected_file
        actual_content = (case_dir / path).read_text(encoding="utf-8")
        if actual_content != content:
            return False, f"程序写入 {path} 的内容错误"
    return True, ""


def check_task(task_id):
    harness = write_harness()
    executable = BUILD / f"{task_id}_harness"
    compiled, detail = compile_executable(
        executable, [harness, IMPLEMENTATION]
    )
    if not compiled:
        return False, detail

    case_dir = prepare_case_directory(task_id)
    passed, detail, _ = run_command(
        [str(executable), task_id], cwd=case_dir, timeout=3
    )
    if not passed:
        return False, "函数测试失败：" + detail
    return check_cli(task_id, case_dir)


def main():
    tasks = [
        ("write", "覆盖写入完整文本", 15),
        ("append", "追加一行日志", 15),
        ("read", "安全读取完整文件", 20),
        ("stats", "流式统计日志", 20),
        ("replace", "跨文件批量替换", 30),
    ]
    results = []
    for task_id, name, max_score in tasks:
        passed, detail = check_task(task_id)
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
        "lab": "lab07",
        "tasks": results,
        "total": total,
        "max_total": 100,
    }
    BUILD.mkdir(exist_ok=True)
    (BUILD / "grade.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Lab 7：社团活动日志归档器")
    for task in results:
        state = "通过" if task["passed"] else "未通过"
        print(f"[{state}] {task['name']}: "
              f"{task['score']}/{task['max_score']}")
        if task["detail"]:
            print("  " + task["detail"])
    print(f"总分：{total}/100")
    print("详细结果已写入 build/grade.json")
    return 0 if total == 100 else 1


if __name__ == "__main__":
    sys.exit(main())
