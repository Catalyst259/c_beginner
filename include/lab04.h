#ifndef LAB04_H
#define LAB04_H

#include <stddef.h>

typedef struct {
    int *data;
    size_t size;
    size_t capacity;
} DynamicArray;

/*
 * Postcondition: when count is positive, returns a newly allocated array of
 * count integers, each initialized to value. Returns NULL when count is zero,
 * the byte-size calculation overflows, or allocation fails.
 */
int *create_filled_array(size_t count, int value);

/*
 * Precondition: when count is positive, source points to at least count ints.
 * Postcondition: when count is positive, returns an independent heap copy of
 * source. Returns NULL when count is zero, the size overflows, or allocation
 * fails. The source array is never modified.
 */
int *clone_array(const int source[], size_t count);

/*
 * Precondition: data is non-NULL; when old_size is positive, *data points to
 * an allocation containing at least old_size ints; when old_size is zero,
 * *data is NULL.
 * Postcondition: on success, returns 1 and changes the allocation to new_size
 * ints, preserving the common prefix and initializing new tail elements with
 * fill. A zero new_size frees the allocation and stores NULL. On allocation
 * failure or size overflow, returns 0 and leaves *data and its contents
 * unchanged.
 */
int resize_array(int **data, size_t old_size, size_t new_size, int fill);

/*
 * Precondition: array points to a writable DynamicArray object.
 * Postcondition: initializes an empty array with the requested capacity and
 * returns 1. On allocation failure or overflow, returns 0 and initializes a
 * safe empty state with all fields zero/NULL. Zero capacity is valid.
 */
int dynamic_array_init(DynamicArray *array, size_t capacity);

/*
 * Postcondition: when array is non-NULL, releases its allocation and resets
 * data, size, and capacity. Calling it repeatedly is safe.
 */
void dynamic_array_destroy(DynamicArray *array);

/*
 * Precondition: array describes a valid DynamicArray.
 * Postcondition: inserts value at index and returns 1. Valid indices are from
 * zero through size inclusive. When full, capacity grows 0 -> 4 -> 8 -> 16...
 * On an invalid index, overflow, or allocation failure, returns 0 and leaves
 * every field and element unchanged.
 */
int dynamic_array_insert(DynamicArray *array, size_t index, int value);

#endif
