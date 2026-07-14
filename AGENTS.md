# AGENTS.md

## 仓库职责

本仓库是 `reverse_ENV` 的独立 Public 逆向知识库。正文、分类和 canonical index 均在本仓维护，并由 `reverse_ENV/article/` submodule 固定版本。

## 强制规则

- 新增或移动文章时同步更新 `INDEX.md` 的分类表和技术标签映射。
- `pending/` 是本地待审核队列；除 `.gitkeep` 外不得提交原始 PDF、HTML、导出包或 raw draft。
- 只收录已脱敏、具有跨项目复用价值且有证据支撑的技术内容；项目三件套继续留在对应 workspace 仓。
- 新文件使用 UTF-8 without BOM + LF；已有文件保持原编码和换行。
- 提交前运行链接检查、敏感信息检查、`git diff --check` 和 `git status --short`。
- 更新知识库后，由 `reverse_ENV` 主仓单独提交新的 submodule gitlink；不得把两个仓库的改动混成一次提交。
