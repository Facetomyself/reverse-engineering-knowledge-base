# 美团外卖商家 WebSocket

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 美团外卖商家后台 WebSocket 长连接、二进制协议与客服自动回复链路。

## 命中特征

- wss 通道 `wmdxlwss` 域；`wpush_server_url`
- 参数：`wmPoiId`、`acctId`、`device_uuid`、`pushToken`、`token`
- 协议对象/函数：`ByteBuffer`、`MTDXPacket`、`get_ws_data`、`get_ws_base64`、`get_message_base64`、`send_init_packet`、`send_auto_reply`
- 心跳/探测包 uri 标记（如 196619 / 196620 / 196611 类）；`TGData.summary`

## 常见链路

```text
商家登录态（Cookie）
→ 提取 wmPoiId、acctId、token、device_uuid、店铺/账号信息
→ 连接 wss
→ onopen 后调用 JS 生成初始化二进制包并发送
→ 定时发送业务心跳
→ 收到服务端 pong / 探测包，必要时回对应 uri
→ 收到业务二进制消息
→ 用 MTDXPacket / ByteBuffer / protobuf 或 JSON 片段解析消息
→ 提取客户 UID、公共通道 ID、消息文本
→ 调用 JS 生成回复二进制包 → 通过当前 WS 发送自动回复
```

常见包头结构：

```text
total_length: uint32 big-endian
uri: uint32 big-endian
appid: uint16 big-endian
payload: bytes
```

uri 决定包类型；payload 内可能混合二进制字段、protobuf、JSON 字符串和 UTF-8 文本。

## 观察优先级

1. 心跳和业务消息使用不同 uri；WebSocket 库的 ping 与业务心跳不是一回事
2. JS 生成初始化包和发送包时可能返回 base64，请求面验证需解码成 bytes 再发送
3. 登录态输入（wmPoiId/acctId/token/device_uuid/店铺/账号）必须来自同一 Cookie、同一店铺、同一账号、同一设备环境；换店铺或账号不能只替换局部字段
4. 消息解析：标准 JSON / `TGData.summary` 优先；摘要不完整时从二进制前缀扫描 UTF-8 文本兜底
5. 区分客户消息、商家侧消息、系统事件、售后/评价等不应自动回复的消息；当前客户 UID 与公共通道 ID 从当前消息动态解析
6. 稳定性：业务心跳线程、send lock 避免并发写、连接状态记录、指数退避重连、断线后重新初始化并重启心跳

## 常见坑

- 只用 WS 握手成功，不发送初始化包
- 使用旧账号/旧店铺的初始化结果
- `device_uuid` 没加实际页面使用的前缀或格式不一致
- 把业务心跳和 WebSocket ping 混淆
- 二进制包大小端、长度字段或 uri 解析错误
- 自动回复固定旧客户 UID，导致回复错人
- 没过滤商家自己发出的消息，造成循环回复
- 日志打印完整 Cookie、token、店铺账号字段

## 验证口径

- WS 握手成功后初始化包发送成功；心跳和服务端探测回包正常
- 能解析当前客户消息，动态提取回复所需的两个会话目标 ID
- 发送回复二进制包后，目标会话实际收到或服务端有可验证回执
- 换店铺/账号后，Cookie、店铺 ID、账号 ID、token、device_uuid 均同源
