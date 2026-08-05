#include "lab05.h"

#include <ctype.h>
#include <limits.h>
#include <stddef.h>

typedef struct {
    const char *cursor;
    CalculatorStatus status;
} Parser;

static long long parse_expression(Parser *parser);
static long long parse_unary(Parser *parser);

static void skip_whitespace(Parser *parser) {
    while (isspace((unsigned char)*parser->cursor)) {
        parser->cursor++;
    }
}

static void fail(Parser *parser, CalculatorStatus status) {
    if (parser->status == CALCULATOR_OK) {
        parser->status = status;
    }
}

static CalculatorStatus checked_add(long long left, long long right,
                                    long long *result) {
    if ((right > 0 && left > LLONG_MAX - right) ||
        (right < 0 && left < LLONG_MIN - right)) {
        return CALCULATOR_OVERFLOW;
    }
    *result = left + right;
    return CALCULATOR_OK;
}

static CalculatorStatus checked_subtract(long long left, long long right,
                                         long long *result) {
    if ((right > 0 && left < LLONG_MIN + right) ||
        (right < 0 && left > LLONG_MAX + right)) {
        return CALCULATOR_OVERFLOW;
    }
    *result = left - right;
    return CALCULATOR_OK;
}

static CalculatorStatus checked_multiply(long long left, long long right,
                                         long long *result) {
    if ((left > 0 && right > 0 && left > LLONG_MAX / right) ||
        (left > 0 && right < 0 && right < LLONG_MIN / left) ||
        (left < 0 && right > 0 && left < LLONG_MIN / right) ||
        (left < 0 && right < 0 && left < LLONG_MAX / right)) {
        return CALCULATOR_OVERFLOW;
    }
    *result = left * right;
    return CALCULATOR_OK;
}

static CalculatorStatus checked_divide(long long left, long long right,
                                       long long *result) {
    if (right == 0) {
        return CALCULATOR_DIVISION_BY_ZERO;
    }
    if (left == LLONG_MIN && right == -1) {
        return CALCULATOR_OVERFLOW;
    }
    *result = left / right;
    return CALCULATOR_OK;
}

static CalculatorStatus checked_negate(long long value, long long *result) {
    if (value == LLONG_MIN) {
        return CALCULATOR_OVERFLOW;
    }
    *result = -value;
    return CALCULATOR_OK;
}

static CalculatorStatus checked_power(long long base, long long exponent,
                                      long long *result) {
    long long accumulated = 1;
    long long factor = base;
    CalculatorStatus status;

    if (exponent < 0) {
        return CALCULATOR_NEGATIVE_EXPONENT;
    }
    while (exponent > 0) {
        if (exponent % 2 != 0) {
            status = checked_multiply(accumulated, factor, &accumulated);
            if (status != CALCULATOR_OK) {
                return status;
            }
        }
        exponent /= 2;
        if (exponent > 0) {
            status = checked_multiply(factor, factor, &factor);
            if (status != CALCULATOR_OK) {
                return status;
            }
        }
    }
    *result = accumulated;
    return CALCULATOR_OK;
}

static long long parse_number(Parser *parser) {
    /*
     * TODO 1: Skip whitespace, require at least one digit, then accumulate
     * digits while advancing cursor. Before value * 10 + digit, compare
     * value with (LLONG_MAX - digit) / 10 and report overflow if needed.
     */
    (void)parser;
    return 0;
}

static long long parse_primary(Parser *parser) {
    skip_whitespace(parser);
    if (*parser->cursor != '(') {
        return parse_number(parser);
    }
    /*
     * TODO 4: Consume '(', parse a complete expression recursively, require
     * and consume the matching ')', then return the inner value.
     */
    fail(parser, CALCULATOR_INVALID_EXPRESSION);
    return 0;
}

static long long parse_power(Parser *parser) {
    /*
     * TODO 3: Parse a primary. If '^' follows, consume it, recursively parse
     * the unary exponent, and call checked_power. Otherwise return the base.
     */
    (void)checked_power;
    return parse_primary(parser);
}

static long long parse_unary(Parser *parser) {
    /*
     * TODO 5: When the next token is unary '+' or '-', consume it and call
     * parse_unary recursively. Use checked_negate for '-'. Without a sign,
     * delegate to parse_power.
     */
    (void)checked_negate;
    return parse_power(parser);
}

static long long parse_term(Parser *parser) {
    /*
     * TODO 2a: Parse the left unary value, then loop over '*' and '/'. For
     * each operator, parse the right unary value and call the matching
     * checked arithmetic helper.
     */
    (void)checked_multiply;
    (void)checked_divide;
    return parse_unary(parser);
}

static long long parse_expression(Parser *parser) {
    /*
     * TODO 2b: Parse the left term, then loop over '+' and '-'. Parse each
     * right term and combine values through the checked arithmetic helpers.
     */
    (void)checked_add;
    (void)checked_subtract;
    return parse_term(parser);
}

CalculatorStatus evaluate_expression(const char *expression,
                                     long long *result) {
    Parser parser;
    long long value;

    if (expression == NULL || result == NULL) {
        return CALCULATOR_INVALID_EXPRESSION;
    }
    parser.cursor = expression;
    parser.status = CALCULATOR_OK;
    value = parse_expression(&parser);
    if (parser.status != CALCULATOR_OK) {
        return parser.status;
    }
    skip_whitespace(&parser);
    if (*parser.cursor != '\0') {
        return CALCULATOR_INVALID_EXPRESSION;
    }
    *result = value;
    return CALCULATOR_OK;
}
