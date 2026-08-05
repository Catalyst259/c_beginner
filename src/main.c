#include "lab01.h"

#include <stdio.h>

static int read_items(int items[], int count) {
    int index;

    for (index = 0; index < count; index++) {
        if (scanf("%d", &items[index]) != 1 ||
            items[index] < 0 || items[index] > 100) {
            return 0;
        }
    }
    return 1;
}

static int has_extra_input(void) {
    char extra;

    return scanf(" %c", &extra) == 1;
}

static void print_items(const int items[], int count) {
    int index;

    for (index = 0; index < count; index++) {
        printf("%s%d", index == 0 ? "" : " ", items[index]);
    }
    printf("\n");
}

int main(void) {
    int task;
    int count;
    int argument = 0;
    int items[LAB01_MAX_ITEMS];

    if (scanf("%d%d", &task, &count) != 2 ||
        task < 1 || task > 5 || count < 1 || count > LAB01_MAX_ITEMS) {
        printf("Error: invalid input\n");
        return 0;
    }
    if ((task == 3 || task == 5) && scanf("%d", &argument) != 1) {
        printf("Error: invalid input\n");
        return 0;
    }
    if ((task == 3 && (argument < 0 || argument > 100)) ||
        (task == 5 && (argument < 0 || argument > 200)) ||
        !read_items(items, count) || has_extra_input()) {
        printf("Error: invalid input\n");
        return 0;
    }

    if (task == 1) {
        printf("Total power: %d\n", total_power(items, count));
    } else if (task == 2) {
        printf("Strongest index: %d\n", strongest_item_index(items, count));
    } else if (task == 3) {
        int qualified[LAB01_MAX_ITEMS];
        int qualified_count = collect_qualified(items, count, argument,
                                                qualified);

        if (qualified_count == 0) {
            printf("Qualified items: none\n");
        } else {
            printf("Qualified items: ");
            print_items(qualified, qualified_count);
        }
    } else if (task == 4) {
        sort_descending(items, count);
        printf("Sorted items: ");
        print_items(items, count);
    } else {
        int best = best_pair_power(items, count, argument);

        if (best < 0) {
            printf("Best pair power: none\n");
        } else {
            printf("Best pair power: %d\n", best);
        }
    }
    return 0;
}
