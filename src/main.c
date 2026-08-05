#include "lab07.h"

#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PATH_CAPACITY 256

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

static int parse_task(const char *text, int *task) {
    char *end;
    long value;

    errno = 0;
    value = strtol(text, &end, 10);
    if (errno != 0 || end == text) {
        return 0;
    }
    while (isspace((unsigned char)*end)) {
        end++;
    }
    if (*end != '\0' || value < 1 || value > 5) {
        return 0;
    }
    *task = (int)value;
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

static int only_whitespace_remains(void) {
    int character;

    while ((character = fgetc(stdin)) != EOF) {
        if (!isspace((unsigned char)character)) {
            return 0;
        }
    }
    return !ferror(stdin);
}

static void print_file_error(FileStatus status) {
    if (status == FILE_STATUS_OPEN_ERROR) {
        printf("Error: cannot open file\n");
    } else if (status == FILE_STATUS_READ_ERROR) {
        printf("Error: file read failed\n");
    } else if (status == FILE_STATUS_WRITE_ERROR) {
        printf("Error: file write failed\n");
    } else if (status == FILE_STATUS_TOO_LARGE) {
        printf("Error: file too large\n");
    }
}

static int run_write_task(void) {
    char path[PATH_CAPACITY];
    char text[LAB07_TEXT_CAPACITY];
    size_t length;
    FileStatus status;

    if (!read_line(path, sizeof(path)) || !valid_path(path)) {
        return 0;
    }
    length = fread(text, 1, sizeof(text), stdin);
    if (ferror(stdin) || length == sizeof(text)) {
        return 0;
    }
    text[length] = '\0';
    status = write_text_file(path, text);
    if (status != FILE_STATUS_OK) {
        print_file_error(status);
    } else {
        printf("Wrote bytes: %zu\n", length);
    }
    return 1;
}

static int run_append_task(void) {
    char path[PATH_CAPACITY];
    char line[LAB07_TEXT_CAPACITY];
    FileStatus status;

    if (!read_line(path, sizeof(path)) || !valid_path(path) ||
            !read_line(line, sizeof(line)) || !only_whitespace_remains()) {
        return 0;
    }
    status = append_text_line(path, line);
    if (status != FILE_STATUS_OK) {
        print_file_error(status);
    } else {
        printf("Appended line\n");
    }
    return 1;
}

static int run_read_task(void) {
    char path[PATH_CAPACITY];
    char text[LAB07_TEXT_CAPACITY];
    size_t length;
    FileStatus status;

    if (!read_line(path, sizeof(path)) || !valid_path(path) ||
            !only_whitespace_remains()) {
        return 0;
    }
    status = read_text_file(path, text, sizeof(text), &length);
    if (status != FILE_STATUS_OK) {
        print_file_error(status);
    } else {
        printf("File content (%zu bytes):\n", length);
        if (length > 0) {
            fwrite(text, 1, length, stdout);
        }
        if (length == 0 || text[length - 1] != '\n') {
            putchar('\n');
        }
    }
    return 1;
}

static int run_stats_task(void) {
    char path[PATH_CAPACITY];
    TextStats stats;
    FileStatus status;

    if (!read_line(path, sizeof(path)) || !valid_path(path) ||
            !only_whitespace_remains()) {
        return 0;
    }
    status = analyze_text_file(path, &stats);
    if (status != FILE_STATUS_OK) {
        print_file_error(status);
    } else {
        printf("Statistics: characters=%zu lines=%zu words=%zu "
               "longest_line=%zu\n",
               stats.characters, stats.lines, stats.words,
               stats.longest_line);
    }
    return 1;
}

static int run_replace_task(void) {
    char source[PATH_CAPACITY];
    char destination[PATH_CAPACITY];
    char target[LAB07_TEXT_CAPACITY];
    char replacement[LAB07_TEXT_CAPACITY];
    size_t count;
    FileStatus status;

    if (!read_line(source, sizeof(source)) || !valid_path(source) ||
            !read_line(destination, sizeof(destination)) ||
            !valid_path(destination) || strcmp(source, destination) == 0 ||
            !read_line(target, sizeof(target)) || target[0] == '\0' ||
            !read_line(replacement, sizeof(replacement)) ||
            !only_whitespace_remains()) {
        return 0;
    }
    status = replace_text_file(source, destination, target, replacement,
                               &count);
    if (status != FILE_STATUS_OK) {
        print_file_error(status);
    } else {
        printf("Replacements: %zu\n", count);
    }
    return 1;
}

int main(void) {
    char task_line[32];
    int task;
    int valid;

    if (!read_line(task_line, sizeof(task_line)) ||
            !parse_task(task_line, &task)) {
        printf("Error: invalid input\n");
        return 0;
    }

    if (task == 1) {
        valid = run_write_task();
    } else if (task == 2) {
        valid = run_append_task();
    } else if (task == 3) {
        valid = run_read_task();
    } else if (task == 4) {
        valid = run_stats_task();
    } else {
        valid = run_replace_task();
    }
    if (!valid) {
        printf("Error: invalid input\n");
    }
    return 0;
}
