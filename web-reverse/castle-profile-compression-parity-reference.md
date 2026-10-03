---
schema_version: 2
id: web-reverse-castle-profile-compression-parity-reference
document_type: reference
original_date: '2026-09-27'
archived_date: '2026-10-03'
scope:
  targets: [castle]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./castle-profile-compression-parity.md#reference-extraction-202
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录入口分流、画像形状与封装元信息角色；不收录向量、Cookie、storage、盐或封装常量，也不把长度校验升格为同源证明。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 四层对照顺序是来源移植建议，不是本轮执行结果或五门 procedure。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: native 缺席 fail-closed、解压成功≠压缩字节一致均为作者陈述；未加载 DLL、未跑 Node、未访问目标。
relations:
  - type: derived_from
    target: ./castle-profile-compression-parity.md#reference-extraction-202
  - type: supplements
    target: ./x-graphql-session-reference.md#request-chain
tags: [Castle, Rl, CompressionStream, deflate-raw, ctypes, parity, source-report]
---

# Castle 画像压缩字节 parity 参考

这张窄卡只整理来源 archive 对 **Castle 本地组装** 的入口分流、完整画像合同、压缩后端与分层验收。X GraphQL 会话卡仍覆盖登录后的 registry/CSRF/业务读回；本文不替代该卡，也不把作者静态对照升格为本轮 runtime、parity 或 server acceptance。

<a id="parameters"></a>
## 入口与画像合同

| 项 | 来源描述 | 类别 | 边界 |
|---|---|---|---|
| `generate()` | 保留 Node/浏览器运行器 | encoding / runner | 自身会碰运行时；不等于默认登录路径。 |
| `generate_pure()` | 接收外部完整 `Rl` 或序列化 profile | encoding / local | 不做 Node、DOM 或网络；只有显式 `pure_rl_values` 才选这条。 |
| `login_by_password_pure()` | 要求显式 profile 且 `pure_required=True` | 入口纪律 | 失败后不得暗中换回运行器。 |
| 向量 / `raw` / `rawB64` | 上游接受完整旧版或现行向量 | fingerprint / 封装 | 数字键须连续；缺槽位失败。长度只证明形状。 |
| `prefix` / `compression` / `inner_variant` / `timestamp_ms` | 字节封装合同 | encoding | 不能当噪声丢掉再填默认值。 |
| `_pure_profile_for_action()` | 按动作或序列选 profile | token / 状态 | 动作后 Cookie/storage 可能变；耗尽后复用最后一项是源码行为，不是“仍有效”。 |

<a id="decision-flow"></a>
## 分层对照顺序

来源把“能解开”和“压缩字节相同”以及“服务端接受”分开。建议检索时按层走：

1. 输入序列化：字段顺序、完整向量、raw 字节、版本。本层过不了，后面的压缩对照无意义。
2. 压缩：后端、参数、输出字节。`generate_pure()` 默认 `compression='native'`，经 `ctypes` 调本地 Chromium-zlib，对齐目标浏览器 `CompressionStream('deflate-raw')`；另有显式 `fallback`。
3. 封装：时间戳、变体、前缀和动态输入。相同长度不保证内部字节相同。
4. 请求上下文：动作、Cookie/storage 版本、传输面。本地 parity 不保证服务端接受。

源码注释把 Chromium 与 CPython zlib 差异归因于字典哈希实现；本轮只确认后端选择与依赖边界，没有重建 DLL 或独立验证该归因。复用时以固定输入 fixture 的字节差异为准。

<a id="validation"></a>
## 验收口径与限制

| 观察 | 来源允许的最小结论 | 不允许的外推 |
|---|---|---|
| native 仅打包 Windows，缺席即抛错 | fail-closed，避免静默换压缩器 | 跨平台无 native 的纯 Python |
| 解压后明文相同 | 压缩编码可能仍不同 | 已与浏览器 CompressionStream 字节一致 |
| 输入形状完整 | 字段可能来自不同页面状态或过期材料 | 序列化函数正确等于会话仍有效 |
| 无需浏览器执行本地组装 | 画像仍须浏览器采集 | 纯算已覆盖采集面 |

## 验证与限制

- 来源不可公开定位；`client` / `version` / `observed_at` 均为 unknown。整体请求装配见 [X GraphQL 与会话分层](./x-graphql-session-reference.md)。
- 分类是“Python 组装 + 可选 native 压缩依赖”。不得复制真实向量、Cookie、storage、盐或封装常量。
- 未加载 DLL、未运行 Node、未访问线上目标；四层顺序不是本轮执行结果，也不构成 procedure。
