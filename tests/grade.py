#!/usr/bin/env python3
"""Lab 8 本地评分器；只使用 Python 标准库。"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PROGRAM = BUILD / "lab08"
IMPLEMENTATION = ROOT / "src" / "lab08.c"
MAIN_SOURCE = ROOT / "src" / "main.c"
INCLUDE = ROOT / "include"
HELPER = BUILD / "lab08_helper"
HARNESS = BUILD / "lab08_harness"
STRICT_FLAGS = [
    "-D_POSIX_C_SOURCE=200809L", "-std=c17", "-Wall", "-Wextra",
    "-Werror", "-pedantic", f"-I{INCLUDE}",
]
SANITIZER_FLAGS = [
    "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
]
RUN_ENV = os.environ.copy()
RUN_ENV["PATH"] = str(BUILD) + os.pathsep + RUN_ENV.get("PATH", "")
RUN_ENV["ASAN_OPTIONS"] = "detect_leaks=1:halt_on_error=1"
RUN_ENV["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"

TASKS = [
    ("task1", "创建并等待子进程", 15),
    ("task2", "执行 PATH 中的命令", 15),
    ("task3", "重定向命令输出", 20),
    ("task4", "通过管道捕获输出", 20),
    ("task5", "二段命令管道", 30),
]


def execute(command, *, cwd=ROOT, program_input=None, timeout=6,
            environment=None):
    env = RUN_ENV if environment is None else environment
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE if program_input is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=env,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(program_input, timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        return False, "运行超时（可能存在未关闭的管道或未回收的子进程）", ""
    if process.returncode != 0:
        diagnostic = (stderr or stdout).strip()
        return False, diagnostic or "程序以非零状态结束", stdout
    return True, "", stdout


def run_command(command, *, cwd=ROOT, program_input=None, timeout=6):
    ok, message, output = execute(
        command, cwd=cwd, program_input=program_input, timeout=timeout
    )
    diagnostic = message or output
    if not ok and "LeakSanitizer has encountered a fatal error" in diagnostic:
        fallback = RUN_ENV.copy()
        fallback["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
        return execute(
            command, cwd=cwd, program_input=program_input,
            timeout=timeout, environment=fallback,
        )
    return ok, message, output


def compile_executable(output, sources, *, sanitized=True):
    flags = [*STRICT_FLAGS]
    if sanitized:
        flags.extend(SANITIZER_FLAGS)
    command = ["gcc", *flags, *map(str, sources), "-o", str(output)]
    try:
        result = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, timeout=15
        )
    except subprocess.TimeoutExpired:
        return False, "编译超时"
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).strip()
        return False, "编译失败：" + (diagnostic or "GCC 未返回诊断")
    return True, ""


HELPER_SOURCE = r'''
#include <ctype.h>
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int parse_count(const char *text, size_t *count) {
    char *end;
    unsigned long value;

    errno = 0;
    value = strtoul(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        return 0;
    }
    *count = (size_t)value;
    return 1;
}

static int write_all(int descriptor, const char *data, size_t length) {
    while (length > 0) {
        ssize_t amount = write(descriptor, data, length);
        if (amount < 0) {
            return 0;
        }
        data += amount;
        length -= (size_t)amount;
    }
    return 1;
}

int main(int argc, char *argv[]) {
    if (argc >= 2 && strcmp(argv[1], "emit") == 0 && argc == 3) {
        return write_all(STDOUT_FILENO, argv[2], strlen(argv[2])) ? 0 : 2;
    }
    if (argc >= 2 && strcmp(argv[1], "line") == 0 && argc == 3) {
        return write_all(STDOUT_FILENO, argv[2], strlen(argv[2])) &&
               write_all(STDOUT_FILENO, "\n", 1) ? 0 : 2;
    }
    if (argc >= 2 && strcmp(argv[1], "binary") == 0 && argc == 2) {
        const char bytes[] = {'A', '\0', 'B'};
        return write_all(STDOUT_FILENO, bytes, sizeof(bytes)) ? 0 : 2;
    }
    if (argc >= 2 && strcmp(argv[1], "bytes") == 0 && argc == 4) {
        char block[4096];
        size_t remaining;
        memset(block, argv[3][0], sizeof(block));
        if (!parse_count(argv[2], &remaining)) {
            return 3;
        }
        while (remaining > 0) {
            size_t amount = remaining < sizeof(block) ? remaining : sizeof(block);
            if (!write_all(STDOUT_FILENO, block, amount)) {
                return 2;
            }
            remaining -= amount;
        }
        return 0;
    }
    if (argc >= 2 && strcmp(argv[1], "exit") == 0 && argc == 3) {
        size_t code;
        if (!parse_count(argv[2], &code) || code > 255) {
            return 3;
        }
        return (int)code;
    }
    if (argc >= 2 && strcmp(argv[1], "signal") == 0 && argc == 3) {
        size_t number;
        if (!parse_count(argv[2], &number)) {
            return 3;
        }
        raise((int)number);
        return 4;
    }
    if (argc >= 2 && strcmp(argv[1], "match") == 0 && argc == 4) {
        return strcmp(argv[2], "alpha") == 0 &&
               strcmp(argv[3], "beta") == 0 ? 0 : 9;
    }
    if (argc >= 2 && strcmp(argv[1], "upper") == 0 && argc == 2) {
        unsigned char buffer[4096];
        ssize_t amount;
        while ((amount = read(STDIN_FILENO, buffer, sizeof(buffer))) > 0) {
            ssize_t index;
            for (index = 0; index < amount; index++) {
                buffer[index] = (unsigned char)toupper(buffer[index]);
            }
            if (!write_all(STDOUT_FILENO, (char *)buffer, (size_t)amount)) {
                return 2;
            }
        }
        return amount < 0 ? 2 : 0;
    }
    if (argc >= 2 && strcmp(argv[1], "count") == 0 && argc == 2) {
        char buffer[4096];
        size_t total = 0;
        ssize_t amount;
        while ((amount = read(STDIN_FILENO, buffer, sizeof(buffer))) > 0) {
            total += (size_t)amount;
        }
        if (amount < 0) {
            return 2;
        }
        printf("%zu\n", total);
        return fflush(stdout) == 0 ? 0 : 2;
    }
    return 64;
}
'''


HARNESS_SOURCE = r'''
#include "lab08.h"

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define CHECK(condition, message) do { if (!(condition)) { \
    fprintf(stderr, "%s (line %d)\n", message, __LINE__); return 1; \
} } while (0)

static int same_result(ProcessResult result, ProcessOutcome outcome,
                       int value) {
    return result.outcome == outcome && result.value == value;
}

static int file_equals(const char *path, const char *expected) {
    char buffer[4096];
    FILE *file = fopen(path, "rb");
    size_t amount;
    size_t expected_length = strlen(expected);

    if (file == NULL) {
        return 0;
    }
    amount = fread(buffer, 1, sizeof(buffer), file);
    return !ferror(file) && fclose(file) == 0 &&
           amount == expected_length &&
           memcmp(buffer, expected, expected_length) == 0;
}

static int capture_stdout_start(const char *path, int *saved) {
    int output = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (output < 0) {
        return 0;
    }
    *saved = dup(STDOUT_FILENO);
    if (*saved < 0 || dup2(output, STDOUT_FILENO) < 0) {
        close(output);
        return 0;
    }
    close(output);
    return 1;
}

static int capture_stdout_stop(int saved) {
    return dup2(saved, STDOUT_FILENO) >= 0 && close(saved) == 0;
}

static int test_task1(void) {
    ProcessResult result = {PROCESS_SIGNALED, 999};
    int status;

    CHECK(spawn_exit_child(0, &result) == PROCESS_STATUS_OK,
          "zero exit status");
    CHECK(same_result(result, PROCESS_EXITED, 0), "zero exit result");
    CHECK(spawn_exit_child(37, &result) == PROCESS_STATUS_OK,
          "nonzero exit status");
    CHECK(same_result(result, PROCESS_EXITED, 37), "nonzero exit result");
    CHECK(spawn_exit_child(255, &result) == PROCESS_STATUS_OK,
          "maximum exit status");
    CHECK(same_result(result, PROCESS_EXITED, 255), "maximum exit result");
    errno = 0;
    CHECK(waitpid(-1, &status, WNOHANG) == -1 && errno == ECHILD,
          "child was not reaped");
    return 0;
}

static int test_task2(void) {
    ProcessResult result = {PROCESS_SIGNALED, 999};
    char *match[] = {"lab08_helper", "match", "alpha", "beta", NULL};
    char *exit23[] = {"lab08_helper", "exit", "23", NULL};
    char signal_text[16];
    char *signaled[] = {"lab08_helper", "signal", signal_text, NULL};
    char *missing[] = {"lab08_command_that_does_not_exist", NULL};

    snprintf(signal_text, sizeof(signal_text), "%d", SIGTERM);
    CHECK(run_command(match, &result) == PROCESS_STATUS_OK,
          "PATH command status");
    CHECK(same_result(result, PROCESS_EXITED, 0), "arguments not preserved");
    CHECK(run_command(exit23, &result) == PROCESS_STATUS_OK,
          "nonzero command status");
    CHECK(same_result(result, PROCESS_EXITED, 23), "nonzero command result");
    CHECK(run_command(signaled, &result) == PROCESS_STATUS_OK,
          "signaled command status");
    CHECK(same_result(result, PROCESS_SIGNALED, SIGTERM),
          "signaled command result");
    CHECK(run_command(missing, &result) == PROCESS_STATUS_OK,
          "missing command lifecycle");
    CHECK(same_result(result, PROCESS_EXITED, 127),
          "missing command must exit 127");
    return 0;
}

static int test_task3(void) {
    ProcessResult result = {PROCESS_SIGNALED, 999};
    char *hello[] = {"lab08_helper", "emit", "hello", NULL};
    char *empty[] = {"lab08_helper", "exit", "19", NULL};

    CHECK(run_command_redirected(hello, "redirect.txt", &result) ==
          PROCESS_STATUS_OK, "redirect status");
    CHECK(same_result(result, PROCESS_EXITED, 0), "redirect result");
    CHECK(file_equals("redirect.txt", "hello"), "redirect content");
    CHECK(run_command_redirected(empty, "redirect.txt", &result) ==
          PROCESS_STATUS_OK, "truncate status");
    CHECK(same_result(result, PROCESS_EXITED, 19), "redirect exit result");
    CHECK(file_equals("redirect.txt", ""), "destination not truncated");
    CHECK(run_command_redirected(hello, "missing/out.txt", &result) ==
          PROCESS_STATUS_OK, "open failure lifecycle");
    CHECK(same_result(result, PROCESS_EXITED, 126),
          "open failure must exit 126");
    return 0;
}

static int test_task4(void) {
    char output[LAB08_OUTPUT_CAPACITY] = "unchanged";
    size_t length = 777;
    ProcessResult result = {PROCESS_SIGNALED, 999};
    char *binary[] = {"lab08_helper", "binary", NULL};
    char *three[] = {"lab08_helper", "emit", "abc", NULL};
    char *large[] = {"lab08_helper", "bytes", "100000", "x", NULL};
    char *missing[] = {"lab08_command_that_does_not_exist", NULL};

    CHECK(capture_command_output(binary, output, sizeof(output), &length,
                                 &result) == PROCESS_STATUS_OK,
          "binary capture status");
    CHECK(length == 3 && output[0] == 'A' && output[1] == '\0' &&
          output[2] == 'B' && output[3] == '\0', "binary capture result");
    CHECK(same_result(result, PROCESS_EXITED, 0), "binary child result");

    strcpy(output, "unchanged");
    length = 777;
    result = (ProcessResult){PROCESS_SIGNALED, 999};
    CHECK(capture_command_output(three, output, 4, &length, &result) ==
          PROCESS_STATUS_OK, "exact capacity status");
    CHECK(length == 3 && strcmp(output, "abc") == 0,
          "exact capacity result");

    strcpy(output, "unchanged");
    length = 777;
    result = (ProcessResult){PROCESS_SIGNALED, 999};
    CHECK(capture_command_output(three, output, 3, &length, &result) ==
          PROCESS_STATUS_TOO_LARGE, "small capacity status");
    CHECK(strcmp(output, "unchanged") == 0 && length == 777 &&
          same_result(result, PROCESS_SIGNALED, 999),
          "capacity failure changed outputs");

    CHECK(capture_command_output(large, output, sizeof(output), &length,
                                 &result) == PROCESS_STATUS_TOO_LARGE,
          "large output status or pipe deadlock");
    CHECK(strcmp(output, "unchanged") == 0 && length == 777 &&
          same_result(result, PROCESS_SIGNALED, 999),
          "large output changed outputs");

    CHECK(capture_command_output(missing, output, sizeof(output), &length,
                                 &result) == PROCESS_STATUS_OK,
          "missing command capture status");
    CHECK(length == 0 && output[0] == '\0' &&
          same_result(result, PROCESS_EXITED, 127),
          "missing command capture result");
    return 0;
}

static int test_task5(void) {
    ProcessResult results[2] = {
        {PROCESS_SIGNALED, 999}, {PROCESS_SIGNALED, 998}
    };
    char *left[] = {"lab08_helper", "emit", "abcDe", NULL};
    char *upper[] = {"lab08_helper", "upper", NULL};
    char *large[] = {"lab08_helper", "bytes", "100000", "q", NULL};
    char *count[] = {"lab08_helper", "count", NULL};
    char *exit7[] = {"lab08_helper", "exit", "7", NULL};
    char *missing[] = {"lab08_command_that_does_not_exist", NULL};
    int saved;

    CHECK(capture_stdout_start("pipeline.txt", &saved),
          "cannot capture pipeline stdout");
    CHECK(run_pipeline(left, upper, results) == PROCESS_STATUS_OK,
          "normal pipeline status");
    CHECK(capture_stdout_stop(saved), "cannot restore stdout");
    CHECK(file_equals("pipeline.txt", "ABCDE"), "normal pipeline content");
    CHECK(same_result(results[0], PROCESS_EXITED, 0) &&
          same_result(results[1], PROCESS_EXITED, 0),
          "normal pipeline results");

    CHECK(capture_stdout_start("pipeline.txt", &saved),
          "cannot capture large pipeline stdout");
    CHECK(run_pipeline(large, count, results) == PROCESS_STATUS_OK,
          "large pipeline status or deadlock");
    CHECK(capture_stdout_stop(saved), "cannot restore large stdout");
    CHECK(file_equals("pipeline.txt", "100000\n"),
          "large pipeline content");

    CHECK(capture_stdout_start("pipeline.txt", &saved),
          "cannot capture exit pipeline stdout");
    CHECK(run_pipeline(exit7, count, results) == PROCESS_STATUS_OK,
          "left failure pipeline status");
    CHECK(capture_stdout_stop(saved), "cannot restore exit stdout");
    CHECK(same_result(results[0], PROCESS_EXITED, 7) &&
          same_result(results[1], PROCESS_EXITED, 0),
          "left failure pipeline results");
    CHECK(file_equals("pipeline.txt", "0\n"),
          "right command did not observe EOF");

    CHECK(capture_stdout_start("pipeline.txt", &saved),
          "cannot capture missing pipeline stdout");
    CHECK(run_pipeline(missing, count, results) == PROCESS_STATUS_OK,
          "missing left pipeline status");
    CHECK(capture_stdout_stop(saved), "cannot restore missing stdout");
    CHECK(same_result(results[0], PROCESS_EXITED, 127) &&
          same_result(results[1], PROCESS_EXITED, 0),
          "missing left pipeline results");
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        return 2;
    }
    if (strcmp(argv[1], "task1") == 0) return test_task1();
    if (strcmp(argv[1], "task2") == 0) return test_task2();
    if (strcmp(argv[1], "task3") == 0) return test_task3();
    if (strcmp(argv[1], "task4") == 0) return test_task4();
    if (strcmp(argv[1], "task5") == 0) return test_task5();
    return 2;
}
'''


def write_generated_sources(directory):
    helper_source = directory / "helper.c"
    harness_source = directory / "harness.c"
    helper_source.write_text(HELPER_SOURCE, encoding="utf-8")
    harness_source.write_text(HARNESS_SOURCE, encoding="utf-8")
    return helper_source, harness_source


def run_cli(program_input, expected, *, cwd=ROOT):
    ok, message, output = run_command(
        [str(PROGRAM)], cwd=cwd, program_input=program_input
    )
    if not ok:
        return False, message
    if output != expected:
        return False, f"CLI 输出不匹配：期望 {expected!r}，实际 {output!r}"
    return True, ""


def cli_check(task_id, workdir):
    if task_id == "task1":
        return run_cli("1\n7\n", "Child exited with code: 7\n", cwd=workdir)
    if task_id == "task2":
        return run_cli(
            "2\nlab08_helper line cli\n",
            "cli\nCommand exited with code: 0\n", cwd=workdir,
        )
    if task_id == "task3":
        ok, message = run_cli(
            "3\ncli-output.txt\nlab08_helper emit saved\n",
            "Command exited with code: 0\nOutput path: cli-output.txt\n",
            cwd=workdir,
        )
        if not ok:
            return ok, message
        if (workdir / "cli-output.txt").read_bytes() != b"saved":
            return False, "CLI 重定向文件内容错误"
        return True, ""
    if task_id == "task4":
        return run_cli(
            "4\nlab08_helper emit captured\n",
            "Command exited with code: 0\nCaptured output (8 bytes):\ncaptured\n",
            cwd=workdir,
        )
    if task_id == "task5":
        return run_cli(
            "5\nlab08_helper line hello\nlab08_helper upper\n",
            "HELLO\nLeft command exited with code: 0\n"
            "Right command exited with code: 0\n",
            cwd=workdir,
        )
    return False, "未知评分 Task"


def grade_task(task_id, workdir):
    ok, message, _ = run_command([str(HARNESS), task_id], cwd=workdir,
                                 timeout=10)
    if not ok:
        return False, "函数测试失败：" + message
    ok, message = cli_check(task_id, workdir)
    if not ok:
        return False, message
    return True, ""


def write_report(results):
    report = {
        "lab": "lab08",
        "tasks": results,
        "total": sum(item["score"] for item in results),
        "max_total": sum(item["max_score"] for item in results),
    }
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "grade.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    generated = Path(tempfile.mkdtemp(prefix="lab08-grade-", dir=BUILD))
    results = []
    compile_error = ""
    try:
        helper_source, harness_source = write_generated_sources(generated)
        ok, compile_error = compile_executable(
            HELPER, [helper_source], sanitized=False
        )
        if ok:
            ok, compile_error = compile_executable(
                HARNESS, [harness_source, IMPLEMENTATION]
            )
        if ok:
            ok, compile_error = compile_executable(
                PROGRAM, [MAIN_SOURCE, IMPLEMENTATION]
            )

        for task_id, name, maximum in TASKS:
            task_workdir = generated / task_id
            task_workdir.mkdir()
            if not ok:
                passed, message = False, compile_error
            else:
                passed, message = grade_task(task_id, task_workdir)
            results.append({
                "id": task_id,
                "name": name,
                "score": maximum if passed else 0,
                "max_score": maximum,
                "passed": passed,
                "feedback": "通过" if passed else message,
            })
    finally:
        shutil.rmtree(generated, ignore_errors=True)

    report = write_report(results)
    for item in results:
        mark = "通过" if item["passed"] else "未通过"
        print(f'{item["name"]}：{item["score"]}/{item["max_score"]}（{mark}）')
        if not item["passed"]:
            print("  " + item["feedback"])
    print(f'总分：{report["total"]}/{report["max_total"]}')
    return 0 if report["total"] == report["max_total"] else 1


if __name__ == "__main__":
    sys.exit(main())
