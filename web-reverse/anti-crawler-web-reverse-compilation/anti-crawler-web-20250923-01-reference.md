---
schema_version: 2
id: akamai-sensor-field-shapes-reference
document_type: reference
original_date: '2025-09-23'
archived_date: '2026-10-02'
scope:
  targets:
    - akamai
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./anti-crawler-web-20250923-01.md#第一篇akamai难点第一弹mst参数的vmp混淆解决思路"
    basis: source-report
  - id: s2
    ref: "./anti-crawler-web-20250923-01.md#第二篇akamai难点第二弹ajr参数得混淆解密"
    basis: source-report
  - id: s3
    ref: "./anti-crawler-web-20250923-01.md#第三篇akamai难点第三弹ffs参数的混淆解密思路"
    basis: source-report
  - id: s4
    ref: "./anti-crawler-web-20250923-01.md#第四篇akamai难点第四弹获取xck字典后的混淆解密思路"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只整理来源对字段形状的描述。UA、屏幕、插件串、字符表、ver 样例和生成样例都不收录。hh 下标未展开。没有运行，也不把作者的生成成功写成验收。
relations:
  - type: derived_from
    target: "./anti-crawler-web-20250923-01.md#第四篇akamai难点第四弹获取xck字典后的混淆解密思路"
tags:
  - akamai
  - sensor-data
  - source-report
---
# Akamai 来源里的 sensor 字段形状

这张卡只回答来源如何描述 dvc、ajr、ffs/inf、xCK 的键，以及 JSON 字符串之后的置换和前缀。POST、Cookie 更新和通过条件仍看产品卡的链路和验收，不在这里重复。环境字面量、字符表和生成样例都不抄。

<a id="parameters"></a>
## 字段形状

### dvc

mst 被写成一组单键对象。来源点名要跟的是 dvc，并把它拆成三段。

> zEK是通过j8函数生成的，nOK解混淆就是时间戳的差值，而tCK经过对比也是一个固定值

长串不是直接加密 UA。粘贴片段先做一轮乘 33 再异或的摘要，负数再转成无符号整数，然后用二进制位从字符表里挑字符，最后用另一串数字做下标。短串用 cMK 的同类摘要与这次摘要相加。

> beg = beg*33

> if (str_2[i] == '1')

> linshi = (beg1 + beg)

### ajr

cMK 进入 L7 时，鼠标串被写成空串，设备数据先经过 WL。nZK 是当前时间戳相对 startTs 的差。WL 把对象的值转成字符串再接起来。VNK 收集因数，个数到 6 就停。

> "mouseMoveData": ""

> 现在的时间戳减去初始的时间戳的差值

### ffs 与 inf

第三篇把 ffs 收成页面 input 的属性编码，并写 inf 用同一套结果。属性如何逐项编码留在来源函数里，这里只保留这个等式。

> inf参数的值跟ffs一样

### xCK 之后

较难的字段在前三篇。第四篇从已经得到的字典往后写：先 JSON 字符串，再按冒号分段交换，再做字符替换，最后加前缀。bm_sz 只作为被读取的 cookie 名出现。

> `JSON']['stringify'](xCK)`

> gTK('bm_sz')

> qW[rq] = qW[SP]

> 这里就是生成了sensor_data的前缀

### 结论

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `zEK是通过j8函数生成的，nOK解混淆就是时间戳的差值，而tCK经过对比也是一个固定值`。dvc 被写成 zEK、nOK、tCK 三段拼接；zEK 来自 j8，nOK 是时间戳差，tCK 被作者写成固定值。 | ./anti-crawler-web-20250923-01.md:59 | source-report | parameters | 未给出 j8 本体。tCK 固定只是作者对照后的说法。 |
| C2 | `beg = beg*33`。长串摘要在同一行写成种子 5381，乘 33 后再异或字符码。 | ./anti-crawler-web-20250923-01.md:118 | source-report | parameters | 输入串里的 UA 片段不收录，也没有重算。 |
| C3 | `beg >>> 0`。摘要为负时，来源把它无符号右移成非负整数，再转二进制。 | ./anti-crawler-web-20250923-01.md:119 | source-report | parameters | 只见于粘贴片段。 |
| C4 | `if (str_2[i] == '1')`。二进制位为 1 时，来源取字符表里对应下标的字符。 | ./anti-crawler-web-20250923-01.md:107 | source-report | parameters | 字符表原文不收录。 |
| C5 | `i%3 == 0`。位为 0 时，来源只在下标能被 3 整除且表内仍有字符时取。 | ./anti-crawler-web-20250923-01.md:107 | source-report | parameters | 与 C4 是同一段循环。 |
| C6 | `String(C6K).concat(window.bmak['startTs']+nZK)`。长串的下标来自 C6K 与 startTs 加 nZK 拼成的数字串。 | ./anti-crawler-web-20250923-01.md:87 | source-report | parameters | C6K 的来历不在这一段。 |
| C7 | `linshi = (beg1 + beg)`。短串用的二进制来自 cMK 的同类摘要与长串摘要相加。 | ./anti-crawler-web-20250923-01.md:153 | source-report | parameters | 相加前的具体值不收录。 |
| C8 | `"mouseMoveData": ""`。ajr 的输入字典把 mouseMoveData 写成空串，并带 startTimestamp、deviceData、totVel 和 deltaTimestamp。 | ./anti-crawler-web-20250923-01.md:180 | source-report | parameters | 同一函数里的 UA、屏幕和插件串不收录。 |
| C9 | `String(value)).join(separator)`。来源把 WL 写成取出对象的值、转成字符串再拼接。 | ./anti-crawler-web-20250923-01.md:210 | source-report | parameters | 作者标明这是取巧复现。 |
| C10 | `现在的时间戳减去初始的时间戳的差值`。nZK 被写成当前时间戳减去 bmak.startTs。 | ./anti-crawler-web-20250923-01.md:222 | source-report | parameters | RZ 的函数体没有单独贴出。 |
| C11 | `RRK["length"] < 6`。VNK 在结果不超过 6 个的前提下收集整数的因数。 | ./anti-crawler-web-20250923-01.md:247 | source-report | parameters | 未运行。 |
| C12 | `inf参数的值跟ffs一样`。ffs 与 inf 被写成同一套 input 属性编码。 | ./anti-crawler-web-20250923-01.md:281 | source-report | parameters | VSK 函数体不整段收录。 |
| C13 | `"mst": whK`。xCK 字典里能定位到 ajr、ffs、inf、mst 这些键。 | ./anti-crawler-web-20250923-01.md:296 | source-report | parameters | ver 的样例值不收录。 |
| C14 | `gTK('bm_sz')`。LDK 读取名为 bm_sz 的 cookie，再按波浪线切开。 | ./anti-crawler-web-20250923-01.md:314 | source-report | parameters | 不收录 cookie 值，hh 下标也没有展开。 |
| C15 | `qW[rq] = qW[SP]`。Mq 把字符串按冒号切开，再交换两段。 | ./anti-crawler-web-20250923-01.md:325 | source-report | parameters | k9 的多数更新式写成 hh[n]，不能当成已展开的常数。 |
| C16 | `这里就是生成了sensor_data的前缀`。nvK 的结果被来源称为 sensor_data 的前缀，再与耗时串和正文用分号接上。 | ./anti-crawler-web-20250923-01.md:344 | source-report | parameters | 生成成功只是作者自述。 |
| C17 | `JSON']['stringify'](xCK)`。进入 Mq 之前，来源先把 xCK 做成 JSON 字符串。 | ./anti-crawler-web-20250923-01.md:305 | source-report | parameters | 未对照浏览器里的 POST 正文。 |

## 验证与限制

产品卡已经有 request-chain 和 validation。本篇的增量是字段形状，不补进那两节，也不另建同名模块。

插桩只被说成在若干日志断点上看输入输出，没有可引用的脚本位置，所以不建 decision-flow。hh 数组没有展开。作者写生成成功，这里保持 source-report。
