---
schema_version: 2
id: web-reverse-iv8-python-v8-runtime-reference
document_type: reference
original_date: '2026-09-24（原文标注）'
archived_date: '2026-10-02'
scope:
  targets: [iv8]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./iv8-python-v8-browser-env.md#reference-extraction-114
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告中的 Python/V8 context、`page.load`、`expose`、`add_resource`、netLog 和 Isolate/GIL 边界；没有 pinned build、完整 ABI、对象生命周期或异常映射验证。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 仅提供离线资源、host callback 与请求观察之间的选择线索；不是可直接执行的补环境 procedure，也不覆盖目标页面的成功条件。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只描述来源报告中的 host fetch → resource injection → JS 请求读取关系；没有统一请求/响应 schema、Cookie/重定向/超时/取消或真实网络验收。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 仅给出版本、资源、时间调度和 callback 边界的核验项目；没有 runtime fixture、local parity、目标业务 readback 或 server acceptance。
relations:
  - type: derived_from
    target: ./iv8-python-v8-browser-env.md#reference-extraction-114
tags: [iv8, Python, V8, host-bridge, page.load, add_resource, netLog, Isolate, GIL, source-report]
---

# iv8 Python/V8 runtime 与 host bridge 参考

这是一张窄范围 `source-report` reference：它把 iv8 归档中可复用的嵌入式 V8 边界整理成检索入口，帮助区分页面输入、宿主回调、离线资源和请求观察。它不是完整 Chrome 兼容层、通用 V8 ABI、指纹基线或服务端成功证明。

<a id="interfaces"></a>
## Runtime 与接口边界

- 来源将 `JSContext`/`RuntimeContext` 描述为带浏览器对象面的单进程 V8 context；`page.load` 接收 HTML、`baseURL` 和资源表，表示把已准备的文档与资源灌入运行时，不等价于真实浏览器导航。
- `expose` 将 Python 侧函数或数据放到 JS 可访问的 host namespace；来源报告的桥接调用以同步回调为主，Python 回调可能重新取得 GIL。回调异常、重入、取消、异步返回和对象生命周期没有闭合合同。
- `add_resource` 用 URL 到响应的离线映射供运行时读取，`netLog` 负责观察请求条目；两者是注入面和观察面，不应混成“iv8 自己已发出真实 HTTP”。
- 来源把一个 Isolate 与其 context 的归属分开讨论，并建议并发时按 Isolate 隔离；不复制来源的 benchmark 数字，也不把该建议当作容量保证。

<a id="decision-flow"></a>
## 选择线索

| 需要回答的问题 | 来源报告中的优先观察面 | 不应直接推出 |
|---|---|---|
| 页面脚本只需要固定 HTML/外联资源吗？ | `page.load` 的 `html`、`baseURL` 与预置 `resources` | 已完成真实导航、Cookie 建立或目标页面成功 |
| JS 需要宿主提供数据或动作吗？ | `expose` / host callback，并记录同步边界 | 已有稳定异步 ABI、错误传播或可取消请求 |
| XHR/fetch 只需离线响应吗？ | `add_resource` 预灌或运行中注入 URL 响应 | iv8 默认直连目标网络 |
| 需要知道脚本请求了什么吗？ | `netLog` 观察请求条目，再与资源注入分开记录 | 观察到请求就等于拿到业务响应或服务端接受 |
| 多 context 并发是否共享宿主状态？ | 以 Isolate/context 所有权和 GIL 交接作为待核验边界 | 进程内多个 context 天然互相隔离或线性扩展 |

这些是来源材料的分流提示，不是闭合步骤。遇到 `drain()`、logical/system time、`wrapNative` 或 `isTrusted` 时，必须把它们视为 iv8 特定版本的行为声明，不直接当成一般浏览器语义。

<a id="request-chain"></a>
## 请求与资源链

来源报告给出的最小关系可以写成：

```text
页面/脚本输入
  -> iv8 JS 请求（XHR/fetch/外联资源）
  -> 离线 resource map 读取
       或 host callback 交给 Python 获取响应
  -> Python 将响应按 URL 注入 add_resource
  -> JS 继续读取响应；netLog 另行记录观察结果
```

这条链只说明宿主桥接与资源表的角色。来源没有提供统一的 body、headers、redirect、cookie、timeout、cancellation、URL normalization 或错误分类合同，因此不能把它改写成通用 HTTP adapter，也不能从 `realFetch` 示例推出当前目标可以直接重放。

<a id="validation"></a>
## 验证边界

发布或复用这张卡时，至少应单独记录：

1. iv8 包与运行时版本，以及 `page.load`/`expose`/`add_resource`/`netLog` 的实际调用形状。
2. 文档 URL、资源 URL、输入字节和响应身份，避免把资源版本或页面分支混为算法差异。
3. logical/system time、microtask/timer 顺序、Isolate 所属和 callback/GIL 交接；不要用来源 benchmark 或 profile defaults 代替测量。
4. JS 侧读回、错误传播和目标业务 response；离线资源命中、netLog 记录和业务 server acceptance 必须分开。

来源只支持 `source-report`：本轮没有执行 iv8、浏览器、WASM、local parity、真实请求或服务端业务回读。WASM 的 imports/exports、memory/pointer-length、view lifetime、callback/error/release contract，以及 Canvas/Worker/Service Worker 等能力的完整性均未在本卡闭合。
