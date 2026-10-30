---
schema_version: 2
id: web-reverse-datadome-plv3-r-purecalc-reference
document_type: reference
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
  - id: s2
    ref: ./datadome-plv3-r-purecalc-case.md#algorithm-boundary
    basis: source-report
  - id: s3
    ref: ./datadome-plv3-r-purecalc-case.md#local-run
    basis: source-report
  - id: s4
    ref: ./products/datadome.md#常见链路
    basis: source-report
  - id: s5
    ref: ./products/datadome.md#观察优先级
    basis: source-report
  - id: s6
    ref: ./datadome-env-patch-reference.md#request-chain
    basis: source-report
  - id: s7
    ref: ./datadome-env-patch-reference.md#parameters
    basis: source-report
  - id: s8
    ref: ./datadome-plv2-plv3-detection-surface-reference.md#detection-patterns
    basis: source-report
  - id: s9
    ref: ./products/datadome.md#命中特征
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: source-report
    limits: 只整理笔记对当前样本正常路径的 fingerprint、header/key、RC4-like 与 Base64URL 分层，以及输入进入哪一层、能否离线。未抄常量表、样本 r 或诊断值。s1 无公开 locator，未复现。不覆盖笔记点名的其他 VM 分支，也不把 README 的对照升成 local-parity。不把 r 统称加密参数。
  - name: request-chain
    anchor: request-chain
    sources: [s1, s4, s5, s6, s7, s9]
    basis: source-report
    limits: 样本内计算链只整理笔记的主路径状态与四层；s1 无公开 locator，未复现。产品 HTTP 链只转述产品索引与补环境参考，不是这次反编译定位到的 URL、方法或 body 键。本次命令未联网。不把本地符号 r 与产品字段 plv3 写成已经绑定的同一发送点。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s8]
    basis: source-report
    limits: 只整理笔记对缺测和伪造读数的失败要求。s1 无公开 locator，未复现。不是服务端原因码，也不复制检测面 reference 的全量清单。不收录像素、UA 或硬件原值。
  - name: validation
    anchor: validation
    sources: [s1, s3]
    basis: source-report
    limits: README 的浏览器对照只是 source-report。本次命令只观察到测试计数、退出码、428 字节和哈希前缀；回执无公开 locator，本模块不升 runtime-observation、local-parity 或 server-accepted。未联网。不是全部 VM 已恢复。
relations:
  - type: derived_from
    target: ./datadome-plv3-r-purecalc-case.md#algorithm-boundary
  - type: supplements
    target: ./datadome-plv2-plv3-detection-surface-reference.md#collection-surfaces
  - type: supplements
    target: ./datadome-plv2-plv3-detection-surface-reference.md#detection-patterns
  - type: supplements
    target: ./products/datadome.md#常见链路
  - type: supplements
    target: ./products/datadome.md#观察优先级
  - type: supplements
    target: ./datadome-env-patch-reference.md#request-chain
  - type: supplements
    target: ./datadome-env-patch-reference.md#parameters
tags: [datadome, plv3, fingerprint, encryption, encoding, request-chain, risk-control, source-report]
---

# DataDome plv3 参数 r 的纯 Python 参考

这张卡分开写三件事。parameters 回答反编译样本里的符号 `r` 在笔记描述的正常路径上如何从显式浏览器原始输入算出，并把 fingerprint、initialization、encryption、encoding 分开，不把 `r` 统称加密参数。request-chain 把样本内计算链和产品 HTTP 链分成两份证据。risk-control 只写这条主路径的读数分组和缺测失败，不替换 [静态检测面](./datadome-plv2-plv3-detection-surface-reference.md#detection-patterns) 的全量类别，也不替换 [补环境参考](./datadome-env-patch-reference.md#request-chain) 的 jsdom 执行细节。落地范围与本次命令见 [案例](./datadome-plv3-r-purecalc-case.md#local-run)。

<a id="parameters"></a>
## 参数机制

生产入口只收浏览器原始环境值、真实渲染测量，以及初始化用的另一次时间、随机和 stack 读数。不收 `header8`、key、18 个已编码字段或寄存器快照。Python 不执行 JavaScript，也不用本机硬件去猜浏览器。

### fingerprint

主体之前有 5 个带种子 hash，种子分别是 `devicePixelRatio`、`XMLDocument.toString().length`（没有则为 0）、`navigator.hardwareConcurrency`、`getTimezoneOffset()`，以及进入主体前那一次 `Date.now()`。形式是 cyrb53：seed 先做 `ToUint32`，初值 `h1 = 3735928559 XOR seed`、`h2 = 1103547991 XOR seed`，按 UTF-16 码元做 `Math.imul`（乘数 2654435761 与 1597334677），收尾用已更新的 `h1`。渲染只用结果的低 32 位。这 5 个 hash 会进入后续 WebGL uniform 和 Canvas / CSS / SVG 的整数式；Python 只消费已经测到的像素和宽度，不光栅化。

`userEnv` 是 `window.ddm.userEnv` 的字符串，缺失则为空串。它不是 `navigator.userAgent`，也不属于上面 5 个 hash。

18 个字段按笔记的序列化顺序如下。值都是该次原始读数或由原始测量算出的整数，不是样例数值。

| 顺序 | 键 | 笔记中的来源类别 |
|---|---|---|
| 1 | `yd5T2w` | `navigator.webdriver` 原值，保留 undefined |
| 2 | `z663p3` | `window.Buffer` 是否为真 |
| 3 | `AkQPHP` | 该次 `Math.random()` |
| 4 | `tsPZLh` | `document.hidden` 是否为真 |
| 5 | `xByFeG` | 临时 DIV 的 `clientWidth`，不能写成固定 46 |
| 6 | `gkcP1m` | `isSecureContext` 原值 |
| 7 | `Gwzno0` | 私有 `_userAgent` 或 resourceLoader `_userAgent` 的短路真值，不是 UA 字符串 |
| 8 | `0y1S7e` | `_virtualConsole` 是否为真 |
| 9 | `fk2WVc` | `atob.toString()` 是否找不到 `[native code]` |
| 10 | `lnZy3p` | `location.pathname` |
| 11 | `lSCDpS` | `Date.now()` 与 `performance.timing.navigationStart` 的差 |
| 12 | `rp3b6b` | WebGL `readPixels` 的 4 字节小端 uint32；无上下文有哨兵 |
| 13 | `zKYJFA` | 第一组嵌套 DIV 的 `offsetWidth` |
| 14 | `SUQxGF` | 主体阶段那次 `performance.now()` |
| 15 | `NWDJDY` | console / Proxy ownKeys 探针之后的剩余长度是否为 0；缺测不能填 false |
| 16 | `o39gwE` | 第二组 CSS 变量布局的 `offsetWidth` |
| 17 | `PeNl8s` | Canvas 读回的绿/蓝通道与一个 hash 低 8 位的整数式 |
| 18 | `zibicJ` | 两次 `isPointInFill` 与路径 `getTotalLength` 的整数式；`Math.round` 是半数向正无穷 |

另有时钟字段 `ZKpWzq`，不计入这 18 个。字段键与源行的机器可读映射在主仓 `workspace/datadome-plv3-purecalc/stages/r-python/fingerprint-fields.json`。笔记点名的 language、另一套 native-code 比较、origin 等分支不是这 18 个键的定义。

### initialization

第二轮 8 个有符号 int32 种子来自独立读数，各自再 XOR 独立的随机 mask（`mask(r) = (r * 4294967295) | 0`）。种子来源是：`Date.now()`、一次辅助 `Math.random()`、数值化的 `new Date()`、`crypto.getRandomValues` 的首字节或回退、`hash31(Error.stack)`、`performance.now()` 或回退、`hash31(userEnv)`、`crypto.randomUUID()` 的 UTF-16 长度或回退。`hash31` 对 UTF-16 码元做 `((hash << 5) - hash + unit) | 0`。0 值的 `performance.now()` 和空串 UUID 是有效读数，不走回退。八个种子再 XOR 成洗牌用的 uint32。

洗牌吃一份 256 字节静态字面量（文件 `initialization-constants.json`，不是浏览器快照）。下标 0 到 254 做分段 xorshift 并交换，255 不动。header 的 8 个字节等于第一次洗牌后槽位 87、225、139、247、206、43、157、96 上的值；后面的固定置换会搬走它们，不改变这 8 个字节。完整移位表不抄入本文。

key 用的是零种子 cyrb53(`userEnv`)：初值就是 `3735928559` 与 `1103547991`，收尾同样先更新 `h1`。`seed53 = 4294967296 * (h2 & 2097151) + (h1 >>> 0)`。`key8[n] = header8[n] XOR` 该 53 位整数的大端 8 字节。header 与 key 只提供其一即可，不默认把空串 hash 当成普适常量。

### encryption

明文是无空白的紧凑文本：以 `{"ZKpWzq":` 加时钟的 JS 数字串开头，再按上表顺序拼接 18 个值。有限数用 binary64 最短十进制，负零为 `0`，NaN 与无穷为 `null`。不能用 Python 默认 `json.dumps` 的数字格式代替。字节化是笔记所称的 sample UTF-8：正常代理项配成四字节，未配对代理项保留三字节，不是严格 UTF-8。

流密码是样本专用 RC4-like。初始状态不是单位置换，完整 `S0` 在 `cipher-constants.json`。KSA 从 `j = 51` 起，第 n 步的下标是 `(98 + n) & 255`，加上 `key8` 的对应字节后交换。PRGA 从 `i = 211`、`j = 119` 起，先丢掉 123 字节，再与明文逐字节 XOR。不能调用标准 RC4 并当成同一算法。

### encoding

插入位置 `p = min(98, 密文长度)`。packet 是密文前 p 字节、8 字节 header、其余密文。`r` 是该 packet 的 Base64URL：`+` 换 `-`，`/` 换 `_`，去掉 `=`。笔记称这里没有额外校验和、MAC 或可变 IV。`r` 是这一步 encoding 的符号，不是 encryption 层的名字。

<a id="input-lifecycle"></a>
### 输入生命周期

生产入口不收 `header8`、key 或 18 个已编码字段。下表只回答每类输入进入哪一层、离线纯算能不能代替浏览器。token 在本样本里没有单独的提交字段；页面上的 `userEnv` 只按笔记的字符串用途写，产品侧的 cid / hash 角色见 request-chain，不提前并进来。

| 输入类 | 进入的层 | 离线边界 |
|---|---|---|
| 5 个渲染种子 | fingerprint。主体前对 `devicePixelRatio`、`XMLDocument.toString().length`（没有则为 0）、`navigator.hardwareConcurrency`、`getTimezoneOffset()`、进入主体前那一次 `Date.now()` 做 cyrb53，渲染只用低 32 位。这 5 个值进入 WebGL uniform 和 Canvas / CSS / SVG 的整数式。不是 encryption，也不是 token。 | 哈希变换可以离线算。种子必须是同一次浏览器读数。不能用 Python 主机的 DPI、线程数、时区或本地时钟代替。 |
| 18 个字段 | fingerprint。按上面的键序快照并序列化进紧凑明文。另有时钟 `ZKpWzq`，不在这 18 个里。 | 纯算只消费已经给出的原值或测量整数。Canvas、WebGL、两组 offsetWidth、clientWidth、SVG 或控制台长度缺测就失败，不能填默认像素或 false。Python 不光栅化。 |
| 第二轮 8 个种子与 mask | initialization。每个有符号 int32 种子 XOR 自己的 mask，再合成洗牌用的 uint32，只为选出 header。不定义那 18 个字段。 | 洗牌可以离线算。8 个读数和 mask 必须是另一轮独立的 random、clock、stack、uuid。0 和空串是有效读数。不能复用主体里那一次 `Math.random()` 或 `Date.now()`。 |
| 静态 S0 与洗牌字面量 | S0 进入 encryption，作为 RC4-like 的初始状态，不是单位置换。256 字节字面量进入 initialization 的洗牌表。两者都是源码字面量，不是某次浏览器快照，也不是 token。 | 常量可以离线使用。表留在主仓 JSON，不抄进本文。 |
| userEnv | 页面 `window.ddm.userEnv`，缺失则空串。它不是 5 个渲染种子，也不是 `navigator.userAgent`。initialization 用 `hash31(userEnv)` 做 8 个种子之一；encryption 的 key 用零种子 cyrb53(`userEnv`) 的 53 位整数与 header 逐字节 XOR。补环境参考把 env / userEnv 记成服务端下发的环境标识（token），没有给出 schema。 | 字符串给定后，两处哈希可以离线算。非字符串真值笔记明确不支持。不把空串哈希当成普适 key。 |

第一轮 `seed_material` 仍不在笔记所称的 `r` 依赖里，所以上表没有把它算进第二轮。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 5 个 hash 与 18 个字段来自显式浏览器读数和测量，键序如上。 | s1，fingerprint-spec 第 1–2 节；s2 | source-report | 笔记所称主路径 | 其他 VM 分支未并入；无样例值。 |
| C2 | header 来自第二轮 8 种子洗牌，key 为 header 与 userEnv 的 53 位 hash 大端字节的 XOR。 | s1，initialization-notes 与 cipher-notes 密钥节；s2 | source-report | 笔记所称正常初始化 | 第一轮种子不在该依赖内；移位表与 256 字节字面量不在本文。 |
| C3 | 流密码是非标准 RC4-like，参数为非单位 `S0`、KSA 起点 51、遍历 `(98+n)&255`、PRGA 初值 211/119、丢弃 123 字节。 | s1，cipher-notes 第 4 节；s2 | source-report | 该笔记中的样本编码 | 本轮未对照 VM 状态；标准 RC4 不等价。 |
| C4 | header 插在 `min(98, 密文长度)`，再做无填充 Base64URL。 | s1，cipher-notes 第 5 节；s2 | source-report | 同上 | 不收录样本 `r`。 |
| C8 | 五类输入按输入生命周期进入 fingerprint、initialization 或 encryption；离线只消费已给出的读数和静态字面量。 | s1，fingerprint-spec 第 1–2、9 节与 README 生产输入、算法分层；s2 | source-report | 笔记所称正常路径 | s1 无 locator，未复现。不能用主机参数代替浏览器读数。 |
| C9 | `r` 是 header 插入后的无填充 Base64URL 符号，属于 encoding。encryption 只指样本专用 RC4-like。不把 `r` 统称加密参数。 | s1，cipher-notes 第 4–5 节；s2 | source-report | 同上 | 不收录样本 `r`。产品字段名 plv3 的绑定见 request-chain，此处不预支。 |

<a id="validation"></a>
## 验证与限制

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | README 称 2 组自然浏览器记录、18 组熵重放、3 组独立采集器与 packet 和 `r` 一致。 | s1，README 已执行验证 | source-report | 笔记列出的本地夹具 | 本轮未重开夹具，不升 local-parity。 |
| C6 | 本次 unittest 20 passed，node test 17 pass，`r.py` 退出码 0，标准输出 428 字节，SHA-256 前 12 位 `914bff724dec`。 | s3 | runtime-observation | 该次回执中的三条命令 | 回执无公开 locator，故本模块 metadata 仍是 source-report；这不是浏览器对照。 |
| C7 | 回执为未联网，且 `serverAccepted=false`。 | s3 | runtime-observation | 该次回执 | 不能写成服务端接受，也不能写成全部 VM 已恢复。 |

缺测的 Canvas、WebGL、CSS、SVG 或控制台长度必须失败，不能填默认像素或 false。能力回退有笔记中的单元测试，自然路径的端到端证据不覆盖所有缺失组合。opaque 分支、被改写的 getter、CSP / Trusted Types，以及任意 JS 对象形态的 userEnv，笔记明确不做通用兼容。cipher-notes 仍把 header 上游标成当时未完成，与后来的 README 集成范围不同；428 字节输出没有单独证明 header 公式。静态检测类别继续以检测面参考为准。请求链缺口与风控分组见下文，不因这 428 字节改变。

<a id="request-chain"></a>
## 请求链路

这里有两条链，证据不是同一份。样本内计算链来自本地纯算笔记，停在符号 `r`。产品 HTTP 链只转述 [产品索引的常见链路](./products/datadome.md#常见链路) 和 [补环境参考的请求链](./datadome-env-patch-reference.md#request-chain)。不能把后者的 POST 写成这次反编译已经定位到的发送点。

### 样本内计算链

笔记把这条链放在样本内部，从原始读数走到符号 `r`。README 的四层是 fingerprint、initialization、encryption、encoding。下面按数据依赖写，不按文件名顺序。

1. fingerprint 的种子 hash。主体之前取 5 个种子，做 cyrb53，渲染只用低 32 位。`userEnv` 同时读出，但不算进这 5 个。
2. fingerprint 的渲染测量。这 5 个 hash 进入 WebGL uniform、Canvas / CSS / SVG 的整数式。Python 只接收已经测到的像素和宽度，不光栅化。
3. fingerprint 的 18 个字段。快照写入槽 818..835，再按 parameters 的键序序列化。时钟 `ZKpWzq` 另计，不在这 18 个里。
4. initialization。第二轮 8 个 int32 种子各自 XOR mask，洗牌那份静态 256 字节字面量，从第一次洗牌后的固定槽位取出 header8。key8 来自零种子 cyrb53(`userEnv`) 与 header 的 XOR。第一轮 `seed_material` 不在这条依赖里。
5. encryption。以 `{"ZKpWzq":` 加时钟的 JS 数字串开头，接上 18 个字段的紧凑明文，按 sample UTF-8 字节化，再用非标准 RC4-like 得到密文。初态是静态 `S0`，不是单位置换。
6. encoding。在 `min(98, 密文长度)` 插入 8 字节 header，做无填充 Base64URL。到这里才叫 `r`。

主路径状态号是笔记所称 `_global837` 的根状态 41，沿正常 API 走出的序列，不是 HTTP 状态：

`41→66→63→38→39→32→52→79→37→50→69→42→34→72→40→51→48→61→62→29→54→65→31→71→78→35→76→44→73→28→60→57→56→43→53→49→47→70→75→30→77`。

替代路径只作排除，不并进这 18 个键的定义：S46 用 language，S55 用 devicePixelRatio，S58 的 native-code 比较为 -36，S67 用 origin 且掩码和字符串算术不同，S64 使用 `Math.floor()`。尚未消除的条件仍是验证限制。

采集器不发请求、不写 cookie。fingerprint-spec 第 9 节写 `browser_fingerprint.js` 没有 fetch、XHR、WebSocket、导航、cookie 或本地存储写入，也不构造 token、不提交。README 写 `browser_inputs.generated.js` 不运行反编译产物，不生成 `r`，不发送请求，不读写 cookie 或浏览器持久存储。`scratch` 可以插入临时 DOM，也会消耗随机源和时钟；那是探针副作用，不是出站请求。

### 产品 HTTP 链

下面两条是产品索引与补环境参考的转述。字段角色用 [补环境参考的参数分层](./datadome-env-patch-reference.md#parameters)。三个 cid 的分法用 [产品索引的观察优先级](./products/datadome.md#观察优先级)。`view` 分叉同时对照 [命中特征](./products/datadome.md#命中特征)。这些段落描述的是保护页上的 HTTP，不是上一节的状态号。

interstitial 无感链，产品索引的顺序是：入口 403 / challenge 上下文 → `var dd` → GET `i.js` → GET `/interstitial/` → 目标 JS 生成 payload、plv3、ps → POST `/interstitial/` → 成功时响应 `view:"redirect"` 并带 datadome cookie → 带 cookie 回到原页面。补环境参考把同一条无感链写成：空 Cookie 的新 Profile 触发设备检查，入口 403 下发临时 datadome Cookie 和 Challenge 上下文，拼出 `/interstitial/` 取 Device Check HTML 和核心 JS，由原脚本自己触发 POST `/interstitial/`，`view=redirect` 且带 Cookie 之后，新建只含该 Cookie 的 Session 再访问业务页。该参考写明 `view=captcha` 表示升级到交互验证，自己不覆盖这条分支。产品索引的命中特征同时列出 `view:"redirect"` 与 `view:"captcha"`，并要求已经看到 `view:"captcha"` 时改走 captcha，不要继续盲补 interstitial。两种写法是同一处分叉，不是本样本里的两个状态号。

captcha 滑块链只按产品索引：入口 403 → `var dd(rt:"c")` → GET `c.js` → GET `/captcha/`，query 里带 initialCid、hash、cid、referer → iframe HTML 里生成 `var ddm` → 滑块或 audio 完成 → `window.captchaCallback()` → GET `/captcha/check` → 返回 datadome cookie → 带 cookie 回到原页面。补环境参考的 request-chain 不展开这条链。

字段角色按补环境参考的 parameters，不收成一个加密参数：

| 字段 | 该参考给的角色 | 类别 |
|---|---|---|
| payload | 环境采集写入内部容器后再编码的提交字段 | encoding（来源称加密结果，该参考不升格为 encryption） |
| plv3 | 与运行环境、布局和时间相关的另一段提交字段 | encoding |
| ps | 页面尺寸 | fingerprint / 布局，不能写死像素 |
| cid / hash | Challenge 页给出的动态配置 | token / 配置，每轮从当前页解析 |
| datadome cookie | 保护链通过后带回原页面的 Cookie | 与 cid 不是同一个字段 |

三个 cid 按产品索引分开：首页 403 里的 `dd.cookie`、captcha iframe 下发的 `ddm.cid`、最终通过后的 `datadome` Cookie。不要混成一个字段。

### 两链之间的缺口

本地笔记把算出来的符号叫做 `r`。产品索引用 `plv3` 指提交字段。本次整理对反编译产物 `decomplied.js` 检索了 `captcha-delivery`、`interstitial`、`jspl`、`XMLHttpRequest`、`datadome`，没有命中。因此这次反编译没有把 `r` 绑定到 URL、方法或 body 键。不能把产品索引里的 POST `/interstitial/` 或 GET `/captcha/check` 写成这个样本已经定位到的发送点。两套名字可以对照着读，不能并成同一条已证实的请求。本次归档命令未联网，也没有重开浏览器。字符串无命中只说明这份静态文本里没有这些字面量，不证明运行时不会拼出 URL；这个判断不升成 static-review。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 样本内计算链是种子 hash、渲染测量、18 字段快照/序列化、header/key、紧凑明文、RC4-like、header 插入、Base64URL。主路径状态号如上。采集器不发请求、不写 cookie。 | s1，fingerprint-spec 第 1、9 节；README 算法分层与独立采集 | source-report | 笔记所称正常路径与独立采集器 | s1 无 locator，未复现。采集顺序不是每条 VM 指令的时序。 |
| C11 | S46、S55、S58、S67、S64 只作为主路径字段定义的排除项。 | s1，fingerprint-spec 第 1 节 | source-report | 笔记点名的这些替代路径 | 未消除的条件仍是限制，不是已证明的死分支。 |
| C12 | interstitial 与 captcha 是产品索引和补环境参考里的两条 HTTP 链。payload、plv3、ps、cid/hash、datadome cookie 角色如上；`view=redirect` 与 `view=captcha` 分叉；三个 cid 不混。 | s4，s5，s6，s7，s9 | source-report | 这些文章所写的保护链 | 不是本样本的发送点定位。未复现 403 或 POST。 |
| C13 | 本地符号叫 `r`；产品索引用 plv3 指提交字段；本次反编译没有把 `r` 绑定到 URL、方法或 body 键。本次命令未联网。 | s1 的采集器契约；本次对 `decomplied.js` 的字符串检索无命中；对照 s4、s6 | source-report | 当前这份反编译产物与本次归档 | 无命中不等于证明运行时没有动态 URL。不升 static-review。 |

<a id="risk-control"></a>
## 风控

这里只写纯算笔记要求客户端读数怎样才算数、缺了必须怎样失败。不编服务端原因码。产品索引的命中特征提到响应里可以出现 `ir`，本笔记没有原因码表，本文不补。静态类别的全量清单仍是 [检测面 reference 的 detection-patterns](./datadome-plv2-plv3-detection-surface-reference.md#detection-patterns)：宿主对象与能力面，以及实现与计算面。下面五组只是这条 `r` 主路径上的读数分组，不是那篇清单的副本。

### 自动化与运行时

读 `navigator.webdriver` 的原值（`yd5T2w`，undefined 保持 undefined，不强转布尔）、`window.Buffer` 是否为真（`z663p3`）、`_virtualConsole` 是否为真（`0y1S7e`）、`atob.toString()` 里找不到 `[native code]`（`fk2WVc`）、顶层 `_userAgent` 或 resourceLoader `_userAgent` 的短路真值（`Gwzno0`）。`Gwzno0` 的完整短路是 `!!window._userAgent || !!(_resourceLoader && _resourceLoader._userAgent)`，不是 UA 字符串。`atob` 缺失或不是函数时，笔记写主块可能抛错；采集器记录错误，不捏造 false。

这组挡的是用主机参数猜一个正常浏览器：把 webdriver 填成 false，留下 Buffer、`_virtualConsole` 或私有 `_userAgent`，或换掉 atob 的原生代码形态。

### 渲染一致性

5 个 hash 进入 WebGL uniform，也进入 Canvas、CSS 和 SVG 的整数式。`xByFeG` 是临时 DIV 的 `clientWidth`，不能固定成 46；宽度 29px 加 padding 17px 只是名义参数，页面 CSS 和缩放才决定测量值。`zKYJFA` 与 `o39gwE` 是两组不同 DOM 的 `offsetWidth`。第二组名义上可写成 clamp / max 再加 26，笔记写明这不是布局等价式，Python 只能收测量宽度。WebGL 无上下文时主路径哨兵是 -1，另有条件分支不是这条成功读回；有上下文才把 `readPixels` 的 4 字节打成小端 uint32，不能按种子把读回换成代数结果。Canvas 的 `PeNl8s` 用实测绿/蓝通道和其中一个 hash 的低 8 位做整数式；像素经过 difference、路径和抗锯齿，不是填进去的 RGB 参数。SVG 的 `zibicJ` 用两次 `isPointInFill`、路径 `getTotalLength` 和 `Math.round`（半数向正无穷）。Canvas、WebGL、CSS、SVG 缺测必须失败，不能填默认像素。

这组挡的是常量像素或写死宽度：种子换了，读回却不变。

### 时间与熵

第二轮的 `Date.now()`、辅助 `Math.random()`、数值化的 `new Date()`、`crypto.getRandomValues` 首字节、`Error.stack`、`performance.now()`、`userEnv` 的 mask、`crypto.randomUUID()` 各自独立，再各自 XOR 自己的 mask。`performance.now()` 为 0、UUID 为空串，都是有效读数，不走回退。回退只在笔记写明的 API 不可用时发生。一个随机数不能填进所有 mask。主体阶段的 `Math.random()`、`Date.now()` 和 `performance.now()` 也不是这一轮。事后只采一份 UA 或屏幕，不能重放已经用过的随机、时钟和 stack。

这组挡的是复用旧随机、旧时钟或旧 stack，去配新的渲染测量。

### 文档状态

`tsPZLh` 读 `document.hidden` 的真值。`lnZy3p` 读 `location.pathname` 的原字符串。`gkcP1m` 读 `isSecureContext` 的原值，不用 `devicePixelRatio` 替换。

这组挡的是把页面猜成可见的安全上下文，或抄另一条路径。

### 控制台探针

`NWDJDY` 来自 `console.groupEnd` 触发 Proxy ownKeys 之后，数组剩余长度是否为 0。默认采集不调用这个探针，字段状态是 uncollected。缺测不能填 false、0 或 null。只有显式打开 console 探针且读到剩余长度，才由该长度推导字段。失败是 error，不写伪造长度。探针可能关掉控制台分组，检查也可能异步发生，笔记不承诺每个环境结果相同。

这组挡的是没有控制台检查却填 false，假装探针已经跑过。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C14 | 自动化/运行时读 webdriver 原值、Buffer、`_virtualConsole`、atob 原生代码形态，以及私有 `_userAgent` 短路。缺测或抛错不能填 false。 | s1，fingerprint-spec 第 1、9 节 | source-report | 笔记所称主路径上的这五个字段 | s1 无 locator，未复现。不是服务端原因码。 |
| C15 | 渲染一致性把 5 个 hash 送进 WebGL、Canvas、CSS、SVG。clientWidth 不能固定 46。两组 offsetWidth、WebGL 4 字节、Canvas 与 SVG 整数式都要实测。缺测失败，不填默认像素。 | s1，fingerprint-spec 第 3–5、7–9 节 | source-report | 同上 | 名义 CSS 式不是布局等价。Python 不光栅化。 |
| C16 | 时间与熵要求第二轮 random、clock、stack、uuid 各自独立。0 和空串是有效读数。不能复用主体那一次随机或事后的 UA/屏幕。 | s1 的边界；initialization-notes 第二轮；README 生产输入 | source-report | 笔记所称第二轮初始化 | 第一轮种子不在 `r` 依赖内。 |
| C17 | 文档状态读 `document.hidden`、`location.pathname`、`isSecureContext` 的原值。 | s1，fingerprint-spec 第 1 节 | source-report | 这三个字段 | 不替换成 devicePixelRatio 或另一条路径。 |
| C18 | 控制台探针 `NWDJDY` 缺测不能填 false、0 或 null。 | s1，fingerprint-spec 第 6、9 节 | source-report | 默认只读采集与显式探针 | 不承诺控制台状态可恢复。 |
| C19 | 以上是笔记要求的客户端失败方式，不是服务端原因码。全量检测类别仍以 detection-patterns 为准，本文不复制。 | s1；s8 | source-report | 本卡这五组与该检测面卡的阅读边界 | 未复现当前 DataDome 行为。`ir` 原因码本笔记没有，不补。 |
