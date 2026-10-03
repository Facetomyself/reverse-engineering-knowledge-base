---
schema_version: 2
id: web-reverse-castle-profile-compression-parity
document_type: archive
scope:
  targets:
  - unknown
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: '`本地项目分析材料（定位不公开）`，`3fe6ea7d`，`utils/castle_token.py`、`utils/castle_crypto.py`、`utils/chromium_deflate.py`、`x_apis/login_api.py`'
  reason: 出处来自原归档来源字段；本地路径已省略，原始材料未随本文公开，本轮未重跑来源实验。
source_completeness: unknown
tags:
- Castle
- Rl
- CompressionStream
- raw-DEFLATE
- ctypes
- parity
original_date: 2026-09-27（本轮源码对照窗口）
archived_date: '2026-09-27'
---

# Castle 对照：完整画像输入、压缩字节一致性与纯算边界

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: `workspace/cv-cat/XApis`，`3fe6ea7d`，`utils/castle_token.py`、`utils/castle_crypto.py`、`utils/chromium_deflate.py`、`x_apis/login_api.py`
> 原始发布时间: 2026-09-27（本轮源码对照窗口）
> 归档日期: 2026-09-27
> 分类: web-reverse
</details>
>
> 把加密和封装改写成 Python，只闭合了计算边界；完整浏览器画像、逐动作状态、压缩后端仍是独立依赖。解压后相同不能代替压缩字节相同，输入齐全也不能代替服务端接受。

## 将运行器与本地计算分成两个入口

`generate()` 保留 Node/浏览器环境运行器，`generate_pure()` 接收外部提供的完整 `Rl` 或序列化 profile，后者自身不做 Node 调用、DOM 仿真或网络请求。两个函数的存在不等于默认登录路径一定纯算：调用链只有提供 `pure_rl_values` 才选后者。

严格入口 `login_by_password_pure()` 要求显式 profile，并传递 `pure_required=True`。这种显式选择优于失败后暗中换路径；运行器产物与本地算法产物应分别记录 provenance。

## “完整输入”是合同，不是随手拼设备字段

上游当前接受完整旧版或现行向量，以及 `raw` / `rawB64` profile。数字键映射必须连续；向量缺槽位会失败。长度校验只能证明形状，不能证明各字段来自同一个页面状态。

profile 还可能携带 `prefix`、`compression`、`inner_variant` 和 `timestamp_ms`。这些元信息属于字节封装合同，不能把它们当噪声丢掉再使用默认值。

登录调用点 `_pure_profile_for_action()` 能按动作或序列选 profile。动作发生后，Cookie、storage、行为材料可能改变；把同一份 profile 无限复用为多个步骤，会把“序列化函数正确”和“状态仍然有效”混为一谈。当前序列选择在耗尽后复用最后一项，是源码行为，不是允许无限复用的验证结论。

## 压缩后能解开，仍可能没有字节 parity

`generate_pure()` 默认 `compression='native'`。上游通过 `ctypes` 加载本地 Chromium-zlib DLL，以匹配其目标浏览器的 `CompressionStream('deflate-raw')`。另有显式 `fallback` 压缩实现。

| 层 | 需要固定的量 | 只验这一层遗漏什么 |
|---|---|---|
| 输入序列化 | 字段顺序、完整向量、raw 字节、版本 | 页面材料是否同源、是否过期 |
| 压缩 | 后端、参数、输出字节 | 能解压不保证压缩编码相同 |
| 封装 | 时间戳、变体、前缀和动态输入 | 相同长度不保证内部字节相同 |
| 请求上下文 | 动作、Cookie/storage 版本、传输面 | 本地 parity 不保证服务端接受 |

源码注释把 Chromium 和 CPython zlib 的输出差异归因于字典哈希实现；本轮只确认后端选择与依赖边界，没有重建 DLL 或独立验证该归因。复用时应以固定输入 fixture 的字节差异为准，而非仅依赖注释。

## “纯 Python”不能吞掉 native 平台限制

`chromium_deflate.py::_load()` 明确限制打包后端为 Windows。默认 native 不可用时抛错，不自动改为 fallback。这是值得保留的 fail-closed：静默换压缩器可能改变 token 字节。

因此准确分类是“Python 组装 + 可选 native 压缩依赖”，不是“跨平台、无 native 依赖的纯 Python”。无需浏览器执行，也不等于无需浏览器采集输入。不得复制作者的真实向量、Cookie、storage、盐或封装常量到知识库。

## 可复用验收顺序

1. 给脱敏 fixture 锁定输入与版本来源，原始画像仅留受限本地。
2. 固定时间和其他动态输入，先比序列化，再比压缩流，再比完整封装；只报告差异位置或摘要。
3. native 缺失、向量缺槽位、元信息不兼容均应显式失败，不用随机值填洞。
4. 单独验证动作间状态变化、会话字段完整性与业务读回。

上述顺序是移植验收建议，不是本轮执行结果。本轮仅静态阅读 [XApis @ 3fe6ea7d](https://github.com/cv-cat/XApis/tree/3fe6ea7d)，没有加载 DLL、运行 Node 或访问线上目标。整体请求装配见 [X GraphQL 与会话分层](./x-twitter-graphql-case.md)。

<a id="reference-extraction-202"></a>
## 提炼说明

本来源保留为完整 archive。按本批全文审查，将 `generate` / `generate_pure` 分流、画像封装元信息、native `deflate-raw` fail-closed 与四层对照，提炼为 [Castle 画像压缩字节 parity 参考](./castle-profile-compression-parity-reference.md)。

X GraphQL 会话卡只覆盖登录后的请求装配。该 reference 只标记 `source-report`；未加载 DLL、未运行 Node 或目标服务，不收录向量、Cookie、storage、盐或封装常量，不表示当前 runtime、parity 或 server acceptance。
