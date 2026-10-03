---
schema_version: 2
id: ruyi-20260424-byted-acrawler-jsvmprt-reference
document_type: reference
original_date: '2026-04-24'
archived_date: '2026-10-02'
scope:
  targets: [byted-acrawler]
  client: web
  version: v2.11.0
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20260424-01.md#第一阶段vm-架构识别"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留入口参数、外部引用数组、操作码置换和 init/sign/getReferer/domNotValid 导出。不复制外部引用整表。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 XOR 2、多态操作码、缺 url 的抛错、短路径和结果外形的名字。不收录签名样值、密钥或自定义码表。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留五个检测函数名和 domDetect 的五项完整性检查。不复制还原后的函数体。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留自动反汇编再手动还原，以及 DEF_FUNC bodyLen 定函数边界。没有失败出口。
relations:
  - type: derived_from
    target: "./ruyi-20260424-01.md#第一阶段vm-架构识别"
tags: [byted-acrawler, jsvmp, source-report]
---

# byted_acrawler v2.11.0 的 _$jsvmprt 边界

这篇卡检索的是：来源如何描述这个虚拟机的入口、操作码置换、字符串加密、检测函数名和签名外形。不提供可执行的反编译器，也不提供签名生成。

<a id="interfaces"></a>
## 入口和导出

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>保护方式写成 _$jsvmprt，同一行标明 byted_acrawler SDK v2.11.0</td><td>s1，源文件第 35 行</td><td>source-report</td><td>来源分析的 acrawler.js</td><td>没有版本核对方法</td></tr>
<tr><td>C2</td><td>第一个参数注释是 b: 字节码（hex字符串），同一行把第二个参数注释成外部引用数组</td><td>s1，源文件第 53 行</td><td>source-report</td><td>该入口函数</td><td>函数体是省略号</td></tr>
<tr><td>C3</td><td>宿主对象的进入方式是：第二个参数是外部引用数组</td><td>s1，源文件第 89 行</td><td>source-report</td><td>VM 调用的第二个参数</td><td>不复制索引整表</td></tr>
<tr><td>C4</td><td>操作码变换写成 13 * opcode % 241</td><td>s1，源文件第 108 行</td><td>source-report</td><td>来源读到的 1 字节操作码</td><td>低两位之后的分派树不在本卡</td></tr>
<tr><td>C5</td><td>导出赋值里有 byted_acrawler.domNotValid = false || domDetect()，同一行还有 init、sign、getReferer</td><td>s1，源文件第 323 行</td><td>source-report</td><td>反汇编末尾的导出</td><td>没有参数类型</td></tr>
</table>

<a id="parameters"></a>
## 常量、操作码和签名外形

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 字符串常量加密写成 XOR 2 | s1，源文件第 73 行 | source-report | 来源数出的字符串常量池 | 不抄明文对照 |
| C7 | 多态写成多个字节码可以映射到同一操作，同一行以 RETURN 有 5 个操作码举例 | s1，源文件第 133 行 | source-report | 来源生成的映射 | 第五个操作码在下一行；不复制全表 |
| C8 | 缺 url 时抛出 url.nonce must be an object with a url property! | s1，源文件第 377 行 | source-report | 作者还原的 getSignature | 不是服务端错误文案 |
| C9 | 无效 DOM 走精简签名路径，否则走同一行的完整签名路径 | s1，源文件第 377 行 | source-report | 作者还原的两条路径 | 密钥和 cookie 读取不在本卡 |
| C10 | 外形名字包括固定前缀，同一行还有版本标记、模式标志和自定义 Base64 密文 | s1，源文件第 395 行 | source-report | 作者给出的一条结果 | 样值、码表和字符替换不在本卡 |

<a id="risk-control"></a>
## 检测名

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 字符串池中的检测名从 domDetect 起，同一行列出 hookDetect、nodeDetect、phantomDetect、webdriverDetect | s1，源文件第 83 行 | source-report | 解密后的常量名 | 没有各函数阈值 |
| C12 | domDetect 的功能行是 DOM环境完整性检测（5项检查） | s1，源文件第 347 行 | source-report | 作者还原表中的该函数 | 不复制第 252 行的函数体 |

<a id="decision-flow"></a>
## 反编译顺序

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C13 | 自动反汇编的产物是字节码 → 带地址的指令列表 | s1，源文件第 332 行 | source-report | 来源的 decompiler.js | 行数是作者计数 |
| C14 | 函数边界靠 identifyFunctions()识别函数边界（DEF_FUNC + bodyLen），同一行还有 parseHeader、disassemble、decompile、decompileToJS | s1，源文件第 214 行 | source-report | 来源的五段管道 | 没有失败出口 |

## 验证与限制

`acrawler`、`byted-acrawler`、`toutiao`、`jsvmp` 上这些模块的查询都是 0。`douyin` 的 parameters 卡只讲请求面的 host、编码和票据，不讲这个虚拟机。头条 a_bogus 归档没有模块。第 6 节的 200 保持作者自述，不设 validation。签名样值、密钥和自定义码表不在本卡。文末的反编译难点只说明栈和多态难还原，不是失败出口。
