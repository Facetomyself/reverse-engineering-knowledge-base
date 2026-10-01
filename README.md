# 逆向工程知识库

跨项目可复用的逆向分析与采集工程文档。保留清洗后的来源文章，按价值提炼参考卡、方法流程与分析案例；来源自述、静态核查和运行时证据分别标注，不把归档完成当作技术验证。

## 目录结构

```
article/
├── README.md                          # 本文件
├── INDEX.md                           # 人工维护的 canonical / 标签索引
├── CATALOG.md                         # 自动生成的逐篇详细目录
├── catalog.json                       # 自动生成的机器可读目录
├── scripts/kb_catalog.py              # catalog 生成、结构检查与高置信清理
├── scripts/kb_migrate.py              # 一次性显式清单迁移、回执与恢复
├── tests/                             # catalog/linter 回归测试
├── protocols/                         # 协议分析
├── anti-detection/                    # 反检测/风控对抗
├── signature-algorithms/              # 签名算法逆向
├── packing-bypass/                    # 加固/混淆绕过
├── native-analysis/                   # Native SO 分析
├── mobile-app-reverse/                # 移动 App 逆向方法/环境/流程
├── collection-engineering/            # 代理并发、可恢复采集、spool/mirror 与生产可靠性
├── drm-content-acquisition/           # DRM 内容获取工程（L3 CDM 提取、license 重放、解密管道）
└── web-reverse/                       # Web 逆向 (webpack/框架/JS)
```

## 使用方式

1. 开始新项目逆向前，先查 `INDEX.md` 的 canonical 入口和技术标签。
2. 需要定位合集子文章时，再查 `CATALOG.md`；自动化工具读取 `catalog.json`。
3. 新格式支持按目标、模块、用途和适用范围组合查询，返回模块锚点与来源边界；未迁移文章明确为 legacy。
4. 先读来源与限制，再判断是否可复用；Public 文章不写本地 workspace 原始证据或凭据。

## 分型、模板与查询

合同与迁移边界见 [知识文档合同 v2](docs/knowledge-contract.md)。模板的单一真源为 [archive](templates/archive.md)、[reference](templates/reference.md)、[procedure](templates/procedure.md)、[case](templates/case.md)。新增/主动迁移文章采用 v2；旧引用块继续兼容，不批量改写。

v2 使用安全 YAML 依赖 `PyYAML>=6,<7`，标题/链接使用 CommonMark 依赖 `markdown-it-py>=3,<5`。安装：`python -m pip install "PyYAML>=6,<7" "markdown-it-py>=3,<5"`。

整库主动迁移使用 `scripts/kb_migrate.py` 的库外 plan → 分批 apply → verify；原始字节、已有日期和历史出处保留，不推断技术验证。缺 locator 与未知出处分别表达；具体清单、备份和 restore 边界见内容合同。apply/restore 的并发写保护仅在 Windows 实现，同一锁定句柄检查/写入，拒绝外部 direct-write 与 atomic-save；不承诺断电原子性。

```powershell
python scripts/kb_catalog.py --root . query --target example --module parameters --type reference --client web --limit 10
python scripts/kb_catalog.py --root . query --type procedure
```

接口、参数机制、请求链路、风控和验证模块只登记有材料的部分；archive 不要求虚构模块。流程图必须回到正文步骤和失败出口，图不新增技术事实。

## Catalog 与校验

```powershell
& "D:\reverse_ENV\.venv\Scripts\python.exe" "D:\reverse_ENV\article\scripts\kb_catalog.py" --root "D:\reverse_ENV\article" generate
& "D:\reverse_ENV\.venv\Scripts\python.exe" "D:\reverse_ENV\article\scripts\kb_catalog.py" --root "D:\reverse_ENV\article" check
& "D:\reverse_ENV\.venv\Scripts\python.exe" -m unittest discover -s "D:\reverse_ENV\article\tests" -v
```

`sanitize` 默认只做 dry-run；只有逐文件确认高置信尾部 marker 后才加 `--apply`。`CATALOG.md` 和 `catalog.json` 禁止手工编辑。

## 收录标准

- [x] 保留来源、完整性缺口与证据边界的清洗归档
- [x] 跨项目可复用的协议/算法/技术分析
- [x] 有可验证证据和代码引用的深度分析
- [x] 普适的逆向方法和技术模式
- [x] 有运行时证据支撑的采集控制面、交付链与非侵入式运维模式
- [ ] 单个项目的业务逻辑分析
- [ ] 项目交付件 (report/triage/findings — 留在 workspace)

## 维护

- 完成一个项目的深度分析后，评估哪些产出有跨项目复用价值。
- 复制到对应分类目录，不要移动（workspace 原文件保留）。
- 同步更新 `INDEX.md` 的分类表和技术标签。
- 正文或索引变更后重新生成 catalog，并以 `check` 和单元测试作为提交门禁。
