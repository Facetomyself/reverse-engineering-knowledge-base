# 京东到家 / 外卖商家 WebSocket

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 京东到家 / 外卖商家后台的订单推送 WebSocket 链路，常与京东 h5st 签名链路组合出现。

## 命中特征

- 接口：`dsm.o2o.order.dongdong.token.query`、`dsm.o2o.order.dongdong.update.connect`、`dsm.o2o.order.cater.pcAllOrderListQuery`、`dsm.o2o.order.cater.pickOrder`
- 字段/参数：`h5st`、`x-rp-client`、`dsm-eid`、`auth`、`auth_result`、`client_heartbeat`、`chat_message`、`ack`、`failure`、`waiterPin`、`eIdMd5`、`nonce`、`stationId` / `stationNo`
- WS URL 携带 `appId`、`clientType`、`token`、`nonce` 动态上下文

同链出现 `h5st/_stk/request_algo/tk03` 时，同时按京东 h5st 产品处理。

## 常见链路

```text
完整商家后台 Cookie
→ 通过 h5st 签名请求 token.query
→ 获取 waiterPin、eIdMd5、token、nonce
→ 构造 WS URL（appId/clientType/token/nonce）→ 连接
→ 发送 type=auth（body.token=token）→ 收到 auth_result
→ 上报 update.connect 在线状态
→ 定时发送 client_heartbeat
→ 收到 chat_message 订单推送 → 发送 receive ack
→ 解析订单提醒、订单号、配送站、买家、消息序号
```

## 观察优先级

1. `h5st` 是连接前 token 请求与在线状态上报的关键前置，不是 WebSocket 帧内字段
2. `token`、`nonce` 需要从当前 Cookie 同轮获取，不复用旧 trace；WS URL 的 token/nonce 是动态上下文
3. `auth_result` 后才算业务鉴权成功，101 握手成功不等于订单推送可用
4. `client_heartbeat` 是业务层 JSON 心跳，不能只依赖 WebSocket 库的 ping
5. `chat_message` 里可能嵌套订单模板数据，需要从 body/template/payload 中提取订单字段；收到推送后发送业务 ACK，避免后续推送或状态异常
6. 与 HTTP 接口配合：订单列表接口用于主动拉取、补单与校验推送；订单操作接口用于执行动作，仍需当前 Cookie、完整 headers 和 h5st

## 常见坑

- 只复制 WS 连接地址，漏掉前置 token.query
- 用 document.cookie 或裁剪 Cookie，导致 token 请求 401
- h5st 使用旧值或没有覆盖当前接口/body
- auth_result 未成功就开始等订单
- 忽略 update.connect 在线/离线状态上报；忽略 ack 只打印推送
- 多窗口或多客户端占用同一客服账号导致账号冲突（如 errorCode=4281 类）
- 固定旧 stationId、stationNo、订单号或 waiterPin

## 验证口径

- token 请求成功并获得当前登录态对应的 token/nonce；WS 握手成功并收到 auth_result
- 心跳有业务层 ACK；收到 chat_message 后能解析订单字段并发送 ACK
- 通过订单列表或详情 HTTP 接口交叉验证订单存在；推送里的订单号不视为已完成业务动作
