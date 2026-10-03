---
schema_version: 2
id: web-reverse-shuffled-jigsaw-slider-protocol-reference
document_type: reference
original_date: '2026-09-05'
archived_date: '2026-10-03'
scope:
  targets: [unknown]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./shuffled-jigsaw-slider-protocol.md#reference-extraction-199
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理来源所述 4 段 JSONP GET 加 1 个业务 POST 的交接；厂商、域名和当前接口未核实，2 张来源图未审。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记 loc 重排、length 偏移、AES 角色和 op 形状；不收录 key/iv、轨迹坐标、fp 或可运行加密器。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 错误码分流与作者自述 code:0 均为 source-report；本轮未请求验证码或业务接口，不能当 server-accepted。
relations:
  - type: derived_from
    target: ./shuffled-jigsaw-slider-protocol.md#reference-extraction-199
tags: [jigsaw, loc-shuffle, JSONP, capTicket, AES-128-CBC, length-offset, trajectory-shape, error-code, source-report]
---

# 拼图打乱重排滑块：loc 重排与错误码分流参考

用于检索“素材图不是显示坐标系”的拼图滑块。目标站点与验证码厂商在来源中未点名。本文只转述链路、参数角色和失败分流，不提供完整协议实现、轨迹生成器或图片结论。

<a id="request-chain"></a>
## 请求链

来源约束是全程 HTTP、不用浏览器拖动。报告的五跳为：

1. init JSONP GET：取 `capTicket` 写入隐藏域。
2. key JSONP GET：用票据换 `capKey`。
3. info JSONP GET：按 `capKey` 取 `loc`（40 个 tile 编号）与素材图。
4. validate JSONP GET：提交加密后的 `op` / `validData` 等，成功时返回 `code:0` 与 `result`。
5. 业务 POST：把 `result` 作为 `rand` 与 `capTicket` 一起提交。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 报告称最终业务表单关键字段是 capTicket 与 rand，rand 来自 validate 的 result。 | s1，来源 PART 02 | source-report | 来源所述查询页 | 域名已打码；未复核当前接口。 |
| C2 | 报告称服务端坐标基准是按 loc 打乱后的显示画布，不是素材原图。 | s1，来源「缺口检测全面失败」 | source-report | 13px 竖条 + loc 重排这一题型 | 2 张图未审，不作为视觉证据。 |

<a id="parameters"></a>
## 参数角色

分开 encoding、signature 与轨迹形状，不统称“加密参数”。

| 参数组 | 来源描述的角色 | 类别 | 边界 |
|---|---|---|---|
| loc | 40 个 tile 编号，把背景 13px 竖条重排成显示画布 | encoding / 显示层 | 未给出编号算法；检测必须在重排之后。 |
| 素材图切分 | 来源称 321×120：左段背景、右段拼图块 | 图像几何 | 尺寸来自作者样本，不能外推其他题。 |
| length | 来源称显示坐标缺口 + 9（前端 D=e+9，轨迹终点再 +1 的叙述并存） | parameters | 1px 偏差可被拒；+9 与 +1 的精确组合未独立闭合。 |
| capTicket → AES | AES-128-CBC / PKCS7，key=iv=16 字节，由票据固定位置抽取 | encryption（仅算法名与角色） | 不公开抽取偏移、key/iv 或密文。 |
| op | 页面绝对坐标、无 mouseup、约 110ms 节流、取整 | fingerprint / 行为编码 | 不复制坐标样值；合成 isTrusted=false 被来源排除。 |
| validData | 来源称加密 `{length, time}`，time 含看图反应 | encoding | schema 未完整公开。 |
| fp | 来源称按 murmurhash3 同算法复现 | fingerprint | 输入与盐未知。 |

<a id="validation"></a>
## 错误码分流

| 观察 | 来源允许的最小结论 | 不允许的外推 |
|---|---|---|
| 返回 -1 | 换缺口位置后再检 | 证明检测算法 |
| 返回 105 | 同位置换一条轨迹；作者称 105→105→0 常见 | 轨迹模型已通过当前风控 |
| 返回 111 / 112 | 换题 | 频控/过期规则已量化 |
| 作者称 code:0 且业务放行 | 该次来源实验的中间/业务口径 | 本轮 server-accepted |
| 模板 top1 分差启发式 | 来源处理凹槽/模板二义性的经验 | 图像阈值已验证 |

适配层（相对位移 → 绝对坐标、抽稀、截断回退、拉伸时长）和 `slider-track-gen` 在来源中未公开，不能当成可运行 procedure。

## 验证与限制

- 来源有公开微信文章 locator，但目标站、厂商、版本和观测窗口仍 unknown。
- 同名目录 2 张图未做像素审查，不得作为缺口或轨迹证据。
- 本轮未执行 JSONP、AES、图像检测或业务提交；不收录轨迹坐标、票据、result 或密钥。
