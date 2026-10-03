---
schema_version: 2
id: meituan-mtgsig-jsvmp-source-limits
document_type: reference
original_date: unknown
archived_date: unknown
scope:
  targets: [mtgsig]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: notes
    ref: null
    basis: source-report
    citation: 本地教学笔记（定位不公开）
    reason: 正式入库不保留讲次与公开定位；原始材料未随本文公开。
modules:
  - name: parameters
    anchor: parameters
    sources: [notes]
    basis: source-report
    limits: 缺 locator，未复现。只有否定式边界：mtgsig 每次变化，不能拿同一个值反复用。无字段表、密钥、opcode 和字节码。不写伪造、并发或重放。
  - name: risk-control
    anchor: risk-control
    sources: [notes]
    basis: source-report
    limits: 缺 locator，未复现。只保留环境采集、反调试、用户行为上传，以及人机判断在服务端。无检测实现，无上报格式，无请求序列。
tags: [mtgsig, parameters, risk-control, jsvmp]
---

# 美团 mtgsig 的分析边界

这份参考说明分析美团 `mtgsig` 时哪些判断可以留下，哪些不能写成算法。目标是 `mtgsig`，不是通用 `jsvmp`。生产脚本被描述为使用了 JSVMP，这只说明实现形态，不能从 [自定义指令集](./jsvmp-custom-isa-interpreter-reference.md) 推出美团字节码。

不建 request-chain。没有可定位的请求序列。不写伪造、纯协议或 HAR。

<a id="parameters"></a>

## 参数边界

逐个关掉携带项，看请求是否还能返回。`mtgsig` 是关键项。每次都不一样。同一个值不能反复使用，这被叫做防重放。没有字段表，所以防重放还不是已验证的协议规则。

这不是 signature 还原，也不是 encryption 还原。主包同时被叫做签名包和加密包，两种称呼没有分开证明。不要把 `mtgsig` 升成其中任何一种算法，也不要写成 token 或 fingerprint。除 `mtgsig` 这个名字以外，cookie 和 header 的全名不采用。请求 URL 不采用。

生成逻辑在一份压缩 JS 里。格式化前像一行。体积一度被报成约 338 KB，格式化后用大模型读。文件不在本知识库，数字未核对。多次下载后哈希和体积被说成一样，因此这次不像「每次都变」的动态混淆。次数前后不一致，不能把哈希一致写成已经复验。

分析顺序是：先找生成点，再做静态语义，再找执行器。解释器主体叫做执行器。解码撞上乱码之后，一大段被改判为死代码和假分支，用来占模型上下文。能稳定留下的语义只有调用、加载、字符串、空、数组。操作码编号不采用。

更小的混淆样本和自写栈或寄存器样本只能当对照。小样本代码未入稿。那些对照不能推出 `mtgsig` 的字节码。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | mtgsig 是关键携带项，每次不同，同一个值不能反复用 | notes | source-report | 参数层 | 无字段表；不是已验证的防重放 |
| C2 | 生成算法、字段布局、密钥、opcode 表和字节码都不进入本文 | notes | source-report | 本模块 | 不能从通用 JSVMP 反推 |
| C3 | 「签名」和「加密」是对主包的两种称呼，没有分开证明 | notes | source-report | 用词边界 | 不是 signature 或 encryption 结论 |
| C4 | 约 338 KB、多次下载哈希相同，因而不是每次都变的动态混淆 | notes | source-report | 未核对的体积与哈希 | 次数互相矛盾；不能升成 static-review |

<a id="risk-control"></a>

## 风控框架

参数虚拟化和风控要分开。变换必须在客户端做完再上传，否则服务端看到的是明文。风控是服务端判断人机，甚至可以人工认定。这是框架，不是算法。页面上没有滚动和鼠标活动，会被当成非人。没有检测点名单。

风控脚本和前面的主包不是同一份材料。文件名不猜。压缩单行格式化之后行数前后不一致，精确行号不采用。「28 个 VM」和「更像栈式虚拟机」都未核对，不写成结构事实。有了操作码含义才能做高级语义还原；含义表未入稿，一条都不能写。

能留下的主题只有三类：环境采集、反调试、用户行为上传。反调试里，看到 CDP 就中断。行为侧监听鼠标移动和点击，并有队列。实现不进入本文，也不写成可以绕过。混淆体系有版本差别，具体版本号不采用。

网络明文、密钥材料和压缩校验被说成已经还原且带强校验。材料本身不记录，也不升成运行时观察。脱离浏览器的纯协议或风控上报不在本文。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 参数变换在客户端完成；人机判断在服务端，两者分开 | notes | source-report | 框架 | 不是算法，也不是服务端接受 |
| C6 | 无滚动、无鼠标活动会被当成非人 | notes | source-report | 行为层 | 无检测点名单；未复现 |
| C7 | 风控主题是环境采集、反调试、用户行为上传 | notes | source-report | 主题名 | 无实现，无上报格式 |
| C8 | 反调试看到 CDP 就中断；行为侧是鼠标移动、点击和队列 | notes | source-report | 主题之下的一层 | 不写检测实现，不写绕过 |
| C9 | 明文、密钥材料和压缩校验已经还原，这只是自述 | notes | source-report | 排除项 | 不能升成 local-parity 或 server-accepted |

## 验证与限制

没有和教学 JSVMP 的 derived_from。密码算法专名、魔改常数、替换表和并发下的伪造成功都不进入正文。没有 fingerprint 模块。

缺 locator，未复现。不能声称服务端接受。
