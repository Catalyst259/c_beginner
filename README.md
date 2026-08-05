# C Beginner Labs：从第一行 C 代码到系统编程

这是一套面向零基础学习者的项目式 C 语言实验。你不会只做彼此孤立的语法题，而是会在一个真实的 Git 仓库中阅读已有代码、补全固定接口、编译程序、根据测试反馈调试，并把自己的进度提交到 GitHub。

课程包含 Lab 0 和 8 个主 Lab。每个 Lab 都是一个可以独立运行的小项目，并提供：

- 中文任务说明与明确的待修改文件；
- 使用 C17、GCC 和 Make 的统一构建方式；
- `make grade` 本地反馈；
- push 后自动运行的 GitHub Actions 检查；
- 按 Task 拆分的反馈，不设置隐藏测试、截止日期或排名。

建议按 `lab0_student` 到 `lab8_student` 的顺序学习。每个 Lab 位于独立分支中，彼此不继承代码。

## 开始前先认识三个名字

下面的操作会反复用到三个概念：

| 名称 | 含义 | 用途 |
| --- | --- | --- |
| 课程源仓库 | `Catalyst259/c_beginner` | 发布课程和各 Lab starter |
| `origin` | 你 Fork 后的个人仓库 | 保存并提交你自己的代码 |
| `upstream` | 课程源仓库在本地的别名 | 获取课程后续更新 |

最重要的原则是：**从课程仓库获取题目，把完成的代码 push 到自己的 `origin`。**

本指南中的 `<你的 GitHub 用户名>` 是占位符。输入命令时要换成你自己的用户名，并且不要输入尖括号。

## 1. 准备开发环境

推荐使用以下环境之一：

- Windows：VS Code + WSL 2 + Ubuntu；
- macOS：Terminal，安装 Xcode Command Line Tools；
- Linux：任意常见发行版。

需要的工具是 Git、GCC、Make、Python 3 和 Bash。在终端中检查：

```bash
git --version
gcc --version
make --version
python3 --version
bash --version
```

Ubuntu 或 WSL 中缺少工具时，可以安装：

```bash
sudo apt update
sudo apt install build-essential git python3
```

macOS 中缺少编译工具时，可以运行：

```bash
xcode-select --install
```

本项目不绑定某个 IDE。即使使用 VS Code，也请在终端中完成本指南里的 Git、编译和测试命令。

## 2. Fork 课程仓库

Fork 会在你的 GitHub 账号下创建一份仓库副本。以后你的学习记录和代码都会 push 到这个副本，不会直接修改课程源仓库。

1. 登录 GitHub，打开课程仓库：<https://github.com/Catalyst259/c_beginner>。
2. 点击页面右上角的 **Fork**。
3. `Owner` 选择你自己的 GitHub 账号。
4. 仓库名建议保持为 `c_beginner`。
5. **取消勾选 `Copy the main branch only`。** 本课程的每个 Lab 都在独立分支；如果只复制 `main`，你的 Fork 中将缺少 `lab0_student` 到 `lab8_student`。
6. 点击 **Create fork**，等待创建完成。

GitHub 页面文字发生变化时，可以对照 [GitHub 官方 Fork 指南](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo)。关键要求不变：不要只复制默认分支。

创建后，浏览器地址应类似：

```text
https://github.com/<你的 GitHub 用户名>/c_beginner
```

打开分支下拉框，确认能看到 `lab0_student`、`lab1_student` 等分支。公开仓库只发布带 `_student` 后缀的练习分支；课程答案保存在独立的私有仓库中，不会出现在这里。

## 3. Clone 你自己的仓库

先在终端进入你准备存放代码的目录，然后 clone **自己的 Fork**。HTTPS 方式适合第一次使用 Git 的同学：

```bash
git clone https://github.com/<你的 GitHub 用户名>/c_beginner.git
cd c_beginner
```

如果你已经为 GitHub 配置过 SSH，也可以使用：

```bash
git clone git@github.com:<你的 GitHub 用户名>/c_beginner.git
cd c_beginner
```

不要使用网页上的 **Download ZIP**：ZIP 文件没有分支和提交历史，也无法正常完成后续的 `git switch`、`git commit` 和 `git push`。

clone 完成后检查远程仓库：

```bash
git remote -v
```

你应该看到 `origin` 的 fetch 和 push 地址都指向你自己的用户名，例如：

```text
origin  https://github.com/your-name/c_beginner.git (fetch)
origin  https://github.com/your-name/c_beginner.git (push)
```

如果这里显示的是 `Catalyst259/c_beginner`，说明你 clone 了课程源仓库。请先停下来，重新 clone 自己的 Fork，否则你没有权限把练习推送到 `origin`。

### 添加 upstream

把课程源仓库登记为 `upstream`，以后可以获取课程更新。这也是 [GitHub 官方文档推荐的 Fork 远程配置](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/configuring-a-remote-repository-for-a-fork)：

```bash
git remote add upstream https://github.com/Catalyst259/c_beginner.git
git remote -v
```

此时应该同时看到：

- `origin` → 你的个人仓库；
- `upstream` → `Catalyst259/c_beginner`。

这个操作只需执行一次。如果 Git 提示 `remote upstream already exists`，说明已经添加过，不需要重复执行。

## 4. 获取并切换到第一个 Lab

先获取远程分支列表：

```bash
git fetch --all --prune
git branch --remotes
```

第一次进入 Lab 0 时，创建本地 `lab0_student` 分支，并让它跟踪你个人仓库中的同名分支：

```bash
git switch --create lab0_student --track origin/lab0_student
```

检查当前分支：

```bash
git status
```

输出第一行应包含：

```text
On branch lab0_student
```

如果本地分支已经创建过，就不需要再次使用 `--create`，直接运行：

```bash
git switch lab0_student
```

### 如果 origin 中没有 student 分支

这通常表示 Fork 时勾选了 `Copy the main branch only`。你仍然可以从课程源仓库创建本地练习分支：

```bash
git fetch upstream
git switch --create lab0_student --track upstream/lab0_student
git push --set-upstream origin lab0_student
```

最后一条命令会把该分支发布到你的 Fork，并把本地分支的跟踪目标改为 `origin/lab0_student`。之后正常使用 `git push` 即可。

## 5. 完成一个 Lab

切换到 Lab 分支后，先阅读该分支根目录下的 `README.md`。每个 Lab 的具体输入输出、函数契约、Task 分数和需要修改的文件，都以该 README 为准。

通用工作流程是：

```bash
make
make grade
```

- `make` 使用严格的 C17 编译选项构建程序；编译器警告也会被视为错误。
- `make grade` 运行全部本地检查，并在 `build/grade.json` 生成机器可读结果。
- `make clean` 可以删除 `build/` 中的编译产物，再进行一次干净构建。

修改过程中可以随时查看状态和差异：

```bash
git status
git diff
```

建议采用“小步修改、小步验证”的节奏：完成一个 Task，就重新运行 `make grade`，先读失败摘要，再定位代码。不要为了让分数变绿而修改 `tests/grade.py`；测试是学习反馈，真正需要完成的是 Lab README 指定的源文件。

## 6. 提交并推送到自己的仓库

在 push 前，先确认当前分支、远程地址和测试结果：

```bash
git status
git remote get-url origin
make grade
```

`origin` 必须指向你自己的 GitHub 仓库。确认无误后，以 Lab 0 为例：

```bash
git add src/main.c
git diff --staged
git commit -m "Complete lab0 budget calculator"
git push --set-upstream origin lab0_student
```

`git diff --staged` 用来复查即将进入提交的内容。后续 Lab 请根据各自 README 中“本 Lab 要修改的文件”执行 `git add`，不要无检查地把临时文件或无关改动一起提交。

`--set-upstream`（可简写为 `-u`）只需在该分支第一次 push 时使用。建立跟踪关系后，后续进度可以这样提交：

```bash
git add src/
git diff --staged
git commit -m "Describe the completed task"
git push
```

push 完成后：

1. 打开你自己的 GitHub 仓库；
2. 切换到刚推送的 `lab0_student` 分支；
3. 打开 **Actions** 或提交旁的状态图标；
4. 查看各 Task 的反馈和总分。

GitHub Actions 会再次运行与本地相同的 `make grade`。检查失败并不会删掉代码：阅读反馈、继续修改、重新 commit 和 push 即可。

### 推送时的身份验证

GitHub 不接受账号密码作为 Git 的 HTTPS 密码。如果终端要求验证，请使用浏览器登录、Git Credential Manager、Personal Access Token，或提前配置 SSH key。不要把 token、密码或私钥写进代码、README、提交记录或聊天截图。

## 7. 进入下一个 Lab

各 Lab 是独立项目，不需要把上一分支 merge 到下一分支。切换前先保证当前修改已经提交；否则 Git 可能拒绝切换，或把未提交改动带到错误的 Lab。

例如完成 Lab 0 后进入 Lab 1：

```bash
git status
git fetch origin
git switch --create lab1_student --track origin/lab1_student
```

如果该本地分支已经存在：

```bash
git switch lab1_student
```

之后重复“阅读 Lab README → 编码 → `make grade` → commit → push”的流程。第一次 push Lab 1 时运行：

```bash
git push --set-upstream origin lab1_student
```

每次切换后都建议执行 `git status`，不要只凭终端目录名判断当前分支。

## Lab 路线图

| 顺序 | 练习分支 | 项目 | 核心知识 |
| ---: | --- | --- | --- |
| 0 | `lab0_student` | 社团活动经费速算器 | `printf`、`scanf`、变量、表达式、分支与输入校验 |
| 1 | `lab1_student` | 游戏背包整理器 | 循环、固定数组、查找、筛选、排序与穷举 |
| 2 | `lab2_student` | 社团消息编辑器 | 指针遍历、字符串、原地修改与安全复制 |
| 3 | `lab3_student` | 冒险者队伍管理器 | 指针、结构体、结构体数组查找与排序 |
| 4 | `lab4_student` | 冒险队补给列表 | `malloc/free`、所有权、动态数组与扩容 |
| 5 | `lab5_student` | 中缀表达式计算器 | 递归下降、优先级、结合性与安全整数运算 |
| 6 | `lab6_student` | 链表任务队列管理器 | 单链表、插入、删除、反转与完整释放 |
| 7 | `lab7_student` | 社团活动日志归档器 | 文本文件、流式处理与错误路径 |
| 8 | `lab8_student` | 迷你命令执行器 | POSIX 进程、`fork/exec/wait`、重定向与管道 |

Lab 0 同时负责验证环境。Lab 1–5 建立 C 编程和数据结构基础；Lab 6–8 将所有权、文件和进程等系统概念串成完整项目。Lab 4–8 的评分还会使用 AddressSanitizer 和 UndefinedBehaviorSanitizer 帮助发现越界、释放后使用、内存泄漏和未定义行为。

## 常见 Git 问题

### `fatal: not a git repository`

你可能不在仓库目录中。先执行：

```bash
cd c_beginner
git status
```

### `fatal: a branch named 'lab0_student' already exists`

本地分支已经存在，直接切换：

```bash
git switch lab0_student
```

### `fatal: invalid reference: origin/lab0_student`

先确认远程分支：

```bash
git fetch --all --prune
git branch --remotes
```

如果只有 `origin/main`，参考上文“如果 origin 中没有 student 分支”，从 `upstream/lab0_student` 创建分支并推送到自己的 Fork。

### Git 拒绝切换分支

先运行 `git status`。如果有未提交修改，优先完成检查并提交；如果只是暂时不想提交，可以使用：

```bash
git stash push -m "unfinished work"
git switch lab0_student
```

回到原分支后用 `git stash pop` 恢复。执行前要确认当前分支，避免把修改恢复到错误位置。

### push 被拒绝，提示 `non-fast-forward`

远程分支包含本地尚未获取的提交。不要使用 `git push --force`。先执行：

```bash
git pull --rebase origin lab0_student
```

这里以 `lab0_student` 为例；其他 Lab 要替换成当前分支名。如果出现冲突，阅读 Git 标出的冲突文件，解决后再继续 rebase 和 push。不确定时保留现场并向课程维护者求助，不要用强制推送覆盖远程进度。

### 不小心在 `main` 写了代码

如果还没有提交，先暂存修改，再基于正确的远程 starter 创建分支：

```bash
git stash push -m "move work from main"
git fetch origin
git switch --create lab0_student --track origin/lab0_student
git stash pop
```

然后检查 `git status`，确认改动在新分支，再提交并 push 到 `origin/lab0_student`。如果本地同名分支已经存在，把第三条命令改为 `git switch lab0_student`。如果 `stash pop` 出现冲突，不要删除任何文件，先求助并说明 `git status` 与 `git branch --all` 的输出。

## 完成本课程后的学习路径

不要把“学完 C 语法”当作终点。本课程更希望你获得三种可迁移能力：把需求拆成函数、借助测试定位问题、理解程序如何管理内存和操作系统资源。完成 Lab 8 后，可以沿下面的路线继续。

### 1. 巩固 C 与计算机基础

- 回头重写 Lab 4、6、8 中最薄弱的一个项目，不看旧实现；
- 学会使用调试器、sanitizer 和系统调用手册，理解编译、链接及进程地址空间；
- 补充位运算、函数指针、模块化接口、静态库与基础数据结构；
- 做一个 500–1000 行的小项目，例如文本索引器、简化 shell 或终端记账工具。

这一阶段的目标不是记更多语法，而是能解释资源由谁创建、由谁释放、错误如何向上传递。

### 2. 学习现代 C++

具备 C 的数组、指针、结构体和动态内存基础后，再进入 C++ 会更容易理解它解决了什么问题。建议依次学习：

1. 引用、函数重载、`const`、命名空间；
2. 类、构造/析构、RAII 和对象生命周期；
3. `std::string`、`std::vector`、迭代器与常用 STL 算法；
4. 智能指针、移动语义、泛型和模板；
5. 使用测试与构建系统组织一个多文件 C++ 项目。

不要把 C 代码简单改成 `.cpp` 后继续手写所有内存管理；重点是理解 RAII、标准容器和算法如何让所有权更清晰。

### 3. 用 OJ 训练数据结构与算法

OJ 适合训练边界分析、复杂度和实现速度，但应与项目练习并行，而不是替代项目。推荐顺序：

1. 输入输出、模拟、枚举、排序与二分；
2. 前缀和、双指针、栈、队列、链表；
3. 哈希、树、堆、并查集；
4. DFS/BFS、最短路和基础动态规划；
5. 根据目标再学习高级数据结构与算法。

每道题通过后记录时间复杂度、空间复杂度、错误边界和另一种解法。初期追求稳定写对，而不是只追求题量或复制模板。

### 4. 进入操作系统与系统编程

Lab 7–8 是操作系统学习的入口，而不是完整的操作系统课程。继续学习前建议先补充计算机组成原理和数据结构，然后关注：

- 程序、进程与线程，用户态与内核态；
- 虚拟内存、页表、栈、堆与内存映射；
- 文件描述符、文件系统、管道与设备；
- 并发、锁、条件变量、死锁和调度；
- 系统调用、异常、中断与基本网络 I/O。

学习时应配合实验：阅读小型教学操作系统源码，修改一个系统调用或调度策略，并用测试验证，而不只是观看课程视频。

### 5. 把几条路线汇合成项目

一个稳妥的顺序是：

```text
C Labs → 数据结构基础 → C++ 与 OJ 并行 → 计算机组成 → 操作系统 → 网络与更完整的系统项目
```

你不需要等一门课“全部学完”才开始下一项。可以用 C/C++ 项目维持工程能力，用 OJ 维持算法训练，再通过操作系统实验理解底层机制。最终作品应同时具备清晰的 README、可复现构建、自动测试和有意义的 Git 提交历史。

## 给学习者的最后建议

- 先读任务契约和现有代码，再动手；
- 一次只解决一个失败原因；
- 编译器警告、测试失败和 sanitizer 报告都是线索；
- 频繁 commit，把每次提交控制在一个清晰目标内；
- 不要害怕查手册，但要能用自己的话解释最终代码；
- 卡住时提供当前分支、运行命令、完整错误信息和已经尝试过的方法。

从 `lab0_student` 开始：Fork、clone、switch、完成第一个 Task，然后把第一次可复现的进度 push 到你自己的仓库。
