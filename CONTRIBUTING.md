# 贡献指南

感谢你对 SIAS Map Agent 的兴趣！欢迎以任何形式参与贡献。

## 报告 Bug

1. 在 Issues 里新建 issue，标题描述问题现象
2. 附上：运行环境（OS / Python 版本 / Ollama 版本）、复现步骤、`examples/runlog.txt` 相关片段
3. 如能提供最小复现指令更好

## 提交 PR

1. Fork 本仓库
2. 基于 `main` 新建分支：`git checkout -b feature/xxx`
3. 修改后跑测试：`python -m unittest discover -s tests -v`
4. 提交并推送到你的 fork，发起 PR
5. 在 PR 描述里说明改动动机与影响

## 代码风格

- Python 3 标准库优先，**尽量不引入第三方依赖**
- 函数与变量命名清晰，关键逻辑加注释
- 新功能请配套单元测试（放在 `tests/` 目录）

## 行为准则

友好、专业、就事论事。欢迎新人，鼓励讨论。
