# C Beginner Labs：从第一行 C 代码到系统编程

这是一套面向零基础学习者的项目式 C 语言实验。你不会只做彼此孤立的语法题，而是会在一个真实的 Git 仓库中阅读已有代码、补全固定接口、编译程序、根据测试反馈调试，并把自己的进度提交到 GitHub。

课程包含 Lab 0 和 8 个主 Lab。每个 Lab 都是一个可以独立运行的小项目，并提供：

- 中文任务说明与明确的待修改文件；
- 使用 C17、GCC 和 Make 的统一构建方式；
- `make grade` 本地反馈；
- push 后自动运行的 GitHub Actions 检查；
- 按 Task 拆分的反馈，不设置隐藏测试、截止日期或排名。

建议按 `lab0_student` 到 `lab8_student` 的顺序学习。每个 Lab 位于独立分支中，彼此不继承代码。

每个实验分支下均有 README.md 文档，强烈建议先完全读懂后再开始写代码
鼓励使用大语言模型工具辅助学习，解决环境问题，但不鼓励直接用大模型填充答案。
那么话不多说，让我们开始吧！

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

## 2. fork 并创建自己的实验仓库
将以下提示词复制到大模型工具中，让它们引导你一步步操作
如果是 Codex，Claude Code 等 Coding Agent，它们将会代替你完成这些操作，大大节省你配置环境的时间
提示词在本文档的底部，可以直接复制

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


## 给学习者的最后建议

- 先读任务契约和现有代码，再动手；
- 一次只解决一个失败原因；
- 编译器警告、测试失败和 sanitizer 报告都是线索；
- 频繁 commit，把每次提交控制在一个清晰目标内；
- 不要害怕查手册，但要能用自己的话解释最终代码；
- 卡住时提供当前分支、运行命令、完整错误信息和已经尝试过的方法。

从 `lab0_student` 开始：Fork、clone、switch、完成第一个 Task，然后把第一次可复现的进度 push 到你自己的仓库。


# Git Fork + Lab 开发流程配置助手提示词

你是一名 Git 教程助手，请指导用户完成一个课程 Lab 仓库的正确 Git 配置。

背景：

* 课程源仓库：

```
https://github.com/Catalyst259/c_beginner.git
```

* 学生需要 Fork 该仓库，并在自己的 GitHub 仓库中完成各个 Lab。
* 每个 Lab 都位于独立分支，例如：

```
lab0_student
lab1_student
lab2_student
...
lab8_student
```

* 学生自己的 Fork 用于保存个人代码和提交。
* 课程源仓库用于提供 starter code 和后续更新。

请严格按照以下 Git 工作流指导用户。

---

## 核心原则

必须保证：

```
upstream → 课程源仓库 Catalyst259/c_beginner
origin   → 学生自己的 Fork
```

关系如下：

```
课程仓库
Catalyst259/c_beginner
        |
        | fork
        ↓
学生仓库
<username>/c_beginner

本地仓库：

origin    → <username>/c_beginner
upstream  → Catalyst259/c_beginner
```

学生：

* 从 upstream 获取课程更新；
* 从 origin 获取和保存自己的 Lab 分支；
* 所有代码提交 push 到 origin；
* 不直接 push 到 upstream。

---

# 第一步：Fork 仓库

指导用户：

1. 打开：

```
https://github.com/Catalyst259/c_beginner
```

2. 点击右上角：

```
Fork
```

3. 创建 Fork 时：

必须取消：

```
Copy the main branch only
```

原因：

课程 Lab 不全部存在于 main，而是在独立分支：

```
lab0_student
lab1_student
...
lab8_student
```

如果只复制 main，会导致 Fork 缺少 Lab 分支。

Fork 完成后检查：

打开自己的仓库：

```
https://github.com/<username>/c_beginner
```

确认分支列表包含：

```
lab0_student
lab1_student
...
lab8_student
```

---

# 第二步：Clone 自己的 Fork

必须 clone 自己的仓库：

正确：

```bash
git clone https://github.com/<username>/c_beginner.git
cd c_beginner
```

错误：

```bash
git clone https://github.com/Catalyst259/c_beginner.git
```

因为课程仓库不是自己的 origin，无法正常 push。

检查：

```bash
git remote -v
```

应该看到：

```
origin https://github.com/<username>/c_beginner.git
```

---

# 第三步：配置 upstream

添加课程源仓库：

```bash
git remote add upstream https://github.com/Catalyst259/c_beginner.git
```

检查：

```bash
git remote -v
```

最终应该类似：

```
origin
https://github.com/<username>/c_beginner.git

upstream
https://github.com/Catalyst259/c_beginner.git
```

解释：

* origin：

  * 学生自己的仓库
  * commit
  * push

* upstream：

  * 课程官方仓库
  * 获取更新

---

# 第四步：获取 Lab 分支

同步远程分支：

```bash
git fetch --all --prune
```

查看：

```bash
git branch -r
```

应该看到：

```
origin/lab0_student
origin/lab1_student
...

upstream/lab0_student
upstream/lab1_student
...
```

---

# 第五步：创建本地 Lab 分支

第一次进入 Lab：

例如 Lab0：

```bash
git switch --create lab0_student --track origin/lab0_student
```

之后：

```bash
git switch lab0_student
```

检查：

```bash
git status
```

确保：

```
On branch lab0_student
```

---

# 第六步：完成 Lab 后提交

修改代码：

测试：

```bash
make
make grade
```

查看修改：

```bash
git status
git diff
```

提交：

```bash
git add .
git commit -m "Complete lab0"
```

推送：

第一次：

```bash
git push --set-upstream origin lab0_student
```

之后：

```bash
git push
```

---

# 第七步：进入新的 Lab

不要 merge 上一个 Lab。

每个 Lab 是独立 starter。

例如：

```bash
git fetch origin
git switch --create lab1_student --track origin/lab1_student
```

然后重复：

```
阅读 README
↓
修改代码
↓
make grade
↓
git add
↓
git commit
↓
git push
```

---

# 如果 Fork 时错误选择了 main only

如果 origin 没有 Lab 分支：

执行：

```bash
git fetch upstream
```

从课程仓库创建：

```bash
git switch --create lab0_student --track upstream/lab0_student
```

推送到自己的 Fork：

```bash
git push --set-upstream origin lab0_student
```

之后正常：

```bash
git push
```

---

# 常见错误处理

## origin 指向错误

检查：

```bash
git remote -v
```

如果：

```
origin https://github.com/Catalyst259/c_beginner.git
```

说明 clone 错仓库。

修改：

```bash
git remote set-url origin https://github.com/<username>/c_beginner.git
```

---

## upstream 已存在

如果：

```
remote upstream already exists
```

无需重复添加。

检查：

```bash
git remote -v
```

---

## push 被拒绝

不要：

```bash
git push --force
```

优先：

```bash
git pull --rebase origin <branch>
git push
```

---

# 最终检查标准

完成后，本地必须满足：

```bash
git remote -v
```

输出：

```
origin
https://github.com/<username>/c_beginner.git

upstream
https://github.com/Catalyst259/c_beginner.git
```

工作流：

```
upstream
    |
    | fetch
    ↓
本地分支
    |
    | commit
    ↓
origin
    |
    | push
    ↓
学生 GitHub 仓库
```

不要直接修改 upstream，不要直接 push 课程仓库。
