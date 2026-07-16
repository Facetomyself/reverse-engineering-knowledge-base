# 「运维」Linux单台机器配置多IP的squid3 http代理

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2017-04-07
> 归档日期: 2026-07-16
> 分类: anti-detection
>
> 在单机绑定多个出口地址，并通过 Squid ACL 将监听地址映射到对应出口 IP，适合构建集中管理的多出口代理节点。

## 配置多 IP 地址

以下使用 RFC 5737 文档网段 `192.0.2.0/24` 演示。实际部署时替换为分配给服务器的真实地址。

```text
auto eno1:90
iface eno1:90 inet static
    address 192.0.2.90
    netmask 255.255.255.0
    gateway 192.0.2.1

auto eno1:91
iface eno1:91 inet static
    address 192.0.2.91
    netmask 255.255.255.0
    gateway 192.0.2.1
```

`eno1` 是物理网卡，`eno1:90` 与 `eno1:91` 是绑定在同一网卡上的逻辑接口。确认系统网络配置方式后，再将等价配置写入 `/etc/network/interfaces` 或当前发行版使用的 NetworkManager/netplan。

## 配置 Squid 多出口

在 `squid.conf` 中按本地监听地址选择对应的出口地址：

```text
acl ip_90 myip 192.0.2.90
tcp_outgoing_address 192.0.2.90 ip_90

acl ip_91 myip 192.0.2.91
tcp_outgoing_address 192.0.2.91 ip_91
```

这样，请求进入不同本地地址时会从对应 IP 发出，实现一台服务器承载多个固定出口。部署后应分别请求出口检测服务，验证监听地址、ACL 命中和实际公网出口一致。
