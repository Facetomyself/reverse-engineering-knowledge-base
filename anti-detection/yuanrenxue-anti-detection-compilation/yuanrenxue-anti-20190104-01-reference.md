---
schema_version: 2
id: grok-anti-detection-yuanrenxue-anti-20190104-01
document_type: reference
original_date: "2019-01-04"
archived_date: "2026-10-02"
scope:
  targets: [requests, chardet, cchardet]
  client: python
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-anti-20190104-01.md#不要相信requests返回的text"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 ISO-8859-1 回退和 GB2312、GBK、GB18030 字数关系的陈述。函数体在截图中，未对照 requests 或 chardet 源码，也没有库版本。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 两步是来源描述的编码获取顺序。未运行 requests，不把该顺序当成当前版本的行为。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源点名的函数、属性，以及 cchardet 对 uchardet 的绑定关系。不提供调用脚本。示例站点未在本轮请求。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 「镕」字实验、chardet 返回值和 GitHub issue 编号都是作者自述。本轮没有复跑，也没有打开这些 issue。
relations:
  - type: derived_from
    target: "./yuanrenxue-anti-20190104-01.md#不要相信requests返回的text"
tags: [requests, chardet, cchardet, encoding]
---

# requests 文本解码把中文解乱的来源边界

这张卡只回答：来源如何描述 `requests` 取得 `response.encoding` 的两步，为什么它说 `chardet` 把国标中文只报成 GB2312，以及它建议用 `cchardet` 检查 `response.content` 而不是直接用 `response.text`。不提供抓取脚本。函数体在截图里，本卡不补写。库版本未知。作者对示例页面和「镕」字实验的结果保持为来源陈述。

<a id="parameters"></a>
## 编码回退与国标范围

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `response.text` 按 `response.encoding` 解码，来源认为这个编码的获取有问题。quote: 通过response.text可以得到解码后的文本数据，解码是根据response.encoding进行的。 | s1 ./yuanrenxue-anti-20190104-01.md:42 | source-report | requests 的 text 与 encoding | 未运行 |
| C2 | 来源读 utils.py 截图后的结论是：Content-Type 包含 text 就被当成 ISO-8859-1，并认为该想法不严谨。quote: 它认为headers里面的‘Content-Type’包含‘text’就是‘ISO-8859-1’编码。 | s1 ./yuanrenxue-anti-20190104-01.md:52 | source-report | get_encoding_from_headers 的来源描述 | 最后两行代码未转写 |
| C3 | 来源用来对照的正规写法带 charset。quote: Content-Type: text/html; charset=UTF-8 | s1 ./yuanrenxue-anti-20190104-01.md:64 | source-report | 来源给出的头格式示例 | 不是抓到的响应原文 |
| C4 | 来源称因此得到 ISO-8859-1，再用它解中文会乱码。quote: ISO-8859-1的编码，再用这个编码去解码中文，当然就会出现乱码。 | s1 ./yuanrenxue-anti-20190104-01.md:67 | source-report | 来源举的中文页 | 本轮未请求该页 |
| C5 | 来源称 chardet 对国标中文只返回 GB2312，而国标还有 GBK 和 GB18030。quote: chardet对国标中文编码返回的就是（只是）GB2312。 | s1 ./yuanrenxue-anti-20190104-01.md:91 | source-report | chardet 的国标检测 | grep 输出在截图中，未复跑 |
| C6 | 来源把三种国标编码的汉字个数写成 GB2312 < GBK < GB18030。quote: GB2312 < GBK < GB18030 | s1 ./yuanrenxue-anti-20190104-01.md:101 | source-report | 来源陈述的字集大小 | 未核对标准文本 |
| C20 | 来源写 GB 2312 标准共收录 6763 个汉字。quote: GB 2312 标准共收录 6763 个汉字 | s1 ./yuanrenxue-anti-20190104-01.md:93 | source-report | 来源陈述的字集大小 | 未核对标准文本 |
| C21 | 来源写共收入 21886 个汉字和图形符号，并写兼容GB2312。quote: 共收入 21886 个汉字和图形符号，兼容GB2312 | s1 ./yuanrenxue-anti-20190104-01.md:95 | source-report | 来源陈述的字集大小 | 未核对标准文本 |
| C22 | 来源写 GB 18030 与 GB 2312-1980 和 GBK 兼容，共收录汉字70244个。quote: 共收录汉字70244个 | s1 ./yuanrenxue-anti-20190104-01.md:97 | source-report | 来源陈述的字集大小 | 未核对标准文本 |

<a id="decision-flow"></a>
## 两步取编码

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 第一步是从 HTTP 响应头里找编码。quote: 第一步：从http返回的headers里面找编码。 | s1 ./yuanrenxue-anti-20190104-01.md:46 | source-report | requests 编码获取的来源描述 | 未对照当前版本 |
| C8 | 第二步是头里得不到编码时，用 chardet 从二进制 content 猜测。quote: 如果不能从响应headers得到编码，就用chardet从二进制的content猜测 | s1 ./yuanrenxue-anti-20190104-01.md:69 | source-report | 头里没有编码时 | 来源把这一步的责任主要记在 chardet |

来源写明第二步的编码问题严格说不是 requests 的，而是 chardet 的，只把 requests 记为失察。两步都依赖截图中的实现，正文没有分支或失败出口，所以不立成 procedure。

<a id="interfaces"></a>
## 函数、示例页与替代检测

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | 第一步被定位到 utils.py 的 get_encoding_from_headers(headers)。quote: 这一步的代码在源文件utils.py里面是get_encoding_from_headers(headers)函数 | s1 ./yuanrenxue-anti-20190104-01.md:48 | source-report | requests 源文件名来自作者 | 函数体未转写 |
| C10 | 来源把示例中文页写成 http://epaper.sxrb.com/ ，并称其 Content-Type 不是上面的正规格式。quote: http://epaper.sxrb.com/ | s1 ./yuanrenxue-anti-20190104-01.md:56 | source-report | 该文举的一个页面 | 响应头截图未转写，本轮未请求 |
| C11 | Response 类在 models.py，由 requests.get() 返回；来源接着看 text()。quote: 在requests的源码models.py中定义了requests.get()返回的类Response。 | s1 ./yuanrenxue-anti-20190104-01.md:73 | source-report | models.py 的 Response | text() 函数体在截图中 |
| C12 | 响应头找不到编码时 self.encoding 为 None，再经 self.apparent_encoding 取值。quote: 响应头找不到编码时，self.encoding就是None。它就会通过self.apparent_encoding获得编码 | s1 ./yuanrenxue-anti-20190104-01.md:77 | source-report | Response 的来源描述 | apparent_encoding 的实现在截图中 |
| C13 | apparent_encoding 被写成通过 chardet 检测。quote: 很简单，就是通过chardet检测的。 | s1 ./yuanrenxue-anti-20190104-01.md:81 | source-report | chardet | 未核对 chardet 的调用参数 |
| C14 | 来源的建议是中文网页用 cchardet 检验 response.content，而不是直接用 response.text。quote: 用cchardet检验response.content，而不是直接用response.text。 | s1 ./yuanrenxue-anti-20190104-01.md:114 | source-report | 来源所说的中文网页 | 没有调用示例，也没有失败出口 |
| C15 | cchardet 被写成 uchardet 的 Python 绑定，uchardet 是 Mozilla 的 C++ 编码检测库。quote: cchardet是uchardet的Python绑定 | s1 ./yuanrenxue-anti-20190104-01.md:116 | source-report | cchardet 与 uchardet 的来源关系 | 未核对包版本或检测结果 |

<a id="validation"></a>
## 来源自己的对照

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C16 | 来源用「镕」说明它不在 GB2312 中，用 GB2312 编码会报错，GBK 编码后再用 GB2312 解码也会报错。quote: 例子中的“镕”字不在GB2312中，用这个编码时就会报错 | s1 ./yuanrenxue-anti-20190104-01.md:107 | source-report | 这一个汉字的来源实验 | 实验代码在截图中，本轮未复跑 |
| C17 | 来源称按 requests 的 errors=replace 再用 GB2312 解码时，「镕」变成乱码。quote: 把errors设置为replace再用GB2312解码得到的文本就会有乱码出现 | s1 ./yuanrenxue-anti-20190104-01.md:109 | source-report | 来源对 replace 行为的描述 | 未复跑 |
| C18 | 来源称 chardet 把该二进制判成 GB2312，但应该是 GBK 或 GB18030，并指向 2014 年的 issue #33。quote: 得到的是GB2312，但应该是GBK或GB18030编码。当然，chardet的这个bug已经有人在github提出issues，最早是2014年的#33， | s1 ./yuanrenxue-anti-20190104-01.md:111 | source-report | 这次 chardet 检测的来源结果 | 输入字节未转写 |
| C19 | 来源接着点名 #99 和 #168，并称当时没有 merge 到 master。quote: 后来有#99，#168，但是不懂中文的老外一直没有merge到master。 | s1 ./yuanrenxue-anti-20190104-01.md:112 | source-report | 来源点名的 issue | 未打开这些 issue，不判断现在是否已合并 |

## 验证与限制

本轮只读了归档正文，没有安装或运行 requests、chardet、cchardet，没有请求示例页，也没有打开 issue。因此上表全部是 source-report，不能当成当前库版本的行为。

字数只取来源原句：`GB 2312 标准共收录 6763 个汉字`，`共收入 21886 个汉字和图形符号`，`共收录汉字70244个`。这些句子没有标准版本号。

缺了三段，所以不是 procedure：cchardet 的返回值没有验收条件；检测仍为 GB2312 时没有失败出口；截图里的调用方式没有转写成可检查的输出。grep 命令出现在正文，匹配结果只在图里。
