#include "lab08.h"

#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LINE_CAPACITY 256
#define MAX_ARGUMENTS 8

static int read_line(char *buffer, size_t capacity) {
    size_t length;
    int next;

    if (fgets(buffer, (int)capacity, stdin) == NULL) {
        return 0;
    }
    length = strlen(buffer);
    if (length > 0 && buffer[length - 1] == '\n') {
        buffer[length - 1] = '\0';
        return 1;
    }
    next = fgetc(stdin);
    if (next == '\n' || next == EOF) {
        return 1;
    }
    while (next != '\n' && next != EOF) {
        next = fgetc(stdin);
    }
    return 0;
}

static int parse_integer(const char *text, int minimum, int maximum,
                         int *value) {
    char *end;
    long parsed;

    errno = 0;
    parsed = strtol(text, &end, 10);
    if (errno != 0 || end == text) {
        return 0;
    }
    while (isspace((unsigned char)*end)) {
        end++;
    }
    if (*end != '\0' || parsed < minimum || parsed > maximum) {
        return 0;
    }
    *value = (int)parsed;
    return 1;
}

static int valid_path(const char *path) {
    const unsigned char *cursor = (const unsigned char *)path;

    if (*cursor == '\0') {
        return 0;
    }
    while (*cursor != '\0') {
        if (*cursor < 32 || *cursor > 126) {
            return 0;
        }
        cursor++;
    }
    return 1;
}

static int split_command(char *line, char *argv[MAX_ARGUMENTS + 1]) {
    size_t count = 0;
    char *cursor = line;

    while (*cursor != '\0') {
        while (isspace((unsigned char)*cursor)) {
            cursor++;
        }
        if (*cursor == '\0') {
            break;
        }
        if (count == MAX_ARGUMENTS) {
            return 0;
        }
        argv[count++] = cursor;
        while (*cursor != '\0' && !isspace((unsigned char)*cursor)) {
            cursor++;
        }
        if (*cursor != '\0') {
            *cursor = '\0';
            cursor++;
        }
    }
    argv[count] = NULL;
    return count > 0;
}

static int only_whitespace_remains(void) {
    int character;

    while ((character = fgetc(stdin)) != EOF) {
        if (!isspace((unsigned char)character)) {
            return 0;
        }
    }
    return !ferror(stdin);
}

static void print_process_result(const char *label, ProcessResult result) {
    if (result.outcome == PROCESS_EXITED) {
        printf("%s exited with code: %d\n", label, result.value);
    } else {
        printf("%s terminated by signal: %d\n", label, result.value);
    }
}

static void print_status_error(ProcessStatus status) {
    if (status == PROCESS_STATUS_FORK_ERROR) {
        printf("Error: fork failed\n");
    } else if (status == PROCESS_STATUS_PIPE_ERROR) {
        printf("Error: pipe failed\n");
    } else if (status == PROCESS_STATUS_READ_ERROR) {
        printf("Error: pipe read failed\n");
    } else if (status == PROCESS_STATUS_WAIT_ERROR) {
        printf("Error: wait failed\n");
    } else if (status == PROCESS_STATUS_TOO_LARGE) {
        printf("Error: output too large\n");
    }
}

static int run_task_one(void) {
    char line[LINE_CAPACITY];
    int exit_code;
    ProcessResult result;
    ProcessStatus status;

    if (!read_line(line, sizeof(line)) ||
            !parse_integer(line, 0, 255, &exit_code) ||
            !only_whitespace_remains()) {
        return 0;
    }
    status = spawn_exit_child(exit_code, &result);
    if (status == PROCESS_STATUS_OK) {
        print_process_result("Child", result);
    } else {
        print_status_error(status);
    }
    return 1;
}

static int run_task_two(void) {
    char line[LINE_CAPACITY];
    char *argv[MAX_ARGUMENTS + 1];
    ProcessResult result;
    ProcessStatus status;

    if (!read_line(line, sizeof(line)) || !split_command(line, argv) ||
            !only_whitespace_remains()) {
        return 0;
    }
    status = run_command(argv, &result);
    if (status == PROCESS_STATUS_OK) {
        print_process_result("Command", result);
    } else {
        print_status_error(status);
    }
    return 1;
}

static int run_task_three(void) {
    char path[LINE_CAPACITY];
    char line[LINE_CAPACITY];
    char *argv[MAX_ARGUMENTS + 1];
    ProcessResult result;
    ProcessStatus status;

    if (!read_line(path, sizeof(path)) || !valid_path(path) ||
            !read_line(line, sizeof(line)) || !split_command(line, argv) ||
            !only_whitespace_remains()) {
        return 0;
    }
    status = run_command_redirected(argv, path, &result);
    if (status == PROCESS_STATUS_OK) {
        print_process_result("Command", result);
        printf("Output path: %s\n", path);
    } else {
        print_status_error(status);
    }
    return 1;
}

static int run_task_four(void) {
    char line[LINE_CAPACITY];
    char *argv[MAX_ARGUMENTS + 1];
    char output[LAB08_OUTPUT_CAPACITY];
    size_t length;
    ProcessResult result;
    ProcessStatus status;

    if (!read_line(line, sizeof(line)) || !split_command(line, argv) ||
            !only_whitespace_remains()) {
        return 0;
    }
    status = capture_command_output(argv, output, sizeof(output), &length,
                                    &result);
    if (status == PROCESS_STATUS_OK) {
        print_process_result("Command", result);
        printf("Captured output (%zu bytes):\n", length);
        if (length > 0) {
            (void)fwrite(output, 1, length, stdout);
        }
        if (length == 0 || output[length - 1] != '\n') {
            putchar('\n');
        }
    } else {
        print_status_error(status);
    }
    return 1;
}

static int run_task_five(void) {
    char left_line[LINE_CAPACITY];
    char right_line[LINE_CAPACITY];
    char *left_argv[MAX_ARGUMENTS + 1];
    char *right_argv[MAX_ARGUMENTS + 1];
    ProcessResult results[2];
    ProcessStatus status;

    if (!read_line(left_line, sizeof(left_line)) ||
            !split_command(left_line, left_argv) ||
            !read_line(right_line, sizeof(right_line)) ||
            !split_command(right_line, right_argv) ||
            !only_whitespace_remains()) {
        return 0;
    }
    status = run_pipeline(left_argv, right_argv, results);
    if (status == PROCESS_STATUS_OK) {
        print_process_result("Left command", results[0]);
        print_process_result("Right command", results[1]);
    } else {
        print_status_error(status);
    }
    return 1;
}

int main(void) {
    char task_line[LINE_CAPACITY];
    int task;
    int valid;

    if (!read_line(task_line, sizeof(task_line)) ||
            !parse_integer(task_line, 1, 5, &task)) {
        printf("Error: invalid input\n");
        return 0;
    }
    if (task == 1) {
        valid = run_task_one();
    } else if (task == 2) {
        valid = run_task_two();
    } else if (task == 3) {
        valid = run_task_three();
    } else if (task == 4) {
        valid = run_task_four();
    } else {
        valid = run_task_five();
    }
    if (!valid) {
        printf("Error: invalid input\n");
    }
    return 0;
}
