#include "lab02.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define INPUT_CAPACITY (LAB02_TEXT_CAPACITY + 2)

static int read_line(char buffer[INPUT_CAPACITY]) {
    size_t length;
    int character;

    if (fgets(buffer, INPUT_CAPACITY, stdin) == NULL) {
        return 0;
    }
    length = strlen(buffer);
    if (length > 0 && buffer[length - 1] == '\n') {
        buffer[length - 1] = '\0';
        length--;
    } else if (!feof(stdin)) {
        while ((character = getchar()) != '\n' && character != EOF) {
        }
        return 0;
    }
    if (length >= LAB02_TEXT_CAPACITY) {
        return 0;
    }
    for (length = 0; buffer[length] != '\0'; length++) {
        unsigned char current = (unsigned char)buffer[length];

        if (current < 32 || current > 126) {
            return 0;
        }
    }
    return 1;
}

static int parse_integer_line(const char *line, long minimum, long maximum,
                              int *value) {
    char *end;
    long parsed;

    errno = 0;
    parsed = strtol(line, &end, 10);
    if (line == end || *end != '\0' || errno == ERANGE ||
        parsed < minimum || parsed > maximum) {
        return 0;
    }
    *value = (int)parsed;
    return 1;
}

static int has_extra_input(void) {
    int character;

    while ((character = getchar()) != EOF) {
        if (character != ' ' && character != '\t' &&
            character != '\r' && character != '\n') {
            return 1;
        }
    }
    return 0;
}

static int run_task(int task) {
    char first[INPUT_CAPACITY];
    char second[INPUT_CAPACITY];
    char third[INPUT_CAPACITY];

    if (task == 1) {
        if (!read_line(first) || has_extra_input()) {
            return 0;
        }
        printf("Text length: %zu\n", text_length(first));
        return 1;
    }
    if (task == 2) {
        const char *found;

        if (!read_line(first) || strlen(first) != 1 ||
            !read_line(second) || has_extra_input()) {
            return 0;
        }
        found = find_first_character(second, first[0]);
        if (found == NULL) {
            printf("First occurrence: none\n");
        } else {
            printf("First occurrence: %td\n", found - second);
        }
        return 1;
    }
    if (task == 3) {
        if (!read_line(first) || has_extra_input()) {
            return 0;
        }
        reverse_text(first);
        printf("Reversed text: %s\n", first);
        return 1;
    }
    if (task == 4) {
        int capacity;
        char copied[LAB02_TEXT_CAPACITY] = "unchanged";

        if (!read_line(first) ||
            !parse_integer_line(first, 1, LAB02_TEXT_CAPACITY, &capacity) ||
            !read_line(second) || has_extra_input()) {
            return 0;
        }
        if (!copy_text(copied, (size_t)capacity, second)) {
            printf("Error: insufficient capacity\n");
        } else {
            printf("Copied text: %s\n", copied);
        }
        return 1;
    }
    if (task == 5) {
        int replacements;

        if (!read_line(first) || first[0] == '\0' ||
            !read_line(second) || !read_line(third) || has_extra_input()) {
            return 0;
        }
        replacements = replace_all(third, LAB02_TEXT_CAPACITY,
                                   first, second);
        if (replacements < 0) {
            printf("Error: insufficient capacity\n");
        } else {
            printf("Replacements: %d; Text: %s\n", replacements, third);
        }
        return 1;
    }
    return 0;
}

int main(void) {
    char task_line[INPUT_CAPACITY];
    int task;

    if (!read_line(task_line) ||
        !parse_integer_line(task_line, 1, 5, &task) ||
        !run_task(task)) {
        printf("Error: invalid input\n");
    }
    return 0;
}
