#include "lab06.h"

#include <stdio.h>
#include <stdlib.h>

#define LAB06_MAX_TASKS 20

static int read_integer(int *value) {
    return scanf("%d", value) == 1;
}

static int input_is_finished(void) {
    int character;

    do {
        character = getchar();
    } while (character == ' ' || character == '\t' || character == '\n' ||
             character == '\r' || character == '\f' || character == '\v');
    return character == EOF;
}

static int task_is_valid(Task task) {
    return task.id >= 1 && task.id <= 9999 &&
           task.priority >= 1 && task.priority <= 5;
}

static int read_tasks(Task tasks[], size_t count) {
    size_t index;
    size_t earlier;

    for (index = 0; index < count; index++) {
        if (!read_integer(&tasks[index].id) ||
            !read_integer(&tasks[index].priority) ||
            !task_is_valid(tasks[index])) {
            return 0;
        }
        for (earlier = 0; earlier < index; earlier++) {
            if (tasks[earlier].id == tasks[index].id) {
                return 0;
            }
        }
    }
    return 1;
}

static int id_is_unused(const Task tasks[], size_t count, int id) {
    size_t index;

    for (index = 0; index < count; index++) {
        if (tasks[index].id == id) {
            return 0;
        }
    }
    return 1;
}

static TaskNode *build_input_list(const Task tasks[], size_t count) {
    TaskNode *head = NULL;
    TaskNode **tail = &head;
    size_t index;

    for (index = 0; index < count; index++) {
        TaskNode *node = malloc(sizeof(*node));

        if (node == NULL) {
            TaskNode *current = head;
            while (current != NULL) {
                TaskNode *next = current->next;
                free(current);
                current = next;
            }
            return NULL;
        }
        node->task = tasks[index];
        node->next = NULL;
        *tail = node;
        tail = &node->next;
    }
    return head;
}

static void free_input_list(TaskNode *head) {
    while (head != NULL) {
        TaskNode *next = head->next;
        free(head);
        head = next;
    }
}

static void print_queue(const char *label, const TaskNode *head) {
    const TaskNode *current;

    printf("%s", label);
    if (head == NULL) {
        printf("empty\n");
        return;
    }
    for (current = head; current != NULL; current = current->next) {
        printf("%s%d(%d)", current == head ? "" : " ",
               current->task.id, current->task.priority);
    }
    printf("\n");
}

static int finish_invalid(void) {
    printf("Error: invalid input\n");
    return 0;
}

static int finish_allocation_error(void) {
    printf("Error: allocation failed\n");
    return 0;
}

int main(void) {
    Task tasks[LAB06_MAX_TASKS];
    int task_number;
    int count_input;
    size_t count;

    if (!read_integer(&task_number) || !read_integer(&count_input) ||
        count_input < 0 || count_input > LAB06_MAX_TASKS) {
        return finish_invalid();
    }
    count = (size_t)count_input;

    if (task_number == 1) {
        TaskNode *head = NULL;

        if (!read_tasks(tasks, count) || !input_is_finished()) {
            return finish_invalid();
        }
        if (!task_list_build(&head, tasks, count)) {
            return finish_allocation_error();
        }
        print_queue("Queue: ", head);
        task_list_destroy(&head);
        return 0;
    }

    if (task_number == 2 || task_number == 4) {
        int target_id;
        TaskNode *head;

        if (!read_integer(&target_id) || target_id < 1 || target_id > 9999 ||
            !read_tasks(tasks, count) || !input_is_finished()) {
            return finish_invalid();
        }
        head = build_input_list(tasks, count);
        if (count > 0 && head == NULL) {
            return finish_allocation_error();
        }
        if (task_number == 2) {
            TaskNode *found = task_list_find(head, target_id);
            if (found == NULL) {
                printf("Task not found\n");
            } else {
                printf("Found task: id=%d priority=%d\n",
                       found->task.id, found->task.priority);
            }
        } else {
            Task removed;
            if (task_list_remove(&head, target_id, &removed)) {
                printf("Removed task: id=%d priority=%d\n",
                       removed.id, removed.priority);
            } else {
                printf("Task not found\n");
            }
            print_queue("Queue after remove: ", head);
        }
        free_input_list(head);
        return 0;
    }

    if (task_number == 3) {
        int index_input;
        Task inserted;
        TaskNode *head;

        if (!read_integer(&index_input) ||
            !read_integer(&inserted.id) || !read_integer(&inserted.priority) ||
            count >= LAB06_MAX_TASKS || index_input < 0 ||
            (size_t)index_input > count || !task_is_valid(inserted) ||
            !read_tasks(tasks, count) ||
            !id_is_unused(tasks, count, inserted.id) ||
            !input_is_finished()) {
            return finish_invalid();
        }
        head = build_input_list(tasks, count);
        if (count > 0 && head == NULL) {
            return finish_allocation_error();
        }
        if (!task_list_insert(&head, (size_t)index_input, inserted)) {
            free_input_list(head);
            return finish_allocation_error();
        }
        print_queue("Queue after insert: ", head);
        free_input_list(head);
        return 0;
    }

    if (task_number == 5) {
        int first_input;
        int last_input;
        TaskNode *head;

        if (!read_integer(&first_input) || !read_integer(&last_input) ||
            count == 0 || first_input < 0 || last_input < first_input ||
            (size_t)last_input >= count || !read_tasks(tasks, count) ||
            !input_is_finished()) {
            return finish_invalid();
        }
        head = build_input_list(tasks, count);
        if (head == NULL) {
            return finish_allocation_error();
        }
        if (!task_list_reverse_range(&head, (size_t)first_input,
                                     (size_t)last_input)) {
            free_input_list(head);
            return finish_invalid();
        }
        print_queue("Queue after reverse: ", head);
        free_input_list(head);
        return 0;
    }

    return finish_invalid();
}
