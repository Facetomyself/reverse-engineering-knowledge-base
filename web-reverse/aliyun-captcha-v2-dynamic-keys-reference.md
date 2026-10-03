---
schema_version: 2
id: web-reverse-aliyun-captcha-v2-dynamic-keys-reference
document_type: reference
original_date: '2025-12-09'
archived_date: '2026-10-02'
scope:
  targets: [aliyun-captcha]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./aliyun-captcha-v2-slider-part2-dynamic-keys.md#reference-extraction-120
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅整理 FeiLin/sg 动态 key、deviceToken 与轨迹 data 的角色和高层变换边界；不包含 key、iv、固定密钥、样值、压缩算法、VMP 语义或可运行 signer。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅记录动态材料进入 Log2 与末段 CaptchaVerifyParam 的来源报告关系；不证明当前 V2 请求顺序、同轮绑定、验证码通过或服务端接受。
relations:
  - type: derived_from
    target: ./aliyun-captcha-v2-slider-part2-dynamic-keys.md#reference-extraction-120
  - type: supplements
    target: ./aliyun-captcha-v2-request-chain-reference.md#request-chain
tags: [aliyun-captcha, V2, FeiLin, sg, dynamic-key, deviceToken, trajectory, source-report]
---

# 阿里云验证码 V2 动态 key 与末段参数参考

这是一张窄范围 `source-report` reference，补充 [V2 请求链参考](./aliyun-captcha-v2-request-chain-reference.md) 没有展开的下篇动态材料。它只登记来源文章描述的字段角色与变换阶段，不复制样值、不从图片提取结论，也不把来源叙述升级为当前运行时或服务端事实。

<a id="parameters"></a>
## 动态 key 与参数边界

来源报告把 FeiLin 动态值放在 Log2 的环境数据一侧：先取得解密后的 `DeviceConfig` 中的 `SessionId`，再与每个资源版本提供的两个动态值进行两次异或并做 Base64。两个值被描述为从资源内的大数组解出；定位线索是版本相关的代码位置或 `ENDPOINTS` 搜索锚点。文章同时提到硬编码可能出现较低成功率，但没有说明服务端实际检查项、版本范围或稳定阈值，因此这里只保留敏感性与版本分叉的来源观察。

sg 动态值被来源报告放在末段 `CaptchaVerifyParam`。文章以 `void 0` 作为某些较新版本的定位锚点，并明确不同大版本需要不同匹配方式。这里记录的是 key 的来源定位和版本分叉，不是 key 表、自动提取器或通用匹配规则。

`deviceToken` 的高层形状是：环境对象组合后经过 AES（依赖 FeiLin key），再经历数组/字符串组合、MD5、中间结果再次组合和 Base64。来源没有给出足以独立复核的 AES 参数、序列化、完整字段集合或输出向量，所以不提供实现。

`data` 的高层形状是：`x/y/time` 轨迹经 sg 控制流转换和 `TextEncoder`，加入两个与轨迹、认证标识和 sg key 相关的 VMP 派生值，转为数组后压缩，再经过固定密钥参与的 VMP 阶段。压缩算法、固定密钥、VMP 语义、字段顺序和编码均未公开，不能据此生成或解码参数。

<a id="request-chain"></a>
## 请求角色与观察边界

按来源文章的上下篇关系，首包获得的环境材料进入前段 Log2/Log3；本篇把 FeiLin 动态值归到 Log2 环境数据，把 sg 动态值、`deviceToken` 和轨迹 `data` 归到末段 `CaptchaVerifyParam`。这只是来源报告的角色交接，完整状态机、同轮资源绑定和业务完成门仍由 [V2 产品 reference](./products/aliyun-captcha-v2.md) 负责。

混淆脚本的定位建议包括在 `JSON.stringify`、`TextEncoder`、`btoa` / `atob` 等宿主原语处观察调用栈；这是一条来源级观察线索，不是已闭合的 Hook procedure，缺少前提、输出合同、清理动作、失败出口和验收 fixture。

## 验证与限制

- 本 reference 与来源 archive 均保持 `source-report`；client、版本、观测窗口和完整性未知，不宣称当前资源或算法兼容。
- 来源 archive 保留 16 张图片，但本轮未做像素审查，也未从图片提取或再发布任何信息；图片中的结果验证不能视为成功或 server acceptance。
- 本轮未运行浏览器/JavaScript、Hook、验证码请求、local parity、请求重放或业务读回；不构成 procedure、signer、decoder、risk-control 规则或绕过方案。
- 本卡不复制 key、iv、固定密钥、token、Cookie、设备/IP、轨迹、密文、压缩结果或请求样值。
