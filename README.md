# Lab 7：社团活动日志归档器

> “Controlling complexity is the essence of computer programming.” — Brian Kernighan

## 本 Lab 学什么

前面的 Lab 已经练习过数组、指针、字符串、结构体、动态内存和递归。本 Lab 开始让数据离开程序内存，保存到文本文件中。你会使用 `FILE *`、`fopen`、`fread`、`fwrite`、`fgetc`、`fputc`、`ferror` 和 `fclose`，并学习文件操作每一步都可能失败。

五个 Task 从覆盖写入、追加和安全读取开始，再进行流式文本统计，最后把读取、字符串替换、容量计算和写入组合成一个跨文件操作。所有任务只处理文本文件，不涉及二进制记录、文件锁或并发访问。

## 本 Lab 要修改的文件

- `src/lab07.c`

`src/main.c` 已负责读取 Task、路径与文本并打印结果；`include/lab07.h` 给出了评分器会直接调用的固定接口。不要修改公开枚举、结构体、函数名称、参数或返回类型。

## 输入/输出与函数契约

程序第一行是 `1` 至 `5` 的 Task 编号，后续各行由 Task 决定。路径最长 255 个可打印 ASCII 字符且不能为空。程序不打印菜单或输入提示。

公开函数使用以下状态：

- `FILE_STATUS_OK`：操作全部成功，包括最后的 `fclose`。
- `FILE_STATUS_OPEN_ERROR`：文件无法打开。
- `FILE_STATUS_READ_ERROR`：读取过程或关闭输入文件失败。
- `FILE_STATUS_WRITE_ERROR`：写入过程或关闭输出文件失败。
- `FILE_STATUS_TOO_LARGE`：文件内容或替换结果放不进固定容量。

文本容量 `LAB07_TEXT_CAPACITY` 为 1024，结尾的 `\0` 也占一个字节，因此最多保存 1023 个文件字节。文件内容中的换行符也属于文件字节。

### Task 1：覆盖写入完整文本

输入 Task、文件路径，随后把剩余标准输入原样作为文件内容：

```text
1
build/activity.txt
meeting at 19:00
room 204
```

成功输出写入的字节数：

```text
Wrote bytes: 26
```

实现 `write_text_file(path, text)`：

- 用 `fopen(path, "w")` 创建文件；文件已存在时覆盖旧内容。
- 写入 `text` 中 `\0` 之前的全部字节，不把 `\0` 写进文件。
- 空字符串合法，会得到一个空文件。
- `fwrite` 短写或 `fclose` 失败都返回 `FILE_STATUS_WRITE_ERROR`。

即使写入调用成功，缓冲数据仍可能在关闭文件时才真正交给系统，因此不能忽略 `fclose` 的返回值。

### Task 2：追加一行日志

输入 Task、路径和一行文本：

```text
2
build/activity.txt
bring extension cables
```

成功输出：

```text
Appended line
```

实现 `append_text_line(path, line)`。用追加模式 `"a"` 打开文件；文件不存在时创建，存在时保留全部原内容。先写入 `line`，再额外写入恰好一个 `\n`。空行合法，会追加一个换行符。

`line` 的前置条件保证其中没有换行。和 Task 1 一样，任何写入或关闭失败都必须返回写错误。

### Task 3：安全读取完整文件

输入 Task 和待读取路径：

```text
3
build/activity.txt
```

输出包含文件字节数和原内容：

```text
File content (49 bytes):
meeting at 19:00
room 204
bring extension cables
```

实现 `read_text_file(path, buffer, capacity, length)`：

- 最多读取 `capacity` 个字节，用是否读满判断文件能否连同 `\0` 放入缓冲区。
- 成功时在内容后写入 `\0`，并把文件字节数保存到 `*length`。
- 空文件成功，得到空字符串和长度 0。
- 打开、读取、关闭或容量检查失败时，调用者原来的 `buffer` 和 `*length` 必须完全不变。

要满足失败保持语义，先把数据读入临时数组；确认整个操作成功后，再一次提交到调用者的输出参数。

### Task 4：流式统计日志

输入 Task 和路径：

```text
4
build/activity.txt
```

输出：

```text
Statistics: characters=49 lines=3 words=8 longest_line=22
```

实现 `analyze_text_file(path, stats)`，逐字符读取并统计：

- `characters`：文件中的字节总数，包括空格、制表符与换行符。
- `lines`：每个 `\n` 结束一行；非空文件末尾未带 `\n` 的剩余部分也算一行。
- `words`：由 `isspace` 所识别空白分开的非空字符序列。
- `longest_line`：最长一行的字节数，不包含结束它的 `\n`。

空文件的四项均为 0。连续换行会形成长度为 0 的空行。调用 `isspace` 前先转换为 `unsigned char`。读取失败时不要修改调用者原来的 `*stats`。

### Task 5：跨文件批量替换

输入 Task、源路径、目标路径、非空目标串和替换串；替换串所在行可以为空：

```text
5
build/activity.txt
build/published.txt
room
venue
```

成功输出：

```text
Replacements: 1
```

实现 `replace_text_file(source, destination, target, replacement, count)`：

- 读取整个源文件，从左到右替换所有互不重叠的 `target`。
- 新插入的 `replacement` 不再参与匹配；例如把 `a` 换成 `aa` 只处理原文件中的 `a`。
- 重叠候选取最靠左的匹配；`aaaa` 中把 `aa` 换成 `X` 得到 `XX`。
- 替换串可以为空，表示删除；没有匹配也要成功写出源文件的完整副本并返回 0。
- 源文件和最终结果都必须能连同 `\0` 放入 `LAB07_TEXT_CAPACITY`。
- 必须先完成读取、替换和容量检查，再以 `"w"` 打开目标文件。这样读取失败或结果过大时不会破坏已有目标文件。
- 只有目标文件成功写完并关闭后才更新 `*count`；任何失败都保持原值。

本 Task 必须自己完成需要的文件操作，不能调用前面四个公开 Task 函数。这样每个 Task 才能由评分器独立检查。

未知 Task、缺行、额外非空白内容、空路径、过长字段、空目标串或相同的源/目标路径统一输出：

```text
Error: invalid input
```

文件操作错误分别输出：

```text
Error: cannot open file
Error: file read failed
Error: file write failed
Error: file too large
```

## Task 与反馈分

| Task | 分数 |
| --- | ---: |
| 覆盖写入完整文本 | 15 |
| 追加一行日志 | 15 |
| 安全读取完整文件 | 20 |
| 流式统计日志 | 20 |
| 跨文件批量替换 | 30 |

每项使用只调用该函数的独立 harness 和对应 CLI 用例检查。后一个 Task 失败不会抹掉前面已经获得的反馈分，前一个 Task 没完成也不会阻止后续正确实现单独得分。结果写入 `build/grade.json`。

## 本地运行

```bash
make
./build/lab07
make grade
```

文件样例可以放在 `build/` 中；`make clean` 会删除整个 `build/`。建议每完成一个 Task 就运行程序，再执行一次 `make grade`。

## 完成与 push 流程

确认 `make grade` 显示 `总分：100/100` 后提交并推送：

```bash
git status
git add src/lab07.c
git commit -m "Complete lab07 file tools"
git push
```

GitHub Actions 会再次运行同一个 `make grade`，上传 `build/grade.json`，并显示当前反馈分。

## 常见错误/调试提示

- `fopen` 返回的是指针；使用前必须检查是否为 `NULL`。
- 模式 `"w"` 会立即截断旧文件，`"a"` 才会保留旧内容并从末尾写入。
- EOF 只表示没有更多字节；循环结束后要用 `ferror` 区分正常 EOF 和读取错误。
- `fwrite` 的返回值是成功写入的元素数量，不是简单的真假值。
- 每条成功打开文件的路径都必须恰好关闭一次，错误分支也不能漏掉。
- 文件字节数不包含字符串的 `\0`，但内存缓冲区容量必须为它多留一个位置。
- 需要满足失败后输出参数不变时，先在局部变量中构造完整结果，最后再赋值。
- 统计单词时维护“当前是否位于单词中”的状态，只有从空白进入非空白时才增加计数。
- Task 5 写目标文件前先完成全部可能的容量检查，否则结果过大时会留下被截断的目标文件。
- 编译器警告在本项目中视为错误；先修复 GCC 输出的第一条诊断。
