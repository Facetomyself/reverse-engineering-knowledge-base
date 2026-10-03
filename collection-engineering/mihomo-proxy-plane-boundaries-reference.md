---
schema_version: 2
id: collection-engineering-mihomo-proxy-plane-boundaries-reference
document_type: reference
scope:
  targets: [Mihomo/Clash proxy chain]
  client: collection engineering
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./mihomo-dialer-proxy-chain.md#三种链式平面不要混合同
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理来源文章区分的内核链、客户端级联和隔离 sidecar 三个平面；没有当前配置、版本锁定或运行时拓扑验收。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只描述代理建链角色与出口身份边界，不提供节点、凭据、真实 host 或业务请求样例。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 出口身份、Sticky/session 和错误分类的验收要求来自来源方法；本轮未执行代理检查、供应商 API 或目标请求。
relations:
  - type: derived_from
    target: ./mihomo-dialer-proxy-chain.md#三种链式平面不要混合同
tags: [Mihomo, Clash, dialer-proxy, preproxy, sidecar, route-identity, source-report]
---

# Mihomo 代理平面与出口身份边界参考

这是一张窄范围 `source-report` reference，用来区分桌面 Mihomo 内核链、客户端级联和隔离 sidecar，避免把“能通过本机 relay”误当成供应商出口身份已验收。完整背景与历史来源仍保留在 [Mihomo 链式代理归档](./mihomo-dialer-proxy-chain.md)。

<a id="interfaces"></a>
## 三种接口平面

| 平面 | 建链者 | 出口身份的归属 | 适用边界 |
|---|---|---|---|
| 内核链 | 正在运行的 Mihomo/Clash 配置 | 当前 profile 选择的落地节点 | 桌面 TUN 或系统代理；会随 GUI 策略状态变化 |
| 客户端级联 | `curl` 等请求客户端 | 业务代理参数指定的供应商网关/租约 | 只为某个客户端提供前置到达，不改变桌面 profile |
| 隔离 sidecar | 单独启动的 Mihomo worker | 每个 loopback listener 绑定的叶子节点 | 多节点探测或并发隔离；不 reload 当前桌面实例 |

内核字段、配置组、客户端 `preproxy` 和 sidecar listener 是不同控制面。不能因为它们都表现为“代理链”就共用同一份身份、Cookie 或并发合同。

<a id="request-chain"></a>
## 请求链边界

```text
桌面应用 -> Mihomo 内核链 -> 落地节点 -> 目标
请求客户端 -> 本机前置 -> 供应商网关/租约 -> 目标
探测 worker -> 独立 sidecar listener -> 叶子节点 -> 目标
```

- 内核链的前跳/后跳关系属于配置面；订阅刷新、策略组选择和 fake-ip 路由可能改变其行为。
- 客户端级联只负责把请求送到业务代理入口，供应商会话、Sticky lease、Cookie 隔离和目标出口仍属于业务控制面。
- sidecar 适合有界 fan-out 和叶子节点对照，运行后应回收自己的 listener，不把它伪装成当前桌面实例的全局状态。
- 旧的链式组配置与当前节点级 `dialer-proxy` 语义不能混写；迁移时应先查当前内核版本和订阅转换行为。

<a id="validation"></a>
## 验收与失败出口

复用这张卡时至少记录：

1. 本机 relay 是否可达，与供应商 route identity / session 是否分别可观测；relay 返回成功不等于目标出口身份正确。
2. 每个 worker 的 route、租约、Cookie 和连接生命周期是否一致；不得把独立身份请求复用到旧 tunnel。
3. `429`、`403/challenge`、transport error、timeout 和内容无效是否分开归因；代理层不能替业务层解释所有失败。
4. 若需要全机桌面链与采集器链，是否使用隔离 profile；误改当前 profile 时先恢复原规则，再重新做 relay 与出口检查。

来源只支持 `source-report`：本轮没有启动 Mihomo、切换配置、探测供应商、执行目标请求或验证服务端接受。文中的节点/账号配置只保留抽象角色，不包含凭据、真实 host、SID、Cookie 或请求样值。
