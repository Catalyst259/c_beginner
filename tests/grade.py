#!/usr/bin/env python3
"""Lab 6 本地评分器；只使用 Python 标准库。"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PROGRAM = BUILD / "lab06"
IMPLEMENTATION = ROOT / "src" / "lab06.c"
MAIN_SOURCE = ROOT / "src" / "main.c"
INCLUDE = ROOT / "include"
HARNESS = BUILD / "lab06_harness"
STRICT_FLAGS = [
    "-std=c17", "-Wall", "-Wextra", "-Werror", "-pedantic",
    f"-I{INCLUDE}",
]
SANITIZER_FLAGS = [
    "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
]
RUN_ENV = os.environ.copy()
RUN_ENV["ASAN_OPTIONS"] = (
    "detect_leaks=1:halt_on_error=1:allocator_may_return_null=1"
)
RUN_ENV["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"

TASKS = [
    ("task1", "创建并释放任务队列", 15),
    ("task2", "查找任务", 15),
    ("task3", "按位置插入任务", 20),
    ("task4", "按 ID 删除任务", 20),
    ("task5", "原地反转链表区间", 30),
]


def execute(command, *, program_input=None, timeout=4, environment=None):
    env = RUN_ENV if environment is None else environment
    try:
        result = subprocess.run(
            command,
            input=program_input,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, "运行超时（链表可能形成了环）", ""
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).strip()
        return False, diagnostic or "程序以非零状态结束", result.stdout
    return True, "", result.stdout


def run_command(command, *, program_input=None, timeout=4):
    ok, message, output = execute(
        command, program_input=program_input, timeout=timeout
    )
    diagnostic = message or output
    if not ok and "LeakSanitizer has encountered a fatal error" in diagnostic:
        fallback = RUN_ENV.copy()
        fallback["ASAN_OPTIONS"] = (
            "detect_leaks=0:halt_on_error=1:allocator_may_return_null=1"
        )
        return execute(
            command, program_input=program_input, timeout=timeout,
            environment=fallback,
        )
    return ok, message, output


def compile_executable(output, sources, *, sanitized=True,
                       linker_flags=None):
    flags = [*STRICT_FLAGS]
    if sanitized:
        flags.extend(SANITIZER_FLAGS)
    command = ["gcc", *flags, *map(str, sources)]
    if linker_flags:
        command.extend(linker_flags)
    command.extend(["-o", str(output)])
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
            [str(PROGRAM)], program_input=program_input
        )
        if not passed:
            return False, "程序测试失败：" + run_detail
        if not matches(output, expected):
            actual = output.replace("\n", "\\n")
            return False, (
                f"输入 {program_input!r}，期望 {expected!r}，实际 {actual!r}"
            )
    return True, ""


HARNESS_SOURCE = r'''
#include "lab06.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(condition, message) do { if (!(condition)) { \
    fprintf(stderr, "%s (line %d)\n", message, __LINE__); return 1; \
} } while (0)

static int list_matches(TaskNode *head, const int ids[], size_t count) {
    size_t index;

    for (index = 0; index < count; index++) {
        if (head == NULL || head->task.id != ids[index]) {
            return 0;
        }
        head = head->next;
    }
    return head == NULL;
}

static TaskNode *allocate_list(const Task tasks[], size_t count) {
    TaskNode *head = NULL;
    TaskNode **tail = &head;
    size_t index;

    for (index = 0; index < count; index++) {
        TaskNode *node = malloc(sizeof(*node));
        if (node == NULL) {
            while (head != NULL) {
                TaskNode *next = head->next;
                free(head);
                head = next;
            }
            return NULL;
        }
        node->task = tasks[index];
        node->next = NULL;
        *tail = node;
        tail = &node->next;
    }
    return head;
}

static void release_list(TaskNode *head) {
    while (head != NULL) {
        TaskNode *next = head->next;
        free(head);
        head = next;
    }
}

static int test_task1(void) {
    Task tasks[] = {{101, 3}, {202, 5}, {303, 2}};
    int expected[] = {101, 202, 303};
    TaskNode *head = NULL;
    TaskNode *first;
    TaskNode *second;

    CHECK(task_list_build(&head, NULL, 0) == 1 && head == NULL,
          "空队列创建失败");
    task_list_destroy(&head);
    task_list_destroy(&head);
    task_list_destroy(NULL);
    CHECK(task_list_build(&head, tasks, 3) == 1,
          "多节点创建返回失败");
    CHECK(list_matches(head, expected, 3), "创建顺序或链接错误");
    first = head;
    second = head->next;
    CHECK(first != second && second != second->next,
          "节点没有分别分配");
    CHECK(first->task.priority == 3 && second->task.priority == 5 &&
          second->next->task.priority == 2,
          "节点任务数据错误");
    task_list_destroy(&head);
    CHECK(head == NULL, "销毁后未将头指针置空");
    task_list_destroy(&head);
    return 0;
}

static int test_task2(void) {
    TaskNode third = {{303, 2}, NULL};
    TaskNode second = {{202, 5}, &third};
    TaskNode first = {{101, 3}, &second};
    TaskNode *found;

    found = task_list_find(&first, 101);
    CHECK(found == &first, "没有返回头节点的原地址");
    found = task_list_find(&first, 202);
    CHECK(found == &second && found->task.priority == 5,
          "没有返回中间节点的原地址");
    CHECK(task_list_find(&first, 303) == &third, "尾节点查找失败");
    CHECK(task_list_find(&first, 999) == NULL, "不存在的 ID 应返回 NULL");
    CHECK(task_list_find(NULL, 101) == NULL, "空队列查找应返回 NULL");
    CHECK(first.next == &second && second.next == &third && third.next == NULL,
          "查找修改了链表");
    return 0;
}

static int test_task3(void) {
    Task original[] = {{101, 3}, {303, 2}};
    int after_middle[] = {101, 202, 303};
    int after_head[] = {50, 101, 202, 303};
    int after_tail[] = {50, 101, 202, 303, 404};
    TaskNode *head = allocate_list(original, 2);
    TaskNode *before;

    CHECK(head != NULL, "测试准备分配失败");
    CHECK(task_list_insert(&head, 1, (Task){202, 5}) == 1,
          "中间插入失败");
    CHECK(list_matches(head, after_middle, 3), "中间插入链接错误");
    CHECK(task_list_insert(&head, 0, (Task){50, 1}) == 1,
          "头部插入失败");
    CHECK(list_matches(head, after_head, 4), "头部插入链接错误");
    CHECK(task_list_insert(&head, 4, (Task){404, 4}) == 1,
          "尾部插入失败");
    CHECK(list_matches(head, after_tail, 5), "尾部插入链接错误");
    before = head;
    CHECK(task_list_insert(&head, 6, (Task){999, 1}) == 0,
          "越界下标应失败");
    CHECK(head == before && list_matches(head, after_tail, 5),
          "越界失败修改了链表");
    release_list(head);
    head = NULL;
    CHECK(task_list_insert(&head, 0, (Task){7, 2}) == 1,
          "空表插入失败");
    CHECK(head != NULL && head->task.id == 7 && head->next == NULL,
          "空表插入结果错误");
    release_list(head);
    return 0;
}

static int test_task4(void) {
    Task tasks[] = {{101, 3}, {202, 5}, {303, 2}, {404, 4}};
    int after_middle[] = {101, 202, 404};
    int after_head[] = {202, 404};
    int after_tail[] = {202};
    TaskNode *head = allocate_list(tasks, 4);
    Task removed = {-1, -1};
    Task unchanged = {88, 4};

    CHECK(head != NULL, "测试准备分配失败");
    CHECK(task_list_remove(&head, 303, &removed) == 1,
          "中间节点删除失败");
    CHECK(removed.id == 303 && removed.priority == 2 &&
          list_matches(head, after_middle, 3),
          "中间节点删除结果错误");
    CHECK(task_list_remove(&head, 101, &removed) == 1 &&
          list_matches(head, after_head, 2), "头节点删除失败");
    CHECK(task_list_remove(&head, 404, &removed) == 1 &&
          list_matches(head, after_tail, 1), "尾节点删除失败");
    CHECK(task_list_remove(&head, 999, &unchanged) == 0,
          "不存在的 ID 应返回失败");
    CHECK(unchanged.id == 88 && unchanged.priority == 4 &&
          list_matches(head, after_tail, 1),
          "未找到时修改了链表或输出");
    CHECK(task_list_remove(&head, 202, &removed) == 1 && head == NULL,
          "唯一节点删除失败");
    CHECK(task_list_remove(&head, 202, &unchanged) == 0,
          "空队列删除应失败");
    return 0;
}

static void connect_five(TaskNode nodes[5]) {
    size_t index;
    for (index = 0; index < 5; index++) {
        nodes[index].task.id = (int)(index + 1);
        nodes[index].task.priority = (int)(5 - index);
        nodes[index].next = index + 1 < 5 ? &nodes[index + 1] : NULL;
    }
}

static int tasks_unchanged(TaskNode nodes[5]) {
    size_t index;
    for (index = 0; index < 5; index++) {
        if (nodes[index].task.id != (int)(index + 1) ||
            nodes[index].task.priority != (int)(5 - index)) {
            return 0;
        }
    }
    return 1;
}

static int test_task5(void) {
    TaskNode nodes[5];
    TaskNode *head;
    int middle[] = {1, 4, 3, 2, 5};
    int prefix[] = {3, 2, 1, 4, 5};
    int suffix[] = {1, 2, 5, 4, 3};
    int whole[] = {5, 4, 3, 2, 1};
    int original[] = {1, 2, 3, 4, 5};

    connect_five(nodes);
    head = &nodes[0];
    CHECK(task_list_reverse_range(&head, 1, 3) == 1 &&
          list_matches(head, middle, 5), "中间区间反转错误");
    CHECK(head == &nodes[0] && head->next == &nodes[3] &&
          head->next->next->next == &nodes[1],
          "反转没有复用原节点");
    CHECK(tasks_unchanged(nodes), "反转交换了节点数据");

    connect_five(nodes);
    head = &nodes[0];
    CHECK(task_list_reverse_range(&head, 0, 2) == 1 &&
          list_matches(head, prefix, 5), "前缀反转错误");
    connect_five(nodes);
    head = &nodes[0];
    CHECK(task_list_reverse_range(&head, 2, 4) == 1 &&
          list_matches(head, suffix, 5), "后缀反转错误");
    connect_five(nodes);
    head = &nodes[0];
    CHECK(task_list_reverse_range(&head, 0, 4) == 1 &&
          list_matches(head, whole, 5), "整表反转错误");
    connect_five(nodes);
    head = &nodes[0];
    CHECK(task_list_reverse_range(&head, 2, 2) == 1 &&
          list_matches(head, original, 5), "单节点区间处理错误");
    CHECK(task_list_reverse_range(&head, 4, 3) == 0 &&
          list_matches(head, original, 5), "逆序区间应失败且不修改");
    CHECK(task_list_reverse_range(&head, 2, 7) == 0 &&
          list_matches(head, original, 5), "越界区间应失败且不修改");
    CHECK(task_list_reverse_range(&head, 7, 7) == 0 &&
          list_matches(head, original, 5), "起点越界应失败且不修改");
    head = NULL;
    CHECK(task_list_reverse_range(&head, 0, 0) == 0 && head == NULL,
          "空队列区间应失败");
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


ALLOCATION_FAILURE_SOURCE = r'''
#include "lab06.h"

#include <stddef.h>
#include <stdio.h>
#include <string.h>

static int allocations;
static int frees;
static int fail_after = -1;

void *__real_malloc(size_t size);
void __real_free(void *pointer);

void *__wrap_malloc(size_t size) {
    if (fail_after >= 0 && allocations >= fail_after) {
        return NULL;
    }
    allocations++;
    return __real_malloc(size);
}

void __wrap_free(void *pointer) {
    if (pointer != NULL) {
        frees++;
    }
    __real_free(pointer);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        return 2;
    }
    if (strcmp(argv[1], "task1") == 0) {
        Task tasks[] = {{1, 1}, {2, 2}, {3, 3}, {4, 4}};
        TaskNode *head = NULL;

        fail_after = 2;
        if (task_list_build(&head, tasks, 4) != 0 || head != NULL ||
            allocations != 2 || frees != 2) {
            fprintf(stderr, "部分分配失败时未完整清理或提交了结果\n");
            return 1;
        }
        return 0;
    }
    if (strcmp(argv[1], "task3") == 0) {
        TaskNode second = {{2, 2}, NULL};
        TaskNode first = {{1, 1}, &second};
        TaskNode *head = &first;

        fail_after = 0;
        if (task_list_insert(&head, 1, (Task){9, 5}) != 0 ||
            head != &first || first.next != &second || second.next != NULL ||
            first.task.id != 1 || second.task.id != 2) {
            fprintf(stderr, "malloc 失败时修改了原链表\n");
            return 1;
        }
        return 0;
    }
    return 2;
}
'''


PROGRAM_CASES = {
    "task1": [
        ("1 3 101 3 202 5 303 2\n", "Queue: 101(3) 202(5) 303(2)"),
        ("1 0\n", "Queue: empty"),
        ("1 2 101 3 101 5\n", "Error: invalid input"),
    ],
    "task2": [
        ("2 3 202 101 3 202 5 303 2\n",
         "Found task: id=202 priority=5"),
        ("2 2 999 101 3 202 5\n", "Task not found"),
        ("2 0 101\n", "Task not found"),
    ],
    "task3": [
        ("3 3 1 404 4 101 3 202 5 303 2\n",
         "Queue after insert: 101(3) 404(4) 202(5) 303(2)"),
        ("3 0 0 7 2\n", "Queue after insert: 7(2)"),
        ("3 2 3 9 1 1 1 2 2\n", "Error: invalid input"),
        ("3 2 1 2 5 1 1 2 2\n", "Error: invalid input"),
    ],
    "task4": [
        ("4 3 202 101 3 202 5 303 2\n",
         "Removed task: id=202 priority=5\n"
         "Queue after remove: 101(3) 303(2)"),
        ("4 1 101 101 3\n",
         "Removed task: id=101 priority=3\nQueue after remove: empty"),
        ("4 2 999 101 3 202 5\n",
         "Task not found\nQueue after remove: 101(3) 202(5)"),
    ],
    "task5": [
        ("5 5 1 3 101 3 202 5 303 2 404 4 505 1\n",
         "Queue after reverse: 101(3) 404(4) 303(2) 202(5) 505(1)"),
        ("5 4 0 3 1 1 2 2 3 3 4 4\n",
         "Queue after reverse: 4(4) 3(3) 2(2) 1(1)"),
        ("5 3 2 2 1 1 2 2 3 3\n",
         "Queue after reverse: 1(1) 2(2) 3(3)"),
        ("5 3 0 3 1 1 2 2 3 3\n", "Error: invalid input"),
    ],
}


def compile_harness():
    BUILD.mkdir(exist_ok=True)
    source = BUILD / "lab06_harness.c"
    source.write_text(HARNESS_SOURCE, encoding="utf-8")
    return compile_executable(HARNESS, [source, IMPLEMENTATION])


def run_failure_harness(task_id):
    if task_id not in {"task1", "task3"}:
        return True, ""
    source = BUILD / f"{task_id}_allocation_harness.c"
    executable = BUILD / f"{task_id}_allocation_harness"
    source.write_text(ALLOCATION_FAILURE_SOURCE, encoding="utf-8")
    compiled, detail = compile_executable(
        executable, [source, IMPLEMENTATION], sanitized=False,
        linker_flags=["-Wl,--wrap=malloc", "-Wl,--wrap=free"],
    )
    if not compiled:
        return False, detail
    passed, detail, _ = run_command([str(executable), task_id])
    if not passed:
        return False, "分配失败测试失败：" + detail
    return True, ""


def run_task(task_id):
    passed, detail, _ = run_command([str(HARNESS), task_id])
    if not passed:
        return False, "函数测试失败：" + detail
    passed, detail = run_failure_harness(task_id)
    if not passed:
        return False, detail
    return run_program_cases(PROGRAM_CASES[task_id])


def write_report(results):
    report = {
        "lab": "lab06",
        "total": sum(item["score"] for item in results),
        "max_total": sum(item["max_score"] for item in results),
        "tasks": results,
    }
    BUILD.mkdir(exist_ok=True)
    (BUILD / "grade.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main():
    compiled, compile_detail = compile_harness()
    results = []

    for task_id, name, maximum in TASKS:
        if compiled:
            passed, detail = run_task(task_id)
        else:
            passed, detail = False, compile_detail
        score = maximum if passed else 0
        results.append({
            "id": task_id,
            "name": name,
            "score": score,
            "max_score": maximum,
            "passed": passed,
            "detail": detail,
        })
        mark = "通过" if passed else "未通过"
        print(f"[{mark}] {name}: {score}/{maximum}")
        if detail:
            print(f"  {detail}")

    report = write_report(results)
    print(f"总分：{report['total']}/{report['max_total']}")
    return 0 if report["total"] == report["max_total"] else 1


if __name__ == "__main__":
    sys.exit(main())
