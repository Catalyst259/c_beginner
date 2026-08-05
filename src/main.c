#include "lab04.h"

#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define INPUT_CAPACITY 4096
#define MAX_VALUES 128
#define MAX_ARRAY_SIZE 20

static int parse_all_integers(int values[MAX_VALUES], size_t *value_count) {
    char input[INPUT_CAPACITY + 1];
    char *cursor;
    size_t length;
    size_t count = 0;

    length = fread(input, 1, INPUT_CAPACITY, stdin);
    if (ferror(stdin) || length == INPUT_CAPACITY) {
        return 0;
    }
    input[length] = '\0';
    cursor = input;
    for (;;) {
        char *end;
        long parsed;

        while (isspace((unsigned char)*cursor)) {
            cursor++;
        }
        if (*cursor == '\0') {
            break;
        }
        if (count == MAX_VALUES) {
            return 0;
        }
        errno = 0;
        parsed = strtol(cursor, &end, 10);
        if (cursor == end || errno == ERANGE || parsed < INT_MIN ||
            parsed > INT_MAX ||
            (*end != '\0' && !isspace((unsigned char)*end))) {
            return 0;
        }
        values[count] = (int)parsed;
        count++;
        cursor = end;
    }
    *value_count = count;
    return 1;
}

static void print_array(const char *label, const int data[], size_t count) {
    size_t index;

    printf("%s", label);
    if (count == 0) {
        printf(" none\n");
        return;
    }
    for (index = 0; index < count; index++) {
        printf(" %d", data[index]);
    }
    printf("\n");
}

static int count_is_valid(int count) {
    return count >= 0 && count <= MAX_ARRAY_SIZE;
}

static int run_task_1(const int values[MAX_VALUES], size_t count) {
    int *data;
    size_t requested;

    if (count != 3 || values[1] < 1 || values[1] > MAX_ARRAY_SIZE) {
        return 0;
    }
    requested = (size_t)values[1];
    data = create_filled_array(requested, values[2]);
    if (data == NULL) {
        printf("Error: allocation failed\n");
        return 1;
    }
    print_array("Filled array:", data, requested);
    free(data);
    return 1;
}

static int run_task_2(const int values[MAX_VALUES], size_t count) {
    int requested;
    int *copy;

    if (count < 2 || !count_is_valid(values[1])) {
        return 0;
    }
    requested = values[1];
    if (count != 2U + (size_t)requested) {
        return 0;
    }
    copy = clone_array(&values[2], (size_t)requested);
    if (requested > 0 && copy == NULL) {
        printf("Error: allocation failed\n");
        return 1;
    }
    print_array("Cloned array:", copy, (size_t)requested);
    free(copy);
    return 1;
}

static int run_task_3(const int values[MAX_VALUES], size_t count) {
    int old_size;
    int new_size;
    int *data = NULL;
    size_t index;

    if (count < 4 || !count_is_valid(values[1]) ||
        !count_is_valid(values[2])) {
        return 0;
    }
    old_size = values[1];
    new_size = values[2];
    if (count != 4U + (size_t)old_size) {
        return 0;
    }
    if (old_size > 0) {
        data = malloc((size_t)old_size * sizeof(*data));
        if (data == NULL) {
            printf("Error: allocation failed\n");
            return 1;
        }
        for (index = 0; index < (size_t)old_size; index++) {
            data[index] = values[4 + index];
        }
    }
    if (!resize_array(&data, (size_t)old_size, (size_t)new_size, values[3])) {
        free(data);
        printf("Error: allocation failed\n");
        return 1;
    }
    print_array("Resized array:", data, (size_t)new_size);
    free(data);
    return 1;
}

static int run_task_4(const int values[MAX_VALUES], size_t count) {
    DynamicArray array;

    if (count != 2 || !count_is_valid(values[1])) {
        return 0;
    }
    if (!dynamic_array_init(&array, (size_t)values[1])) {
        printf("Error: allocation failed\n");
        return 1;
    }
    printf("Dynamic array: size=%zu capacity=%zu\n",
           array.size, array.capacity);
    dynamic_array_destroy(&array);
    return 1;
}

static int run_task_5(const int values[MAX_VALUES], size_t count) {
    DynamicArray array = {NULL, 0, 0};
    int initial_capacity;
    int operation_count;
    size_t operation;

    if (count < 3 || !count_is_valid(values[1]) ||
        !count_is_valid(values[2])) {
        return 0;
    }
    initial_capacity = values[1];
    operation_count = values[2];
    if (count != 3U + (size_t)operation_count * 2U) {
        return 0;
    }
    if (initial_capacity > 0) {
        array.data = malloc((size_t)initial_capacity * sizeof(*array.data));
        if (array.data == NULL) {
            printf("Error: allocation failed\n");
            return 1;
        }
        array.capacity = (size_t)initial_capacity;
    }
    for (operation = 0; operation < (size_t)operation_count; operation++) {
        int raw_index = values[3 + operation * 2];
        int value = values[4 + operation * 2];

        if (raw_index < 0 || (size_t)raw_index > array.size) {
            free(array.data);
            return 0;
        }
        if (!dynamic_array_insert(&array, (size_t)raw_index, value)) {
            free(array.data);
            printf("Error: allocation failed\n");
            return 1;
        }
    }
    print_array("Dynamic array:", array.data, array.size);
    free(array.data);
    return 1;
}

int main(void) {
    int values[MAX_VALUES];
    size_t count;
    int valid = 0;

    if (!parse_all_integers(values, &count) || count == 0) {
        printf("Error: invalid input\n");
        return 0;
    }
    if (values[0] == 1) {
        valid = run_task_1(values, count);
    } else if (values[0] == 2) {
        valid = run_task_2(values, count);
    } else if (values[0] == 3) {
        valid = run_task_3(values, count);
    } else if (values[0] == 4) {
        valid = run_task_4(values, count);
    } else if (values[0] == 5) {
        valid = run_task_5(values, count);
    }
    if (!valid) {
        printf("Error: invalid input\n");
    }
    return 0;
}
