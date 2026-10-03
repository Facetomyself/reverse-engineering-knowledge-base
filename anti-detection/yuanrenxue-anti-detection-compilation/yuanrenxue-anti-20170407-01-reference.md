---
schema_version: 2
id: yuanrenxue-squid3-myip-egress-reference
document_type: reference
original_date: '2017-04-07'
archived_date: '2026-10-02'
scope:
  targets:
    - squid3
  client: linux
  version: squid3
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-anti-20170407-01.md#配置多-ip-地址"
    basis: source-report
  - id: s2
    ref: "./yuanrenxue-anti-20170407-01.md#配置-squid-多出口"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留来源写下的逻辑接口名和 address、netmask、gateway 三项。地址是 RFC 5737 文档网段，网卡名是示例，没有发行版命令。
  - name: interfaces
    anchor: interfaces
    sources: [s2]
    basis: source-report
    limits: 只保留 myip ACL 与 tcp_outgoing_address 的成对写法。没有监听指令，也没有未命中时的默认出口。
  - name: validation
    anchor: validation
    sources: [s2]
    basis: source-report
    limits: 来源只要求核对三项是否一致，没有点名检测服务，也没有不一致时的处理。本轮未执行核对。
relations:
  - type: derived_from
    target: "./yuanrenxue-anti-20170407-01.md#运维linux单台机器配置多ip的squid3-http代理"
tags:
  - squid3
  - tcp-outgoing-address
  - source-report
---

# Squid3 按本地地址选择出口

这张卡只回答：来源怎样把同一块网卡上的两个逻辑地址，和 `squid.conf` 里的 `myip` ACL、`tcp_outgoing_address` 绑在一起，以及它要求部署后核对什么。不提供监听端口、发行版命令，也不补 ACL 未命中时的行为。示例地址是文档网段，不是实测出口。

<a id="parameters"></a>
## 主机侧地址

来源用 RFC 5737 的 `192.0.2.0/24` 演示，并写明部署时要换成分配给服务器的地址。物理网卡示例是 `eno1`，逻辑接口是 `eno1:90` 与 `eno1:91`。每个逻辑接口各写静态 `address`、`netmask` 和 `gateway`。两个示例的 netmask 都是 `255.255.255.0`，gateway 都是文档网段里的 `.1`。

> 实际部署时替换为分配给服务器的真实地址

> `eno1` 是物理网卡，`eno1:90` 与 `eno1:91` 是绑定在同一网卡上的逻辑接口。

来源要求先确认系统用的是 `/etc/network/interfaces`、NetworkManager 还是 netplan，再写等价配置。它没有给出后两种的写法。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 实际部署时替换为分配给服务器的真实地址 | s1 ./yuanrenxue-anti-20170407-01.md:37 | source-report | squid3 | 文档网段，不是实测地址 |
| C2 | 绑定在同一网卡上的逻辑接口 | s1 ./yuanrenxue-anti-20170407-01.md:53 | source-report | squid3 | 网卡名是示例 |

<a id="interfaces"></a>
## squid.conf 绑定

来源在 `squid.conf` 里按本地监听地址选择出口。一对示例是：`myip` ACL 命中 `192.0.2.90` 时，`tcp_outgoing_address` 也用 `192.0.2.90`。`192.0.2.91` 同样成对。ACL 名字是 `ip_90` 与 `ip_91`。

> 在 `squid.conf` 中按本地监听地址选择对应的出口地址

> acl ip_90 myip 192.0.2.90

> tcp_outgoing_address 192.0.2.90 ip_90

文中没有 `http_port`，也没有写 ACL 都未命中时从哪一个地址出去。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 按本地监听地址选择对应的出口地址 | s2 ./yuanrenxue-anti-20170407-01.md:57 | source-report | squid3 | 没有监听指令 |
| C4 | tcp_outgoing_address 192.0.2.90 ip_90 | s2 ./yuanrenxue-anti-20170407-01.md:61 | source-report | squid3 | 文档网段示例；上一行是对应的 myip ACL，91 是同一写法 |

<a id="validation"></a>
## 来源要求的核对

来源的通过说法是：请求进入不同本地地址时，从对应 IP 发出。它要求部署后分别请求出口检测服务，看监听地址、ACL 命中和实际公网出口是否一致。检测服务没有名字，文中也没有核对记录。

> 验证监听地址、ACL 命中和实际公网出口一致

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 验证监听地址、ACL 命中和实际公网出口一致 | s2 ./yuanrenxue-anti-20170407-01.md:67 | source-report | squid3 | 未执行；没有失配后的动作 |

## 验证与限制

- 标题写 squid3，配置片段没有包版本。
- 没有监听指令、默认出口，也没有两个 gateway 冲突时的说明。
- 近邻 Mihomo/Clash 代理平面卡是另一个目标，不覆盖这条 `myip` 绑定。
- 没有失败出口，所以不是流程卡。依据停在 source-report。
