# Lab 1：游戏背包整理器

> “An algorithm must be seen to be believed.” — Donald E. Knuth

## 本 Lab 学什么

本练习用一个装有固定数量物品的游戏背包，带你感受循环与数组的威力。你会从遍历求和开始，逐步完成查找、筛选、原地排序，最后用双重循环找出受战力上限约束的最佳双物品组合。

五个 Task 都有独立的任务编号、函数接口和评分反馈。你可以一次只运行一个 Task 来调试；`make grade` 会检查全部 Task，只有全部完成才能得到 `100/100`。

## 本 Lab 要修改的文件

- `src/lab01.c`

`src/main.c` 已经负责读取输入和分发任务，`include/lab01.h` 给出了评分器会直接调用的固定接口。不要修改公开函数的名称和参数。

## 输入/输出与函数契约

背包包含 1–20 件物品，每件物品用一个 0–100 的整数表示战力。所有位置都使用 C 数组的零基下标：第一件物品的下标是 `0`。

### Task 1：计算总战力

输入 `1 count items...`，使用循环累加所有物品：

```text
1 5 20 80 50 10 90
```

输出：

```text
Total power: 250
```

实现 `total_power(items, count)`，返回数组前 `count` 项的总和。

### Task 2：寻找最强物品

输入 `2 count items...`：

```text
2 5 20 90 50 90 10
```

输出：

```text
Strongest index: 1
```

实现 `strongest_item_index(items, count)`。如果最大战力出现多次，返回第一次出现的零基下标。

### Task 3：按门槛筛选

输入 `3 count minimum items...`：

```text
3 5 50 20 80 50 10 90
```

输出：

```text
Qualified items: 80 50 90
```

实现 `collect_qualified(items, count, minimum, qualified)`，将所有大于等于门槛的战力按原顺序复制到 `qualified`，并返回复制数量。没有物品达标时程序输出 `Qualified items: none`。

### Task 4：整理背包

输入 `4 count items...`：

```text
4 5 20 80 50 10 90
```

输出：

```text
Sorted items: 90 80 50 20 10
```

实现 `sort_descending(items, count)`，使用循环交换元素，将原数组按战力从高到低排列。不要调用库排序函数。

### Task 5：最佳双物品组合

输入 `5 count limit items...`：

```text
5 5 130 20 80 50 10 90
```

输出：

```text
Best pair power: 130
```

实现 `best_pair_power(items, count, limit)`：选择两个不同位置的物品，在战力和不超过 `limit` 的前提下让总和最大。不能把同一件物品使用两次；无合法组合时返回 `-1`，程序输出 `Best pair power: none`。

所有输入必须恰好包含当前任务需要的整数。未知任务号、缺项、额外内容，以及数量、战力、门槛或上限越界都会输出：

```text
Error: invalid input
```

`include/lab01.h` 中的函数以前置条件保证数组和参数合法；你的实现只需满足每个函数注明的后置结果。

## Task 与反馈分

| Task | 分数 |
| --- | ---: |
| 总战力 | 15 |
| 最强物品 | 15 |
| 门槛筛选 | 20 |
| 背包排序 | 20 |
| 最佳双物品组合 | 30 |

每一项由独立函数测试和对应的程序输入检查。后面的 Task 没完成，不会抹掉前面已经获得的反馈分；五项全部通过才会得到满分。详细结果同时写入 `build/grade.json`。

## 本地运行

```bash
make
./build/lab01
make grade
```

运行程序后手动输入任意一个 Task 的样例。修改某个函数后，可以再次选择对应任务号单独观察结果，再用 `make grade` 检查全部 Task。

## 完成与 push 流程

确认 `make grade` 显示 `总分：100/100` 后提交并推送：

```bash
git status
git add src/lab01.c
git commit -m "Complete lab01 inventory organizer"
git push
```

GitHub Actions 会再次运行同一个 `make grade`，上传 `build/grade.json`，并显示当前反馈分。

## 常见错误/调试提示

- 数组第一个元素的下标是 `0`，最后一个元素的下标是 `count - 1`。
- 循环条件通常使用 `index < count`；写成 `<=` 会访问数组范围之外。
- 求最大值时应保存最强物品的下标，而不只是保存它的战力。
- 筛选数组需要单独维护输出数量，不能直接用输入下标作为输出下标。
- 交换两个元素需要一个临时变量，否则先写入的值会丢失。
- 最佳组合的第二层循环从 `first + 1` 开始，就不会重复使用同一位置或把同一对物品检查两次。
- 可临时用 `printf` 打印下标和中间结果；提交前删除调试输出。
- 编译器警告在本项目中是错误。先修复最前面的 GCC 诊断，再重新运行 `make grade`。
