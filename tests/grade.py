#!/usr/bin/env python3
"""Lab 4 本地评分器；只使用 Python 标准库。"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PROGRAM = BUILD / "lab04"
IMPLEMENTATION = ROOT / "src" / "lab04.c"
MAIN_SOURCE = ROOT / "src" / "main.c"
INCLUDE = ROOT / "include"
STRICT_FLAGS = [
    "-std=c17", "-Wall", "-Wextra", "-Werror", "-pedantic", f"-I{INCLUDE}"
]
SANITIZER_FLAGS = [
    "-fsanitize=address,undefined", "-fno-omit-frame-pointer"
]
RUN_ENV = os.environ.copy()
RUN_ENV["ASAN_OPTIONS"] = (
    "detect_leaks=1:halt_on_error=1:allocator_may_return_null=1"
)
RUN_ENV["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"


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
            fallback_env["ASAN_OPTIONS"] = (
                "detect_leaks=0:halt_on_error=1:allocator_may_return_null=1"
            )
            result = execute(fallback_env)
    except subprocess.TimeoutExpired:
        return False, "运行超时", ""
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).strip()
        return False, diagnostic or "程序以非零状态结束", result.stdout
    return True, "", result.stdout


def compile_executable(output, sources, *, sanitize=True, linker_flags=None):
    flags = [*STRICT_FLAGS]
    if sanitize:
        flags.extend(SANITIZER_FLAGS)
    command = ["gcc", *flags, *map(str, sources)]
    if linker_flags:
        command.extend(linker_flags)
    command.extend(["-o", str(output)])
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


def write_and_run_harness(task_id, source, *, suffix="", sanitize=True,
                          linker_flags=None):
    BUILD.mkdir(exist_ok=True)
    stem = task_id + suffix
    harness = BUILD / f"{stem}_harness.c"
    executable = BUILD / f"{stem}_harness"
    harness.write_text(source, encoding="utf-8")
    compiled, detail = compile_executable(
        executable,
        [harness, IMPLEMENTATION],
        sanitize=sanitize,
        linker_flags=linker_flags,
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


def run_task(task_id, harness, failure_harness, cases):
    passed, detail = write_and_run_harness(task_id, harness)
    if not passed:
        return False, detail
    if failure_harness is not None:
        passed, detail = write_and_run_harness(
            task_id,
            failure_harness,
            suffix="_allocation_failure",
            sanitize=False,
            linker_flags=["-Wl,--wrap=malloc"],
        )
        if not passed:
            return False, detail
    return run_program_cases(cases)


CREATE_HARNESS = r'''
#include "lab04.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *data;
    size_t index;

    if (create_filled_array(0, 7) != NULL ||
        create_filled_array(SIZE_MAX, 7) != NULL) {
        fprintf(stderr, "零长度或溢出长度应返回 NULL\n");
        return 1;
    }
    data = create_filled_array(5, -12);
    if (data == NULL) {
        fprintf(stderr, "正常分配失败\n");
        return 1;
    }
    for (index = 0; index < 5; index++) {
        if (data[index] != -12) {
            fprintf(stderr, "位置 %zu 未正确初始化\n", index);
            free(data);
            return 1;
        }
    }
    free(data);
    return 0;
}
'''

CREATE_FAILURE_HARNESS = r'''
#include "lab04.h"

#include <stddef.h>
#include <stdio.h>

static int fail_allocations;
void *__real_malloc(size_t size);

void *__wrap_malloc(size_t size) {
    if (fail_allocations) {
        return NULL;
    }
    return __real_malloc(size);
}

int main(void) {
    fail_allocations = 1;
    if (create_filled_array(3, 9) != NULL) {
        fprintf(stderr, "malloc 失败时应返回 NULL\n");
        return 1;
    }
    return 0;
}
'''

CLONE_HARNESS = r'''
#include "lab04.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int source[] = {4, -2, 9, 4};
    int *copy;
    size_t index;

    if (clone_array(NULL, 0) != NULL ||
        clone_array(source, SIZE_MAX) != NULL) {
        fprintf(stderr, "空数组或溢出长度应返回 NULL\n");
        return 1;
    }
    copy = clone_array(source, 4);
    if (copy == NULL || copy == source) {
        fprintf(stderr, "没有创建独立副本\n");
        return 1;
    }
    for (index = 0; index < 4; index++) {
        if (copy[index] != source[index]) {
            fprintf(stderr, "副本内容错误\n");
            free(copy);
            return 1;
        }
    }
    copy[0] = 100;
    if (source[0] != 4) {
        fprintf(stderr, "修改副本影响了源数组\n");
        free(copy);
        return 1;
    }
    free(copy);
    return 0;
}
'''

CLONE_FAILURE_HARNESS = CREATE_FAILURE_HARNESS.replace(
    "create_filled_array(3, 9)", "clone_array((int[]){1, 2, 3}, 3)"
)

RESIZE_HARNESS = r'''
#include "lab04.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *data = malloc(3 * sizeof(*data));
    int *before;

    if (data == NULL) {
        return 1;
    }
    data[0] = 3;
    data[1] = 6;
    data[2] = 9;
    if (!resize_array(&data, 3, 6, -1) || data[0] != 3 || data[1] != 6 ||
        data[2] != 9 || data[3] != -1 || data[4] != -1 || data[5] != -1) {
        fprintf(stderr, "扩容内容错误\n");
        free(data);
        return 1;
    }
    if (!resize_array(&data, 6, 2, 77) || data[0] != 3 || data[1] != 6) {
        fprintf(stderr, "缩容内容错误\n");
        free(data);
        return 1;
    }
    before = data;
    if (resize_array(&data, 2, SIZE_MAX, 0) != 0 || data != before ||
        data[0] != 3 || data[1] != 6) {
        fprintf(stderr, "溢出失败时修改了原数组\n");
        free(data);
        return 1;
    }
    if (!resize_array(&data, 2, 0, 0) || data != NULL) {
        fprintf(stderr, "缩为零时没有释放并置空\n");
        free(data);
        return 1;
    }
    if (!resize_array(&data, 0, 3, 8) || data == NULL || data[0] != 8 ||
        data[1] != 8 || data[2] != 8) {
        fprintf(stderr, "从空数组扩容失败\n");
        free(data);
        return 1;
    }
    free(data);
    return 0;
}
'''

RESIZE_FAILURE_HARNESS = r'''
#include "lab04.h"

#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

static int fail_allocations;
void *__real_malloc(size_t size);

void *__wrap_malloc(size_t size) {
    if (fail_allocations) {
        return NULL;
    }
    return __real_malloc(size);
}

int main(void) {
    int *data = malloc(2 * sizeof(*data));
    int *before;

    if (data == NULL) {
        return 1;
    }
    data[0] = 11;
    data[1] = 22;
    before = data;
    fail_allocations = 1;
    if (resize_array(&data, 2, 5, 9) != 0 || data != before ||
        data[0] != 11 || data[1] != 22) {
        fprintf(stderr, "malloc 失败时没有保持原数组\n");
        fail_allocations = 0;
        free(data);
        return 1;
    }
    fail_allocations = 0;
    free(data);
    return 0;
}
'''

LIFECYCLE_HARNESS = r'''
#include "lab04.h"

#include <stdint.h>
#include <stdio.h>

int main(void) {
    DynamicArray array = {(int *)1, 99, 99};

    if (!dynamic_array_init(&array, 0) || array.data != NULL ||
        array.size != 0 || array.capacity != 0) {
        fprintf(stderr, "零容量初始化错误\n");
        return 1;
    }
    if (!dynamic_array_init(&array, 3) || array.data == NULL ||
        array.size != 0 || array.capacity != 3) {
        fprintf(stderr, "正常初始化错误\n");
        return 1;
    }
    array.data[0] = 42;
    dynamic_array_destroy(&array);
    if (array.data != NULL || array.size != 0 || array.capacity != 0) {
        fprintf(stderr, "销毁后没有重置字段\n");
        return 1;
    }
    dynamic_array_destroy(&array);
    dynamic_array_destroy(NULL);
    if (dynamic_array_init(&array, SIZE_MAX) != 0 || array.data != NULL ||
        array.size != 0 || array.capacity != 0) {
        fprintf(stderr, "溢出失败后不是安全空状态\n");
        return 1;
    }
    return 0;
}
'''

LIFECYCLE_FAILURE_HARNESS = r'''
#include "lab04.h"

#include <stddef.h>
#include <stdio.h>

static int fail_allocations;
void *__real_malloc(size_t size);

void *__wrap_malloc(size_t size) {
    if (fail_allocations) {
        return NULL;
    }
    return __real_malloc(size);
}

int main(void) {
    DynamicArray array = {(int *)1, 7, 8};

    fail_allocations = 1;
    if (dynamic_array_init(&array, 4) != 0 || array.data != NULL ||
        array.size != 0 || array.capacity != 0) {
        fprintf(stderr, "malloc 失败后不是安全空状态\n");
        return 1;
    }
    return 0;
}
'''

INSERT_HARNESS = r'''
#include "lab04.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static int expect(const DynamicArray *array, const int values[], size_t count) {
    size_t index;

    if (array->size != count) {
        return 0;
    }
    for (index = 0; index < count; index++) {
        if (array->data[index] != values[index]) {
            return 0;
        }
    }
    return 1;
}

int main(void) {
    DynamicArray array = {NULL, 0, 0};
    DynamicArray full;
    int expected[] = {5, 7, 15, 10, 20};
    int full_expected[] = {1, 2, 99, 3};
    int *before;
    size_t before_capacity;

    if (!dynamic_array_insert(&array, 0, 10) || array.capacity != 4 ||
        !dynamic_array_insert(&array, 0, 5) ||
        !dynamic_array_insert(&array, 1, 7) ||
        !dynamic_array_insert(&array, 3, 20) ||
        !dynamic_array_insert(&array, 2, 15) || array.capacity != 8 ||
        !expect(&array, expected, 5)) {
        fprintf(stderr, "自动扩容或插入次序错误\n");
        free(array.data);
        return 1;
    }
    before = array.data;
    before_capacity = array.capacity;
    if (dynamic_array_insert(&array, 6, 100) != 0 || array.data != before ||
        array.capacity != before_capacity || !expect(&array, expected, 5)) {
        fprintf(stderr, "非法下标改变了数组\n");
        free(array.data);
        return 1;
    }
    full.data = malloc(3 * sizeof(*full.data));
    if (full.data == NULL) {
        free(array.data);
        return 1;
    }
    full.data[0] = 1;
    full.data[1] = 2;
    full.data[2] = 3;
    full.size = 3;
    full.capacity = 3;
    if (!dynamic_array_insert(&full, 2, 99) || full.capacity != 6 ||
        !expect(&full, full_expected, 4)) {
        fprintf(stderr, "非二次幂容量扩容错误\n");
        free(array.data);
        free(full.data);
        return 1;
    }
    free(array.data);
    free(full.data);
    return 0;
}
'''

INSERT_FAILURE_HARNESS = r'''
#include "lab04.h"

#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

static int fail_allocations;
void *__real_malloc(size_t size);

void *__wrap_malloc(size_t size) {
    if (fail_allocations) {
        return NULL;
    }
    return __real_malloc(size);
}

int main(void) {
    DynamicArray array;
    int *before;

    array.data = malloc(2 * sizeof(*array.data));
    if (array.data == NULL) {
        return 1;
    }
    array.data[0] = 4;
    array.data[1] = 8;
    array.size = 2;
    array.capacity = 2;
    before = array.data;
    fail_allocations = 1;
    if (dynamic_array_insert(&array, 1, 6) != 0 || array.data != before ||
        array.size != 2 || array.capacity != 2 || array.data[0] != 4 ||
        array.data[1] != 8) {
        fprintf(stderr, "扩容失败时没有保持完整状态\n");
        fail_allocations = 0;
        free(array.data);
        return 1;
    }
    fail_allocations = 0;
    free(array.data);
    return 0;
}
'''


def main():
    tasks = [
        (
            "create_filled_array", "分配并初始化堆数组", 15,
            lambda: run_task(
                "create_filled_array", CREATE_HARNESS,
                CREATE_FAILURE_HARNESS,
                [
                    ("1 4 -2\n", "Filled array: -2 -2 -2 -2"),
                    ("1 1 99\n", "Filled array: 99"),
                    ("1 0 5\n", "Error: invalid input"),
                    ("1 3 8 extra\n", "Error: invalid input"),
                ],
            ),
        ),
        (
            "clone_array", "创建独立副本", 15,
            lambda: run_task(
                "clone_array", CLONE_HARNESS, CLONE_FAILURE_HARNESS,
                [
                    ("2 4 3 -1 8 3\n", "Cloned array: 3 -1 8 3"),
                    ("2 0\n", "Cloned array: none"),
                    ("2 2 1\n", "Error: invalid input"),
                    ("2 -1\n", "Error: invalid input"),
                ],
            ),
        ),
        (
            "resize_array", "安全扩缩容", 20,
            lambda: run_task(
                "resize_array", RESIZE_HARNESS, RESIZE_FAILURE_HARNESS,
                [
                    ("3 3 6 -1 3 6 9\n", "Resized array: 3 6 9 -1 -1 -1"),
                    ("3 4 2 0 5 6 7 8\n", "Resized array: 5 6"),
                    ("3 2 0 9 4 8\n", "Resized array: none"),
                    ("3 0 3 7\n", "Resized array: 7 7 7"),
                    ("3 1 2 0 5 6\n", "Error: invalid input"),
                ],
            ),
        ),
        (
            "dynamic_array_lifecycle", "动态数组生命周期", 20,
            lambda: run_task(
                "dynamic_array_lifecycle", LIFECYCLE_HARNESS,
                LIFECYCLE_FAILURE_HARNESS,
                [
                    ("4 0\n", "Dynamic array: size=0 capacity=0"),
                    ("4 5\n", "Dynamic array: size=0 capacity=5"),
                    ("4 -1\n", "Error: invalid input"),
                    ("4 21\n", "Error: invalid input"),
                ],
            ),
        ),
        (
            "dynamic_array_insert", "自动扩容插入", 30,
            lambda: run_task(
                "dynamic_array_insert", INSERT_HARNESS,
                INSERT_FAILURE_HARNESS,
                [
                    (
                        "5 0 5 0 10 0 5 1 7 3 20 2 15\n",
                        "Dynamic array: 5 7 15 10 20",
                    ),
                    ("5 1 3 0 8 1 10 1 9\n", "Dynamic array: 8 9 10"),
                    ("5 0 0\n", "Dynamic array: none"),
                    ("5 2 2 0 4 2 8\n", "Error: invalid input"),
                    ("6 0 0\n", "Error: invalid input"),
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
        "lab": "lab04",
        "tasks": results,
        "total": total,
        "max_total": 100,
    }
    BUILD.mkdir(exist_ok=True)
    (BUILD / "grade.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Lab 4：冒险队补给列表")
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
