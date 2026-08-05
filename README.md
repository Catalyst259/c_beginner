# Lab 4：冒险队补给列表

> “The only way to learn a new programming language is by writing programs in it.” — Dennis Ritchie

## 本 Lab 学什么

前面的 Lab 已经使用过固定长度数组、指针和结构体。本练习把补给列表搬到堆内存中：你会用 `malloc` 按运行时长度申请空间，用 `free` 交还不再需要的空间，并在扩容时正确转移数组的所有权。

五个 Task 从裸 `int *` 开始，逐步过渡到同时保存 `data`、`size` 和 `capacity` 的 `DynamicArray`。最后一个 Task 要在任意位置插入元素，并在空间不足时自动扩容。

本 Lab 不使用 `realloc`。扩容统一采用“申请新空间、复制元素、释放旧空间”的过程，以便看清每个地址何时有效、由谁负责释放。编译和评分会启用 AddressSanitizer、UndefinedBehaviorSanitizer 与泄漏检查。

## 本 Lab 要修改的文件

- `src/lab04.c`

`src/main.c` 已负责读取输入、校验、输出和各条路径的清理；`include/lab04.h` 给出了评分器会直接调用的固定接口。不要修改公开函数的名称、参数或返回类型。

## 输入/输出与函数契约

所有输入都是由任意空白分隔的整数。数组最多包含 20 个元素；元素本身可以是任意 `int`。输入必须恰好包含当前 Task 所需的字段，未知 Task、缺项、多项、非法数量或非法插入下标统一输出：

```text
Error: invalid input
```

正常的小规模练习不会耗尽内存；如果系统拒绝一次合法分配，程序输出 `Error: allocation failed`。

### Task 1：分配并初始化堆数组

输入 `1 count fill`：

```text
1 4 -2
```

输出：

```text
Filled array: -2 -2 -2 -2
```

实现 `create_filled_array(count, value)`：用 `malloc` 申请 `count` 个 `int`，将每项初始化为 `value` 并返回首地址。`count == 0`、字节数溢出或分配失败时返回 `NULL`。

使用 `count * sizeof(*data)` 计算字节数。不要把元素数量误当成字节数量，也不要对 `malloc` 返回的地址做强制类型转换。

### Task 2：创建独立副本

输入 `2 count values...`：

```text
2 4 3 -1 8 3
```

输出：

```text
Cloned array: 3 -1 8 3
```

实现 `clone_array(source, count)`：申请一个等长堆数组并逐项复制。返回的新地址必须拥有自己的存储空间；修改副本不能影响源数组。空数组、大小溢出或分配失败返回 `NULL`。

### Task 3：安全扩缩容

输入 `3 old_size new_size fill values...`：

```text
3 3 6 -1 3 6 9
```

输出：

```text
Resized array: 3 6 9 -1 -1 -1
```

实现 `resize_array(data, old_size, new_size, fill)`：

- 通过 `int **data` 修改调用者保存的堆地址。
- 保留前 `min(old_size, new_size)` 项；扩展出来的位置写入 `fill`。
- `new_size == 0` 时释放旧数组、把 `*data` 设为 `NULL` 并返回 `1`。
- 扩缩容时先申请新空间。只有分配和复制都成功后，才能 `free(*data)` 并更新地址。
- 分配失败或大小溢出返回 `0`，旧地址和旧内容必须完全不变。

### Task 4：动态数组生命周期

动态数组结构体定义为：

```c
typedef struct {
    int *data;
    size_t size;
    size_t capacity;
} DynamicArray;
```

输入 `4 capacity`：

```text
4 5
```

输出：

```text
Dynamic array: size=0 capacity=5
```

实现两个函数：

- `dynamic_array_init(array, capacity)` 建立一个 `size == 0` 的空列表。零容量合法；失败时三个字段也必须处于安全空状态。
- `dynamic_array_destroy(array)` 释放 `data` 并把 `data`、`size`、`capacity` 全部重置。对已经销毁的数组再次调用也必须安全。

`size` 表示已经保存多少个元素，`capacity` 表示当前空间最多能容纳多少个元素，两者含义不同。

### Task 5：自动扩容插入

输入 `5 initial_capacity operation_count index value...`。每组 `index value` 都对前一组操作后的数组生效：

```text
5 0 5 0 10 0 5 1 7 3 20 2 15
```

输出：

```text
Dynamic array: 5 7 15 10 20
```

实现 `dynamic_array_insert(array, index, value)`：

- `index` 可以是 `0` 到当前 `size`，其中 `index == size` 表示追加。
- 空间足够时，从数组尾部开始向右移动元素，再写入新值。
- `size == capacity` 时先扩容：容量按 `0 → 4 → 8 → 16...` 增长；已有非零容量总是翻倍。
- 扩容必须使用 `malloc`、复制和 `free`，不要使用 `realloc`。
- 成功返回 `1` 并增加 `size`。
- 下标非法、容量计算溢出或分配失败时返回 `0`，地址、字段和所有旧元素都必须保持不变。

## Task 与反馈分

| Task | 分数 |
| --- | ---: |
| 分配并初始化堆数组 | 15 |
| 创建独立副本 | 15 |
| 安全扩缩容 | 20 |
| 动态数组生命周期 | 20 |
| 自动扩容插入 | 30 |

每项都有独立函数测试和对应程序输入检查。前一个函数没有完成时，后面的正确函数仍可独立获得反馈分。评分器也会模拟 `malloc` 失败并检查失败前后的状态，将结果写入 `build/grade.json`。

## 本地运行

```bash
make
./build/lab04
make grade
```

运行程序后手动输入任意 Task 的样例。sanitizer 报错通常会包含越界地址、释放位置或泄漏来源；先阅读报告最上方的错误类型，再定位第一处指向 `src/lab04.c` 的行号。

## 完成与 push 流程

确认 `make grade` 显示 `总分：100/100` 后提交并推送：

```bash
git status
git add src/lab04.c
git commit -m "Complete lab04 supply list"
git push
```

GitHub Actions 会再次运行同一个 `make grade`，上传 `build/grade.json`，并显示当前反馈分。

## 常见错误/调试提示

- `malloc` 的参数是字节数，不是元素数量；分配后立即检查返回值是否为 `NULL`。
- 每一块成功申请的堆内存最终必须恰好 `free` 一次；`free(NULL)` 是安全的。
- `free(pointer)` 不会自动把变量改成 `NULL`，需要显式赋值。
- 不要在新空间申请成功前释放旧空间，否则失败时无法恢复原数组。
- `int **data` 表示函数需要修改调用者保存的 `int *`；更新地址时写 `*data = new_data`。
- 插入时从后向前搬移元素；从前向后会覆盖还没来得及复制的数据。
- 每次访问数组前确认下标小于 `size`，写入前还要确认空间小于 `capacity`。
- sanitizer 报告不是额外的编译器噪声，而是对越界、重复释放、释放后使用或泄漏的直接反馈。
- 编译器警告在本项目中视为错误。先修复最前面的 GCC 诊断，再重新运行 `make grade`。
