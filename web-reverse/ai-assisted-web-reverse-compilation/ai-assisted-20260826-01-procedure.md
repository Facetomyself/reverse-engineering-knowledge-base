---
schema_version: 2
id: grok-web-reverse-ai-assisted-20260826-01
document_type: procedure
original_date: "2026-08-26"
archived_date: "2026-10-02"
scope:
  targets: [shein-x-gw-auth]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ai-assisted-20260826-01.md#五决胜一招把它扣进空白页给它插一行日志"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 d 的改判。不记录摘要原值，也不把 canvas 库写成 d 的输入。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留来源写出的字段角色、canonical 模板和占位 key 形状。SECRET 与 APP_ID 不在来源正文里。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 步骤只整理来源已经写出的定位分支。不补脚本、偏移或请求。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 逐字节和返回码都是作者自述。本轮没有重写签名，也没有发请求。
relations:
  - type: derived_from
    target: "./ai-assisted-20260826-01.md#五决胜一招把它扣进空白页给它插一行日志"
tags: [shein-x-gw-auth, wasm2js, hmac]
---

# shein x-gw-auth 的来源定位流程

这份流程只回答来源自己如何把网关头 `x-gw-auth` 从“钩子够不到”收到“占位 SECRET 的 HMAC 形状”。它不提供签名器，不记录摘要或密钥原值，也不把作者对返回码的自述当成当前结果。`../../signature-algorithms/shein-random-md5-trace.md` 的目标是另一条 random 参数，不覆盖这个头。

<a id="risk-control"></a>
## 来源纠正过的 d

来源先把跨会话稳定、与 URL 无关的 d 当成设备指纹，并看到模块里有 canvas 采集。quote: d 跟 URL 无关。后文改判：d 是一个写死字符串的 MD5，canvas 库与 d 无关。quote: d = md5("unknown:unknown")。等号后的摘要不进入本卡。把“稳定”和“附近有指纹代码”当成 d 的算法，是这条来源写明的失败判断。

<a id="parameters"></a>
## 字段角色

来源把头写成四段。quote: x-gw-auth = a=<appId@版本> & b=<毫秒时间戳> & d=<32位hex> & e=<5字符前缀 + base64(64位hex)>。a 是抄一次的 bundle 标识，b 是毫秒时间戳。送入后段哈希的串被写成四项模板。quote: canonical = "x-app-id={appId}&timestamp={ts}&url={url}&client-id={d}"。key 的形状是占位 SECRET 再拼 5 字符盐，盐同时是 e 的前缀。quote: key = SECRET(30字符) + 盐(5字符)。来源声明关键常量以占位代替，不提供成品签名器。quote: 不提供成品签名器。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 签名 bundle | 来源称它自包含，自己带 wasm 数据并往 window 挂函数 | 不是自包含就走 F2，本流程没有第二套加载方法 |
| 空白页 | 用来加载抠出的 bundle，而不是在原页单步 | 单步崩页时停止，不改成别的调试器步骤 |
| 运行时脚本 | new Function 或 eval 在编译时能落盘 | 落不下脚本就停在 F1 |
| 对照样本 | 来源用真实签名器输出和浏览器产出的签名做对照 | 没有样本就不能做下面的验收 |
| 常量 | SECRET 与 APP_ID 在归档里是占位 | 缺占位以外的材料时走 F2，不把占位当成 key |

<a id="steps"></a>
## 步骤与分支

下表只整理来源已经写明的顺序。不补编译偏移，不补请求。

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 点式钩子停在三层动态编译外面时，转储运行时生成的脚本，再在请求拦截器里找入口 | 来源称入口是一个等待 wasm 实例化的全局函数，输入是相对 path。quote: 三层动态编译（embind→new Function→wasm2js）够不到，就 dump 运行时脚本找入口 | 找到入口走 S2，否则 F1 |
| S2 | 用不同 URL 和同一 URL 的两次调用分开 d 与 e，并读 orchestrator 的四项输入 | d 不随 URL 变，e 随时间变。canonical 为上表模板 | 四项对得上走 S3，否则 F2 |
| S3 | 若 d 像设备指纹，先读赋值，而不是去逆 canvas | 来源改判为固定字符串的 MD5 | 改判成立就不再为 d 逆采集库，并进入 F1 判断暴力是否已经失败。改判不成立走 F2 |
| S4 | 可观测 key 的暴力已经 0 命中后，把 bundle 放进空白页，只在 SHA-256 变换处看 64 字节块 | 尾部全 0x36 被来源认成 ipad。quote: 某个块 ⊕ 0x36，尾部全是 0x36 | 认不出 ipad 走 F2。认出后只记录占位 key 形状，不在本卡填 SECRET |

S3 成立只说明 d 不再按设备指纹处理。暴力 0 命中仍是 F1，只有 F1 允许时才进入 S4。

<a id="outputs"></a>
## 输出

交付的是来源文本里的形状，不是签名结果：四字段角色、canonical 模板、d 为固定字符串的 MD5、e 为 5 字符盐加一段 base64，且 key 被写成占位 SECRET 拼同一盐。不交付摘要十六进制、SECRET、APP_ID、样例 URL 或可运行实现。

<a id="acceptance"></a>
## 验收

来源自己的通过句是：三个不同盐的样本与真实签名器输出逐字节一致。quote: 3 个不同盐的样本 3/3。来源还称用提取出的 SECRET 核过浏览器产出的签名。这两句都只证明作者如此报告。来源另称离线签名直接发出后得到业务数据。quote: 服务端返回 200 + 真实数据（推荐流、搜索、ABT 配置等）。本轮没有签名样本，没有发请求，所以这些句子都不是本卡的通过结果。缺样本、缺占位以外的 SECRET，或只做到自签自比，都走 F2。

<a id="failure-exits"></a>
## 失败出口

F1：点式钩子进不到签名代码，或可观测材料上的暴力全部不中。quote: 全部 0 命中。此时停止继续枚举可观测字符串。只有运行时脚本已经落盘、并且空白页能跑到哈希变换时，才回到 S4；否则停止，不改写算法。

F2：单步编译码崩页、空白页不是自包含 bundle、SECRET 仍只有占位、或者需要补来源没有写出的接口与请求。停止相关结论。作者的返回码不能用来填这些缺口。来源已写不提供成品签名器。quote: 不提供成品签名器。
