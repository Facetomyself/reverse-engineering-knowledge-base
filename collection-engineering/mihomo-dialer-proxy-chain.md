# Mihomo 链式代理：dialer-proxy、全局脚本与采集器前置链

> 来源: — (GitHub 归档)
> 原始发布时间: 2026-08-13
> 归档日期: 2026-09-06
> 分类: collection-engineering
>
> 从 Clash Verge Rev 全局脚本与 Mihomo 官方 `dialer-proxy` 文档提炼：内核链式代理、已废弃的 `relay` 组、TUN fake-ip 排除坑，以及它和采集器 `curl --preproxy` / 隔离 sidecar 为什么不是同一条合同。

## 结论先行

1. **Mihomo 内核链式代理的现行字段是 `dialer-proxy`，不是 `relay` 组。** 当前节点通过 `dialer-proxy` 指向的节点或组去建连；目标站只看见落地节点 IP，本机运营商只看见前置节点。
2. **`proxy-groups` 不能直接写 `dialer-proxy`。** 官方迁移路径是：把后跳放进 `proxy-providers`，用 `override.dialer-proxy` 一次打到整组；或在具体 `proxies` 条目上写该字段。
3. **Clash Verge 全局脚本解决的是桌面 TUN / 系统代理的日常分流，不是采集器身份合同。** 它会重建规则、丢掉订阅自带的 App 服务组，并把住宅 SOCKS 凭据写进脚本配置。
4. **reverse_ENV 现有主线不必改成这套脚本。** 采集与逆向已经用 `127.0.0.1:7897` 当前置、`curl --preproxy` 做客户端级联、`mihomo_fanout.py` 做隔离 listener；出口身份在供应商 route / SID 上验收，不依赖 GUI 策略组。

## 来源与证据边界

| 来源 | 角色 | 边界 |
|------|------|------|
| [LunFengChen/clash-proxychain-script](https://github.com/LunFengChen/clash-proxychain-script) | Clash Verge Rev 全局脚本模板：`USER_CONFIG` 生成 hop 链与国内/国外两组 | 2026-08-13 仍活跃；无许可证；Stars 低，当机制说明，不当生产依赖 |
| [MetaCubeX `dialer-proxy` 文档](https://github.com/MetaCubeX/Meta-Docs/blob/main/docs/config/proxies/dialer-proxy.en.md) | 内核语义、`relay` 废弃、`proxy-providers.override` 迁移 | 字段合同以这份为准 |
| `skill/proxy-usage` 现行用法 | `7897` listener、`--preproxy`、`mihomo_fanout.py` | 采集/逆向主线；本文对照用，不改其完成门 |

仓库模板含 `server` / `username` / `password` 占位符。归档只保留机制，不收录真实落地节点或脚本全文。

## 内核链：谁看见谁

官方例子里，落地节点 `ss1` 的 `dialer-proxy` 指向前置组，组内是 `ss2`。流量路径是：

```text
core --(ss1 载荷)--> ss2 封装 ===ss2==> ss2 服务器 --(ss1)--> ss1 服务器 --> 目标
```

对外可见性：

| 观察者 | 看见 |
|--------|------|
| 目标站 / IP 查询页 | 只有落地 `ss1` 的出口 |
| 本机运营商 / 防火墙 | 只有前置 `ss2` |
| 前置服务器 | 正在连落地 `ss1`，不知道最终 URL |
| 落地服务器 | 正在访问目标 |

这和采集器要的「机场只负责到达供应商网关，住宅 IP 才是业务出口」是同一拓扑，只是实现平面不同。

### 多跳怎么叠

脚本把 hop 数组按顺序展开：每个 hop 复制一份代理，并把 `dialer-proxy` 指向上一跳；第一跳默认指 `Chain-Front`。两条 hop 时：

```text
本机 -> Chain-Front（机场自动选择/节点选择）-> hop1 中继 -> hop2 落地 -> 目标
```

某条链要钉死前置时，把 `front` 写成具体节点名或订阅里的 `自动选择`。`Chain-Front` 本身是 `select` 组，优先挂订阅的 `自动选择`，前置挂了可以自动换。

### `relay` 为什么不要再用

`relay` 类型代理组已废弃。组对象也不直接支持 `dialer-proxy`。官方替代是：

- 前跳放进 `select` 组；
- 后跳放进 `proxy-providers`；
- 对该 provider 写 `override.dialer-proxy: <前跳组名>`。

订阅转换器常会剥掉手工写的 `dialer-proxy`。落地节点应放在 Clash Verge 的节点编辑或全局增强里，不要指望订阅刷新后字段还在。

### 落地协议限制

官方提醒：用订阅节点当中继去接自建落地时，落地不要选 UDP 向协议（`hy2` / `tuic` / `wg`）或 Reality / ShadowTLS 这类伪装。订阅节点经常转不好。推荐落地用简单的 SS AEAD 或 VMess。脚本模板默认落地是 SOCKS5，符合「住宅供应商给 SOCKS」的常见形态。

## 全局脚本实际改了什么

脚本不是再维护一套「B 站 / 抖音 / 某某服务」分流，而是强制成普通人能看懂的桶：

```text
进程例外 -> 本机/LAN 直连 -> GEOIP CN / .cn -> Domestic-Sites -> 其余 MATCH Foreign-Sites
```

生成的可选组通常是：

| 组 | 作用 |
|----|------|
| `Domestic-Sites` | 国内桶，可选 `DIRECT` 或某条链 |
| `Foreign-Sites` | 国外桶，默认走落地链 |
| `Chain-*` | 单条链：链式落地 / 单独 SOCKS / `DIRECT` |
| `Chain-Front` | 全链共用前置 |
| `Default` | 兜底入口 |

安装面是 Clash Verge 的全局 Script：GUI 粘贴，或覆盖 profiles 目录下的 `Script.js` 后刷新订阅。脚本会：

1. 按 hop 生成直连副本和带 `dialer-proxy` 的链式副本；
2. 丢掉订阅里未列入白名单的服务组，避免它们抢先命中；
3. 有进程规则时打开 `find-process-mode: always`；
4. `directDomains` 写成 `DOMAIN,...,DIRECT`，并给 `dns.nameserver-policy` 配 `system`；
5. `directIpRanges` 同时写入 `IP-CIDR` 和 `tun.route-exclude-address`。

### TUN 直连超时：不要排除 fake-ip

关 Clash / TUN 能访问、开 TUN 后同一域名即使规则是 DIRECT 仍超时，通常是流量仍被 TUN 接管。这时只能把**真实公网 IP / CIDR** 放进 `tun.route-exclude-address`。

不要把 Mihomo fake-ip 段（常见 `28.0.0.0/8`、`198.18.0.0/15`）写进排除列表。fake-ip 会动态复用；排除后，其他域名可能拿到同一个假地址，再被直连到无效地址并超时。

进程例外只留给微信 / QQ / 企业微信这类「TUN 下登录或媒体会怪」的应用，名单保持短。这是桌面日常问题，不是采集器 worker 模型。

## 三种链式平面，不要混合同

| 平面 | 谁建链 | 出口身份写在哪 | 适用 |
|------|--------|----------------|------|
| Mihomo `dialer-proxy` | 正在跑的 Clash Verge / 内核 | 当前配置的落地节点，随 GUI 组选择变 | 桌面 TUN、系统代理、全机应用共用一条链 |
| 客户端 `--preproxy` | `curl` / `proxy_check.py` / `cliproxy_test.py` | `-x` 上的供应商网关；`--preproxy` 只负责到达网关 | 本机到 Cliproxy / TNB / 快代理网关受限时的验收 |
| 隔离 sidecar | `mihomo_fanout.py` 另起 mihomo | 每个 loopback listener 的 `proxy: <叶子节点>` | 多订阅节点并发探测，且不许改当前 Verge 选择 |

采集器还多一层供应商语义：Cliproxy `sid` / `t`、TNB `session`、Sticky lease。这些写在用户名或 white API 的 `time` 上，内核 `dialer-proxy` 不知道 SID，也不会做 429 / 403 分类。控制面仍见 [高并发 HTTP 采集控制面](./high-concurrency-http-collector-control-plane.md)。

官方文档里还有一种**方向相反**的 `dialer-proxy`：环境只能经某条 SOCKS 出网，于是给整个订阅 provider `override.dialer-proxy: socks1`。目标站看见的是**机场节点 IP**，不是住宅落地。这解决「内网出网」，不解决「住宅出口」。reverse_ENV 的 `--preproxy` 是「Clash 到达供应商，供应商才是出口」，不要和这种 override 对调。

## 对 reverse_ENV 现行用法的判定

现行主线已经是：

```text
本机工具 -> 127.0.0.1:7897（或 SOCKS 7897）-> 供应商网关（Cliproxy / TNB / 快代理）-> 目标
```

业务客户端永远走 `7897`，不走 Controller `9097`。常规请求不切换本机节点。需要同时打多个订阅叶子节点时，另起 sidecar，跑完即停。`--preproxy` 只证明「到得了网关」；`route_identity_verified` 必须看供应商出口，HTTP/HTTPS relay 的 200 不算 Cliproxy 成功。

对照全局脚本后，**主线不需要改成 Verge Script / 内核 `dialer-proxy`**，原因是合同冲突，不是脚本写得差：

1. **出口身份会从请求参数逃到 GUI 状态。** 脚本把落地写进当前 profile 后，`7897` 的出口随 `Foreign-Sites` / `Chain-*` 选择变。现行合同是：`7897` 只是本机 relay，供应商身份单独验收。
2. **凭据平面错位。** 脚本要求把 SOCKS 账密写进 `USER_CONFIG`。现行凭据只在 `skill/proxy-usage/.env` 或进程环境；Clash YAML / Script 不承载供应商密码。
3. **会改正在用的 Verge。** 脚本重建规则并隐藏订阅服务组。`mihomo_fanout.py` 的前提是不 reload、不改当前实例。
4. **没有 Sticky / 并发合同。** 进程名分流和 `GEOIP,CN` 桶解决日常上网；采集要的是 per-worker SID、Cookie 隔离和有界 fan-out。
5. **`requests` 本来就不能代理到代理。** 需要级联时已经切到 curl `--preproxy`。把链搬进内核，只让「走系统代理的桌面应用」受益，不让 Python / ruyi 的显式 `proxies=` 更正确。

可以保持不变的具体做法：

- 继续用 `clash_controller.py check` 验证 `7897`，不要为了链式去 `switch` / `rotate`。
- Cliproxy / TNB 继续 `--preproxy socks5h://127.0.0.1:7897`（或 HTTP `7897`，但 HTTP relay 不计出口身份）。
- 多节点并发继续 `mihomo_fanout.py`，不要在当前 Verge 上叠 `dialer-proxy` 冒充并发。
- 不要把该仓库的 `Script.js` 贴进正在给逆向/采集用的 Clash Verge profile。

### 唯一可选的「改」

只有桌面日常 TUN 需要「全机应用先经机场、再出住宅 SOCKS」，并且这条链与 `7897` 采集合同隔离时，才在**独立 Clash profile** 上使用 `dialer-proxy` 或该脚本。那是本机上网配置，不是 `proxy-usage` 主线，也不进 Git。

若误把全局脚本装进当前采集用 Verge，先恢复订阅原规则，再重跑 `clash_controller.py check`；在恢复前不要把 `7897` 当作已验收的供应商前置。

## 速查

| 问题 | 答案 |
|------|------|
| 内核链式字段 | `proxies[].dialer-proxy` 或 `proxy-providers.override.dialer-proxy` |
| 不要用 | `relay` 组；在 `proxy-groups` 上写 `dialer-proxy` |
| 落地协议 | SOCKS5 / SS AEAD / VMess；避免 hy2、tuic、wg、Reality、ShadowTLS 当被中继的落地 |
| TUN DIRECT 仍超时 | 排除真实公网 CIDR；禁止排除 fake-ip 段 |
| 采集器链式 | `curl --preproxy` + 供应商 `-x`；不是 Verge 全局脚本 |
| 多节点并发 | `mihomo_fanout.py` sidecar；不是改当前策略组 |
| 脚本凭据 | 只放本机私有 profile；禁止提交 `server` / 账密 |
