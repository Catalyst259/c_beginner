#ifndef LAB07_H
#define LAB07_H

#include <stddef.h>

#define LAB07_TEXT_CAPACITY 1024

typedef enum {
    FILE_STATUS_OK,
    FILE_STATUS_OPEN_ERROR,
    FILE_STATUS_READ_ERROR,
    FILE_STATUS_WRITE_ERROR,
    FILE_STATUS_TOO_LARGE
} FileStatus;

typedef struct {
    size_t characters;
    size_t lines;
    size_t words;
    size_t longest_line;
} TextStats;

/*
 * Precondition: path is a nonempty string and text is null-terminated.
 * Postcondition: creates or replaces path with exactly the bytes in text.
 * Returns FILE_STATUS_OK on success or an open/write status on failure.
 */
FileStatus write_text_file(const char *path, const char *text);

/*
 * Precondition: path is a nonempty string; line is null-terminated and does
 * not contain a newline.
 * Postcondition: appends line followed by one '\n', creating path if needed.
 * Returns FILE_STATUS_OK on success or an open/write status on failure.
 */
FileStatus append_text_line(const char *path, const char *line);

/*
 * Precondition: path is a nonempty string; buffer has capacity bytes;
 * 1 <= capacity <= LAB07_TEXT_CAPACITY; length is non-NULL.
 * Postcondition: on success, stores the whole file followed by '\0' in buffer,
 * stores the byte count in *length, and returns FILE_STATUS_OK. If the file
 * does not fit, returns FILE_STATUS_TOO_LARGE. On every failure, buffer and
 * *length remain unchanged.
 */
FileStatus read_text_file(const char *path, char buffer[], size_t capacity,
                          size_t *length);

/*
 * Precondition: path is a nonempty string and stats is non-NULL.
 * Postcondition: on success, reports file bytes, logical lines, whitespace-
 * separated words, and the longest line length excluding '\n'. A nonempty
 * final segment without '\n' counts as a line. On failure, *stats is unchanged.
 */
FileStatus analyze_text_file(const char *path, TextStats *stats);

/*
 * Precondition: all pointers are non-NULL; source and destination are
 * different nonempty paths; target is nonempty; target and replacement are
 * null-terminated.
 * Postcondition: replaces left-to-right non-overlapping target occurrences
 * from source and writes the result to destination. Inserted text is not
 * rescanned. Source input and output must each fit LAB07_TEXT_CAPACITY bytes,
 * including the final '\0'. On success, stores the replacement count. Before
 * destination is opened, every failure leaves an existing destination file
 * unchanged. On every failure, *count is unchanged.
 */
FileStatus replace_text_file(const char *source, const char *destination,
                             const char *target, const char *replacement,
                             size_t *count);

#endif
