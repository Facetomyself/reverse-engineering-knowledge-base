---
schema_version: 2
id: web-reverse-jd-jcap-tp30-curve-slider-reference
document_type: reference
original_date: '2026-08-26'
archived_date: '2026-10-03'
scope:
  targets: [jd]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./jd-jcap-tp30-curve-slider.md#reference-extraction-205
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理 si→vt 状态链与刷新时机；未访问 JCAP，不能视为当前接口可用性。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 记录角色、依赖和编码层级；不收录 si/vt、轨迹坐标、Cookie、密钥或可运行算法。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 曲线反查与失败分类是来源方法，不是已验证 CV/runtime。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: code==0 且非空 vt 是来源成功口径；作者 20/20 未重跑。
relations:
  - type: derived_from
    target: ./jd-jcap-tp30-curve-slider.md#reference-extraction-205
  - type: supplements
    target: ./products/jd-jcap-slider.md#常见链路
  - type: supplements
    target: ./products/jd-jcap-captcha.md#常见链路
tags: [jd, JCAP, tp:30, n1, se, ii, tk, curve-mapping, source-report]
---

# 京东 JCAP tp:30 曲线映射与 si→vt 参考

这张窄卡只整理来源 archive 对 **业务侧 tp:30 拖箭头滑块** 的参数依赖：`n1` 曲线、透明边距、离散反函数、`ii` 回放和 `tk` 字节合同。[JCAP 图形验证码](./products/jd-jcap-captcha.md) 负责题型分流与 `vt`；[滑块专项](./products/jd-jcap-slider.md) 负责视觉答案与 drag proof。本文不覆盖 tp=26 / tp=22，也不手写混淆算法。

<a id="request-chain"></a>
## si → vt

```text
业务组件下发新鲜 si
  -> fp 初始化：fp 写回 devcInfo.capfp，给出初始 st
  -> 挑战：tp / st / b1 / b2 / n1（成组）
  -> render_target（内容边距 + 尺寸换算）
  -> endpoint = argmin |f(p) − render_target|
  -> 模板轨迹缩放并在同版本曲线实例上 down/move/up → ii
  -> sensorInfo / ct / payload / tk / cs
  -> check：code==0 且非空 vt
  -> 可恢复失败：用最新 st 生成 se，刷新下一挑战
```

同一 `si` 只初始化一次。图片刷新保持 `si`、更换 `st`。重新初始化才换 `si`。当前响应的 `st`、图片和曲线状态必须成组，不能混入上一挑战。

<a id="parameters"></a>
## 字段角色

| 参数 | 来源描述的角色 | 类别 | 边界 |
|---|---|---|---|
| `si` | 短时会话标识，不是答案 | token | 求解器不能凭空构造。 |
| `fp` / `capfp` | 初始化指纹；写回设备态 | fingerprint | 漏写回只表现为普通校验失败。 |
| `st` | 挑战/过渡游标 | token | 无图响应也可能更新；优先挑战 `st`。 |
| `se` | `f([si, st])`，顺序敏感 | signature | 先接受新 `st` 再判断有没有图。 |
| `n1` | 不提交，却参与曲线初始化 | encoding / 本地状态 | 不要手工解密；每张新图重解析。 |
| `b1` / `b2` | 背景与拼块 | 图像 | 拼块透明边距必须修正。 |
| `render_target` | `round((x_match − piece_left) / source_w * render_w)` | 坐标 | 是拼块目标，不是鼠标末点。 |
| `endpoint` | 离散反查鼠标末点 | 坐标 | 登录滑块的 CV≈末点捷径不适用。 |
| `ii` | 完整事件序列后的实例标识 | token | 不是 `list` 的静态散列。 |
| `ct` | `[si, sensorInfo]` | signature | 绑定当前设备态。 |
| `tk` | `[si, st, encodeURI(compact payload JSON), touchMessage JSON]` | signature | 空格 JSON、重复 URI、键序、旧 `st` 都会漂。 |
| `vt` | 成功 check 响应 | token | 单次消费；不是 h5st。 |

参数函数仍调用同版本运行时。定位标准是包装器返回值与请求字段逐字节一致，再做单变量差分。

<a id="decision-flow"></a>
## 曲线反查与失败分流

1. 模板匹配得到图层位置；用 alpha/灰度包围盒减去拼块内容左边距，再换算渲染宽。
2. 在当前 `tp/b1/b2/n1` 上建立 `f(p)`，对整数轨道枚举 `endpoint = argmin |f(p) − render_target|`。探测枚举后必须重新初始化曲线，避免污染正式回放。
3. 轨迹用已验证模板：x 同比缩放到 `endpoint`，y/时间受控扰动，末点 x 强制对齐；在本地曲线实例上回放事件（不是 OS 鼠标）。
4. 回放后再读 `mapped_endpoint`，残差超阈不提交。
5. 失败分类：`si` 过期则停；仅新 `st` 的过渡不占有效挑战次数；行为拒绝则刷新换图换模板。

<a id="validation"></a>
## 验收口径与限制

| 观察 | 来源允许的最小结论 | 不允许的外推 |
|---|---|---|
| `code==0` 且 `vt` 非空 | 验证码阶段完成 | 登录/业务已通过 |
| 残差约 1 像素（作者 translate3d 对照） | 坐标修正在其样本上成立 | 本轮 CV 已复现 |
| 作者 20 个新鲜 `si` 20/20、平均 2.75 次有效挑战 | 来源自测 | 当前服务端或本轮 runtime |
| 字段结构与登录滑块同构 | 引擎同源 | 可改 type 码套用登录脚本 |

## 验证与限制

- 作者已脱敏域名、路径、令牌和可重放字段；`client` / `version` / `observed_at` 未知。
- 4 张图未审，不作为证据。不收录 `si`/`vt`、轨迹点、Cookie 或密钥。
- 未运行 JCAP、OpenCV 或浏览器。h5st 与 tp=22 空间推理不在本卡。
