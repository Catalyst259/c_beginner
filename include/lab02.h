#ifndef LAB02_H
#define LAB02_H

#include <stddef.h>

#define LAB02_TEXT_CAPACITY 128

/*
 * Precondition: text points to a null-terminated string.
 * Postcondition: returns the number of characters before the null terminator.
 */
size_t text_length(const char *text);

/*
 * Precondition: text points to a null-terminated string.
 * Postcondition: returns a pointer to the first target character in text,
 * or NULL when target does not occur.
 */
const char *find_first_character(const char *text, char target);

/*
 * Precondition: text points to a writable null-terminated string.
 * Postcondition: reverses the characters in text in place.
 */
void reverse_text(char *text);

/*
 * Precondition: destination points to a writable array of capacity bytes,
 * source points to a null-terminated string, capacity is positive, and the
 * source and destination regions do not overlap.
 * Postcondition: returns 1 and copies source, including its null terminator,
 * when it fits. Returns 0 and leaves destination unchanged otherwise.
 */
int copy_text(char *destination, size_t capacity, const char *source);

/*
 * Precondition: text points to a writable array of capacity bytes containing
 * a null-terminated string; 1 <= capacity <= LAB02_TEXT_CAPACITY; target is
 * nonempty; replacement is a null-terminated string; all referenced regions
 * are separate.
 * Postcondition: replaces non-overlapping target occurrences from left to
 * right without scanning inserted text. Returns the replacement count, or -1
 * and leaves text unchanged when the final string would exceed capacity.
 */
int replace_all(char *text, size_t capacity,
                const char *target, const char *replacement);

#endif
