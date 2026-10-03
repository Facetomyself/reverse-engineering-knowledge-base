---
schema_version: 2
id: web-reverse-wasm-js-fallback-version-reference
document_type: reference
original_date: '2026-06-22（导出文件标注）'
archived_date: '2026-10-02'
scope:
  targets: [unknown]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./wasm-js-fallback-version-parity.md#reference-extraction-105
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告提出的 WASM 指针/长度与 memory-view 生命周期检查项；没有模块、ABI、返回缓冲区或释放行为的独立证据。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅整理资源版本、活动分支和输入字节身份；没有目标端点、资源 hash、完整输入合同或可复用算法。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 仅提供首处分叉与结果措辞边界；没有 fixture、阈值、runtime parity、业务读回或服务端接受证据。
relations:
  - type: derived_from
    target: ./wasm-js-fallback-version-parity.md#reference-extraction-105
tags: [WASM, JS fallback, version binding, branch provenance, pointer-length, source-report]
---

# WASM 与 JS fallback 版本边界参考

这是一张窄范围 source-report reference：用于避免把同一页面中的 WASM、旧 JS fallback 和新 fallback bundle 按同名函数或文件名直接视作等价实现。它记录应固定的资源身份和边界差异，不证明任何当前目标的算法或业务成功。

<a id="interfaces"></a>
## WASM 边界与资源身份

| 层 | 应记录的身份 | 不能单独作为身份的线索 |
|---|---|---|
| 页面加载器 | 入口脚本 hash、版本选择分支、实际模块 URL 的证据 | 文件名中的产品词 |
| WASM 模块 | 模块 hash、imports/exports、加载方式、实例边界 | 页面出现 `WebAssembly` 字样 |
| JS fallback | fallback hash、选择条件、对应版本 | 函数同名或都叫 `sign` |
| WASM pointer/length 边界 | 字符串编码、memory-view 有效期、内存增长、返回长度、释放责任 | 仅比较最终字符串长度 |

上表是来源报告的记录框架，不是当前资源清单。JS wrapper 边界一致只能说明 wrapper 输入/输出形状相近，不能据此恢复 WASM 内部语义；浏览器支持 WASM 也不能证明当前请求实际走了 WASM。

<a id="parameters"></a>
## 活动分支与输入字节

先绑定实际活动分支，再比较输入合同。对同一受控输入，应按以下边界记录：业务字段、JSON/URL 编码后的文本、进入模块的字节、边界返回值、最终请求字段。若核心算法之前的字节已经不同，优先记录为输入合同分叉，不直接归因于算法不同。

输入维度可覆盖空串、非 ASCII、保留字符、重复字段、空值和边界长度；随机或有状态输入需固定条件或记录 provenance，不强行要求两个合法实现产生相同字节。这里没有补写 key、资源 hash、时间值或业务样例。

<a id="validation"></a>
## 结果措辞与证据边界

| 观察措辞 | 允许的最小结论 | 不允许的外推 |
|---|---|---|
| 旧 fallback 匹配旧 fixture | 该资源与该输入集合匹配 | 当前版本或服务端接受 |
| WASM 与 fallback 不匹配 | 记录边界差异，继续排查输入/版本/状态 | 直接证明算法不同 |
| 受限输入下边界对照一致 | 限定资源身份、输入集合与状态的局部一致 | 所有版本等价或 fallback 可无条件替代 |
| 当前业务读回成功 | 需要独立 runtime 请求与业务结果证据 | 从离线 fixture 推导成功 |

## 验证与限制

本 reference 的三个模块均为 `source-report`。来源没有公开定位、目标端点、client/version、资源文件、loader trace、runtime fixture 或当前请求；本轮也未执行 WASM、fallback、浏览器运行时、local parity、业务读回或服务端验收。因此它只适用于整理资源身份、活动分支和首处分叉的检索入口，不是 procedure、算法实现或通用风险控制规则。
