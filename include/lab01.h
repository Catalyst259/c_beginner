#ifndef LAB01_H
#define LAB01_H

#define LAB01_MAX_ITEMS 20

/*
 * Precondition: items contains count valid item powers and 1 <= count <= 20.
 * Postcondition: returns the sum of all count powers.
 */
int total_power(const int items[], int count);

/*
 * Precondition: items contains count valid item powers and 1 <= count <= 20.
 * Postcondition: returns the zero-based index of the first largest power.
 */
int strongest_item_index(const int items[], int count);

/*
 * Precondition: items contains count valid item powers, 1 <= count <= 20,
 * 0 <= minimum <= 100, and qualified has room for count integers.
 * Postcondition: copies powers >= minimum into qualified without reordering
 * them and returns the number copied.
 */
int collect_qualified(const int items[], int count,
                      int minimum, int qualified[]);

/*
 * Precondition: items contains count valid item powers and 1 <= count <= 20.
 * Postcondition: rearranges the same values into descending order.
 */
void sort_descending(int items[], int count);

/*
 * Precondition: items contains count valid item powers, 1 <= count <= 20,
 * and 0 <= limit <= 200.
 * Postcondition: returns the largest sum <= limit made from two different
 * array elements, or -1 when no such pair exists.
 */
int best_pair_power(const int items[], int count, int limit);

#endif
