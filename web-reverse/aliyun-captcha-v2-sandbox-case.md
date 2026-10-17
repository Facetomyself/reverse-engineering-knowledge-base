---
schema_version: 2
id: web-reverse-aliyun-captcha-v2-sandbox-case
document_type: case
original_date: unknown
archived_date: "2026-10-13"
scope:
  targets: [aliyun-captcha]
  client: web
  version: "V2"
  observed_at: unknown
sources:
  - id: s1
    ref: ./aliyun-captcha-v2-sandbox-source-archive.md#source-body
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅记录来源报告对单站阶段交接的描述；未验证当前服务或其他集成的完整请求顺序。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 仅整理来源对请求真实性、设备 / 行为分流和返回码的解释；本轮未运行 SDK 或复核服务端结果。
relations:
  - type: derived_from
    target: ./aliyun-captcha-v2-sandbox-source-archive.md#source-body
  - type: supplements
    target: ./aliyun-captcha-v2-dynamic-keys-reference.md#request-chain
tags: [aliyun-captcha, V2, sandbox, environment-parity, request-chain, validation, source-report]
---

# AliyunCaptcha V2 单站补环境案例（来源报告）

## 问题与范围

来源描述一个站点在请求过程中由 `acw_sc_v2` 阶段转入 AliyunCaptcha V2 滑块，并报告以 Node 沙箱承载 AliyunCaptcha SDK、FeiLin 与 `sg` 的单次分析。目标 URL 在来源中以 Base64 表示，公共归档中未解码；本文范围限定为该来源所述的 V2 流程，不代表所有 AliyunCaptcha 集成。

原文中的会话样值、设备字段、密钥及行为数据不进入本 case。清洗后的可见来源文字与缺口见 [AliyunCaptcha V2 来源归档](./aliyun-captcha-v2-sandbox-source-archive.md#source-body)。

<a id="request-chain"></a>
## 过程与关键证据

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源称滑块入口表现为业务 POST 返回 `200` 状态和 HTML 质询页；其中 `requestInfo` 承载原请求体的编码形式及当轮会话材料。 | s1，惩罚页部分 | source-report | 来源描述的单站流程 | 未保留请求体、token、trace ID、站点标识或 HAR。 |
| C2 | 来源把 AliyunCaptcha SDK、FeiLin 与 `sg` 分为初始化、设备数据和行为采集等职责，并描述 `InitCaptchaV2`、日志提交与 `VerifyCaptchaV2` 的阶段交接。 | s1，请求链部分 | source-report | 来源所述 AliyunCaptcha V2 滑块 | 不等于当前服务的完整协议规范，也未独立验证每个 Action。 |
| C3 | 来源报告了 Node 沙箱中的动态脚本加载、跨 realm 参数、FeiLin 导出与拖动事件等排查点。 | s1，沙箱及补环境部分 | source-report | 来源所述单次分析 | 未提供完整沙箱项目、SDK bundle、HAR 或版本 hash。 |

<a id="validation"></a>
## 结论与反例

来源提出以请求日志和 Verify 响应判断请求是否实际发出；仅见 SDK success 回调不足以证明初始化请求成功。来源还把环境一致性和拖动行为质量视为不同判分面，并按报告中的返回码区分行为未通过、格式未通过与通过。

来源报告称最终曾得到通过码并完成业务重放；本轮没有目标地址、请求材料或本地复现，因此这些结果保持 `source-report`，不是 runtime observation、local parity 或 server acceptance。返回码语义也只按该来源描述，不外推到其他版本。

## 未决项与复用启示

- 导出中的原图是 1×1 占位图，没有实际截图附件；原始目标地址、session 材料、设备样值、密钥和行为数据不进入公共文章。
- 没有当前 SDK bundle、HAR、轨迹或真实浏览器对照数据；本轮未请求目标，也未运行来源中的 Node 环境。
- 上下篇公开来源中，动态 key 与参数边界见 [AliyunCaptcha V2 动态 key 参考](./aliyun-captcha-v2-dynamic-keys-reference.md)；本 case 只补充单站沙箱诊断与证据分层。
