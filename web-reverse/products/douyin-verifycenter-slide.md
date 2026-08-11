# 抖音 VerifyCenter 滑块验证码

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 抖音 / 字节 VerifyCenter 滑块验证码链路：captcha/v2 初始化、captcha/get 题面、captchaBody 加密提交与登录联动。

## 命中特征

- 请求链出现 verifycenter 的 `/verifycenter/captcha/v2`、`/captcha/get`、`/captcha/verify`
- 初始化 URL 或题面参数出现 `aid`、`repoId`、`subtype=slide`、`fp=verify_*`、`h5_check_version`、`vc_version`
- 页面或资源链出现 `rmc-captcha`、captcha.js、index.wasm、bdms.js、verifycenter-collect、webmssdk、SecureSDK、web_protect
- 日志出现 `turing_verify_sdk`、`h5_init`、`h5_acquire_data`、`h5_action`、`h5_wasm_call`、`h5_jm`、`h5_result`
- 最终提交字段为 `captchaBody`，运行链出现 `captcha.wasm.encrypt`、`TextDecoder.decode(Uint8Array ...)`、`encrypt_version=7`
- 登录触发验证码时业务响应常见 `error_code=1105`，验证码通过后再次登录进入业务层

同链出现 `a_bogus`、`msToken`、`verifyFp`、`fp`、bdms/webmssdk/SecureSDK 签名追加时，同时按 a_bogus 产品处理。

## 常见链路

```text
登录接口返回需滑块验证（如 error_code=1105）
→ GET /verifycenter/captcha/v2 初始化 SDK 和题面上下文
→ GET /captcha/get 获取本轮 challenge、mode=slide、图片、缺口和提示字段
→ 生成滑动事件、行为 proof 和环境聚合
→ captcha.verify({modified_img_width}) → wasm.encrypt → TextDecoder.decode → h5_jm
→ JSON.stringify({captchaBody}) → POST /captcha/verify 提交
→ 响应 code=200 且消息为验证通过
→ 再次登录进入业务层；验证码通过后的业务失败不等于滑块失败
```

## 观察优先级

1. 锁定成功 round 作为基准，失败提交只能用于排除错误轨迹或环境，不得作为 proof 真值
2. 先对齐请求边界、题面字段、challenge、滑动距离、body 结构与响应判定，再补 DOM/BOM 公开 API（matchMedia、Storage、HTMLCollection、document.all、External、TouchEvent、Canvas、WebGL、Font、Audio、screen、MediaCapabilities）
3. Canvas/WebGL/Font hash 不盲目硬改：trace 只给 toDataURL 摘要时不能反推完整 PNG；WebGL 参数表对齐不代表 hash 完整对齐；字体表对齐后不继续盲补字体
4. 轨迹要保证 proof 进入加密：稳定形态是长步数、总时长合理的滑动轨迹，本地 captchaBody 与完整 body 长度对齐后再继续在线验证
5. 展示层差异字段（vendor、scale、fps 等）必须先找公开 DOM/BOM 读取证据和因果作用，不能因成功证据中不同就直接覆盖
6. `TouchEvent is not defined`、`Operation is not supported` 等异常可能是成功证据也存在的噪声，与成功进程异常分区比对后再判断

## 常见坑

- 把失败 verify round 当成功 proof
- 把 verify 之后才发生的公共请求当 verify 前置边界
- 从截断 dataURL、hash 或展示字段直接硬编码环境输出
- 沿 VMP/opcode/handler/解释器内部路线推进
- 搜索到 V8 内部全局代理命名不等于 JS Proxy 包装，不作为代理残留证据

## 验证口径

- 在线 `/captcha/verify` 返回 code=200，且后续登录响应与成功证据同口径进入业务层（登录错误码变化表示验证码已通过）
- 连续稳定性建议至少 5 次，记录 verify_code、captchaBody_len 与 trace 一致性、delta、body_len、登录错误码、异步错误数与耗时
- 本地语法检查与语法编译通过；最终以真实 verify 响应和后续登录响应同时验收，不只看本地 body 长度
