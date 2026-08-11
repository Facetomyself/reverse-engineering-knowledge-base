# 饿了么商家 ACCS / 钉钉 LWP WebSocket

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 商家后台 ACCS 通知通道与 DingTalk IMPaaS LWP 业务通道的双通道 WebSocket 链路。

## 命中特征

- ACCS 通道：`ws-msgacs` 域 `/accs/auth`；`ACCS_H5`、`getAccsToken`、`AuthCenterService.getToken`、getAccsToken 类 HTTP 接口
- LWP 通道：wss 连接 `wss-cntaobao.dingtalk.com`；`/reg`、`/s/sync`、`/r/MessageSend/sendByReceiverScope`
- 接口/参数：`alsc-im-paas` 的 getLoginToken、`imPaaS2LoginToken`、`LWP`、`app-key`、`did`、`wv`、`sync`、`mid`、`cid`、`conversationType`

## 常见链路

双通道模型：

```text
ACCS 通道 = ws-msgacs.../accs/auth?token=... 偏通知、信号、业务唤醒
LWP 通道  = wss-cntaobao... /reg 注册后承载真正业务消息、同步、发送消息
```

```text
商家登录态（Cookie / ksid / shopId / deviceId）
→ HTTP getAccsToken → 连接 ACCS → 接收通知并 ACK

商家登录态
→ HTTP getLoginToken → 取 imPaaS2LoginToken → 连接 LWP
→ 发送 /reg 注册包（code=200）→ 定时心跳 → 接收推送或 /s/sync 同步信号
→ 必要时 getState / ackDiff 补拉和确认
→ 使用 /r/MessageSend/sendByReceiverScope 发送文本
```

不要把 ACCS 能收到通知误判为已经具备发送消息能力，文本发送通常走 LWP。

## 观察优先级

1. `/reg` headers（cache-header: app-key token ua wv；sync；did；subscribe-server-push）来自当前登录态与当前设备环境，不复用旧 login token 或旧 did
2. 发送 body 的 `cid` 是当前客户会话/groupId，必须从当前消息或会话列表动态取得
3. ACCS 消息是否需要 ACK；LWP push 包是否需要返回 code=200；`/s/sync` 是否只是同步信号、需进一步 getState/ackDiff
4. `mid` 如何匹配请求和响应；发送消息返回是请求成功还是业务发送成功

## 常见坑

- 只连 ACCS 不连 LWP，导致只能收到信号不能发消息
- `/reg` 未成功就发送业务消息
- login token、ksid、deviceId 与 Cookie 不属于同一登录态
- 固定旧客户 cid/groupId
- 忽略 `/s/sync` 后的补拉与 ackDiff；没有按 mid 匹配请求/响应
- 只看 WebSocket 连接成功，不看 `/reg code=200`

## 验证口径

- ACCS token 和 LWP login token 都能从当前 Cookie 获取；LWP `/reg` 返回 code=200；心跳持续正常
- 能解析当前客户会话 cid；发送文本接口返回业务成功，并能在目标会话实际看到消息或收到服务端回执
