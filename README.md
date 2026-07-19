# 逆向工程知识库

跨项目可复用的逆向分析文档。从 `workspace/` 中提取经过验证、具有通用参考价值的分析成果。

## 目录结构

```
article/
├── README.md                          # 本文件
├── INDEX.md                           # 人工维护的 canonical / 标签索引
├── CATALOG.md                         # 自动生成的逐篇详细目录
├── catalog.json                       # 自动生成的机器可读目录
├── scripts/kb_catalog.py              # catalog 生成、结构检查与高置信清理
├── tests/                             # catalog/linter 回归测试
├── protocols/                         # 协议分析
├── anti-detection/                    # 反检测/风控对抗
├── signature-algorithms/              # 签名算法逆向
├── packing-bypass/                    # 加固/混淆绕过
├── native-analysis/                   # Native SO 分析
├── mobile-app-reverse/                # 移动 App 逆向方法/环境/流程
└── web-reverse/                       # Web 逆向 (webpack/框架/JS)
```

## 使用方式

1. 开始新项目逆向前，先查 `INDEX.md` 的 canonical 入口和技术标签。
2. 需要定位合集子文章时，再查 `CATALOG.md`；自动化工具读取 `catalog.json`。
3. 文章来自真实项目实践，包含可复现的技术细节和代码级证据。
4. 每篇文章标注来源项目，需要更多上下文时可回 `workspace/<project>/` 查看。

## Catalog 与校验

```powershell
& "D:\reverse_ENV\.venv\Scripts\python.exe" "D:\reverse_ENV\article\scripts\kb_catalog.py" --root "D:\reverse_ENV\article" generate
& "D:\reverse_ENV\.venv\Scripts\python.exe" "D:\reverse_ENV\article\scripts\kb_catalog.py" --root "D:\reverse_ENV\article" check
& "D:\reverse_ENV\.venv\Scripts\python.exe" -m unittest discover -s "D:\reverse_ENV\article\tests" -v
```

`sanitize` 默认只做 dry-run；只有逐文件确认高置信尾部 marker 后才加 `--apply`。`CATALOG.md` 和 `catalog.json` 禁止手工编辑。

## 收录标准

- [x] 跨项目可复用的协议/算法/技术分析
- [x] 有可验证证据和代码引用的深度分析
- [x] 普适的逆向方法和技术模式
- [ ] 单个项目的业务逻辑分析
- [ ] 项目交付件 (report/triage/findings — 留在 workspace)

## 维护

- 完成一个项目的深度分析后，评估哪些产出有跨项目复用价值。
- 复制到对应分类目录，不要移动（workspace 原文件保留）。
- 同步更新 `INDEX.md` 的分类表和技术标签。
- 正文或索引变更后重新生成 catalog，并以 `check` 和单元测试作为提交门禁。
