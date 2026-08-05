#include "lab03.h"

#include <stddef.h>

void swap_stats(int *health, int *attack) {
    /* TODO 1: Dereference both pointers and exchange their values. */
    (void)health;
    (void)attack;
}

void initialize_adventurer(Adventurer *adventurer,
                           int id, int health, int attack) {
    /* TODO 2: Store all supplied values through the structure pointer. */
    (void)adventurer;
    (void)id;
    (void)health;
    (void)attack;
}

int combat_power(const Adventurer *adventurer) {
    /* TODO 3: Read the structure through this const pointer. */
    (void)adventurer;
    return 0;
}

Adventurer *find_adventurer(Adventurer *team, size_t count, int id) {
    /* TODO 4: Return the address of the first matching array element. */
    (void)team;
    (void)count;
    (void)id;
    return NULL;
}

void rank_team(Adventurer *team, size_t count) {
    /*
     * TODO 5: Sort complete Adventurer records by descending combat power.
     * When powers tie, place the smaller id first.
     */
    (void)team;
    (void)count;
}
