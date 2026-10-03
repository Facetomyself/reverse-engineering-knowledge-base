---
schema_version: 2
id: ruyi-20260528-firefox-socks5-fpfile-procedure
document_type: procedure
original_date: '2026-05-28'
archived_date: '2026-10-02'
scope:
  targets: [firefox]
  client: firefox
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260528-01.md#目标
    basis: source-report
  - id: s2
    ref: ./ruyi-20260528-01.md#修改文件
    basis: source-report
  - id: s3
    ref: ./ruyi-20260528-01.md#fpfile-支持格式
    basis: source-report
  - id: s4
    ref: ./ruyi-20260528-01.md#使用方式
    basis: source-report
  - id: s5
    ref: ./ruyi-20260528-01.md#已验证场景
    basis: source-report
  - id: s6
    ref: ./ruyi-20260528-01.md#注意事项
    basis: source-report
  - id: s7
    ref: ./ruyi-20260528-01.md#编译命令
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1, s3]
    basis: source-report
    limits: 只整理已有 SOCKS5 认证接口、手动路径传空，以及三种 fpfile 格式的限制。不抄样例账号。
  - name: decision-flow
    anchor: steps
    sources: [s2, s4]
    basis: source-report
    limits: 只写到文件、类型常量和启动参数。关键代码第 2 到 6 节没有函数体，本卡不补。
  - name: validation
    anchor: acceptance
    sources: [s5, s7]
    basis: source-report
    limits: 验收清单和编译通过都是作者自述。本轮没有源码树，也没有 xpcshell。
relations:
  - type: derived_from
    target: ./ruyi-20260528-01.md#目标
tags: [firefox, socks5, fpfile, source-report]
---

# Firefox 手动 SOCKS5 从 --fpfile 取账号密码

这份流程只回答：2026-05-28 这篇归档把手动 SOCKS5 的空账号密码补在哪两个文件、哪种 fpfile 才匹配、以及哪些输入明确不注入。它不提供解析函数的源码。

`kb_catalog.py query --target firefox --module parameters` 与 `--module decision-flow` 都是 0。Mihomo 卡是另一套代理平面，不覆盖 nsProtocolProxyService。

适用前提是来源点名的 Firefox 网络栈已经有 SOCKS5 用户名密码握手，缺的只是手动 prefs 没把凭据放进 nsIProxyInfo。需要函数体、或样例里的代理账号时，不适用。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 作者写下的要求 | 不足时 |
|---|---|---|
| 已有接口 | nsIProxyInfo 已有 username / password；newProxyInfoWithAuth 能建带认证的 SOCKS；nsSOCKSIOLayer.cpp 已做 RFC1929 握手 | F1 |
| 缺口 | 手动代理 prefs 创建 nsIProxyInfo 时始终传空 username/password | F1 |
| 改动面 | 只准备改 netwerk/base/nsProtocolProxyService.cpp 和同目录头文件 | F1 |
| 代理类型 | 手动代理是 SOCKS5。SOCKS4、HTTP、HTTPS、PAC、system proxy 不在范围内 | F3 |
| fpfile | 启动参数 --fpfile 指向凭据文件。一行格式仅 DNS 或 IPv4，账号密码不能含冒号；否则用 key-value | F2 |
| 构建 | 作者写只改了 C++，命令是 ./mach build binaries。当前 mozconfig 使用了 --disable-tests，所以作者不跑 mach xpcshell-test | 没有源码树走 F1 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 对照前提。确认要复用的是已有握手，而不是新写一套 SOCKS5 | 三个已有符号是否在来源点名的位置 | 缺任一符号走 F1，否则 S2 |
| S2 | 只在 nsProtocolProxyService.cpp/.h 增加 --fpfile 读取、凭据结构和缓存声明，并在创建 nsIProxyInfo 之前注入。类型限于 kProxyType_SOCKS | 两文件的改动清单 | 要改其他代理类型走 F3；要看解析函数正文走 F1 |
| S3 | 选格式。一行是 host、port、username、password 用冒号分隔，只给 DNS 或 IPv4。全局键只在没有更具体的 host/port 匹配时使用。指定 host 的 key-value 匹配大小写不敏感 | 选定的格式，不含样例账号 | 一行格式碰到 IPv6 或冒号走 F2，否则 S4 |
| S4 | 按来源的手动代理 prefs：network.proxy.type = 1，并设置 socks 主机、端口和 socks_version = 5。启动参数写成 firefox.exe --fpfile | prefs 与启动参数清单 | 没有 --fpfile 走 F4，否则 S5 |
| S5 | 仅当 username 与 password 都非空才注入。握手仍留给 nsSOCKSIOLayer.cpp | 是否注入的条件 | 只有一边有值走 F3；作者自述的对照走验收，缺函数体仍是 F1 |

流程图节点沿用 S1 到 S5 与 F1 到 F4。正文是行为真源。关键代码第 2 到 6 节在来源里是空标题，不能把它们画成已实现的函数。

<a id="outputs"></a>
## 输出

交付的是边界，不是补丁文件。来源把输出写成：SOCKS5 的 nsIProxyInfo 在匹配成功时带上 username 与 password；不新增 UI；不新增 prefs；密码不写入 profile；底层握手文件不变。作者另写 ./mach build binaries 并且已经编译通过。这句保持 source-report。本卡不附带 fpfile 样例。

<a id="acceptance"></a>
## 验收

下列各项都是作者用当前 objdir 的 xpcshell.exe 写下的对照，本轮没有复现。通过只表示来源这么写，不表示当前树已经注入。

| 来源对照 | 作者写下的结果 |
|---|---|
| host:port:user:pass 正向匹配 | 成功注入 username/password |
| 无 --fpfile | 不注入 |
| 文件在但 host/port 不匹配 | 不注入 |
| 全局 socksauth 键 | 成功注入 |
| 带 host/port 的 key-value | 成功注入 |
| host 大小写不同 | 仍匹配 |
| fpfile 路径含空格 | 正常 |
| fpfile 不存在 | 不注入 |
| SOCKS4 | 不注入 username/password |

反例：把上述任何一条写成已经在本机跑过，或把“已经编译通过”写成当前构建成功。

<a id="failure-exits"></a>
## 失败出口

F1：关键代码第 2 到 6 节没有函数体，文末写完整文档代码修改位于星球。需要解析或注入实现时停止，不补写 C++。

F2：一行冒号格式不支持 IPv6 host，也不支持账号或密码里的冒号。改用 key-value，或停止这一格式。

F3：password-only 不支持，username 与 password 必须都非空才注入。SOCKS4、HTTP、HTTPS、PAC 和 system proxy 不注入。

F4：没有 --fpfile、fpfile 不存在，或 host/port 不匹配且没有可用的全局凭据时，不注入。不要把空注入说成认证已启用。
