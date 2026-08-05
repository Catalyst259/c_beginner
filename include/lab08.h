#ifndef LAB08_H
#define LAB08_H

#include <stddef.h>

#define LAB08_OUTPUT_CAPACITY 1024

typedef enum {
    PROCESS_STATUS_OK,
    PROCESS_STATUS_FORK_ERROR,
    PROCESS_STATUS_PIPE_ERROR,
    PROCESS_STATUS_READ_ERROR,
    PROCESS_STATUS_WAIT_ERROR,
    PROCESS_STATUS_TOO_LARGE
} ProcessStatus;

typedef enum {
    PROCESS_EXITED,
    PROCESS_SIGNALED
} ProcessOutcome;

typedef struct {
    ProcessOutcome outcome;
    int value;
} ProcessResult;

/*
 * Forks one child that immediately exits with exit_code, then waits for it.
 * Precondition: 0 <= exit_code <= 255 and result is non-NULL.
 * On success, stores the child's termination result. On failure, leaves
 * *result unchanged.
 */
ProcessStatus spawn_exit_child(int exit_code, ProcessResult *result);

/*
 * Runs argv[0] using execvp and waits for the child.
 * Precondition: argv, argv[0], and result are non-NULL and argv is terminated
 * by NULL. An execvp failure is reported as a normal child exit with code 127.
 * On a parent-side failure, *result remains unchanged.
 */
ProcessStatus run_command(char *const argv[], ProcessResult *result);

/*
 * Runs argv with standard output replaced by output_path. The destination is
 * created or truncated with mode 0644 (subject to umask). A child-side open or
 * dup2 failure exits with code 126; execvp failure exits with code 127.
 * On a parent-side failure, *result remains unchanged.
 */
ProcessStatus run_command_redirected(char *const argv[],
                                     const char *output_path,
                                     ProcessResult *result);

/*
 * Captures all bytes written to the command's standard output. Capacity
 * includes the final '\0'. On success, output is null-terminated, *length is
 * the byte count, and *result describes the child. If the output does not fit,
 * returns PROCESS_STATUS_TOO_LARGE after draining and reaping the child.
 * Every failure leaves output, *length, and *result unchanged.
 */
ProcessStatus capture_command_output(char *const argv[],
                                     char output[], size_t capacity,
                                     size_t *length, ProcessResult *result);

/*
 * Runs left_argv | right_argv. The left child's stdout feeds the right child's
 * stdin; every other standard stream is inherited. On success, results[0]
 * describes the left child and results[1] the right child. A parent-side
 * failure leaves both elements unchanged.
 */
ProcessStatus run_pipeline(char *const left_argv[],
                           char *const right_argv[],
                           ProcessResult results[2]);

#endif
