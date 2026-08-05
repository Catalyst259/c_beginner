# Lab 2：社团消息编辑器

> “Programs must be written for people to read, and only incidentally for machines to execute.” — Harold Abelson and Gerald Jay Sussman

## 本 Lab 学什么

本练习用一个固定容量的消息缓冲区，带你理解指针如何在字符串中移动。你会从只读指针遍历开始，逐步完成返回位置指针、使用首尾指针原地反转、安全复制，最后实现带容量保护的批量子串替换。

五个 Task 都有独立的任务编号、函数接口和评分反馈。你可以一次只运行一个 Task 来调试；`make grade` 会检查全部 Task，只有全部完成才能得到 `100/100`。

本 Lab 只使用固定容量字符数组，不需要也不应使用 `malloc` 或 `free`。自动评分检查函数契约与程序行为，不根据变量名或某一种特定写法评分。

## 本 Lab 要修改的文件

- `src/lab02.c`

`src/main.c` 已经负责按行读取输入、校验和分发任务，`include/lab02.h` 给出了评分器会直接调用的固定接口。不要修改公开函数的名称、参数或返回类型。

## 输入/输出与函数契约

消息使用最多 127 个可打印 ASCII 字符，可以包含空格，也可以是空字符串。缓冲区容量 `LAB02_TEXT_CAPACITY` 为 128，容量计算必须为结尾的 `'\0'` 留出一个字节。

程序输入按行组织。第一行只放 Task 编号，后续各行的含义由 Task 决定。消息行的首尾空格也是消息内容，不会被忽略。

### Task 1：计算消息长度

输入 Task 编号和消息：

```text
1
hello world
```

输出：

```text
Text length: 11
```

实现 `text_length(text)`。让指针从第一个字符移动到 `'\0'`，返回经过的字符数。不要把结尾的 `'\0'` 计入长度。

### Task 2：查找第一个字符

第二行是恰好一个目标字符，第三行是消息：

```text
2
a
banana
```

输出：

```text
First occurrence: 1
```

实现 `find_first_character(text, target)`，返回目标字符第一次出现位置的指针。不存在时返回 `NULL`，程序输出 `First occurrence: none`。`src/main.c` 会用返回指针与消息首地址的差计算零基下标。

目标字符也可以是一个空格：此时第二行只包含一个空格。

### Task 3：反转消息

输入：

```text
3
pointer
```

输出：

```text
Reversed text: retniop
```

实现 `reverse_text(text)`。使用分别指向首字符和尾字符的指针交换内容，原地反转字符串。空字符串和单字符字符串应保持不变。

### Task 4：安全复制

第二行是目标缓冲区容量，第三行是源消息：

```text
4
6
hello
```

输出：

```text
Copied text: hello
```

实现 `copy_text(destination, capacity, source)`。`hello` 的五个字符加上 `'\0'` 恰好需要容量 6，因此复制成功并返回 `1`。

如果容量不足，函数返回 `0`，并保证 `destination` 中原有内容完全不变。程序输出：

```text
Error: insufficient capacity
```

源和目标缓冲区互不重叠；你不需要处理同一数组内部的重叠复制。

### Task 5：批量子串替换

第二行是非空目标子串，第三行是替换子串，第四行是消息：

```text
5
cat
dog
cat and cat
```

输出：

```text
Replacements: 2; Text: dog and dog
```

实现 `replace_all(text, capacity, target, replacement)`，从左到右替换所有互不重叠的目标子串并返回替换次数：

- 新插入的内容不再参与匹配。例如把 `a` 替换为 `aa` 只替换原有的 `a`。
- 匹配候选重叠时取最靠左的一项。例如在 `aaa` 中把 `aa` 替换为 `X`，结果为 `Xa`，返回 `1`。
- `replacement` 可以是空字符串，此时相当于删除；`target` 不可为空。
- 没有匹配时返回 `0`，消息保持不变。
- 如果最终文本连同 `'\0'` 放不进容量，返回 `-1`，并保证原消息完全不变；程序输出 `Error: insufficient capacity`。

所有输入行都必须满足当前 Task 的要求。未知任务号、缺行、额外的非空白内容、非法容量、超长行、控制字符、Task 2 目标不是单个字符或 Task 5 目标为空，统一输出：

```text
Error: invalid input
```

`include/lab02.h` 中的函数以前置条件保证参数和指针合法；你的实现只需满足每个函数注明的后置结果。

## Task 与反馈分

| Task | 分数 |
| --- | ---: |
| 消息长度 | 15 |
| 查找字符 | 15 |
| 反转消息 | 20 |
| 安全复制 | 20 |
| 批量子串替换 | 30 |

每一项由独立函数测试和对应的程序输入检查。后面的 Task 没完成，不会抹掉前面已经获得的反馈分；五项全部通过才会得到满分。详细结果同时写入 `build/grade.json`。

## 本地运行

```bash
make
./build/lab02
make grade
```

运行程序后手动逐行输入任意一个 Task 的样例。修改某个函数后，可以再次选择对应任务号观察结果，再用 `make grade` 检查全部 Task。

## 完成与 push 流程

确认 `make grade` 显示 `总分：100/100` 后提交并推送：

```bash
git status
git add src/lab02.c
git commit -m "Complete lab02 message editor"
git push
```

GitHub Actions 会再次运行同一个 `make grade`，上传 `build/grade.json`，并显示当前反馈分。

## 常见错误/调试提示

- C 字符串以 `'\0'` 结束；容量检查忘记这个字节会造成越界。
- `pointer++` 移动指针，`(*pointer)++` 修改指针当前指向的字符，两者含义不同。
- 只读输入使用 `const char *`；不要通过它修改字符。
- Task 2 要返回消息中的地址，不要返回局部数组中的地址。
- 反转空字符串时不存在“最后一个字符”，先处理长度小于 2 的情况。
- 安全复制应先确认完整字符串能够放下，再写入目标；否则无法保证失败时内容不变。
- 子串替换要区分原始输入和新插入内容，扩张文本前也要先确定最终容量。
- 可临时用 `printf("%td\n", pointer - text)` 观察指针位置；提交前删除调试输出。
- 编译器警告在本项目中是错误。先修复最前面的 GCC 诊断，再重新运行 `make grade`。
