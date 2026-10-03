---
schema_version: 2
id: grok-anti-detection-benru-anti-20260206-01
document_type: procedure
original_date: "2026-02-06"
archived_date: "2026-10-02"
scope:
  targets: [curl_cffi, curl-impersonate]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-anti-20260206-01.md#四如何使用curl_cffi模仿chrome"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 TLS 握手差异的描述。没有 ClientHello 样本，也没有指纹原值。
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: impersonate 取值和安装命令都是来源文本。未核对当前库还接受哪些档名。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 步骤只整理来源已经写出的 TLS 回显检查。不扩展会话、口令或零售页抓取。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 验收句子是作者自述。本轮没有请求 tls.browserleaks.com，也没有请求作者举的零售页。
relations:
  - type: derived_from
    target: "./benru-anti-20260206-01.md#四如何使用curl_cffi模仿chrome"
tags: [curl_cffi, curl-impersonate, ja3]
---

# curl_cffi 的 impersonate 与 JA3 字段检查

这份流程只回答：来源自己如何描述 curl_cffi 的安装前提、`impersonate` 参数，以及它用什么字段声称 TLS 模拟成立。它不提供新的抓取脚本，不记录指纹原值，也不把作者对零售页标题的自述当成当前结果。百家号参考卡虽然关键词里有 curl_cffi，目标是 baijiahao，不覆盖这个库的参数。

<a id="risk-control"></a>
## 来源所称的识别面

来源写，普通 Python HTTP 客户端即使改了 User-Agent，TLS 握手特征仍与真实浏览器有明显差异。quote: 握手特征仍与真实浏览器有明显差异。它把 TLS 指纹放在握手阶段，内容是客户端支持的加密套件和扩展列表，而不是一个已给出的哈希原值。quote: 包含了客户端支持的加密套件、扩展列表等信息。库的差异被写成精确模拟 TLS 签名和 JA3，底层是 curl-impersonate。quote: 其底层基于 curl-impersonate。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| Python | 3.8 或以上。quote: 确保你的 Python 版本在 3.8 或以上 | F1 |
| 包 | `pip install curl_cffi --upgrade`。quote: pip install curl_cffi --upgrade | 导入失败走 F1，不把未导入当成模拟成功 |
| 模拟档 | 具体档 `impersonate="chrome110"`，以及 `safari15_5`、`edge101`、`chrome99_android` 等来源点名的档名。quote: impersonate="chrome110" | 档名不在来源点名范围内时，本流程没有依据 |
| 回显地址 | 来源用 `"https://tls.browserleaks.com/json"` 读 JSON。quote: "https://tls.browserleaks.com/json" | 没有这份 JSON 就不能做下面的字段验收 |

来源还写预编译包通常覆盖 Linux、macOS 和 Windows。这是作者的安装说明，不是本轮环境清单。

<a id="steps"></a>
## 步骤与分支

下表整理来源已经写明的检查顺序，不补请求体，也不把后文的会话示例收成步骤。

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 核对 Python 版本并按来源命令安装 curl_cffi | 能否导入 | 能导入走 S2；导入失败走 F1 |
| S2 | 按来源对 TLS 回显地址发 GET，并带上点名的 impersonate 档 | 响应是否为 JSON | 有 JSON 走 S3；没有 JSON 走 F2 |
| S3 | 只看来源点名的 `ja3n_hash` 字段是否出现 | 字段有无 | 字段出现则进入验收；字段缺失走 F2 |

来源后文还有 Session、POST 和 AsyncSession 示例。那些例子里的演示口令和演示会话路径不进入本流程。零售页示例只留在输出和失败出口里，作为作者自述，不单列成要执行的抓取步骤。

<a id="outputs"></a>
## 输出

TLS 检查的交付是回显 JSON 里是否出现 `ja3n_hash`。quote: ja3n_hash。来源没有给出该字段的原值，本卡也不补。

作者另举了一个零售搜索页，URL 为 `"https://www.walmart.com/search?q=keyboard"`，并在代码注释里写成功时打印 `成功输出：Electronics - Walmart.com`。quote: 成功输出：Electronics - Walmart.com。这是作者自述的标题，不是本轮输出。

<a id="acceptance"></a>
## 验收

| 编号 | 通过条件 | 反例 |
|---|---|---|
| A1 | 来源写：模拟成功时，`ja3n_hash` 与真实 Chrome 110 完全一致。quote: 如果模拟成功，这个哈希值将与真实的 Chrome 110 | 本轮没有浏览器对照，不能把 A1 勾成已通过 |
| A2 | 作者把零售页标题 `Electronics - Walmart.com` 写成成功输出 | 去掉 impersonate 时，作者写标题很可能是 “Robot or human?”。quote: 不加该参数，返回的标题很可能是 “Robot or human?” |

A1 和 A2 都停在 source-report。编辑上能对上引文，不等于技术验收已经发生。

<a id="failure-exits"></a>
## 失败出口

F1：导入失败时，来源把最常见原因写成缺少 libcurl 开发文件。quote: 如果安装后导入库失败，最常见的原因是系统缺少 libcurl 的开发文件。作者只给了 Ubuntu 或 Debian 的 `sudo apt-get install libcurl4-openssl-dev`。quote: sudo apt-get install libcurl4-openssl-dev。其他系统没有对应命令；命令未执行成功就停止，不继续声称指纹一致。

F2：来源写，去掉 impersonate 通常会得到反爬页面。quote: 如果此处移除 impersonate 参数，通常会得到反爬页面。回显 JSON 缺失，或 `ja3n_hash` 不出现时，同样停止，不把请求发出本身当成通过。

F3：材料只剩会话、POST 或异步示例，或者只剩零售页标题注释时，不把它升级成 TLS 验收。演示用的口令和会话路径不抄录，也不再补。
