#include <stdio.h>

int main(void) {
    double a, b;
    char op;

    if (scanf("%lf %c %lf", &a, &op, &b) != 3) {
        printf("Error: invalid input\n");
        return 0;
    }

    int c;
    do {
        c = getchar();
    } while (c == ' ' || c == '\t' || c == '\r' || c == '\n');
    if (c != EOF) {
        printf("Error: invalid input\n");
        return 0;
    }

    if (a < 0 || b < 0) {
        printf("Error: invalid input\n");
        return 0;
    }

    if (op == '+') {
        printf("Combined budget: %.2f\n", a + b);
    } else if (op == '-') {
        printf("Remaining budget: %.2f\n", a - b);
    } else if (op == '*') {
        printf("Total cost: %.2f\n", a * b);
    } else if (op == '/') {
        if (b == 0.0) {
            printf("Error: division by zero\n");
            return 0;
        }
        printf("Per-person cost: %.2f\n", a / b);
    } else {
        printf("Error: invalid input\n");
    }

    return 0;
}
