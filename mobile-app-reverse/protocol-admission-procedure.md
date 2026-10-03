---
schema_version: 2
id: protocol-admission-procedure
document_type: procedure
scope:
  targets: [app-protocol-admission]
  client: mobile
  version: unknown
  observed_at: unknown
sources:
  - id: admission-gates
    ref: ./protocol-admission-four-gates.md#完成门先于四关
    basis: source-report
  - id: diagnostic-order
    ref: ./protocol-admission-four-gates.md#空壳诊断顺序
    basis: source-report
  - id: sdk-state
    ref: ./protocol-admission-four-gates.md#sdk-状态机四关之外的第五项
    basis: source-report
  - id: working-checklist
    ref: ./protocol-admission-four-gates.md#本环境检查单
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [admission-gates, diagnostic-order, sdk-state, working-checklist]
    basis: source-report
    limits: 将既有方法文整理为诊断流程，未对新目标运行设备采集、签名对拍或服务端验收；四关为并联成立条件，步骤顺序不是实际网络请求顺序。
relations:
  - type: derived_from
    target: ./protocol-admission-four-gates.md#空壳诊断顺序
tags: [protocol-admission, device-consistency, interceptor, host-routing, transport-fingerprint, registration]
---

# App 协议准入诊断流程：从空响应到有边界的验收

适用于带设备状态、请求签名和独立网络栈的 App 协议客户端：请求能发出、甚至返回 HTTP 200，但业务 readback 为空，或注册签发了标识却尚未完成引导。纯 Web JS 参数、单函数算法移植和仅做脱壳不使用此流程。

本流程提炼自 [准入四关](./protocol-admission-four-gates.md)。来源文标注日期为 2026-09-06；这里保留的是排查方法，不继承其推导语料的目标版本、域名、常量或验证成果。本文所有方法依据均为 `source-report`，不表示已经在当前目标上通过。

四关是设备、签名、主机和传输必须**并联成立**的条件；S1–S8 只是诊断工作的优先顺序，不是注册包的发送顺序。实际请求依赖必须来自当前样本，不能按这张流程表直接串行重放。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 最低内容 | 不足时 |
|---|---|---|
| 目标与完成标准 | App/Web 边界、操作、版本或明确未知项；一份能够判断业务字段是否有效的响应基线 | F1；HTTP 状态码不能替代业务定义 |
| 设备与应用样本 | 同一设备/安装状态的画像、包版本、证书与相关 SDK 版本记录；无法取得的字段明确缺失 | F1；不以拼装字段或编造持久标识补齐 |
| 干净请求时间线 | 从冷启动、引导、注册/激活到一次低权限业务读的请求与响应关联；注明采集环境可能造成的变化 | F1；没有 HAR 不猜具体 path 或包顺序 |
| 复现对照材料 | 待检请求的 canonical 输入、body 字节、头部依赖、目标网络引擎及独立 TLS 会话记录 | 缺哪一关就停在哪一关，不把 unknown 当通过 |

原始流量、身份与会话值留在受控分析材料中；知识库只记录脱敏结构和证据定位。先冻结一份基线，后续一次只改变要检验的因素，避免同时换身份、主机和签名而无法归因。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 确认完成标准与材料齐备，区分业务 readback、空 JSON/列表和挑战响应 | 目标范围、响应判据、缺失项清单 | 材料可支撑本轮检查走 S2；否则 F1。已有有效 readback 也不能跳过其余完成门 |
| S2 | 检查设备画像的联合一致性与多次采集演化，排除混合机型/ROM、版本错配及采集环境伪影 | 设备/应用一致性表，注明哪些字段已对照、哪些未知 | 当前问题已解释且证据可定位走 S3；冲突或关键未知走 F2 |
| S3 | 按当前时间线核对注册、引导/激活、配置与业务读的状态依赖 | 状态迁移表及每一步的生产/消费关系，不只记录已签发标识 | 引导/激活闭合且有响应依据走 S4；缺步或只拿到标识走 F2 |
| S4 | 区分业务、注册/激活、指纹、boot 和区域路由；对照实际拨打而非静态域名能力表 | 主机分层与请求归属表、静态/运行时差异 | 目标操作的主机与区域有证据支持走 S5；错路由或证据缺口走 F2 |
| S5 | 对照目标网络引擎的 TLS/ALPN/HTTP2 等传输面，不用 User-Agent 相似替代 | 传输差异与控制变量记录，未采到的面明确未知 | 能说明当前会话的传输边界走 S6；差异未解释或缺对照走 F2 |
| S6 | 按拦截器依赖核对时钟、设备证明、canonical query/body、完整性与封装版本；有冲突实现先对拍 | 逐切面字节对照及输入依赖记录，明确本地实现与远程签名服务的边界 | 所需本地参数对照闭合走 S7；版本/MAGIC 不匹配、输入缺口或仅有远程 RPC 走 F2 |
| S7 | 在独立 TLS 会话检查非空业务 readback，并把公开对象与个性化接口等产品保护差异分开 | 响应判定和本次四关状态的关联；不以“头都齐了”替代成功 | 存在有效 readback 走 S8；仍为空或挑战走 F3 |
| S8 | 对照四个完成门，限定可对外报告的范围，并核查后续请求是否沿用同一套 SDK 状态 | 完成门矩阵、证据索引、残留限制 | 四门均有当前证据，输出有边界的验收结果；否则 F2。流程结束不自动推广到其他接口、身份或版本 |

步骤来源：S1、S8 对照 [完成门](./protocol-admission-four-gates.md#完成门先于四关)；S2–S7 对照 [空壳诊断顺序](./protocol-admission-four-gates.md#空壳诊断顺序)；S3 另对照 [SDK 状态机](./protocol-admission-four-gates.md#sdk-状态机四关之外的第五项)。这些是执行时应形成的证据，不是本次整理已经生成的实验结果。

<a id="process-map"></a>
## 流程图

图节点固定沿用 S1–S8、F1–F3；成功出口仅表示四门均满足的限定范围。正文是行为与分支真源，图不得添加跳过证据门的捷径。

![App 协议准入诊断：S1–S6 与材料 / 当前项失败出口](./assets/protocol-admission/diagnostic-steps.svg)

图 1：S1–S6 是诊断优先顺序，不是网络请求时序。实线只在该步证据闭合后推进；虚线表示冲突或关键未知，进入 F2。F1 补齐材料后回 S1；F2 单变量补采后回具体项及受影响的后续步骤，禁止无限盲试。

![App 协议准入诊断：S7–S8 与四门 AND 验收](./assets/protocol-admission/completion-gates.svg)

图 2：S7 有效业务 readback 不能跳过 S8；`localReproduced`、`serverAccepted`、`registrationComplete`、`sessionConsistent` 四门均须有当前证据，任一缺失或 unknown 都进 F2。F3 仅在有新可检验假说时回对应步骤，否则未闭合退出。这里的限定验收不推广到其他接口、身份或版本。

两图依据正文 [步骤与分支](#steps)、[验收](#acceptance)、[失败出口](#failure-exits) 整理，均为来源自述 / `source-report`，未新增目标实测。设备、签名、主机、传输四关必须并联成立；图中文字与渲染校验不是技术验收证据。PNG 与 `.mmd` 同目录提供备用阅读和维护源。

<a id="outputs"></a>
## 输出

1. **范围与证据索引**：目标操作、client、版本/时间窗的已知与未知、基线与复现的关联；公开稿不含身份或会话原值。
2. **四关诊断表**：每关的输入、观测、冲突、证据定位与下一项实验；没有依据的项保留 unknown。
3. **注册状态表**：当前目标实际观察到的引导、签发、激活、配置及业务依赖；不把示意状态机当真实包顺序。
4. **完成门矩阵**：分别记录 `localReproduced`、`serverAccepted`、`registrationComplete`、`sessionConsistent`，不可合并成笼统的“成功”。
5. **失败出口或限定验收**：结束于哪个步骤、缺什么、下一步补采什么，以及不能推广的接口/版本边界。

<a id="acceptance"></a>
## 验收

| 完成门 | 执行时必须提供的依据 | 不能代替它的东西 |
|---|---|---|
| `localReproduced` | 本地参数与目标 HAR 中对应字节、输入和版本的对照 | 公开脚本不报错、头名齐全、商业远程签名 RPC |
| `serverAccepted` | 独立 TLS 会话中的非空有效业务 readback，且响应判据在 S1 已明确 | HTTP 200、空列表、空 JSON、挑战页 |
| `registrationComplete` | 干净设备的注册与引导/激活均有时间线及响应依据 | 只获得 did、iid 或 token 字符串 |
| `sessionConsistent` | 后续请求所用设备、签名、主机和传输状态来自同一套 SDK/身份上下文 | 换出口继续沿用旧身份、签名对但路由错 |

只有对当前范围具备上述全部证据，才报告该范围的流程验收完成。文字整理、schema 校验或流程图渲染通过不属于这四个技术完成门。本次产物只是方法卡，四个门均没有新增目标的实测成果。

<a id="failure-exits"></a>
## 失败出口

- **F1 — 材料不足**：停止后续结论；补目标范围、干净时间线或基线响应后回 S1。不猜未知字段、真实 path、注册依赖或包顺序。
- **F2 — 当前关/完成门未闭合**：保留失败和未知；先定位到 S2–S6 或 S8 的具体项，做单变量补采/修正，再回到该项及受影响的后续步骤。它不是“继续换一版签名”的通用出口，也不允许无限盲试。
- **F3 — 四关检查后仍无有效业务读**：记录当前接口、状态与产品保护差异，承认尚无 `serverAccepted`；有新的可检验假说才回对应步骤，否则以未闭合退出。公开对象成功不能覆盖个性化接口失败，不能把所有空响应反写成签名错误。

## 适用边界

来源给出的是方法论，未提供所有 App 的统一状态机。具体版本、SDK、传输与路由变化会使历史对照失效；该变化应触发新样本检查，而不是往本文填一套永久常量。需要协议客户端工程结构时，再查 [纯协议 SDK 重建](./pure-protocol-sdk-reconstruction.md)，不要把采集并发或产能当成准入完成标准。

## 提炼说明（448）
retain 既有准入 procedure。
四门并联，非请求顺序。
本轮不改正文结构。
