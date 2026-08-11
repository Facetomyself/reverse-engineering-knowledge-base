# 阿里 Baxia / AWSC bx-ua 与 fire_ua

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 阿里系登录态业务中的安全 Header + body metas 链路：bx-ua / bx-umidtoken 与 140 字段 AsuraId / fire_ua / fire_umid。

## 命中特征

- 业务请求 Header 出现 `bx-ua`（值常以 `231!` 或 `234!` 前缀开头）、`bx-umidtoken`
- 业务请求 body/metas 出现 `AsuraId`、`fire_ua`、`fire_umid`（常以 `140#` 前缀开头）
- 页面加载 alsc-h5-sec 的 `securityHeader.min.js`、baxiaCommon.js、fireyejs（1.231.x / 1.234.x）、WebUMID um.js、uab collina.js、et_f.js
- 运行链出现 `securityHeader.initSecurity`、`securityHeader.getSecurityHeaders`、`AWSC.configFY`、`fyOBJ.getUA`、`getUabModule`
- storage 出现 `lswucn`、`_um_cn_umsvtn`、`_um_cn__umdata`、`_uab_collina`、`tfstk__` 等状态键
- 请求链出现 UMID / nt2 / fourier / mmstat 类异步上报端点
- 最终业务接口返回 `FAIL_SYS_USER_VALIDATE`、x5 captcha、showCaptcha 或同类用户验证拦截

`231!` 与 `234!` 是同一 bx-ua 家族的版本/变体线索，不要因前缀是 `234!` 就跳过本产品。

## 常见链路

```text
目标页入口
→ 加载 securityHeader / AWSC / fireyejs / WebUMID / uab 相关脚本
→ securityHeader.initSecurity({ dependHeaders: [...] })
→ 准备 localStorage / cookie / performance / XHR / message / 事件环境
→ 回放依赖的 window message 与登录前真实行为事件
→ getSecurityHeaders 取 headers
→ 异步上报推进（UMID / 行为日志 / performance 资源）
→ 再次 getSecurityHeaders，将消费边界那次结果写入最终业务请求
```

核心边界是 Header + body metas 组合，职责拆分：

```text
Header:      bx-ua、bx-umidtoken
Body metas:  AsuraId、fire_ua、fire_umid
231/234:     securityHeader / Baxia / fireyejs 行为链产出
140:         AWSC / WebUMID / uab-collina 产出
```

可能出现两次 `getSecurityHeaders`，只有请求边界实际消费的那次可用于业务请求，不能默认取第一次或最长值。`bx-ua` 只生成一小段时，通常说明行为链、message、XHR 上报或 storage 有缺口。

## 观察优先级

1. 定位 `initSecurity` 入参与 `dependHeaders` 集合，确认是否还有站点额外 Header
2. 定位每次 `getSecurityHeaders` 的调用序号、调用栈与消费边界
3. 确认 storage 状态（lswucn、UMID token 等）的读写时机，`bx-umidtoken` 不是普通静态 token
4. 确认 message 事件、UMID/上报请求的响应体与响应头来自同一轮证据
5. 行为事件序列（事件类型、target 的 DOM 类型、字段）按事件证据提取，不手写固定动作
6. 检查前缀与长度量级：140/231/234 类字段常见千级长度，UMID/token 常见几十字节级
7. 最终业务响应是否离开用户验证 / x5 / 验证码 / 风险拦截

## 常见坑

- 把 `bx-ua` 当普通签名参数，只调 `getSecurityHeaders`，不回放事件和异步上报
- 只补 231 不补 140（或反之），最终业务接口仍因材料不完整被拦截
- 固定旧 `lswucn`、`_um_cn_umsvtn`、`bx-umidtoken` 或旧 Cookie
- 忽略 message 事件导致初始化状态不完整；忽略 UMID/上报请求和响应
- 事件 target 用普通对象，缺少真实 `HTMLInputElement`、`HTMLButtonElement`、`HTMLFormElement` 外观
- 本地断言前缀通过就宣布成功，没有跑最终业务接口
- 遇到 x5 / captcha 误判为账号问题；这类响应通常表示安全链仍未对齐

## 验证口径

- `bx-ua` 前缀正确且长度级别贴近当前浏览器证据；`bx-umidtoken` / `fire_umid` 同轮生成
- `AsuraId / fire_ua` 与 140 链同轮产出，与最终业务请求同一 Cookie/storage/UA 上下文
- 最终业务接口返回正常业务 JSON 或正常业务错误（如"账号不存在"），不再是用户验证、x5、验证码或风险拦截
- 传输层指纹与浏览器相容；同参数用标准 HTTP 客户端仍被拦时优先查 TLS/HTTP 指纹，不把 JS 参数正确误判成全链路通过
