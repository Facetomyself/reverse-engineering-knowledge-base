---
schema_version: 2
id: web-reverse-datadome-plv3-r-purecalc-case
document_type: case
original_date: unknown
archived_date: "2026-10-30"
scope:
  targets: [datadome]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: 本地笔记 README《浏览器原始输入 → 纯 Python `r`》，以及同目录 cipher-notes、initialization-notes、fingerprint-spec
    reason: 原材料在本地待审目录，未提供可公开定位的链接。
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录这次案例能支持的分层和离线边界。s1 无公开 locator，未复现。不把 r 统称加密参数，也不把产品字段 plv3 写成已绑定的发送点。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 这次命令只覆盖样本内计算链的离线入口。s1 无公开 locator，未复现。产品 HTTP 链不是本次反编译定位到的 URL、方法或 body 键。未联网。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只记录笔记要求的缺测失败和五组读数。s1 无公开 locator，未复现。不是服务端原因码，也不复制检测面全量清单。
tags: [datadome, plv3, r, purecalc, parameters, request-chain, risk-control, source-report]
relations:
  - type: supplements
    target: ./datadome-plv2-plv3-detection-surface-reference.md#collection-surfaces
  - type: supplements
    target: ./datadome-plv2-plv3-detection-surface-reference.md#detection-patterns
  - type: supplements
    target: ./datadome-plv3-r-purecalc-reference.md#parameters
  - type: supplements
    target: ./datadome-plv3-r-purecalc-reference.md#input-lifecycle
  - type: supplements
    target: ./datadome-plv3-r-purecalc-reference.md#request-chain
  - type: supplements
    target: ./datadome-plv3-r-purecalc-reference.md#risk-control
---

# DataDome plv3 参数 r 纯 Python 落地案例

## 问题与范围

这次只记录一件事：把已反编译样本上的 plv3 参数 `r`，用纯 Python 从显式浏览器原始输入算出来，并在本机离线跑过现有测试与入口。它不是 [静态检测面参考](./datadome-plv2-plv3-detection-surface-reference.md) 里的 API 清单，那篇写明没有可运行实现，依据是 source-report。也不是 [无感 interstitial 补环境](./datadome-env-patch-reference.md) 的 jsdom 跑原脚本。产品命中仍以 [DataDome 产品索引](./products/datadome.md#常见链路) 为准。

范围停在笔记所称的正常浏览器路径：调用方交出环境测量、时钟和随机读数，不交出 header、key 或 18 个已编码字段。样本版本笔记没有写成可核对的发行号，这里 version 保持 unknown。运行回执没有时间戳，observed_at 不用归档日代替。

<a id="algorithm-boundary"></a>
## 过程与关键证据

笔记把管道分成四层，不能统称加密：

- fingerprint：5 个带种子 hash，再排成 18 个字段。像素、宽度和 SVG 结果必须是浏览器测到的数。
- initialization：第二轮 8 个 int32 种子选出 header，再用 userEnv 的 hash 得到 key。第一轮 `seed_material` 不在笔记所称的 `r` 依赖里。
- encryption：样本专用 RC4-like，不是标准 RC4。
- encoding：在密文中插入 8 字节 header，再做无填充 Base64URL。

常量表留在主仓相对路径 `workspace/datadome-plv3-purecalc/stages/r-python/` 的 `cipher-constants.json`、`initialization-constants.json` 和 `fingerprint-fields.json`，不抄进本文。诊断 JSON、样本输入、`r` 正文、cookie、UA 和硬件原值也不进入本文。

cipher-notes 自己的限制仍写 header 的上游不在那份编码笔记里；后来的 README 把 `initialization.py` 放进同一入口。这是笔记之间的范围差，不是本轮新证明的冲突。fingerprint-spec 写明当时只闭合输入来源，不单独等于整条 `r` 等价。

<a id="local-run"></a>
## 本次命令

回执只允许记下列事实。unittest：20 passed，失败 0。node test：17 pass，失败 0。`r.py`：退出码 0，标准输出 428 字节，SHA-256 前 12 个十六进制字符 `914bff724dec`，标准错误为空；正文按回执省略，这里不重放。回执记录未联网，`serverAccepted` 为 false。

这些是本次进程的退出状态和输出长度，不是与浏览器 oracle 的逐字节对照，所以不是 local-parity。回执不在 Public 文章仓库里，不能当作可定位来源把 v2 模块升成 runtime-observation。README 里“2 组自然浏览器记录、18 组熵重放、3 组独立采集器与 packet/`r` 一致”仍只是 source-report；本轮没有打开那些夹具。

<a id="parameters"></a>
## 参数

这次案例能支持的判断停在笔记的入口合同：调用方交的是 environment 里的原始读数，加上 initialization 里的另一轮时间、随机和 stack，不是 header、key 或 18 个已编码字段。笔记把管道分成 fingerprint、initialization、encryption、encoding。`r` 只是最后无填充 Base64URL 的符号，不是统称的加密参数。本次 `r.py` 退出 0、标准输出 428 字节，只说明这条入口在回执那次跑完，不说明缺掉的浏览器读数可以用主机参数补上。

能分开的输入是：

- 5 个渲染种子和 18 个字段进 fingerprint。像素、宽度和 SVG 必须是测到的数。
- 第二轮 8 个种子和各自的 mask 只进 initialization，用来选出 header。
- 静态 S0 进 encryption，洗牌字面量进 initialization。两者都是源码字面量，不是浏览器快照。
- `userEnv` 是页面 `ddm.userEnv` 的字符串。它参与 key 的哈希，不是 `navigator.userAgent`，也不是那 5 个种子。

离线纯算可以做哈希、洗牌、RC4-like 和 Base64URL。Canvas、WebGL、CSS、SVG 或控制台长度缺测就必须失败。同一条缺口是：本地符号叫 `r`，产品索引用 plv3 指提交字段，这次反编译没有把 `r` 绑到 URL、方法或 body 键。键序、公式和生命周期表见 [参数机制](./datadome-plv3-r-purecalc-reference.md#parameters) 与 [输入生命周期](./datadome-plv3-r-purecalc-reference.md#input-lifecycle)。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 这次案例只支持「显式原始输入进四层、`r` 属于 encoding」；428 字节不证明主机参数可以代替浏览器读数。 | s1，README 生产输入与算法分层 | source-report | 笔记所称正常路径入口 | s1 无 locator，未复现。不升 local-parity。 |

<a id="request-chain"></a>
## 请求链路

这次案例能支持的是样本内计算链的离线一半。回执里的命令没有联网，`serverAccepted` 为 false。笔记里的独立采集器不发请求、不写 cookie，也不生成 `r`。从种子 hash、渲染测量、18 字段快照/序列化，到 header/key、紧凑明文、RC4-like、header 插入和 Base64URL，步骤与主路径状态号写在参考里。S46、S55、S58、S67、S64 在笔记里只是排除项，这次案例没有把它们收成另一条已跑通的链。

这次案例不能支持的是产品 HTTP 链已经在样本里找到发送点。interstitial 的 POST `/interstitial/` 和 captcha 的 GET `/captcha/check` 来自产品索引和补环境参考。payload、plv3、ps 是不同角色的提交或布局字段，cid/hash 是当轮配置，datadome cookie 不是这三个 cid 里的任何一个。`view=redirect` 与 `view=captcha` 是保护链分叉，不是本样本的状态号。

同一条缺口：整理时对反编译产物检索 `captcha-delivery`、`interstitial`、`jspl`、`XMLHttpRequest`、`datadome` 没有命中，没有把 `r` 绑定到 URL、方法或 body 键。不能把产品索引的 POST 写成这次已经定位到的发送点。两条链的对照见 [请求链路](./datadome-plv3-r-purecalc-reference.md#request-chain)。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 这次离线命令只支持样本内计算链跑完；产品 HTTP 链不是本次定位到的发送点。 | s1 的采集器契约；本次回执未联网；字符串检索无命中 | source-report | 该次回执与当前反编译文本 | 无命中不升 static-review。未复现 403 或 POST。 |

<a id="risk-control"></a>
## 风控

这次案例能支持的是笔记自己的失败规则，不是服务端原因码，也没有 `ir` 码表。缺测的 Canvas、WebGL、CSS、SVG 或控制台长度必须失败，不能填默认像素或 false。五组只列这次案例用到的分界：自动化/运行时保留 webdriver 的 undefined，并检查 Buffer、`_virtualConsole`、atob 原生代码和私有 `_userAgent` 短路；渲染一致性拒绝固定 clientWidth 46，也拒绝与 5 个 hash 脱节的常量像素和两组 offsetWidth；时间与熵要求第二轮 random、clock、stack、uuid 独立，0 和空串仍是有效读数；文档状态读 hidden、pathname、isSecureContext 的原值；控制台探针 `NWDJDY` 缺测不能填 false。

本次命令没有重开那 2 组自然记录或 18 组熵重放，所以测试计数通过不能写成这些伪造已经在服务端被挡住。检测类别全量仍见 [detection-patterns](./datadome-plv2-plv3-detection-surface-reference.md#detection-patterns)。分组和缺测条件见 [风控](./datadome-plv3-r-purecalc-reference.md#risk-control)。

同一条缺口：这些读数分组没有变成一条已定位的 HTTP 发送点。`r` 仍只是本地符号。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 这次案例只支持笔记写明的五组缺测失败；不支持服务端原因码或全量检测清单。 | s1，fingerprint-spec 第 1、6、9 节与 README 明确边界 | source-report | 笔记所称正常路径的缺测契约 | s1 无 locator，未复现。本轮未重开夹具。 |

## 结论与反例

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 笔记给出从显式原始输入到 `r` 的纯 Python 分层，并称正常路径已对照本地记录。 | s1，README 交付与已执行验证 | source-report | 笔记所称的当前样本正常路径 | 作者自述；本轮不升 local-parity。 |
| C2 | 本次三条本地命令按上节计数通过或退出 0；输出 428 字节，哈希前缀如上。 | 本次离线回执 | runtime-observation | 该次回执里的命令 | 无公开 locator，案例不设更高 basis 的模块；不是服务端接受。 |
| C3 | 反例：未联网，`serverAccepted=false`；不是全部 VM 或全部异常分支已恢复。 | 本次回执；s1 明确边界 | source-report | 该次回执与笔记自述边界 | 不能从 428 字节推出服务端会接受。 |

## 未决项与复用启示

未决的是：笔记没有公开版本号；GPU、Canvas、CSS、SVG 和控制台读数仍要目标浏览器实测，不能用 Python 主机参数代替；能力缺失的组合笔记称只有单元测试、没有自然路径端到端。可复用的分层、两条链和五组失败规则见 [参数](./datadome-plv3-r-purecalc-reference.md#parameters)、[请求链路](./datadome-plv3-r-purecalc-reference.md#request-chain) 和 [风控](./datadome-plv3-r-purecalc-reference.md#risk-control)。检测面文章继续只回答静态类别，不因本篇改成已复现。
