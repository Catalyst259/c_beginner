#include "lab06.h"

#include <stdlib.h>

int task_list_build(TaskNode **head, const Task tasks[], size_t count) {
    /*
     * TODO 1: allocate one node per task, preserve input order, and commit
     * the completed list to *head. If any malloc fails, release every node
     * already created and leave *head NULL.
     */
    (void)head;
    (void)tasks;
    (void)count;
    return 0;
}

void task_list_destroy(TaskNode **head) {
    /*
     * TODO 1: walk through the list while saving each next pointer before
     * free, then store NULL in *head. Also handle head == NULL safely.
     */
    (void)head;
}

TaskNode *task_list_find(TaskNode *head, int id) {
    /* TODO 2: traverse the original nodes and return the matching address. */
    (void)head;
    (void)id;
    return NULL;
}

int task_list_insert(TaskNode **head, size_t index, Task task) {
    /*
     * TODO 3: first locate and validate the requested link, then allocate
     * and connect one new node. Any failure must leave the list unchanged.
     */
    (void)head;
    (void)index;
    (void)task;
    return 0;
}

int task_list_remove(TaskNode **head, int id, Task *removed) {
    /*
     * TODO 4: find the link pointing at the matching node, unlink it, free
     * it, and commit its saved Task to *removed. Preserve outputs if absent.
     */
    (void)head;
    (void)id;
    (void)removed;
    return 0;
}

int task_list_reverse_range(TaskNode **head, size_t first, size_t last) {
    /*
     * TODO 5: validate the complete inclusive range before changing links,
     * reverse only that segment, and reconnect both of its outside edges.
     * Do not allocate, free, or exchange Task values.
     */
    (void)head;
    (void)first;
    (void)last;
    return 0;
}
