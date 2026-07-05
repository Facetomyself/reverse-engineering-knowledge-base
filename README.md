# 逆向工程知识库

跨项目可复用的逆向分析文档。从 `workspace/` 中提取经过验证、具有通用参考价值的分析成果。

## 目录结构

```
article/
├── README.md                          # 本文件
├── protocols/                         # 协议分析
├── anti-detection/                    # 反检测/风控对抗
├── signature-algorithms/              # 签名算法逆向
├── packing-bypass/                    # 加固/混淆绕过
├── native-analysis/                   # Native SO 分析
└── web-reverse/                       # Web 逆向 (webpack/框架/JS)
```

## 使用方式

1. 开始新项目逆向前，查阅 `docs/article-index.md` 按主题/技术标签检索相关文章
2. 文章来自真实项目实践，包含可复现的技术细节和代码级别的证据
3. 每篇文章标注了来源项目，需要更多上下文时可回 `workspace/<project>/` 查看

## 收录标准

- [x] 跨项目可复用的协议/算法/技术分析
- [x] 有可验证证据和代码引用的深度分析
- [x] 普适的逆向方法和技术模式
- [ ] 单个项目的业务逻辑分析
- [ ] 项目交付件 (report/triage/findings — 留在 workspace)

## 维护

- 完成一个项目的深度分析后，评估哪些产出有跨项目复用价值
- 复制到对应分类目录，不要移动（workspace 原文件保留）
- 同步更新 `docs/article-index.md` 索引
