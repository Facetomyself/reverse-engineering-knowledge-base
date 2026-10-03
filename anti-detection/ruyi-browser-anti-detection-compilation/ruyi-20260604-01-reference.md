---
schema_version: 2
id: firefox-container-tab-socks
document_type: reference
original_date: '2026-06-04'
archived_date: '2026-10-02'
scope:
  targets: [firefox-container-socks]
  client: firefox
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260604-01.md#14-代理配置格式
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留轮换开关、两种耗尽字面量，以及冒号和 IPv6 限制。不记录示例代理。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留 userContextId 的顺序绑定和进程内记忆。普通 tab 不能用这条区分。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: SOCKS5 走 nsProxyInfo 的 username 和 RFC1929。HTTP Basic 只属于 HTTP 类型。
relations:
  - type: derived_from
    target: ./ruyi-20260604-01.md#14-代理配置格式
  - type: derived_from
    target: ./ruyi-20260604-01.md#13-为什么必须用-container-tab
  - type: derived_from
    target: ./ruyi-20260604-01.md#15-socks5-认证路径
  - type: derived_from
    target: ./ruyi-20260604-01.md#16-http-密码代理兼容
tags: [firefox, socks5, container-tab, source-report]
---

# Firefox container tab 的 SOCKS5 轮换绑定

这篇卡检索 per-tab 代理怎样用非零 userContextId 选择列表项，耗尽时怎样停，以及 SOCKS5 认证为什么不走 Proxy-Authorization。不记录示例代理。

<a id="parameters"></a>
## 轮换字段

开关、回绕和停止都写在推荐格式的字段说明里。

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>  * ` proxy.rotate.enabled=true  ` ：开启 per-tab 代理轮换。</td><td>s1，源文件第 146 行</td><td>source-report</td><td>推荐字段</td><td>不展开兼容前缀</td></tr>
<tr><td>C2</td><td>  * ` proxy.rotate.exhausted=wrap  ` ：tab 数超过代理数时从头复用代理。</td><td>s1，源文件第 148 行</td><td>source-report</td><td>代理少于 tab</td><td>从头复用</td></tr>
<tr><td>C3</td><td>  * ` proxy.rotate.exhausted=direct|none|stop  ` ：代理不足时不继续分配轮换代理。</td><td>s1，源文件第 150 行</td><td>source-report</td><td>代理不足</td><td>不再分配轮换代理</td></tr>
<tr><td>C4</td><td>  * ` username  ` 和  ` password  ` 里不能包含冒号。</td><td>s1，源文件第 158 行</td><td>source-report</td><td>单行解析</td><td>不记录示例账号</td></tr>
<tr><td>C5</td><td>  * 当前解析不支持 IPv6 字面量 host。</td><td>s1，源文件第 160 行</td><td>source-report</td><td>host</td><td>不支持 IPv6 字面量</td></tr>
</table>

<a id="decision-flow"></a>
## 谁和哪一条代理绑定

container 的 userContextId 是来源给出的稳定序号。绑定不写出进程。

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C6</td><td>  6. 每个 container tab 的网络请求带有不同的  ` OriginAttributes.mUserContextId  ` 。</td><td>s1，源文件第 59 行</td><td>source-report</td><td>container tab</td><td>每个请求带 userContextId</td></tr>
<tr><td>C7</td><td>  7. ` nsProtocolProxyService::Resolve_Internal(...)  ` 根据  ` userContextId  ` 按顺序选代理。</td><td>s1，源文件第 61 行</td><td>source-report</td><td>Resolve_Internal</td><td>按 userContextId 顺序</td></tr>
<tr><td>C8</td><td>普通 tab 没有稳定的非零  ` userContextId  ` ，网络层无法可靠区分“第几个 tab”。</td><td>s1，源文件第 102 行</td><td>source-report</td><td>普通 tab</td><td>没有稳定非零 id</td></tr>
<tr><td>C9</td><td>    第 1 个出现的非零 userContextId -> 代理列表第 1 条</td><td>s1，源文件第 110 行</td><td>source-report</td><td>首次出现的 id</td><td>对应列表第一条</td></tr>
<tr><td>C10</td><td>绑定关系保存在 Firefox 进程内存中的  ` mRuyiHTTPProxyUserContexts  ` 。同一个 Firefox 进程内，同一个</td><td>s1，源文件第 115 行</td><td>source-report</td><td>同一 Firefox 进程</td><td>绑定只在内存</td></tr>
</table>

<a id="request-chain"></a>
## 认证走哪一层

SOCKS5 与 HTTP Basic 在来源里是两条路径。

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C11</td><td>SOCKS5 不走 HTTP  ` Proxy-Authorization  ` 头。</td><td>s1，源文件第 164 行</td><td>source-report</td><td>SOCKS5</td><td>不走 Proxy-Authorization</td></tr>
<tr><td>C12</td><td>如果  ` nsProxyInfo  ` 中有 username，SOCKS5 greeting 会提供 username/password auth 方法</td><td>s1，源文件第 185 行</td><td>source-report</td><td>nsProxyInfo 有 username</td><td>greeting 提供认证方法</td></tr>
<tr><td>C13</td><td>` 0x02  ` ，再按 RFC1929 发送 username/password。</td><td>s1，源文件第 186 行</td><td>source-report</td><td>方法 0x02</td><td>按 RFC1929 发送，不展开报文</td></tr>
<tr><td>C14</td><td>per-tab SOCKS5 的核心在  ` nsProtocolProxyService.*  ` 。</td><td>s1，源文件第 190 行</td><td>source-report</td><td>选择代理</td><td>核心在 nsProtocolProxyService</td></tr>
<tr><td>C15</td><td>同时保留了 HTTP 密码代理兼容：当代理类型是 HTTP，并且  ` nsProxyInfo  ` 中有 username/password 时，  `
nsHttpChannelAuthProvider.*  ` 会生成 Basic  ` Proxy-Authorization  ` 凭据。</td><td>s1，源文件第 192–193 行</td><td>source-report</td><td>HTTP 密码代理兼容</td><td>不是 SOCKS5 路径</td></tr>
</table>

## 验证与限制

firefox-container-socks、socks5、firefox 的对应模块查询都是 0。更早的“每个窗口不同 SOCKS5”归档没有这组 userContextId 规则，也还不是同 target 的卡片。第 192–193 行在表里做了不带账号的改写，原文仍是证据 quote。数据流末端没有验收条件。描述保持 source-report。
