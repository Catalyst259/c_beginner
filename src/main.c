#include "lab03.h"

#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#define INPUT_CAPACITY 2048
#define MAX_VALUES 64
#define MAX_TEAM_SIZE 20

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
            parsed > INT_MAX) {
            return 0;
        }
        if (*end != '\0' && !isspace((unsigned char)*end)) {
            return 0;
        }
        values[count] = (int)parsed;
        count++;
        cursor = end;
    }
    *value_count = count;
    return 1;
}

static int valid_id(int id) {
    return id >= 1 && id <= 9999;
}

static int valid_stat(int value) {
    return value >= 0 && value <= 100;
}

static int load_team(const int values[MAX_VALUES], size_t start,
                     size_t count, Adventurer team[MAX_TEAM_SIZE]) {
    size_t index;

    for (index = 0; index < count; index++) {
        int id = values[start + index * 3];
        int health = values[start + index * 3 + 1];
        int attack = values[start + index * 3 + 2];
        size_t earlier;

        if (!valid_id(id) || !valid_stat(health) || !valid_stat(attack)) {
            return 0;
        }
        for (earlier = 0; earlier < index; earlier++) {
            if (team[earlier].id == id) {
                return 0;
            }
        }
        initialize_adventurer(&team[index], id, health, attack);
    }
    return 1;
}

static int run_task_1(const int values[MAX_VALUES], size_t count) {
    int health;
    int attack;

    if (count != 3 || !valid_stat(values[1]) || !valid_stat(values[2])) {
        return 0;
    }
    health = values[1];
    attack = values[2];
    swap_stats(&health, &attack);
    printf("Swapped stats: %d %d\n", health, attack);
    return 1;
}

static int run_task_2(const int values[MAX_VALUES], size_t count) {
    Adventurer adventurer;

    if (count != 4 || !valid_id(values[1]) || !valid_stat(values[2]) ||
        !valid_stat(values[3])) {
        return 0;
    }
    initialize_adventurer(&adventurer, values[1], values[2], values[3]);
    printf("Adventurer: id=%d health=%d attack=%d\n",
           adventurer.id, adventurer.health, adventurer.attack);
    return 1;
}

static int run_task_3(const int values[MAX_VALUES], size_t count) {
    Adventurer adventurer;

    if (count != 4 || !valid_id(values[1]) || !valid_stat(values[2]) ||
        !valid_stat(values[3])) {
        return 0;
    }
    initialize_adventurer(&adventurer, values[1], values[2], values[3]);
    printf("Combat power: %d\n", combat_power(&adventurer));
    return 1;
}

static int run_task_4(const int values[MAX_VALUES], size_t value_count) {
    Adventurer team[MAX_TEAM_SIZE];
    Adventurer *found;
    int requested_count;

    if (value_count < 3) {
        return 0;
    }
    requested_count = values[1];
    if (requested_count < 1 || requested_count > MAX_TEAM_SIZE ||
        !valid_id(values[2]) ||
        value_count != 3U + (size_t)requested_count * 3U ||
        !load_team(values, 3, (size_t)requested_count, team)) {
        return 0;
    }
    found = find_adventurer(team, (size_t)requested_count, values[2]);
    if (found == NULL) {
        printf("Adventurer not found\n");
    } else {
        printf("Found adventurer: id=%d health=%d attack=%d\n",
               found->id, found->health, found->attack);
    }
    return 1;
}

static int run_task_5(const int values[MAX_VALUES], size_t value_count) {
    Adventurer team[MAX_TEAM_SIZE];
    int requested_count;
    size_t index;

    if (value_count < 2) {
        return 0;
    }
    requested_count = values[1];
    if (requested_count < 1 || requested_count > MAX_TEAM_SIZE ||
        value_count != 2U + (size_t)requested_count * 3U ||
        !load_team(values, 2, (size_t)requested_count, team)) {
        return 0;
    }
    rank_team(team, (size_t)requested_count);
    printf("Ranked IDs:");
    for (index = 0; index < (size_t)requested_count; index++) {
        printf(" %d", team[index].id);
    }
    printf("\n");
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
