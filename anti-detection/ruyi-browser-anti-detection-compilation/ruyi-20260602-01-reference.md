---
schema_version: 2
id: webkit-curl-http-proxy-credentials
document_type: reference
original_date: '2026-06-02'
archived_date: '2026-10-02'
scope:
  targets: [webkit-curl-proxy]
  client: webkit
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260602-01.md#运行配置
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留字段优先级、四个关闭字面量和自动补 http://。不记录示例账号。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留地址与密码分开，以及认证挑战必须是当前代理。空文件节不补接口。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只保留 CONNECT 阶段认证，以及 error 28 的两种来源解释。
relations:
  - type: derived_from
    target: ./ruyi-20260602-01.md#运行配置
  - type: derived_from
    target: ./ruyi-20260602-01.md#整体链路
  - type: derived_from
    target: ./ruyi-20260602-01.md#为什么要这样改
  - type: derived_from
    target: ./ruyi-20260602-01.md#为什么要同时处理-authenticationchallenge
tags: [webkit, curl, http-proxy, source-report]
---

# WebKit curl HTTP 代理的凭据分离

这篇卡检索 MiniBrowser 从 fp.txt 读取 HTTP 代理时的字段优先级、关闭字面量，以及凭据为什么不能留在代理 URL 里，也不能应答普通网站的认证挑战。不记录示例账号。

<a id="parameters"></a>
## 读哪些字段

优先级和关闭写法都在运行配置一节。

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>也就是说，优先使用  ` http_proxy  ` ，如果没有写这个字段，再尝试读取  ` proxy  ` 和  ` proxy_url  ` 。</td><td>s1，源文件第 77 行</td><td>source-report</td><td>fp.txt 三个字段</td><td>不记录示例账号</td></tr>
<tr><td>C2</td><td>    http_proxy=0
    http_proxy=false
    http_proxy=none
    http_proxy=disable</td><td>s1，源文件第 84–87 行</td><td>source-report</td><td>关闭代理</td><td>不推断其它假值</td></tr>
<tr><td>C3</td><td>  * 自动给没有协议头的代理地址补  ` http://  ` 。</td><td>s1，源文件第 139 行</td><td>source-report</td><td>没有协议头的地址</td><td>不记录补完后的整段</td></tr>
</table>

<a id="decision-flow"></a>
## 凭据在什么时候才能提交

原则是分开保存。自动填入还有 host、port 和是否为代理这三道限制。

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C4</td><td>    代理地址和代理密码分开保存、分开传递。</td><td>s1，源文件第 125 行</td><td>source-report</td><td>保存和传递</td><td>不从空文件节补接口</td></tr>
<tr><td>C5</td><td>不要长期把密码放在代理 URL 里。</td><td>s1，源文件第 127 行</td><td>source-report</td><td>代理 URL</td><td>不长期放密码</td></tr>
<tr><td>C6</td><td>    URL 只保存代理地址。</td><td>s1，源文件第 236 行</td><td>source-report</td><td>分开后的 URL</td><td>赋值行不复制</td></tr>
<tr><td>C7</td><td>  * 当 WebKit 收到代理认证挑战时，只对当前配置的代理 host/port 自动填入账号密码。</td><td>s1，源文件第 149 行</td><td>source-report</td><td>认证挑战</td><td>仅当前代理 host/port</td></tr>
<tr><td>C8</td><td>  * 是否是代理认证：  ` WKProtectionSpaceGetIsProxy(protectionSpace)  `</td><td>s1，源文件第 153 行</td><td>source-report</td><td>代理认证判断</td><td>还要核对 host 与 port</td></tr>
<tr><td>C9</td><td>这样可以避免把代理账号密码错误地发给普通网站。</td><td>s1，源文件第 159 行</td><td>source-report</td><td>普通网站</td><td>避免送出代理账号</td></tr>
<tr><td>C13</td><td>然后只在确认是当前代理服务器的挑战时，才自动提交代理凭据。</td><td>s1，源文件第 274 行</td><td>source-report</td><td>自动提交</td><td>先确认是当前代理</td></tr>
<tr><td>C14</td><td>这样既能兼容 WebKit 的认证流程，又不会把代理密码发给普通网站。</td><td>s1，源文件第 276 行</td><td>source-report</td><td>WebKit 认证流程</td><td>没有反例流量</td></tr>
</table>

<a id="request-chain"></a>
## HTTPS 失败时能说什么

CONNECT 认证失败和线路超时在来源里会叠在同一个 curl 28 上。

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C10</td><td>    HTTP 密码代理访问 HTTPS 网站时，需要在 CONNECT 阶段完成代理认证。</td><td>s1，源文件第 184 行</td><td>source-report</td><td>HTTPS 经由 HTTP 代理</td><td>认证发生在 CONNECT</td></tr>
<tr><td>C11</td><td>如果代理账号密码没有正确传给 libcurl，HTTPS 访问就容易失败，表现为：</td><td>s1，源文件第 197 行</td><td>source-report</td><td>凭据未到达 libcurl</td><td>失败表现不逐条复制</td></tr>
<tr><td>C12</td><td>其中  ` Error code 28  ` 是 curl timeout，可能是代理认证问题，也可能是代理线路到目标网站不稳定。</td><td>s1，源文件第 208 行</td><td>source-report</td><td>curl error 28</td><td>timeout 不能单独判定认证失败</td></tr>
</table>

## 验证与限制

webkit-win-minibrowser 的 parameters、decision-flow、interfaces 查询都是 0。那篇是 Win11 构建入口，不覆盖 curl 的凭据字段。修改文件清单里有多处空标题，所以不建 interfaces。第 84–87 行的关闭字面量在表内改写了顺序说明，原文四行仍是证据 quote。没有验收步骤。描述保持 source-report。
