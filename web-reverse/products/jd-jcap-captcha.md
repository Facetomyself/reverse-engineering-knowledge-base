# 京东 JCAP 图形验证码

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 京东 PC 登录图形验证码 / JCAP 滑块链路：fp、refresh/check、交互证明 ct/tk/cs、服务端签发的 vt 与登录提交联动。

## 命中特征

- 请求链出现 `/cgi-bin/api/fp`、`/cgi-bin/api/refresh`、`/cgi-bin/api/check`
- 登录页或脚本出现 `requireCaptchaPc.js`、`jcap_*.js`、`window.jdCAP`、`jdCAP.captcha(info)`
- 登录链出现 graphic/sessionId/refresh；登录提交体出现 `graphicCaptchaSessionId`、`graphicCaptchaJwtToken`、`graphicCaptchaVerifyToken`
- JCAP 请求体出现 `si`、`ct`、`tk`、`cs`、`se`、`version`、`lang`、`client`；响应出现 `st`、`fp`、`tp`、`img`、`vt`
- 滑块题面响应 `tp=30`，`img` 中包含背景图和滑块小图
- 最终校验失败出现 `code=16807`、`s_code=16130`、`code=16808`、`msg=验证失败/验证未通过`
- 后续登录提交同时出现 `h5st`、`_stk`、`aksParamsU`、`aksParamsB`

同目标命中 h5st 链时同时按京东 h5st 产品处理；本文负责 JCAP 滑块与 vt，h5st 文档负责业务签名与风控判断。

## 核心边界

目标不是直接登录成功，而是拿到当前会话可用的图形验证码通过 token：`graphicCaptchaVerifyToken = vt`。`vt` 来自 JCAP `/api/check` 校验成功后的服务端响应，不是登录接口返回值，也不是 h5st/密码加密产物。它绑定同轮 sessionId/jwtToken/Cookie/st/fp 状态，单次消费或短时效，浏览器现场先消费后本地重放常失败，拿到后应立即注入登录提交。

## 常见链路

```text
登录页 → 读 hidden fields、cookie、eid/fp/uuid、public key
→ GET sessionId/refresh → sessionId/jwtToken/appId/status
→ 加载 requireCaptchaPc → jdCAP.captcha(info) 初始化 → factory(option) 创建实例
→ POST /api/fp → fp/st
→ 题面阶段 /api/check 或 /api/refresh → tp=30/img
→ 生成滑块答案 A、touchList、records/fpt
→ POST /api/check 提交答案证明 → code=0 且带 vt
→ 将 vt 写入 graphicCaptchaVerifyToken → 构造登录 body
→ ParamsSign 生成 h5st/_stk → 加密生成 aksParamsU/aksParamsB → POST 登录接口
```

`/api/check` 双阶段：题面阶段（返回 tp/img/st，无 vt）与答题阶段（返回 vt）。题面由 /refresh 还是 /check 返回按当前请求包确认，不硬套端点顺序；`code=0` 不等于验证码最终通过。

## 观察优先级

1. 字段职责：`si`=sessionId；`ct`=设备/光标证明；`tk`=答案证明（入参形态常为 sessionId+st+编码答案+轨迹序列）；`cs`=采集证明（sessionId+records/fpt）；`se`=刷新证明
2. `st` 是后续生成 tk 或请求下一阶段的重要状态，不跨会话复用
3. A/touchList 与滑块 offset、时间节奏同轮一致；点数量、耗时、编码后长度影响 tk/ct/cs 长度级别
4. 失败 16807 类优先排查 offset、轨迹、证明输入、st 同轮性、sessionId/jwtToken/Cookie fresh 度，不先怀疑登录加密
5. 滑块 offset 只是答案一部分，还要转换为脚本需要的交互结构与证明字段

## 常见坑

- 把 /api/fp 的 fp/st 当最终验证码 token；把题面阶段 code=0 当通过
- 固定旧 vt、st、tk/ct/cs 长期重放；浏览器现场先消费的 vt 再拿本地用
- 只提交滑块 x 坐标，不生成脚本需要的 A/touchList/tk/cs
- 证明长度级别与浏览器样本不一致仍按签名错误排查
- JCAP 用一个会话、登录提交用另一个 cookie jar
- 登录 plain body 有 vt 但加密后的 aksParamsB 实际没包含它；忘记同时生成 h5st/_stk，把验证码失败与签名失败混为一谈

## 验证口径

按顺序验证：session refresh（拿到 sessionId/jwtToken）→ /api/fp（code=0、st/fp）→ 题面阶段（tp/img）→ 答案 check（code=0 且 vt 非空）→ 同会话立即注入登录。登录接口越过"图形验证码参数校验失败"、返回账号密码错误、newSafeVerify 或安全验证时，说明 JCAP 链已进入业务层；后续问题属于账号态或业务安全验证。
