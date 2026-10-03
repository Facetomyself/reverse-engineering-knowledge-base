---
schema_version: 2
id: web-reverse-wasm-decrypt-loader-reference
document_type: reference
scope:
  targets: [unknown]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./wasm-decrypt-ai-one-prompt-recovery.md#reference-extraction-110
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告中的 JS wrapper、decrypt export 与 WASM instance 边界；缺少实际模块、imports/exports、pointer/length ABI、内存所有权和 endpoint schema。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅记录响应字段到 wrapper、loader 和 export 的来源链；没有请求 URL、输入输出 fixture、业务响应或可运行解密实现。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 作者的测试成功和 SM2/SM4 叙述依赖未审图片与缺失代码；本轮没有 runtime、byte parity、业务读回或 server acceptance。
relations:
  - type: derived_from
    target: ./wasm-decrypt-ai-one-prompt-recovery.md#reference-extraction-110
  - type: supplements
    target: ./wasm-js-fallback-version-reference.md#interfaces
tags: [WASM, decrypt, loader, WebAssembly.Instance, AI-assisted, source-report]
---

# WASM decrypt loader 与 AI 分析边界参考

这是一张窄范围 `source-report` reference。它补充现有 WASM/JS fallback reference 的一个来源案例：页面字段进入 JS wrapper，wrapper 调用 WASM decrypt export，加载器可从异步 fetch/instantiate 改为本地同步实例化；同时记录 AI 辅助恢复叙述的证据边界。它不发布算法实现、私钥、密文、明文或可运行 decryptor。

<a id="interfaces"></a>
## JS wrapper 与 WASM export

来源报告描述了一个名为 `secure_decrypt_data` 的 WASM 导出以及其上层 wrapper。页面字段在 JS 侧先进入 wrapper，wrapper 再把两个参数交给导出对象；来源示例把实例化得到的 exports 组织成一个本地对象。这里能复用的是“wrapper 与模块实例是两个边界”，而不是某个导出名就能代表稳定 ABI。

仍需独立取得并记录的接口材料包括：模块 bytes/hash、imports/exports、字符串或 bytes 编码、pointer/length 约定、memory-view 生命周期、返回缓冲区所有权、释放行为和异常路径。来源没有给出这些材料，本卡不补写。

<a id="request-chain"></a>
## Loader 与字段调用链

来源文章给出的最小链路是：

```text
响应中的待解密字段
  → JS decrypt wrapper
  → 异步 fetch + instantiate，或本地 bytes + Module/Instance
  → WASM decrypt export
  → wrapper 返回值
```

本地同步分支只是作者展示的分析替代路径，不能直接当作生产部署或跨版本兼容方案。AI 分析叙述还包括读取 JS bridge、检查导出、使用 wasm2wat/wasm-decompile、尝试纯 JS 恢复和测试；这些是来源报告的工作记录，不满足 procedure 所需的固定前提、产物、失败出口与验收门。

来源摘要提到 URL/Base64 和 SM2/SM4 的两段变换，但正文可审计材料没有包含完整实现、输入输出 fixture 或算法报告正文；因此该标签只作为来源叙述的 provenance，不作为本卡的算法结论。

<a id="validation"></a>
## 验证边界

| 材料 | 可以保留的最小结论 | 不允许的外推 |
|---|---|---|
| JS wrapper / export 名称 | 来源报告存在一个 JS 到 WASM 的调用边界 | 稳定 ABI、可移植实现或当前页面接口 |
| Loader 改写示例 | 来源报告展示了异步与本地同步的两种初始化叙述 | 当前资源匹配、生产可用或跨版本等价 |
| 截图中的算法/测试 | 作者声称有算法分析和测试结果 | 独立 SM2/SM4 事实、local parity、业务读回或 server acceptance |

本轮未审查 30 张来源图片像素，也未取得 JS/WASM artifact、AI workspace、恢复代码、密文/明文样例、私钥、目标地址或测试向量。来源和本卡均保持 `source-report`；没有执行浏览器、Node、WASM、decompiler、runtime request、local parity 或服务端验收。因此本卡不是 procedure、risk-control reference 或纯算法实现。
