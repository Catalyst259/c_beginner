# Lab 8：迷你命令执行器

> “A process is a program in execution.” — Abraham Silberschatz

## 本 Lab 学什么

前面的 Lab 已经练习过内存、递归和文件。本 Lab 开始进入 POSIX 系统编程：程序不再只处理自己的数据，而是创建子进程、启动其他程序，并连接它们的标准输入输出。

你会使用 `fork`、`execvp`、`waitpid`、`open`、`dup2`、`pipe`、`read`、`close` 和 `_exit`。五个 Task 沿着一个 shell 执行外部命令时的真实路径递进：创建并回收子进程、执行 PATH 中的程序、重定向输出、捕获输出，最后实现 `left | right` 二段管道。

本 Lab 是课程的最后一个练习，范围止于外部命令执行、重定向、输出捕获和二段管道；不再加入循环读取命令、shell 引号与展开、`cd`、`exit` 等内建命令或完整的交互式终端。

## 本 Lab 要修改的文件

- `src/lab08.c`

`src/main.c` 已负责读取输入、把命令行按空白拆成 `argv`、校验和打印结果；`include/lab08.h` 给出了评分器直接调用的固定接口。不要修改公开枚举、结构体、函数名称、参数或返回类型。

本 Lab 只支持 POSIX 系统，如 Linux、WSL 和 macOS。构建时定义 `_POSIX_C_SOURCE=200809L`，让系统头文件公开所需接口。

## 先理解三个关键事实

### `fork` 返回两次

`fork()` 成功后，父进程得到子进程 PID，子进程得到 `0`。两个进程从同一行代码后继续运行，但拥有各自独立的地址空间。

```c
pid_t child = fork();

if (child < 0) {
    /* 创建失败，只存在父进程 */
} else if (child == 0) {
    /* 子进程路径 */
} else {
    /* 父进程路径，child 是子进程 PID */
}
```

### `execvp` 成功后不会返回

`execvp(argv[0], argv)` 用新程序替换当前进程映像。成功时，后面的 C 代码已经不存在；只有失败才会返回。`p` 表示按环境变量 `PATH` 搜索命令。

本 Lab 约定：

- `execvp` 失败时，子进程 `_exit(127)`；
- 重定向的 `open` 或 `dup2` 失败时，子进程 `_exit(126)`；
- 子进程用 `_exit`，不使用 `exit`，避免重复刷新从父进程继承的 stdio 缓冲。

126 和 127 是子进程的退出结果，不是父进程侧的 `ProcessStatus` 错误。

### pipe 的 EOF 取决于所有写端

`pipe(descriptors)` 得到读取端 `descriptors[0]` 和写入端 `descriptors[1]`。只要任意进程仍然持有写端，读取端就不会得到 EOF。因此父子进程都必须关闭自己不使用的端点。

## 状态与结果

成功回收子进程后，用 `ProcessResult` 区分正常退出和信号终止：

```c
typedef struct {
    ProcessOutcome outcome;
    int value;
} ProcessResult;
```

- `PROCESS_EXITED`：`value` 是 `0..255` 的退出码。
- `PROCESS_SIGNALED`：`value` 是终止子进程的信号编号。

父进程侧系统调用错误使用：

- `PROCESS_STATUS_FORK_ERROR`
- `PROCESS_STATUS_PIPE_ERROR`
- `PROCESS_STATUS_READ_ERROR`
- `PROCESS_STATUS_WAIT_ERROR`
- `PROCESS_STATUS_TOO_LARGE`

所有公开函数只有在返回 `PROCESS_STATUS_OK` 后才提交输出参数；父进程侧失败时，调用者原来的结果必须保持不变。`waitpid` 如果被信号以 `EINTR` 中断，应重试。

### Task 1：创建并等待子进程

输入 Task 和退出码：

```text
1
7
```

输出：

```text
Child exited with code: 7
```

实现 `spawn_exit_child(exit_code, result)`：

1. 调用 `fork`。
2. 子进程立即 `_exit(exit_code)`。
3. 父进程用 `waitpid(child, &status, 0)` 等待指定子进程。
4. 使用 `WIFEXITED`、`WEXITSTATUS`、`WIFSIGNALED` 和 `WTERMSIG` 解码等待状态。

不能把 `waitpid` 写在子进程路径，也不能让父进程直接返回而留下僵尸进程。

### Task 2：执行 PATH 中的命令

输入一行命令：

```text
2
printf hello
```

命令 stdout 由父进程直接继承，随后程序打印执行结果：

```text
helloCommand exited with code: 0
```

实现 `run_command(argv, result)`。子进程调用 `execvp(argv[0], argv)`；失败后必须 `_exit(127)`。父进程只能等待，不能调用 `execvp`，否则 Lab8 程序自身会被替换。

CLI 最多接收 8 个由 ASCII 空白分隔的参数，不处理引号、反斜杠、变量展开、通配符或重定向符号。评分器直接调用公开函数时会覆盖普通参数、非零退出、信号终止与不存在的命令。

### Task 3：重定向命令输出

输入输出路径与命令：

```text
3
build/message.txt
printf saved
```

成功输出：

```text
Command exited with code: 0
Output path: build/message.txt
```

文件内容为 `saved`。实现 `run_command_redirected(argv, output_path, result)`：

1. 仍然先 `fork`。
2. 子进程用 `open(output_path, O_WRONLY | O_CREAT | O_TRUNC, 0644)` 打开文件。
3. 用 `dup2(output, STDOUT_FILENO)` 让标准输出指向该文件。
4. 关闭原始的 `output` 描述符，再执行命令。

重定向只发生在子进程，因此父进程仍可正常打印结果。文件权限 `0644` 会继续受到当前 `umask` 影响。打开或复制描述符失败时，子进程以 126 退出。

### Task 4：通过管道捕获输出

输入命令：

```text
4
printf captured
```

输出：

```text
Command exited with code: 0
Captured output (8 bytes):
captured
```

实现 `capture_command_output(argv, output, capacity, length, result)`：

- fork 前创建 pipe；子进程把 stdout `dup2` 到写端后执行命令。
- 父进程关闭写端，反复 `read` 读取端直到 EOF。
- `capacity` 包含结尾 `\0`；成功时保存全部输出字节、补终止符并记录字节数。
- 输出可能包含 `\0`，因此不能依赖 `strlen` 判断捕获长度。
- 输出过大时仍要继续读取并丢弃剩余字节，关闭读取端并回收子进程，最后返回 `PROCESS_STATUS_TOO_LARGE`。

父进程必须先排空 pipe，再调用 `waitpid`。如果先等待，而子进程写满系统 pipe 缓冲区后也在等待父进程读取，两个进程会永久阻塞。

### Task 5：二段命令管道

输入左右两条命令：

```text
5
printf hello
wc -c
```

右命令输出后打印两个进程的结果：

```text
5
Left command exited with code: 0
Right command exited with code: 0
```

实现 `run_pipeline(left_argv, right_argv, results)`，等价于：

```text
left command | right command
```

必须完成：

1. fork 前创建一个 pipe。
2. 左子进程关闭读取端，把 stdout 复制到写入端，关闭原写入端并 `execvp`。
3. 右子进程关闭写入端，把 stdin 复制到读取端，关闭原读取端并 `execvp`。
4. 父进程关闭自己的两个 pipe 端点。
5. 父进程回收两个指定 PID，将左、右结果依次写入 `results[0]` 和 `results[1]`。

右命令 stdout、两个命令 stderr 都保持继承。若第二次 `fork` 失败，父进程必须关闭 pipe，终止并回收已经创建的左子进程，不能遗留后台进程。

## 输入限制与错误输出

路径最长 255 个可打印 ASCII 字符且不能为空。命令行最长 255 字节、包含 1–8 个参数。未知 Task、缺行、空命令、参数过多、退出码不在 `0..255`、空路径或额外非空白输入统一输出：

```text
Error: invalid input
```

父进程侧错误分别输出：

```text
Error: fork failed
Error: pipe failed
Error: pipe read failed
Error: wait failed
Error: output too large
```

## Task 与反馈分

| Task | 分数 |
| --- | ---: |
| 创建并等待子进程 | 15 |
| 执行 PATH 中的命令 | 15 |
| 重定向命令输出 | 20 |
| 通过管道捕获输出 | 20 |
| 二段命令管道 | 30 |

每项使用只调用本 Task 函数的独立 harness 和对应 CLI 用例检查。后一个 Task 不得调用前一个公开 Task 函数，以保证它们可以独立得分。结果写入 `build/grade.json`。

## 本地运行

```bash
make
./build/lab08
make grade
```

评分器会创建确定性的辅助命令，不依赖系统安装的 `grep`、`tr` 等工具。每个进程用例都有超时保护；Task 4 或 Task 5 超时时，优先检查未关闭的 pipe 端点和先 wait 后 read 的死锁。

## 完成与 push 流程

确认 `make grade` 显示 `总分：100/100` 后提交并推送：

```bash
git status
git add src/lab08.c
git commit -m "Complete lab08 process runner"
git push
```

GitHub Actions 会再次运行同一个 `make grade`，上传 `build/grade.json`，并显示当前反馈分。

## 常见错误/调试提示

- `fork` 后父子进程都会继续执行；每条分支必须清楚自己应该关闭哪些描述符。
- 不要用 `if (fork())` 隐藏错误情况；`-1` 也会被当成真值。
- `execvp` 成功不返回；它后面的代码只能处理失败。
- 等待状态不是退出码，必须先使用 `WIFEXITED` 或 `WIFSIGNALED` 判断。
- `dup2(source, STDOUT_FILENO)` 后仍要关闭不再使用的 `source`。
- 父进程自己保留一个 pipe 写端，就足以让读取端永远收不到 EOF。
- `read` 和 `waitpid` 都可能因 `EINTR` 暂时失败；不要立刻当成永久错误。
- 捕获输出时使用返回的字节数，不使用字符串函数处理尚未补 `\0` 的数据。
- 子进程设置失败用 `_exit(126)`，执行失败用 `_exit(127)`；不要从子进程 `return` 回 Lab8 的 `main`。
- 编译器警告在本项目中视为错误；先修复 GCC 输出的第一条诊断。
