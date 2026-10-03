---
schema_version: 2
id: libflutter-file-offset-layout
document_type: reference
original_date: "2026-03-24"
archived_date: "2026-10-02"
scope:
  targets: [libflutter]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-app-20260324-01.md#使用-ai-实现最新版本-flutter-https-明文抓包"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留正文里的换算和 SSLFilter 偏移。不收录定位提示词、示例地址或设备命令。偏移未在本地 so 上核对。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 两种 so 落点是来源陈述。不写推送命令，也不写具体包名。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 明文和数据包都是作者看着截图下的结论。模型输出被来源自己写成有随机性。本轮未跑设备。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20260324-01.md#使用-ai-实现最新版本-flutter-https-明文抓包"
tags: [libflutter, boringssl]
---

# libflutter.so 的文件偏移和两种落点

这张卡只回答一个检索问题：来源如何区分 IDA 虚拟地址和 ecapture 要的文件偏移，以及 libflutter.so 已解压和仍留在 APK 里时各看哪里。不提供定位步骤，也不提供抓包命令。

<a id="parameters"></a>
## 地址换算和 SSLFilter 布局

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | Flutter 被写成内嵌自己的 BoringSSL，不用系统 SSL 库。quote: Flutter 内嵌了自己的 BoringSSL | s1 ./yuanrenxue-app-20260324-01.md:39 | source-report | 来源解释抓包困难的那一句 | 未打开 so |
| C2 | 来源把文件偏移写成 IDA 虚拟地址减 0x1000。quote: file_offset = IDA_VA - 0x1000 | s1 ./yuanrenxue-app-20260324-01.md:94 | source-report | 来源称 .text 上 VirtAddr 比 FileOffset 大 0x1000 的 so | 不是所有装载地址 |
| C3 | ssl_read_inner_offset 是同一段内的相对值，来源写不用再减 0x1000。quote: 无需减 0x1000 | s1 ./yuanrenxue-app-20260324-01.md:94 | source-report | BL 地址减去 SSL_read 入口 | 未计算样本 |
| C4 | SSLFilter 的 ssl_ 被写在 offset 0x18。quote: `ssl_` @ offset 0x18 | s1 ./yuanrenxue-app-20260324-01.md:94 | source-report | 来源提示词里的成员布局 | 未在 so 里核对 |
| C5 | socket_side_ 被写在 offset 0x20。quote: `socket_side_` @ offset 0x20 | s1 ./yuanrenxue-app-20260324-01.md:94 | source-report | 同一布局句 | 未核对 |
| C6 | buffers_ 从 offset 0x30 起，每 8 字节一个。quote: `buffers_[0..3]` 从 offset 0x30 | s1 ./yuanrenxue-app-20260324-01.md:94 | source-report | 同一布局句 | 未核对 |
| C7 | 偏移确定后，同一 Flutter 版本可复用。quote: 同一 Flutter 版本可复用 | s1 ./yuanrenxue-app-20260324-01.md:50 | source-report | 来源对版本内换 App 的说法 | 版本号未给出 |

<a id="decision-flow"></a>
## so 在磁盘上还是在 APK 里

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 默认情况是 libflutter.so 已经解压到应用的 lib/arm64 目录。quote: libflutter.so  解压到 | s1 ./yuanrenxue-app-20260324-01.md:114 | source-report | 来源说的多数 App | 路径是省略号，不是实测路径 |
| C9 | 另一种是清单里 extractNativeLibs 为 false。quote: extractNativeLibs = false | s1 ./yuanrenxue-app-20260324-01.md:116 | source-report | 来源点名的清单属性 | 未看清单 |
| C10 | 这时 so 不会出现在文件系统，而是留在 APK 里。quote: 不会解压到文件系统 | s1 ./yuanrenxue-app-20260324-01.md:117 | source-report | C9 的后果 | 未列目录 |
| C11 | 来源写把 APK 路径交给工具后，工具自己加上 so 在包内的数据偏移。quote: ecapture 会自动找到 APK 内 so 的数据偏移并叠加到地址上 | s1 ./yuanrenxue-app-20260324-01.md:129 | source-report | 未解压这一形态 | 不收录命令 |
| C12 | 两种形态下，传入的仍是 so 文件自身的偏移，来源写不用手算包内偏移。quote: 无需手动计算 | s1 ./yuanrenxue-app-20260324-01.md:134 | source-report | 来源对 APK 路径的补充 | 未验证该工具 |

<a id="validation"></a>
## 来源自己的通过句和随机性

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C13 | MCP 加载被写成不报错并且 IDA 里有输出就算成功。quote: 如果不报错，就证明加载成功了 | s1 ./yuanrenxue-app-20260324-01.md:84 | source-report | 来源的工具安装段 | 输出内容来源说不用在意 |
| C14 | 来源写拿到了明文请求和响应。quote: 成功获取明文的请求和响应数据 | s1 ./yuanrenxue-app-20260324-01.md:141 | source-report | 作者的第一个样本 | 截图不能当本轮结果 |
| C15 | extractNativeLibs 改为 false 后，来源仍写拿到了数据包。quote: 成功获取到了数据包 | s1 ./yuanrenxue-app-20260324-01.md:144 | source-report | 作者改清单后的同一次实验 | 第三个 App 没有名字 |
| C16 | 来源同时写大模型输出有随机性。quote: 大模型输出本身有随机性 | s1 ./yuanrenxue-app-20260324-01.md:104 | source-report | 偏移是模型生成的场合 | 没有失败样本 |

## 验证与限制

`kb_catalog.py query` 对 libflutter 的 parameters、decision-flow、validation 都是 0。带 flutter-hybrid 标签的升学 e 网通卡是另一目标的登录算法。定位用的九步提示词、示例地址、推送命令和包名都不进入本卡。没有本地运行证据。
