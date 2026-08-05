#ifndef LAB05_H
#define LAB05_H

typedef enum {
    CALCULATOR_OK,
    CALCULATOR_INVALID_EXPRESSION,
    CALCULATOR_DIVISION_BY_ZERO,
    CALCULATOR_NEGATIVE_EXPONENT,
    CALCULATOR_OVERFLOW
} CalculatorStatus;

/*
 * Evaluates one integer infix expression.
 *
 * Supported operators are +, -, *, /, and ^, together with unary +/-,
 * parentheses, and arbitrary whitespace between tokens. Division truncates
 * toward zero and exponentiation is right-associative. On success, stores the
 * value in *result and returns CALCULATOR_OK. On failure, returns a specific
 * error status and leaves *result unchanged.
 *
 * Precondition: expression and result are non-NULL.
 */
CalculatorStatus evaluate_expression(const char *expression,
                                     long long *result);

#endif
