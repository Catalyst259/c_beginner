# Lab 0：社团活动经费速算器

> “Don't rush into coding!” — Edsger W. Dijkstra

## 本 Lab 学什么

本练习用一个社团活动经费速算器学习 `printf`、`scanf`、数值和字符变量、四则表达式、`if / else` 与固定格式输出。同时请确认你能在本地编译、评分并 `git push`。

## 本 Lab 要修改的文件

- `src/main.c`

评分器和其他文件是课程基础设施；完成练习只需要修改上面的一个文件。

## 输入/输出与函数契约

程序读取一行 `数字 运算符 数字`，允许各部分周围有任意空白。数字必须是非负整数或常见十进制小数。只输出一行结果，不要输出标题、菜单或输入提示。

| 运算符 | 含义 | 输出标签 |
| --- | --- | --- |
| `+` | 合并两笔预算 | `Combined budget:` |
| `-` | 总预算减已花金额 | `Remaining budget:` |
| `*` | 单价乘数量 | `Total cost:` |
| `/` | 总额按人数分摊 | `Per-person cost:` |

正常结果固定保留两位小数，例如 `Per-person cost: 15.00`。减法结果可以为负，但输入数字不能为负。格式不完整、负输入、未知运算符、非数字或有尾随内容时输出 `Error: invalid input`；仅当输入完全合法且除数为零时输出 `Error: division by zero`。

## Task 与反馈分

| Task | 分数 |
| --- | ---: |
| 合并预算 (`+`) | 15 |
| 剩余预算 (`-`) | 15 |
| 总费用 (`*`) | 15 |
| 人均费用 (`/`) | 15 |
| 除零处理 | 10 |
| 非法输入处理 | 10 |
| 浮点兼容 | 20 |

`make grade` 会分别报告每项结果，并把同样的信息写入 `build/grade.json`。

## 本地运行

```bash
make
./build/lab00
make grade
```

运行程序后，请手动输入一个样例，例如 `120 + 30`。

## 完成与 push 流程

确认 `make grade` 显示 `总分：100/100` 后，检查改动并提交、推送：

```bash
git status
git add src/main.c
git commit -m "Complete lab00 budget calculator"
git push
```

GitHub Actions 会再次运行同一条 `make grade` 命令，并上传 `build/grade.json`。

## 常见错误/调试提示

- `scanf` 的格式字符串前加空白可跳过运算符前的任意空白。
- 检查 `scanf` 的返回值，并再读取一个字符来确认没有尾随内容。
- 用 `%.2f` 输出金额；标签、冒号和空格必须完全一致。
- 先用 `printf` 输出变量值检查，再删除调试输出；正式程序只能输出规定的一行。
- 编译器警告在本项目中是错误：请逐条阅读 GCC 的诊断。
