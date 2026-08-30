# 小红书 x-s / x-t / x-s-common

> 来源: `workspace/cv-cat`（Spider_XHS 2026-08-18 只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-08-30
> 分类: web-reverse
>
> 小红书 PC Web 与创作者平台的签名头族：`x-s`、`x-t`、`x-s-common`、`b1`、mns 档位与 ds 锚点。文档只给命中特征、材料出处和观察顺序，不收录 mns keystream、自定义字母表或可执行签名器。

## 命中特征

- 业务域 `edith.xiaohongshu.com`；创作者域 `creator.xiaohongshu.com`；安全域 `as.xiaohongshu.com`
- 请求头出现 `x-s`（`XYS_` 前缀）、`x-t`、`x-s-common`；部分路径还有 `x-rap-param`、`x-b3-traceid`、`x-xray-traceid`、`xy-direction`
- Cookie 出现 `a1`、`web_session`、`webId`、`webBuild`、`loadts`、`gid`、`websectiga`、`sec_poison_id`
- 脚本或栈出现 `seccore_signv2`、`mns0101_` / `mns0201_` / `mns0301_`、`XsCommon`、`getdss`、`_$c` / Sabo VMP
- ds 接口：`/api/sec/v1/ds?appId=xhs-pc-web` 或 `appId=ugc`，响应是混淆 JS，明文含 `function getdss() { return '<13位时间戳>'; }`

算法权威在现行 `xhs_core` / `xhs_pc` / `xhs_creator` 分层。2026-04 的 `execjs` + `xhs_main_260411.js` 快照是旧 XsCommon（`x8` 静态 blob、无 `x12=dsl`），不能当现行签名。

## 常见链路

```text
Cookie 必须含 a1；登录态还要 web_session（服务端发，本地不能造）
→ 会话态：loadts / webBuild / ets / seq / envConst
→ b1：19 字段指纹快照（冷登录允许空）
→ dsl_pair = dsllt ; _dsl
     dsllt = 本地 Date.now()
     _dsl  = ds 接口 getdss()，TTL 与 cache-control max-age=300 对齐
→ mns 按档位打出 x3
→ x-s = XYS_ + 自定义编码(JSON {x0..x4})，x3 即 mns 串
→ x-t = mns 算完后再采的 Date.now()
→ x-s-common 含 x5=a1、x8=b1、x10=signCount、x12=dsl_pair
→ 旁路头 x-b3-traceid / x-xray-traceid 不进 mns 明文
```

PC 档位（指纹是否就绪决定）：

| 状态 | 接口面 | 档位 |
|------|--------|------|
| 指纹未就绪 | `/api/sec/v1/*`、验证码、sem | mns0201 |
| 指纹未就绪 | 内容接口 | mns0101 |
| 指纹就绪 | 全部 | mns0301 |

Creator：`appId=ugc`，无 0301。非 bootstrap 的 mns0101 必须把服务端 DS 程序交给隔离 `vm` 跑 `_dsf`（16 字节），不能只用本地 ARX。蒲公英只要 `x-s` / `x-t`，不造 `x-s-common`。千帆模板往往只有 traceid，不走 xs 族。

`websectiga` 是服务端下发的 JSVMP，最小宿主执行后写入 Cookie，不是零宿主纯算。

## 观察优先级

1. 先定请求边界再拆算法：普通签名 / RAP / `xy-direction` / 安全域 0201 / 蒲公英无 x-s-common，头序不同。
2. 确认 `x-s` 是否 `XYS_` 前缀，`x-s-common` 是否带 `x12=dsllt;_dsl`。缺 `x12` 就是旧代 XsCommon。
3. 分清材料出处：`a1` 本地可造；`web_session` / `gid` / `sec_poison_id` / captcha 不能本地造；`_dsl` 从 ds 接口正则提取，不跑 Sabo VMP。
4. PC 与 Creator 不要混：`xhs-pc-web` + `a3` + 0301 ≠ `ugc` + `a1` + 无 0301。
5. `seq` / `signCount` / `loadts` 是会话计数，禁止每次随机。
6. 传输层：TLS impersonate 与 Chrome Client Hints 头序单独验收。

## 常见坑

- 用旧 `execjs` 包或静态 `fff` 当 `x8`，对不齐现网 `x12=dsl`
- 把 ds 响应整段 VMP 当必须执行；生产路径通常只取 `getdss()`
- 混用 PC / Creator 的 appId、档位、profile 模板
- 只生成三个 x-* 头，忽略 RAP 白名单、`xy-direction`、头序和 HTTP/2
- 把 RAP / mns 的 keystream 与 AES 常量当跨版本稳定协议
- 运营台或 Agent skill 封装当成算法源；算法只认现行 `xhs_core`

## 验证口径

- 目标接口返回业务 JSON，而不是验证码、登录失效或安全域 0201 死循环
- 记录当前 `appId`、mns 档位、`dsl` 缓存时刻、`signCount`、是否带 RAP
- `websectiga` / `_dsf` 失败时记 runtime-pending，不得用随机 Cookie 顶替

落地选型见 [平台签名落地方法](../sign-landing-methods.md)。
