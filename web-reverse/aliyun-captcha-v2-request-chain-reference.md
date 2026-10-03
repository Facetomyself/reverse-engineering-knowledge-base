---
schema_version: 2
id: web-reverse-aliyun-captcha-v2-request-chain-reference
document_type: reference
scope:
  targets: [aliyun-captcha]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./aliyun-captcha-v2-slider-part1-request-chain.md#reference-extraction-109
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅整理 Signature 的参数来源/编码形状与 DeviceConfig 到 Data key 的来源报告边界；不包含 key、iv、nonce、签名、Cookie、设备/IP 或 payload 样值。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅保留上篇的首包、Log2/Log3 与末段字段交接及上下篇职责边界；现有 V2 产品 reference 才是状态机检索入口，本卡不证明当前请求顺序或服务端接受。
relations:
  - type: derived_from
    target: ./aliyun-captcha-v2-slider-part1-request-chain.md#reference-extraction-109
  - type: supplements
    target: ./products/aliyun-captcha-v2.md#常见链路
tags: [aliyun-captcha, V2, Signature, HMAC, DeviceConfig, Log2, Log3, source-report]
---

# 阿里云验证码 V2 请求链与参数来源参考

这是一张窄范围 `source-report` reference，补充 [V2 状态机 reference](./products/aliyun-captcha-v2.md#常见链路) 没有展开的上篇参数来源与调试边界。它不复制敏感值、不重建滑块流程，也不把来源文章的中间指标当作当前服务端验收。

<a id="parameters"></a>
## Signature 与 DeviceConfig 参数边界

来源报告把首个初始化请求的材料分成几类：部分字段来自触发验证响应中的 `requestInfo`，`SignatureNonce` 由随机方法生成，`Signature` 则由已知参数对象与固定字符串进入 URL 编码、HMAC、Base64 的连续变换。文章没有给出可公开复核的哈希选择、密钥值、完整 canonical 输入或服务端验收样本，因此这里仅登记形状，不提供 signer。

首包响应中的 `DeviceConfig` 被来源报告描述为先用固定 key/iv 解密，再按 `#` 取首段并 Base64 解码，作为 Log2/Log3 `Data` 多重 AES 链的一个 key 来源。`Data` 的环境对象、轮换 key 与固定 IV 只按来源叙述保留；`AliyunCaptcha.js` 的 `decrypt:` 入口和 WordArray 转换是作者建议的观察点，不是本轮实际 Hook 结果。

字段角色必须与值分开登记：本卡不保存 `SignatureNonce`、Signature、DeviceConfig、Data、key/iv、Cookie、设备/IP、目标地址或任何请求样值。下篇的 FeiLin/sg 动态 key、`deviceToken`、轨迹 `data` 与 `CaptchaVerifyParam` 不在本卡重复展开。

<a id="request-chain"></a>
## 上篇请求角色与上下篇边界

来源报告描述的历史角色关系如下：

```text
首个 captcha-pro-open 请求
  → 响应 requestInfo / DeviceConfig
  → device.captcha-open 的 Log2
  → device.captcha-open 的 Log3
  → 再次提交 CaptchaVerifyParam
  → 业务请求消费 CertifyId / requestInfo.token 角色
```

这里的箭头表示来源文章的角色交接，不是本轮捕获的时序证明。作者把首篇的重点放在首包 Signature 和 Log2/Log3 `Data`，把动态 key、末段 `CaptchaVerifyParam` 和轨迹材料留给下篇；现有产品 reference 负责把同轮资源、proof 四字段和最终业务 readback 分开验收。

来源还把 `VerifyCode=T001` 描述为中间通过信号，并把 `CertifyId` / `requestInfo.token` 的角色带入后续业务请求。它们在本卡只作为历史字段角色，不能替代 fresh round、同轮 proof、业务成功响应或 `server-accepted` 证据。

## 证据与限制

- 来源正文 33 张图已随 archive 保留，但本轮未做像素审查；没有从图片提取结论。
- 本卡与来源均保持 `source-report`，client、版本、观测窗口和 source completeness 未补猜。
- 本轮未访问目标站点、运行浏览器/JS、重放请求、做 local parity 或检查当前服务端；不构成 procedure、risk-control 规则或绕过方案。
