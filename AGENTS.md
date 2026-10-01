# AGENTS.md

## 仓库职责

本仓库是 `reverse_ENV` 的独立 Public 逆向知识库。正文、分类和 canonical index 均在本仓维护，并由 `reverse_ENV/article/` submodule 固定版本。

## 强制规则

- 新增或移动文章时同步更新 `INDEX.md` 的分类表和技术标签映射；`CATALOG.md` / `catalog.json` 由 `scripts/kb_catalog.py generate` 生成，禁止手工编辑。
- `pending/` 是本地待审核队列；除 `.gitkeep` 外不得提交原始 PDF、HTML、导出包或 raw draft。
- 只收录已脱敏、具有跨项目复用价值且有证据支撑的技术内容；项目三件套继续留在对应 workspace 仓。
- `collection-engineering/` 只收录代理并发、checkpoint、spool/mirror、采集可靠性与非侵入式运维模式；业务目标、活跃区间、生产路径、host、SID、Cookie、原始 ACK/progress 不得进入 Public article。
- 新文件使用 UTF-8 without BOM + LF；已有文件保持原编码和换行。
- `CATALOG.md` / `catalog.json` 是 deterministic generated artifacts，固定由 `kb_catalog.py generate` 写为 UTF-8 without BOM + LF；不得为匹配 Git working-tree autocrlf 再转成 CRLF，否则字节级 `check` 会报 stale。
- 正文或索引变更后运行 `kb_catalog.py generate`、`kb_catalog.py check` 和 `python -m unittest discover -s tests -v`。
- 新增或主动迁移文章遵循 `docs/knowledge-contract.md`，只用 `templates/` 的四分型模板；保留来源，按需提炼，不全库改写。v2 元数据采用 PyYAML SafeLoader（`PyYAML>=6,<7`），链接/标题使用 `markdown-it-py>=3,<5`；旧引用块兼容为 legacy，不能推断其技术验证状态。
- `kind=canonical/nested` 仍表示布局，`document_type` 表示用途；通过 `kb_catalog.py query` 按 target/module/type/scope 定位实际模块与证据边界。`templates/` 和 `docs/` 不入文章 catalog。
- 模块/结论按实际 basis 与 limits 表达，unknown/source-report 不自动升级；procedure 必须有前提、步骤、输出、验收、失败出口，图文一致性与来源语义需人工复核。
- `sanitize` 默认 dry-run；仅对逐文件确认的高置信尾部噪声使用 `--apply`，正文截断声明不得当广告机械删除。
- 提交前运行敏感信息检查、`git diff --check` 和 `git status --short`。
- 更新知识库后，由 `reverse_ENV` 主仓单独提交新的 submodule gitlink；不得把两个仓库的改动混成一次提交。

- 整库迁移使用 `scripts/kb_migrate.py` 的显式清单 plan/apply/verify，先库外全量备份与隔离验收；保留原字节和历史来源，不自动删除/提交。缺 locator 与未知出处区分见内容合同，日期不得冒充观测时间。
