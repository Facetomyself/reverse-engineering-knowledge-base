# 知识文档合同 v2

## 处理路线与兼容边界

保留清洗后的来源文章，按价值提炼，不全库重写。`archive` 只负责保真归档；`reference` 给出可查模块；`procedure` 提供条件化行动；`case` 保留一次分析的范围与正反结果。目录 category 与 `kind=canonical/nested` 的旧布局语义不变。

新建与主动迁移文章使用 YAML front matter v2，H1 是标题真源，category 来自目录。未迁移的引用块文章继续原有校验，catalog 显式标为 `document_type=legacy`、`metadata_status=legacy`、`id=null`，不推断类型、目标或验证状态。文章正文不因生成 catalog 被改写。

依赖为 PyYAML `>=6,<7` 与 markdown-it-py `>=3,<5`：`python -m pip install "PyYAML>=6,<7" "markdown-it-py>=3,<5"`。后者以 CommonMark token 统一链接与标题识别，正确排除缩进、围栏及行内代码，支持 setext 标题和引用式链接；缺包明确报错，不退回不可靠 regex。解析器基于 SafeLoader，拒绝重复键、YAML alias、自定义对象标签和未声明字段，不实现简化 YAML。日期形标量作为字符串保留。仅旧文时可不安装 PyYAML，但链接结构校验仍依赖 markdown-it-py。

## 最小 schema

```yaml
---
schema_version: 2
id: example-web-reference
document_type: reference
scope:
  targets: [example]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./source-article.md#request-material
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅整理来源作者陈述；未复现算法或验证当前服务端行为。
relations:
  - type: derived_from
    target: ./source-article.md#request-material
tags: [session]
---
```

示例路径是格式说明，不可直接留入正式文章。稳定 ID 使用小写 ASCII kebab-case，文档改名不改 ID；全库唯一。source ID 仅在本篇唯一，使用相同命名规则。除 `modules`、`relations`、`tags` 外以上字段必需；`reference` 必須至少一个实际模块。`archive` 额外必需 `source_completeness: complete|partial|unknown`，其他类型可选；归档不必填写模块。`scope` 四项全部必需，无法判断使用明确的 `unknown`，不得以归档日期代替观测时间。`observed_at` 为日期/时间窗原文，不自动解析成验证时间；过滤为精确匹配。

可选 `original_date`、`archived_date` 是非空字符串，未知使用 `unknown`。前者只表示原始发布日期/原始分析日期，后者保留既有归档日期；不从 `scope.observed_at`、当前整理日期或多来源中自动挑选。YAML 隐式日期形标量仍以字符串解析。catalog 保持既有 `original_date` / `archive_date` 字段及类型；v2 显式值优先，未声明时保留历史记录/日期文件名兼容。作者署名保留在正文。

可用模块：`interfaces`、`parameters`、`request-chain`、`risk-control`、`validation`、`decision-flow`。一个名称在本篇只登记一次，必须指向有正文的锚点。推荐使用稳定显式锚点 `<a id="parameters"></a>`，随后写标题和内容；也支持 GitHub 风格标题锚点。

## 来源、模块与结论证据

`basis` 必填且只能为：`unknown`、`source-report`、`static-review`、`runtime-observation`、`local-parity`、`server-accepted`。它们不是自动逐级升级的分数；不存在全文 verified 字段。

- 来源作者报告的结果一律为 `source-report`，不因文章写了“成功”而升级为整理者 runtime 事实。
- 模块的 `sources` 必须引用本篇声明的来源；`limits` 必须明确未覆盖范围。除 unknown/source-report 外，模块 basis 必须有同 basis 的来源支撑。
- 本地来源声明技术 basis 时，目标 v2 模块也必须明确有相同 basis；legacy 或未知来源只能支持 unknown/source-report。外部公开来源的 basis 是明确声明，人工审查仍须核验其依据，工具不替代真实性判断。
- source `ref` 可用公开 HTTP(S) URL、相对文章路径加可选锚点、`kb:stable-id#anchor`。本地引用不得越出仓库、指向非文章、使用本机绝对路径或缺失锚点；公网 URL 只检查形式，不在线验证可达性。
- `relations` 类型：`derived_from`、`supplements`、`supersedes`、`conflicts_with`、`applies_to`；前者必须带定位锚点。来源/derived_from 不能自引用或成环，补充/冲突关系可以互为引用。
- v2 禁止同时维护旧引用块元数据，避免两份真源冲突。迁移时可把精确识别的旧元数据行无损包在 `<details data-kb-history="legacy-metadata">` 与 `</details>` 内，并使用固定摘要“历史来源记录（迁移前元数据，非当前真源）”；它们是不可当作当前声明的历史记录，解析器只对这一保留标记排除 active metadata。回执记录原行号、字节范围和 hash，不用泛化 regex 删除。正文可正常使用其他引语。
- 保真 `archive` 允许保留多个围栏外 H1，catalog 取首个；其他类型必须恰一个。缺 H1 时仅允许审核后的索引标题或明确机械文件名标题，并在迁移回执记录插入依据；不把代码块中的 `#` 当文章标题。

### 缺少定位链接不等于来源未知

可以定位的来源仍使用 `ref`。仅有明确作者、文章名、栏目名或脱敏本地报告出处但没有可公开定位的链接时，`archive` / `reference` / `case` 可以使用：

```yaml
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: 原材料中实际存在的作者或出处文字
    reason: 原始材料未提供可公开定位的链接
```

`citation` 必须来自可核对的原始出处，不能把本文、迁移快照、当前仓库 HEAD、随意推测的作者当作原始来源。原始出处含私有路径时只保留已有材料支撑的脱敏描述；完整历史正文和回执仍按既有可见性策略处理，不向新元数据复制敏感值。`reason` 非空。非定位来源最多支撑 `source-report`，引用它的模块需在 `limits` 说明缺 locator、未复现；不能支撑 static/runtime/parity/server 依据。`procedure` 不接受非定位来源。

真正无出处时只允许 `archive` 使用 `ref: null`、`basis: unknown`、非空 `reason`，且不提供 `citation`。它不能支撑任何 `source-report` 或更强模块；本地引用全 unknown 来源文档也只能声明 unknown。不得为通过检查填造 URL、selfref 或 source-report。

历史 archive 正文存在未围栏代码形如 `a[b](argument)` 时，非路径、非锚点、无文件扩展且不存在、同时可识别为数字/引号数组下标调用的 link 候选只记 `ambiguous_body_link` warning，原文保留，不宣称链接可用。显式相对/绝对路径、文件扩展、锚点和实际存在路径仍严格校验；正文可链接现存目录，sources 仍必须定位文章。reference/procedure/case 的正文引用不走此保真兼容分支。

一模块包含不同依据的结论时，使用结论表细分，不把最高 basis 覆盖整个模块；模块按保守边界标注，详细结论以表为准：

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 有范围的命题 | s1 与具体段落 | source-report | 端/版本/时间窗/操作 | 未知与反例 |

结论表与语义一致性目前是人工复核门；脚本只强制模块级来源、范围、依据与限制。不能把结构通过当成算法或服务端验收通过。

## 方法流程门禁

`procedure` 必须有以下非空稳定锚点：`prerequisites`（前提与输入）、`steps`（步骤及分支）、`outputs`（输出）、`acceptance`（验收）、`failure-exits`（失败出口）。正文步骤使用 S1/S2 等稳定 ID；图节点沿用同一 ID，图不新增事实。步骤编号、决策合理性、图文等义当前需人工复核，不声称已自动验证。

图源和预览放在文章同名资源目录。流程/时序优先可维护的 Mermaid 源与 SVG，精致总览可以用 diagram-design 的 SVG/HTML；格式、布局和渲染检查由各绘图 skill 完成，知识证据仍以本文为准。

## 模板与命令

`templates/archive.md`、`templates/reference.md`、`templates/procedure.md`、`templates/case.md` 是单一模板真源。模板与 `docs/` 不参与文章枚举，不必进入 INDEX。

保留 `generate` / `check` / `sanitize` 原入口，catalog JSON 顶层版本升为 2；既有字段、路径排序和 Markdown 目录布局保持兼容。新增字段供过滤与证据边界展示，不反写文章。

```powershell
python scripts/kb_catalog.py --root . query --target example --module parameters --type reference --client web --limit 10
python scripts/kb_catalog.py --root . query --type procedure --basis source-report
python scripts/kb_catalog.py --root . generate
python scripts/kb_catalog.py --root . check
python -m unittest discover -s tests -v
```

`query` 为大小写不敏感的精确 AND 过滤，还支持 `--version`、`--observed-at`、`--tag`、`--basis`；返回紧凑 JSON，包含 count/returned/results，每条给出稳定 ID、path、anchor、module、scope、basis、limits 和来源。未提供 module 时一模块一条，无模块文章返回一条 unknown 边界记录；`--type legacy` 可显式查看未迁移文章。过滤当前正文而非可能 stale 的 catalog；v2 合同/引用错误令查询失败，不把坏元数据悄悄隐藏。

`check` 保留旧文既有门禁与 warning；新增 schema、唯一 ID、scope、source、模块锚点、来源依据、关系与环校验。`generate` 是构建，不代替 `check`。legacy 缺口不自动升级成全库新错误。发布前仍执行敏感信息检查、人工语义/图示抽查与 `git diff --check`。

## 一次性整库迁移

`scripts/kb_migrate.py` 只消费经过盘点及语义审签的显式 JSON 清单，不根据文件名自动猜用途/模块，也不是常驻入库服务。已有 v2 可标 `action: preserve_v2`，必须 hash 一致且继续通过全库检查。

清单格式：`schema_version: 1`，`records` 每项包含仓库相对 `path`、原始字节 `pre_sha256`、完整 v2 `metadata`。可额外携带盘点证据。无 H1 项必须显式 `title_if_missing` 和 `title_basis`（兼容 `title_fallback_basis`），已有 H1 不允许覆盖标题。自动迁移限明确审签的 archive/reference/case；新 procedure 另行逐步提炼并验收。

```powershell
python scripts/kb_migrate.py --root . plan --manifest ../workspace/article/migration/manifest.json --out ../workspace/article/migration/plan
python scripts/kb_migrate.py --root . apply --plan ../workspace/article/migration/plan --batch-size 100
python scripts/kb_migrate.py --root . verify --plan ../workspace/article/migration/plan
# 仅在未发生外部更改且确需回退本计划时：
python scripts/kb_migrate.py --root . restore --plan ../workspace/article/migration/plan
```

- `plan` 就是 dry-run：只在库外创建完整逐目标备份、暂存正文/确定性 catalog、输入快照、字段差异及原字节保真回执；全库隔离副本通过 generate/check 才生成可 apply 的计划。不会写文章库。
- `apply` 写前复核计划、所有输入/附件/合同的 hash、目标清单、备份和暂存 hash，并再次隔离验完整投影。输入与锁内目标均禁止 hardlink（link count 必须为 1），拒绝借同 inode 修改仓外别名。Windows 目标文件通过同一拒 WRITE/DELETE 的独占写句柄复核 hash、seek/write/truncate/flush，防止原地写入及编辑器 atomic-save 竞态覆盖；每篇写前持久化 inflight journal，catalog 最后发布。代价是允许读者短暂看到中间态、不保证断电原子；常规写失败在持锁窗口尽可能恢复原字节，硬终止后的未知 hash 必须人工核对备份，不自动覆盖。apply/restore 在非 Windows fail-closed；plan/verify 仍可运行。分批中间态不是最终验收。
- 原正文、代码、图片引用、截断说明的字节保留，仅插入 front matter、精确历史元数据包装及必要的显式补标题；BOM 和既有混合换行保留。完整来源不因迁移被推断为 complete。
- apply 重复执行幂等，中断后按目标 before/after hash 续跑；任何其他字节变化或文件集合变化均 fail closed，不覆盖用户后续编辑。
- `verify` 必须所有目标达到 after hash 且正式库完整检查通过；未完成批次明确 incomplete。`restore` 仅恢复本计划列出的目标到备份字节，拒绝外部改动/越界，支持分批和重入；不删除文件、不自动撤销其他用户改动。
- 不自动删除 pending、commit 或 push；INDEX 路径布局不变时不机械重写。警告和技术证据边界必须进入正式回执。
