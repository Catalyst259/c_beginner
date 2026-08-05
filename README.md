# Lab 6：链表任务队列管理器

> “Bad programmers worry about the code. Good programmers worry about data structures and their relationships.” — Linus Torvalds

## 本 Lab 学什么

前面的 Lab 已经练习过结构体、指针和动态内存。本 Lab 把这些知识组合成单链表：每个任务节点分别分配在堆上，并通过 `next` 指针组成任务队列。你会练习创建和完整释放链表、遍历查找、在任意位置插入、断开并删除节点，最后原地反转链表中的一个区间。

五个 Task 独立评分。后一个 Task 不调用前一个 Task 的公开函数，因此即使前面的实现尚未完成，也可以单独获得后续 Task 的反馈。编译和评分启用 AddressSanitizer、UndefinedBehaviorSanitizer 与泄漏检查。

## 本 Lab 要修改的文件

- `src/lab06.c`

`src/main.c` 已负责读取输入、验证任务数据、建立评分所需的辅助链表并打印结果；`include/lab06.h` 给出了评分器直接调用的固定接口。不要修改公开结构体、函数名称、参数或返回类型。

## 输入/输出与函数契约

一个任务和一个链表节点分别表示为：

```c
typedef struct {
    int id;
    int priority;
} Task;

typedef struct TaskNode {
    Task task;
    struct TaskNode *next;
} TaskNode;
```

队列包含 0–20 项任务。`id` 范围为 1–9999，同一队列中不能重复；`priority` 范围为 1–5。所有位置使用零基下标。输入由任意空白分隔的整数组成，必须恰好包含当前 Task 需要的字段。

### Task 1：创建并释放任务队列

输入 Task、节点数量及每个节点的 `id priority`：

```text
1 3 101 3 202 5 303 2
```

输出：

```text
Queue: 101(3) 202(5) 303(2)
```

实现 `task_list_build(head, tasks, count)`，为每个任务分别调用 `malloc`，按输入顺序连接节点。成功返回 `1`；分配失败时返回 `0`，释放已经创建的所有节点，并保持 `*head == NULL`。`count == 0` 合法，表示成功创建空队列。

同时实现 `task_list_destroy(head)`：释放从 `*head` 可达的全部节点，最后把 `*head` 设为 `NULL`。传入 `NULL`、销毁空队列或对同一头指针重复调用都必须安全。

### Task 2：查找任务

输入 Task、节点数量、目标 ID，再输入队列内容：

```text
2 3 202 101 3 202 5 303 2
```

输出：

```text
Found task: id=202 priority=5
```

实现 `task_list_find(head, id)`，从头开始遍历并返回匹配节点在原链表中的地址。不存在时返回 `NULL`，程序输出 `Task not found`。查找不得修改节点或链接。

### Task 3：按位置插入任务

输入 Task、原节点数量、插入下标、新任务及原队列：

```text
3 3 1 404 4 101 3 202 5 303 2
```

输出：

```text
Queue after insert: 101(3) 404(4) 202(5) 303(2)
```

实现 `task_list_insert(head, index, task)`。合法位置为 `0..length`，包括空表的下标 0、头部和尾部。函数应先确认下标合法，再分配新节点并修改链接。成功返回 `1`；下标非法或 `malloc` 失败时返回 `0`，原链表必须完全不变。

### Task 4：按 ID 删除任务

输入 Task、节点数量、待删除 ID 和原队列：

```text
4 3 202 101 3 202 5 303 2
```

输出：

```text
Removed task: id=202 priority=5
Queue after remove: 101(3) 303(2)
```

实现 `task_list_remove(head, id, removed)`。找到节点时，先保存任务数据，再让前一条链接跳过该节点，释放节点，写入 `*removed` 并返回 `1`。未找到时返回 `0`，链表与调用者原来的 `*removed` 都保持不变。删除唯一节点后头指针应变为 `NULL`。

### Task 5：原地反转链表区间

输入 Task、节点数量、区间首尾下标及队列：

```text
5 5 1 3 101 3 202 5 303 2 404 4 505 1
```

输出：

```text
Queue after reverse: 101(3) 404(4) 303(2) 202(5) 505(1)
```

实现 `task_list_reverse_range(head, first, last)`，原地反转闭区间 `[first, last]`：

- 只能修改 `next` 链接，不分配或释放节点，也不能交换节点中的 `Task` 数据。
- 必须重新连接区间前驱、反转后的区间头尾以及区间后继。
- `first == last` 合法，链表保持原样并返回 `1`。
- `first > last` 或任一端点越界时返回 `0`，且链表完全不变。因此必须先验证整个区间，再开始修改链接。

未知 Task、缺项、多项、重复 ID、字段越界或非法下标统一输出：

```text
Error: invalid input
```

合法操作遇到动态分配失败时输出：

```text
Error: allocation failed
```

## Task 与反馈分

| Task | 分数 |
| --- | ---: |
| 创建并释放任务队列 | 15 |
| 查找任务 | 15 |
| 按位置插入任务 | 20 |
| 按 ID 删除任务 | 20 |
| 原地反转链表区间 | 30 |

每项使用只调用本 Task 函数的独立 harness 和对应 CLI 用例检查。前一个 Task 未完成不会阻止后续正确实现单独得分。结果写入 `build/grade.json`。

## 本地运行

```bash
make
./build/lab06
make grade
```

## 完成与 push 流程

确认 `make grade` 显示 `总分：100/100` 后提交并推送：

```bash
git status
git add src/lab06.c
git commit -m "Complete lab06 task queue"
git push
```

GitHub Actions 会再次运行同一个 `make grade`，上传 `build/grade.json`，并显示当前反馈分。

## 常见错误/调试提示

- `head` 保存第一个节点的地址；需要替换头节点时，函数参数必须是 `TaskNode **`。
- 遍历前保存 `current->next`，再 `free(current)`；释放后不能继续读取原节点。
- 插入和删除头节点时没有前驱节点，使用“指向链接的指针”可以统一处理头部与中间位置。
- `malloc(sizeof(TaskNode *))` 只分配了一个指针的空间；节点应使用 `sizeof(*node)`。
- 销毁链表后要把头指针设为 `NULL`，否则它仍是一个悬空指针。
- 反转区间后不要遗漏区间两端的外部链接，否则会丢失节点或形成环。
- 修改链接前先确认下标有效，才能保证失败时原链表不变。
- 编译器警告在本项目中视为错误；先修复 GCC 输出的第一条诊断，再重新运行 `make grade`。
