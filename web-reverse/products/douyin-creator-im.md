# 抖音创作 IM 私信链路

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 抖音 Creator Web 私信发送链路：Cookie 会话、identity token、ticket guard、action_report、IM HTTP 接口与可选 WS 观察组成的完整业务链路。

## 命中特征

- IM HTTP 接口：`/v1/message/send`、`/v2/message/get_by_user_init`、`/v2/conversation/create`、`/v3/conversation/mark_read`
- WS 通道 `/ws/v2`；identity 接口 `get_identity_security_token/`；行为上报 `/aweme/v1/im/consistency/action/report`
- Header 或 Cookie 出现 `bd-ticket-guard-client-data`、`bd-ticket-guard-ree-public-key`、`bd_ticket_guard_client_data`
- 运行链出现 `identity_security_token`、`identity_security_device_id`、`ActionConsistencyManager`、`ActionType`、`getUidFromSecUid`
- 业务字段出现 `conversation_id`、`conversation_short_id`、`ticket`

同链出现 `a_bogus`、`msToken`、`webmssdk`、`sdk-glue`、`bdms` 时，同时按 a_bogus 产品处理。

## 常见链路

```text
Cookie / 登录态
→ 获取或刷新 identity_security_token
→ action_report 行为一致性上报
→ 获取已有会话（get_by_user_init）或创建会话（conversation/create）
→ 可选 mark_read
→ /v1/message/send 发送文本消息
→ 可选 WS 观察回执或消息推送
```

WS 能连接成功不等于私信发送链路完整：关键业务路径是 HTTP IM 接口，WS 更多用于长连接、通知、回执和辅助观察。

## 观察优先级

1. 最小业务输入收敛为：Cookie、发送方数字 UID、目标数字 UID、发送文本
2. 目标 UID 是数字 UID；昵称或短号须先经搜索/主页链路拿 `sec_uid`，再经 uid 转换接口转数字 UID
3. 无历史会话时：用双方 UID 组装 1:1 conversation_id 候选 → conversation/create → 取 conversation_id / short_id / ticket → 刷新 identity token → action_report → send
4. ticket guard 材料（ticket、ts_sign、EC key、公钥、服务端证书）依赖同一登录/浏览器环境动态生成，按请求、路径、时间戳上下文产出，不得跨账号/跨环境混用
5. `identity_security_token` / `identity_security_device_id` 是发送前动态安全上下文字段，不作为稳定配置手填
6. action_report 缺失或不匹配时，最终 send 可能返回风控、审核、空服务端 ID 或看似发送但实际未到达
7. protobuf 字段编号只能作为当前版本经验，新目标从当前请求体、响应体和 JS encode/decode 逻辑确认

## 常见坑

- 把 WS 能连上误判为私信发送链路完成
- 给动态目标发送时仍使用旧 conversation_short_id、ticket 或 conversation_id
- 把 hash 形态的 Cookie 值当作数字 IM UID；把昵称、短号、sec_uid 当作目标 UID
- 对无历史会话目标跳过 conversation/create
- 把 identity token、bd-ticket-guard-client-data 当作长期固定配置或静态 Header
- 用另一个 Cookie/浏览器环境的 guard 材料
- 看见发送回执或检查响应就认为对方一定收到；需从服务端 ID、检查码、业务状态和实际到达验证

## 验证口径

- 会话字段（conversation_id / short_id / ticket）从当前登录态同轮获取；send 返回服务端消息 ID 与明确业务状态
- 目标会话实际收到或服务端可验证回执；不输出账号、密码、token、凭据等敏感值
