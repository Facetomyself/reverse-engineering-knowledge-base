---
schema_version: 2
id: web-reverse-material-provenance-ledger-reference
document_type: reference
original_date: '2026-09-23'
archived_date: '2026-10-02'
scope:
  targets: [unknown]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./material-provenance-ledger.md#四类出处
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只整理字段出处、生命周期、TTL/cache 与绑定边界；站点字段是历史来源例证，不是当前接口合同，不复制 Cookie、token、设备标识或样值。
  - name: decision-flow
    anchor: resolution-decision-flow
    sources: [s1]
    basis: source-report
    limits: 账本伪代码和分类启发式只支持静态决策框架；没有版本化输入、运行时 fixture、重试合同或可执行实现。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 只保留 localReproduced 与 serverAccepted 的记录边界和完成门；本卡没有执行请求、对拍或服务端验收。
relations:
  - type: derived_from
    target: ./material-provenance-ledger.md#四类出处
tags: [provenance, server_issued, unproven_synthetic, TTL, state-machine, fail-closed, localReproduced, serverAccepted, source-report]
---

# 签名材料出处账本参考

这张卡只提炼 [材料出处账本](./material-provenance-ledger.md) 的通用部分：一个字段能否本地生成，取决于它的 provenance、生命周期和绑定关系，而不取决于“能不能写出一个看起来像的字符串”。站点字段表、目标版本和作者自述均保持 `source-report`，不能从这张卡推导当前协议或服务端规则。

<a id="parameters"></a>
## Provenance 桶与生命周期

来源文章给出四类主要出处。实现时可以把它们落到字段账本的 `bucket`，并把来源、TTL、绑定上下文和缺失行为一起记录：

| bucket | 来源边界 | 缺失或过期时的处理 | 可复用边界 |
|---|---|---|---|
| `local` | 时钟、计数器或本会话状态机能够稳定产生 | 按已知状态机生成；不能用每次 `random()` 代替状态 | 需要同一字段的输入、顺序和版本依据 |
| `server` | 响应、Set-Cookie、响应头或页面运行时下发 | 读取未过期缓存或直接失败；不能本地伪造 | 必须保留签发来源和过期行为 |
| `runtime` | 页面 JS、Node VM 或其他隔离程序的输出 | 运行指定程序；无输出就失败，不降级成随机串 | 需要固定运行边界、输入形状和 provenance |
| `device` | 与同一进程、登录态、私钥或设备上下文绑定 | 校验绑定关系；不匹配就停止发送并整组重采 | 只能在绑定上下文仍成立时复用 |

账本伪代码还把 `user` 作为独立生命周期桶，用来记录扫码、短信或显式交互等材料；它不是上述四类的替代品。来源中小红书的六桶是一个站点实现例子，不能当作所有站点的统一枚举。

`unproven_synthetic` 只表示“本地留下了无法证明出处的合成值”，不是一种合法的 `local` 生成策略。字段能通过格式或长度检查，也不能因此获得服务端签发或接受的 provenance。

### TTL 与缓存

缓存策略必须跟随来源观察到的生命周期：

- 记录 `issued_at`、`expires_at` 或可核对的 TTL 来源；不要凭经验设置时长。
- 未过期的服务端或 runtime 材料可以按原来源规则复用，复用时仍保留 provenance 和关联会话。
- 过期先刷新；刷新失败只有在来源逻辑明确允许回退时才能使用旧值，否则失败。
- 把“函数能返回一个值”和“该值属于本次请求上下文”分开记录，避免用缓存或随机值掩盖来源丢失。

<a id="resolution-decision-flow"></a>
## 缺字段时的解析决策

下面是来源账本可以复用的静态决策顺序，不是某个站点的可执行请求流程：

1. 列出当前 path 所需字段，给每个字段登记 `bucket`、来源定位、TTL 和绑定上下文。
2. 先检查现有值是否仍在生命周期内；过期值不能仅因格式正确而继续使用。
3. `local` 字段走已有状态机，`server` 字段走签发值或允许的缓存，`runtime` 字段走指定隔离程序，`device` 字段先验证同进程/同登录绑定。
4. 任一必需字段缺失、过期、绑定不匹配或 runtime 无输出时，在发送前失败；不要用随机串、旧抓包值或另一端字段填洞。
5. 记录本次解析结果的 provenance 和失败原因。若只得到本地出参，不把状态写成服务端接受。

该顺序的重点是把“缺材料”翻译为可定位的失败，而不是把失败隐藏在一个形式正确的占位值里。它不提供具体签名、加密、Cookie 或设备参数的生成算法。

<a id="validation"></a>
## 完成门：localReproduced 与 serverAccepted

来源账本要求把两个状态分开：

| 状态 | 只表示 | 不能推出 |
|---|---|---|
| `localReproduced` | 本地观察、形状检查或对照结果与某个输入边界一致 | 不表示当前前端一致、不表示请求已发出、不表示业务成功 |
| `serverAccepted` | 有明确的服务端业务读回或等价的接受证据 | 不能由 HTTP 200、进程退出码、签名函数返回值或格式/长度检查单独推出 |

提交前的 check-gate 至少要能回答：

- 每个业务请求字段的出处是什么，是否仍在有效期内；
- 缺失、过期、绑定失败和隔离程序无输出时是否会在发送前停止；
- 本地产出、传输层完成和服务端业务读回分别记录在哪里；
- 是否有字段被 `unproven_synthetic` 标记，却被错误写成 `serverAccepted`。

这张卡没有 runtime、local parity 或 server acceptance 结果。它是来源报告驱动的 provenance/check-gate 参考，不是可直接运行的 signer、采集器或绕过流程。

## 来源范围与限制

- 来源的 Douyin、Xiaohongshu、Kuaishou、Xianyu 字段只用于说明分类方式；目标、版本、客户端和观测窗口均未知。
- 具体站点应另查对应 source archive 和版本化代码，再决定字段是本地、服务端、runtime 还是设备绑定。
- 本卡不复制 Cookie、token、设备标识、IP、账号、私有路径或样值，也不把作者报告升级为当前服务端事实。
