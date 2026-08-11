# 抖音 / 字节 Ticket Guard 与 SecureSDK

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> ByteDance Web Ticket Guard 与 SecureSDK 状态链：bd-ticket-guard-* 头族、security-sdk storage 状态与请求完整性校验。

## 命中特征

- 请求头出现 `bd-ticket-guard-client-data`、`bd-ticket-guard-ree-public-key`、`bd-ticket-guard-web-version`、`bd-ticket-guard-web-sign-type`、`bd-ticket-guard-version`
- Cookie 出现 `bd_ticket_guard_client_data`、`bd_ticket_guard_client_data_v2`、`_bd_ticket_crypt_cookie`、`__security_mc_*` 等标记
- storage 出现 `security-sdk/s_sdk_crypt_sdk`、`security-sdk/s_sdk_cert_key`、`security-sdk/s_sdk_server_cert_key`、`security-sdk/s_sdk_sign_data_key/web_protect`、`web_secsdk_runtime_cache` 等键
- 脚本或栈出现 `SecureSDK`、`web_protect`、`ticket_guard`、`get_client_cert`、`get_sec_ts`、`startDTrait`
- 登录/bootstrap 路径下出现 /passport/ticket_guard/、get_sec_ts、token/beat、QR 确认或 MFA 验证类接口

产品边界：Ticket Guard 是请求完整性状态，与 `a_bogus`（查询签名）、`msToken`（会话 token）、`x-tt-session-dtrait`（加密会话材料）、浏览器 Cookie 登录态是不同的组件。一个请求可以同时携带全部组件，一个组件正确不代表其它组件正确，不要把失败全部归因到 a_bogus 或 TLS 假设。

## 常见链路

```text
SecureSDK 初始化
→ 创建或加载本地密钥材料
→ 请求 client/server 证书材料
→ 收到 sec_ts 或等价挑战状态
→ 用本地私钥和服务端证书派生证明
→ 持久化匹配的 Cookie 与 security storage 状态

受保护请求
→ 选择当前路径与会话上下文
→ 构建 fresh Ticket Guard 请求头
→ 需要时单独构建或附加 dtrait 与查询签名状态
→ 发送请求

认证完成
→ 服务端可能下发新的 server-data / 绑定材料
→ 浏览器持久化新的匹配状态
```

材料角色（名称与 JSON 形状版本相关，以当前 Cookie/storage 写入与 SecureSDK 源码确认）：client_data 携带客户端公钥/证书标记；client_data_v2 携带 ts_sign 与 sec_ts 证明；crypt_sdk 是本地密钥对（私钥仅本地）；cert_key 客户端公钥/证书；server_cert_key 服务端证书；sign_data 是 ticket 与 ts_sign 请求签名状态。Cookie 字段能标识绑定，但不含私钥；公钥、crypt-cookie 标记或 ts_sign 不能当作重建私钥或伪造 profile 的充分信息。

## 观察优先级

1. 把 Cookie jar、localStorage security-sdk 状态、sessionStorage、浏览器 profile 与当前动态响应状态视为一个原子安全 profile，不作为可互换的文件或头
2. 一致性检查：账号标识与 profile 元数据及只读身份响应一致；Cookie 中 guard 公钥与 security storage 客户端证书一致；`ts_sign` 与 web_protect 签名状态一致；webid/verifyFp/uifid 同代生成；浏览器族与 UA/client-hint 状态一致
3. 同账号 UID 不足为凭：后登录、换浏览器或重新绑定可以有相同 UID，但 guard 公钥、ts_sign、ticket、服务端证书或会话状态不同
4. 认证完成边界：心跳/HTTP 200 不是绑定完成；certificate/sec_ts 端点可能正常返回但不下发新 server-data；新 server-data 出现在成功认证完成（确认登录或验证/MFA 完成）时
5. 每个 `bd-ticket-guard-*` 头定位精确的请求边界注入点；每个 storage 键映射到当前 trace 的写入/读取并记录持久/会话/响应下发属性
6. 失败先分类：profile 不匹配（Cookie 公钥/ts_sign 与本地 security storage 冲突）、缺绑定材料、动态状态过期、路径作用域 guard 缺失、独立签名器不匹配、认证/验证门
7. 受保护路径与请求时间戳可能进入 guard 证明，其序列化方式以当前 SecureSDK/请求边界证据为准；dtrait 有独立时间相位与加密随机性，不强制与 guard 时间戳共享

## 常见坑

- 把登录 Cookie 当作整个安全 profile
- 混用另一会话的 Cookie 与 storage/路径头
- 把同账号 UID 当作两个浏览器绑定可互换的证明
- 复制历史 guard header 或 dtrait 到新请求
- 生成新密钥对后把 get_sec_ts 或 token-beat 成功当作服务端绑定证明
- 把 a_bogus、dtrait、TLS persona 与 Ticket Guard 混成一个参数问题
- 请求返回 HTTP 200 就宣布成功，不检查正确响应/状态判据
- 分析产物落盘私钥、完整 ticket、证书、Cookie 或完整头值

## 验证口径

- 复用已有 profile 前先匹配当前 Cookie 身份、guard 公钥与 ts_sign；不匹配即在请求构造前拒绝
- 新浏览器绑定的假设必须有当前响应实际下发绑定材料；setup/心跳响应不足为凭
- 先用非破坏性、当前会话判据验证；不把公开读接口的成功当作受保护动作的成功
