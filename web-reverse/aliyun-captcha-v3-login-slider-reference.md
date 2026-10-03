---
schema_version: 2
id: web-reverse-aliyun-captcha-v3-login-slider-reference
document_type: reference
original_date: '2026-09-23'
archived_date: '2026-10-03'
scope:
  targets: [aliyun-captcha]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./aliyun-captcha-v3-login-slider.md#reference-extraction-205
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理来源登录滑块窗口的 Init/Log2/Verify 三包；与产品卡 CHECK_BOX Log1 先行链可能不是同一分支，未验证当前 Action 顺序。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录字段角色与变换类别；不收录 AES key/iv、Signature 前缀字段、压缩算法、轨迹、Cookie 或 AccessKeyId。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 作者“请求成功”是来源自述；45 张图未审；本轮未跑浏览器或目标。
relations:
  - type: derived_from
    target: ./aliyun-captcha-v3-login-slider.md#reference-extraction-205
  - type: supplements
    target: ./products/aliyun-captcha-v3.md#常见链路
tags: [aliyun-captcha, V3, InitCaptchaV3, Log2, CaptchaVerifyParam, HmacSHA1, FeiLin, source-report]
---

# 阿里云验证码 V3 登录滑块参数链参考

这张窄卡只整理来源 archive 对 **V3 登录滑块** 的 InitCaptchaV3 / Log2 / VerifyCaptchaV3 字段角色。[V3 产品索引](./products/aliyun-captcha-v3.md) 覆盖 CHECK_BOX 命中与 Log1→FeiLin→Init→dynamicJS/cx 状态机；[V2 请求链卡](./aliyun-captcha-v2-request-chain-reference.md) 是另一版本。作者未公开密钥与扣码，本文不是可运行 signer。

<a id="request-chain"></a>
## 来源窗口的三包

来源称一轮可见五个 Action：InitCaptchaV3、UploadLog、Log2、Log3、VerifyCaptchaV3；作者实测 UploadLog 与 Log3 可不发，Verify 仍能发出。这与产品卡的 Log1 先行、CHECK_BOX 行为链不是同一份状态机，检索时按分支并列，不要互相覆盖。

```text
InitCaptchaV3（DeviceData / SignatureNonce / Signature）
  -> 响应 AES 解密得到动态 FeiLin 脚本地址
  -> Log2（data 为 # 拼接后 AES，指纹段来自 initFeiLin）
  -> VerifyCaptchaV3（CaptchaVerifyParam = deviceToken + data；CertifyId 来自首包）
```

<a id="parameters"></a>
## 字段角色

| 字段 | 来源描述 | 类别 | 边界 |
|---|---|---|---|
| `DeviceData` | 固定 key/iv 的 AES | encryption | key/iv 未公开。 |
| `SignatureNonce` | 类 UUID 随机 | token | 每轮新值。 |
| `Signature` | 请求体 `&` 拼接，前面另拼两个字段，再 HmacSHA1 | signature | 前缀字段未公开；不是 V2 URL-encode HMAC 卡。 |
| Init 响应密文 | 同样 AES，解出字典，含动态 FeiLin URL | encryption / 配置 | URL 当轮派生，不跨轮复用。 |
| Log2 `data` | `#` 拼接多段后 AES；其中指纹段由 `window.FEILIN.initFeiLin(Br, r)` 动态脚本生成 | fingerprint + encryption | 作者用补环境出值，代码未公开。 |
| `CertifyId` | 首包返回 | token | 绑定当轮。 |
| `CaptchaVerifyParam.deviceToken` | 补环境材料 AES，内含一步 MD5 | encryption | 明文不收录。 |
| `CaptchaVerifyParam.data` | 轨迹压缩转 Base64，再加密，再 `btoa` | encoding / encryption | 压缩与加密细节未公开。 |

截图中的 `AccessKeyId` 是验证码前端公开下发的客户端标识，本文不回写样值。

<a id="validation"></a>
## 验收口径与限制

| 观察 | 来源允许的最小结论 | 不允许的外推 |
|---|---|---|
| 三包能发出 Verify | 作者窗口里 UploadLog/Log3 可省 | 当前站点可跳过诊断包 |
| 作者“请求成功” | 来源自述 | 本轮 server-accepted 或密钥已恢复 |
| FeiLin 动态脚本 | 地址来自首包解密 | 与 51job 反 Hook 清单等同 |
| 45 张本地图 | 归档保真 | 未审图不是证据 |

## 验证与限制

- `client` / `version` / `observed_at` 均为 unknown。密钥、iv、Signature 前缀、轨迹压缩和补环境代码未公开，不得补造。
- 未运行浏览器、hook 或目标服务。FeiLin 检测面见既有 anti-detection 文档，不在本卡展开。
- 图片未审，不作为证据。
