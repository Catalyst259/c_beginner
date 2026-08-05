#ifndef LAB06_H
#define LAB06_H

#include <stddef.h>

typedef struct {
    int id;
    int priority;
} Task;

typedef struct TaskNode {
    Task task;
    struct TaskNode *next;
} TaskNode;

/*
 * Precondition: head is non-NULL and *head is NULL. When count is positive,
 * tasks points to at least count valid Task objects.
 * Postcondition: builds a newly allocated list in input order and returns 1.
 * On allocation failure, returns 0, frees every partial node, and leaves
 * *head NULL. A zero count successfully builds an empty list.
 */
int task_list_build(TaskNode **head, const Task tasks[], size_t count);

/*
 * Releases every node reachable from *head and stores NULL in *head.
 * Passing NULL or an already-empty list is safe.
 */
void task_list_destroy(TaskNode **head);

/*
 * Returns the node whose task has the requested id, or NULL when absent.
 * The returned pointer, when non-NULL, points into the original list.
 * The list is never modified.
 */
TaskNode *task_list_find(TaskNode *head, int id);

/*
 * Inserts a newly allocated node at the zero-based index. Valid indices are
 * zero through the current list length, inclusive. Returns 1 on success.
 * On an invalid index or allocation failure, returns 0 and leaves the list
 * unchanged.
 */
int task_list_insert(TaskNode **head, size_t index, Task task);

/*
 * Removes and frees the node whose task has the requested id. On success,
 * stores its task in *removed and returns 1. If no node matches, returns 0
 * and leaves both the list and *removed unchanged.
 */
int task_list_remove(TaskNode **head, int id, Task *removed);

/*
 * Reverses the inclusive zero-based range [first, last] by changing links.
 * Returns 1 on success. If first > last or either endpoint is outside the
 * list, returns 0 and leaves the list unchanged. No nodes are allocated,
 * freed, or copied.
 */
int task_list_reverse_range(TaskNode **head, size_t first, size_t last);

#endif
