#include "lab07.h"

FileStatus write_text_file(const char *path, const char *text) {
    /*
     * TODO 1: Open path in write mode, write all bytes from text, and check
     * both the write operation and fclose.
     */
    (void)path;
    (void)text;
    return FILE_STATUS_OPEN_ERROR;
}

FileStatus append_text_line(const char *path, const char *line) {
    /*
     * TODO 2: Open path in append mode, append line and one newline, and
     * report opening or writing failures.
     */
    (void)path;
    (void)line;
    return FILE_STATUS_OPEN_ERROR;
}

FileStatus read_text_file(const char *path, char buffer[], size_t capacity,
                          size_t *length) {
    /*
     * TODO 3: Read through a temporary array, detect a file that cannot fit,
     * then commit the text and length only after the whole read succeeds.
     */
    (void)path;
    (void)buffer;
    (void)capacity;
    (void)length;
    return FILE_STATUS_OPEN_ERROR;
}

FileStatus analyze_text_file(const char *path, TextStats *stats) {
    /*
     * TODO 4: Read one character at a time and count bytes, logical lines,
     * whitespace-separated words, and the longest line.
     */
    (void)path;
    (void)stats;
    return FILE_STATUS_OPEN_ERROR;
}

FileStatus replace_text_file(const char *source, const char *destination,
                             const char *target, const char *replacement,
                             size_t *count) {
    /*
     * TODO 5: Read source, build the complete left-to-right replacement in
     * memory with capacity checks, then write destination and commit count.
     */
    (void)source;
    (void)destination;
    (void)target;
    (void)replacement;
    (void)count;
    return FILE_STATUS_OPEN_ERROR;
}
