#include "lab05.h"

#include <stdio.h>

#define INPUT_CAPACITY 256

int main(void) {
    char input[INPUT_CAPACITY + 1];
    size_t length;
    long long result;
    CalculatorStatus status;

    length = fread(input, 1, INPUT_CAPACITY, stdin);
    if (ferror(stdin) || length == INPUT_CAPACITY) {
        printf("Error: invalid expression\n");
        return 0;
    }
    input[length] = '\0';
    status = evaluate_expression(input, &result);
    if (status == CALCULATOR_OK) {
        printf("Result: %lld\n", result);
    } else if (status == CALCULATOR_DIVISION_BY_ZERO) {
        printf("Error: division by zero\n");
    } else if (status == CALCULATOR_NEGATIVE_EXPONENT) {
        printf("Error: negative exponent\n");
    } else if (status == CALCULATOR_OVERFLOW) {
        printf("Error: arithmetic overflow\n");
    } else {
        printf("Error: invalid expression\n");
    }
    return 0;
}
