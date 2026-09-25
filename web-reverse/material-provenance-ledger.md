# 方法论：签名材料出处账本

> 来源: `workspace/cv-cat`（DouYin_Spider、Spider_XHS、KuaiShou-Spider、XianYuApis 的材料分类）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 一个字段能算出来，只说明算法边界闭合。它能不能本地造，要先记账：本地状态机、服务端下发、隔离程序、设备绑定。缺了就失败或用缓存，不用随机串占位。随机串只能标 `unproven_synthetic`。

站点细节见 [抖音会话材料](./douyin-session-materials-case.md) 和 [小红书装配](./xiaohongshu-assembly-case.md)。

## 四类出处

| 出处 | 判定 | 允许的失败行为 |
|------|------|----------------|
| 本地可造 | 输入是时钟、计数器、本会话已有字段，规则稳定 | 按状态机生成。禁止每次 `random()` |
| 服务端下发 | 只出现在 Set-Cookie、响应头、HTML runtime | 缓存到 TTL。不能本地伪造 |
| 隔离程序 | 必须跑页面 JS / Node vm / 官方字节码才有值 | provenance 记 runtime。失败不降级成随机 |
| 设备绑定 | 与某次进程、某份 Cookie、某把私钥同源 | 换设备或换登录就要整组重采 |

小红书把这套写成六桶：`local_algorithm`、`reverse_alignment_override`、`managed_lifecycle_state`、`remote_program_or_anchor`、`server_issued`、`user_interaction`。`parameter_sources()` 只读暴露这张表。直接 `new Auth()` 被禁止，只能走 `from_cookie` / 扫码 / 短信，避免业务层「缺什么造什么」。

## 真实记账

| 字段 | 出处 | 源码里的门 |
|------|------|------------|
| 抖音 `msToken` | 服务端。`get_mstoken` 读 `x-ms-token` 或 Set-Cookie | 失败返回空串。旁边的 `generate_msToken()` 是长度 107 的本地随机，不是这条链 |
| 抖音 `__ac_signature` | 隔离程序。输入是 `__ac_nonce` + Cookie | strict 模式无签名就抛；非 strict 也不写入假值。成功 provenance 为 `node_page_js` |
| 抖音 ticket / `ts_sign` / 私钥 | 同一次登录 | `ticket_matches_session()` 失败则写接口不发 |
| 抖音 `x-tt-session-dtrait` | 会话内复用第一段，按 path 重算第二段 | `require_dtrait=True` 时生成失败则不发 |
| 小红书 `a1` / `webId` | 本地可造，但是有状态 | 允许算法生成，禁止每次随机 |
| 小红书 `web_session` | 服务端 | Cookie 登录缺它直接 `ValueError` |
| 小红书 `_dsl` | 远端锚。正则取 `getdss()`，TTL 300 秒 | 刷新失败且有缓存则用缓存，否则抛。不跑整段 VMP，也不随机 |
| 小红书 `websectiga` / Creator `_dsf` | 隔离程序 | 64 hex 或 16 字节程序输出。缺 `dsProgram` 直接失败 |
| 快手 `kwfv1` / `kwscode` | 隔离程序，但是本地脚本算的，不是 Set-Cookie 原文 | 必须用当次 `signUrl`。`kww` 头在初始化时冻结，后续 Set-Cookie 不得覆盖 |
| 闲鱼 Web `tfstk` | 隔离程序，`node gen_tfstk.js` | 失败不造随机 `tfstk` |
| 闲鱼 Web `_m_h5_tk` | 服务端。对照仓用空 sign POST 引导 | 业务 sign 用下划线前半段。空 sign 只属于引导，不属于业务请求 |
| 闲鱼 App `utdid` / `umid` | 设备绑定 | 必须与被 hook 的进程同源 |

## 账本伪代码

```text
class Ledger:
    buckets = {local, server, runtime, device, user}

record(name, bucket, ttl, source):
    assert bucket in buckets
    store(name, value=None, bucket, ttl, source)

resolve(name):
    item = ledger[name]
    if item.value and not expired(item):
        return item.value
    if item.bucket == local:
        item.value = state_machine(name)          # seq / count / clock
    elif item.bucket == server:
        item.value = from_cache_or_raise(name)    # never random
    elif item.bucket == runtime:
        item.value = run_isolated(name)           # provenance = runtime
        if not item.value:
            raise Missing(name)
    elif item.bucket == device:
        require same_process_or_same_login(item)
    return item.value

before_sign(required):
    for name in required:
        resolve(name)
    # 随机串若被留下，标记 unproven_synthetic，不能标 serverAccepted
```

## 怎么给新字段归类

1. 清 Cookie 再加载页面。字段消失或被 Set-Cookie 写回，就是服务端下发。
2. 字段只在跑完一段脚本后出现，响应里没有它，就是隔离程序。
3. 同一会话里多次请求，字段按计数器或时钟变，规则稳定，就是本地状态机。
4. 换设备或换私钥后整组头都变，就是设备绑定。
5. 两个函数同名时分开记账。`generate_msToken` 和 `get_mstoken` 不是同一出处。

TTL 跟浏览器缓存对齐。小红书 DS 的 300 秒来自 `cache-control max-age`，不是拍脑袋。过期后先刷新；刷新失败时，只有源码明确写了「回缓存」才允许用旧值，否则失败。

## 完成门

账本上每个业务请求用到的字段都有出处和失败行为。出现 `unproven_synthetic` 的请求不能记成 `serverAccepted`。本地复现出参只是 `localReproduced`。
