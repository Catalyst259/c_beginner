#include "lab02.h"

size_t text_length(const char *text) {
    /* TODO 1: Move a read-only pointer to '\0' and return the distance. */
    (void)text;
    return 0;
}

const char *find_first_character(const char *text, char target) {
    /*
     * TODO 2: Return a pointer to the first target character, or NULL when
     * the character does not occur.
     */
    (void)text;
    (void)target;
    return NULL;
}

void reverse_text(char *text) {
    /* TODO 3: Swap characters through pointers to reverse text in place. */
    (void)text;
}

int copy_text(char *destination, size_t capacity, const char *source) {
    /*
     * TODO 4: Copy the complete string only when it fits. On failure, return
     * 0 without changing destination.
     */
    (void)destination;
    (void)capacity;
    (void)source;
    return 0;
}

int replace_all(char *text, size_t capacity,
                const char *target, const char *replacement) {
    /*
     * TODO 5: Replace left-to-right, non-overlapping matches. Return -1 and
     * keep text unchanged if the final string cannot fit.
     */
    (void)text;
    (void)capacity;
    (void)target;
    (void)replacement;
    return -1;
}
