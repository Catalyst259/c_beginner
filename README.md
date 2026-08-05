# Lab 3：冒险者队伍管理器

> “Pointers are the heart and soul of C.” — Dennis Ritchie

## 本 Lab 学什么

本练习用一支冒险者队伍串起指针与结构体的核心操作。你会先把普通变量的地址传给函数并通过解引用修改它们，再使用结构体指针读写字段，最后在结构体数组中查找元素并原地完成阵容排名。

Lab 1 已练习循环与数组，Lab 2 已练习指针在字符串中的移动。本 Lab 不使用动态内存和复杂字符串处理，重点是理解“数据存在哪里、指针指向谁，以及通过这个地址能修改什么”。

五个 Task 都有独立评分。完成练习只需要修改 `src/lab03.c` 中的 TODO；`src/main.c`、`include/lab03.h` 和评分器均已提供，不要修改公开函数的名称、参数或返回类型。

## 数据模型与输入规则

一名冒险者由结构体表示：

```c
typedef struct {
    int id;
    int health;
    int attack;
} Adventurer;
```

- `id` 范围为 1–9999；同一支队伍中的 `id` 不能重复。
- `health` 和 `attack` 范围均为 0–100。
- 队伍包含 1–20 名冒险者。
- 输入中的所有字段都是整数，可以由任意空白分隔，但不能缺少或多出字段。
- 任意非法输入统一输出 `Error: invalid input`。

## Task 1：交换属性

输入 Task 编号、生命值和攻击力：

```text
1 80 35
```

输出：

```text
Swapped stats: 35 80
```

实现 `swap_stats(health, attack)`。`src/main.c` 使用 `&health` 和 `&attack` 取得两个变量的地址；函数内部使用 `*health` 和 `*attack` 访问并交换原变量的值。两个指针指向同一个对象时，该对象应保持不变。

## Task 2：初始化冒险者

输入 Task 编号以及 `id health attack`：

```text
2 101 80 35
```

输出：

```text
Adventurer: id=101 health=80 attack=35
```

实现 `initialize_adventurer(adventurer, id, health, attack)`，通过结构体指针写入所有字段。`adventurer->health` 与 `(*adventurer).health` 含义相同；前一种写法更简洁。

## Task 3：计算战力

输入：

```text
3 101 80 35
```

输出：

```text
Combat power: 150
```

实现 `combat_power(adventurer)`，使用公式：

```text
health + attack * 2
```

参数类型是 `const Adventurer *`，可以读取它所指向的结构体，但不能通过该指针修改字段。

## Task 4：查找队员

输入格式为 `4 count target_id`，后面跟随 `count` 组 `id health attack`：

```text
4 3 202 101 80 35 202 60 50 303 100 20
```

找到时输出原数组中的记录：

```text
Found adventurer: id=202 health=60 attack=50
```

没有对应 `id` 时输出：

```text
Adventurer not found
```

实现 `find_adventurer(team, count, id)`。返回匹配元素在原数组中的地址，而不是局部副本；不存在时返回 `NULL`。

## Task 5：阵容排名

输入格式为 `5 count`，后面跟随 `count` 组 `id health attack`：

```text
5 3 101 80 35 202 60 50 303 100 20
```

三人的战力分别是 150、160 和 140，因此输出：

```text
Ranked IDs: 202 101 303
```

实现 `rank_team(team, count)`：

- 按 `combat_power` 从高到低原地排列结构体数组。
- 战力相同时，`id` 较小者排在前面。
- 交换时必须移动完整的 `Adventurer`，不能只交换 `id`。
- 使用循环和结构体交换，不调用 `qsort`。
- `count` 为 0 或 1 的直接函数调用也必须安全处理。

## 函数契约

`include/lab03.h` 给出了评分器会直接调用的固定接口和完整前置、后置条件：

- `swap_stats` 修改两个指针所指向的整数。
- `initialize_adventurer` 写入一整个结构体对象。
- `combat_power` 只读结构体并返回战力。
- `find_adventurer` 返回原结构体数组中的元素地址或 `NULL`。
- `rank_team` 原地重排数组，同时保留每条完整记录。

## Task 与反馈分

| Task | 分数 |
| --- | ---: |
| 交换属性 | 15 |
| 初始化冒险者 | 15 |
| 计算战力 | 15 |
| 查找队员 | 20 |
| 阵容排名 | 35 |

`make grade` 会独立检查五个函数及对应程序行为，并将相同结果写入 `build/grade.json`。

## 本地运行

```bash
make
./build/lab03
make grade
```

## 完成与 push 流程

确认 `make grade` 显示 `总分：100/100` 后提交并推送：

```bash
git status
git add src/lab03.c
git commit -m "Complete lab03 adventurer manager"
git push
```

GitHub Actions 会再次运行评分器并上传 `build/grade.json`。

## 常见错误与调试提示

- `&value` 取得变量地址，`*pointer` 访问该地址中的值；不要混淆 `pointer++` 与 `(*pointer)++`。
- 结构体对象使用 `.`，结构体指针使用 `->`。
- `find_adventurer` 必须返回数组元素地址，不能返回局部结构体变量的地址。
- 交换排名元素时使用临时 `Adventurer`，确保 `id`、`health` 和 `attack` 一起移动。
- 比较排名时先比较战力，再处理 `id` 的平局规则。
- 编译器警告在本项目中视为错误；先修复最前面的 GCC 诊断，再重新运行 `make grade`。
