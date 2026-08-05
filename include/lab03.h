#ifndef LAB03_H
#define LAB03_H

#include <stddef.h>

typedef struct {
    int id;
    int health;
    int attack;
} Adventurer;

/*
 * Precondition: health and attack point to writable int objects.
 * Postcondition: exchanges the two pointed-to values. If both pointers refer
 * to the same object, that object is unchanged.
 */
void swap_stats(int *health, int *attack);

/*
 * Precondition: adventurer points to a writable Adventurer object; id is in
 * [1, 9999], and health and attack are in [0, 100].
 * Postcondition: stores all three supplied fields in *adventurer.
 */
void initialize_adventurer(Adventurer *adventurer,
                           int id, int health, int attack);

/*
 * Precondition: adventurer points to a valid Adventurer object.
 * Postcondition: returns health + attack * 2 without modifying the object.
 */
int combat_power(const Adventurer *adventurer);

/*
 * Precondition: when count is positive, team points to an array containing at
 * least count Adventurer objects.
 * Postcondition: returns the address of the first element whose id matches,
 * or NULL if no element matches. The array is not modified.
 */
Adventurer *find_adventurer(Adventurer *team, size_t count, int id);

/*
 * Precondition: when count is positive, team points to an array containing at
 * least count Adventurer objects with unique ids.
 * Postcondition: sorts the array in place by descending combat power; ties
 * are ordered by ascending id. Every complete Adventurer record is preserved.
 */
void rank_team(Adventurer *team, size_t count);

#endif
