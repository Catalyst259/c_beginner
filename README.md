# Lab 5：中缀表达式计算器

> “To iterate is human, to recurse divine.” — L. Peter Deutsch

## 本 Lab 学什么

前四个 Lab 已经练习过循环、数组、指针、结构体和动态内存。本 Lab 是第一阶段的收官项目：你会把一串普通的数学表达式拆成层次清楚的语法，并用递归下降的方法计算结果。

最终的计算器支持多步整数运算、`+`、`-`、`*`、`/`、`^`、一元正负号以及任意嵌套的小括号。例如：

```text
2 + 3 * (4 - 1)^2
```

结果为：

```text
Result: 29
```

直接一次写完整个解析器很困难，因此五个 Task 按解析层逐步开放能力。starter 已提供游标状态、空白处理、顶层接口和安全整数运算；你只需要集中完成 `parse_number`、`parse_term`、`parse_expression`、`parse_power`、`parse_primary` 和 `parse_unary` 中标出的 TODO。

## 本 Lab 要修改的文件

- `src/lab05.c`

`src/main.c` 已负责读取输入和输出错误；`include/lab05.h` 给出了评分器会直接调用的固定接口。不要修改公开枚举、函数名称、参数或返回类型。

## 输入/输出与函数契约

程序从标准输入读取一个不超过 255 字节的表达式，不打印菜单或输入提示。运算符、数字和括号之间允许任意空白。

成功时输出：

```text
Result: VALUE
```

计算使用 `long long`。除法向零截断，因此 `20 / 3` 的结果是 `6`。乘方符号为单个 `^`，它从右向左结合：

```text
2^3^2 == 2^(3^2) == 512
```

乘方优先于一元负号，因此：

```text
-2^2   == -(2^2)  == -4
(-2)^2 == 4
```

支持 `-2`、`2 * -3`、`-(1 + 2)` 和 `--2`。指数必须大于等于零；`0^0` 在本 Lab 中定义为 `1`。不支持小数、`**` 或省略乘号的 `2(3)`。

错误输出固定为：

```text
Error: invalid expression
Error: division by zero
Error: negative exponent
Error: arithmetic overflow
```

实现 `evaluate_expression(expression, result)`：成功时返回 `CALCULATOR_OK` 并写入结果；失败时返回对应状态，且不能修改调用者原来的 `*result`。

## 先读懂这份文法

每一行负责一种优先级。越靠下，结合得越紧：

```text
expression = term { ("+" | "-") term }
term       = unary { ("*" | "/") unary }
unary      = ("+" | "-") unary | power
power      = primary [ "^" unary ]
primary    = number | "(" expression ")"
number     = digit { digit }
```

`Parser.cursor` 永远指向“下一个还没有处理的字符”。每层函数只消费自己认识的部分，然后把游标留给调用者。例如解析 `2 + 3 * 4` 时：

1. `parse_expression` 先让 `parse_term` 读出 `2`。
2. 它看见 `+`，再让 `parse_term` 读取右侧。
3. 第二次 `parse_term` 先读出 `3`，发现 `*` 后继续读出 `4`。
4. `parse_term` 返回 `12`，最外层再得到 `2 + 12 == 14`。

每次检查当前字符前先调用 `skip_whitespace`。一旦 `parser->status` 不再是 `CALCULATOR_OK`，立即停止当前层并把错误交回上层，不要继续移动游标。

### Task 1：读取整数与移动游标

先实现 `parse_number`。跳过开头空白，确认当前字符是数字，然后逐位完成：

```text
value = value * 10 + digit
```

每读一位都要移动 `cursor`。starter 已留下不会触发溢出的判断位置；没有数字时设置 `CALCULATOR_INVALID_EXPRESSION`，文字超过 `LLONG_MAX` 时设置 `CALCULATOR_OVERFLOW`。

完成后，单个整数已经可以通过整个程序运行：

```text
42
```

```text
Result: 42
```

### Task 2：四则多步运算

实现 `parse_term` 和 `parse_expression` 中的循环。

- `parse_term` 调用 `parse_unary` 取得左值，只循环处理 `*` 和 `/`。
- `parse_expression` 调用 `parse_term` 取得左值，只循环处理 `+` 和 `-`。
- 每次发现属于本层的运算符：保存运算符、移动游标、解析右值、调用相应的 `checked_*` 辅助函数，再把结果作为新的左值。
- 看见不属于本层的字符时直接结束循环，不能把它当作错误；它可能属于外层，也可能由顶层统一发现。

这种“先得到左值，再循环吸收同级运算符”的结构同时保证优先级和同级左结合。

### Task 3：乘方与右结合

实现 `parse_power`。先用 `parse_primary` 读取底数；如果后面没有 `^`，直接返回底数。

发现 `^` 后，右侧必须调用 `parse_unary`，而不是用循环读取另一个 `primary`。这个递归调用会让 `2^3^2` 先计算右边的 `3^2`。实际乘方和溢出检查已由 `checked_power` 提供。

### Task 4：括号与递归

扩展 `parse_primary`：

- 当前字符不是 `(` 时，仍交给 `parse_number`。
- 当前字符是 `(` 时，先消费它，再递归调用最外层的 `parse_expression`。
- 内部表达式结束后必须找到并消费配对的 `)`；缺失时报告非法表达式。

因为括号内部重新进入完整的 `expression`，同一份代码自然支持任意嵌套，不需要分别处理一层、两层或三层括号。

### Task 5：一元符号与完整表达式

实现 `parse_unary`。没有看到 `+` 或 `-` 时交给 `parse_power`；看到符号时先消费，再递归调用 `parse_unary`。一元 `+` 原样返回，一元 `-` 使用 `checked_negate`。

这里的调用顺序决定 `-2^2 == -4`，也允许 `2^-1` 被完整解析后返回 `CALCULATOR_NEGATIVE_EXPONENT`。完成后，用混合表达式检查所有解析层是否能协作：

```text
2 + 3 * (4 - 1)^2
```

## Task 与反馈分

| Task | 分数 |
| --- | ---: |
| 读取整数与移动游标 | 15 |
| 四则多步运算 | 25 |
| 乘方与右结合 | 20 |
| 括号与递归 | 20 |
| 一元符号与完整表达式 | 20 |

五项都通过同一个 `evaluate_expression` 接口验收，但评分器会分别运行各能力范围的函数测试和程序输入。每项独立记录反馈，不使用“前一项失败就不运行后一项”的门禁。结果写入 `build/grade.json`。

## 本地运行

```bash
make
./build/lab05
make grade
```

建议每完成一个 Task 就运行一次程序样例和 `make grade`。不要等全部函数写完后才第一次编译。

## 完成与 push 流程

确认 `make grade` 显示 `总分：100/100` 后提交并推送：

```bash
git status
git add src/lab05.c
git commit -m "Complete lab05 calculator"
git push
```

GitHub Actions 会再次运行同一个 `make grade`，上传 `build/grade.json`，并显示当前反馈分。

## 常见错误/调试提示

- 不要在每一层都尝试识别所有运算符；一个函数只负责文法中属于自己的那一行。
- 解析右操作数前一定先移动过运算符，否则递归会在同一字符上反复调用。
- `parse_term` 和 `parse_expression` 使用循环是为了左结合；`parse_power` 使用递归是为了右结合。
- 括号内部调用 `parse_expression`，不是只调用 `parse_number`，否则括号里不能出现多步运算。
- 返回错误后不要覆盖 `parser->status`；starter 的 `fail` 会保留最先发现的错误。
- 不要直接写 `left + right` 或 `base * base`；有符号整数溢出属于未定义行为，应调用已提供的 `checked_*` 函数。
- 调用 `isdigit`、`isspace` 等 `ctype` 函数前必须先转换为 `unsigned char`，starter 已展示正确写法。
- 如果结果正确但评分仍失败，检查是否还有未消费的字符、错误状态是否正确，以及失败时有没有改写 `*result`。
- 编译器警告在本项目中视为错误；先修复 GCC 输出的第一条诊断。
