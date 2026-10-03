---
schema_version: 2
id: fenbi-leo-3932-requestencoder-md5-chain
document_type: reference
original_date: '2025-12-14'
archived_date: '2026-10-02'
scope:
  targets: [com.fenbi.android.leo]
  client: Android
  version: '3.93.2'
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20251214-01.md#32-继续分析
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 类名、SO 名和 0x61bd4 来自讲义模板与 JNI 日志。未重载 APK。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留五轮拼接顺序和分钟桶。固定 key、长数字串和证书字节不写入本卡。
  - name: validation
    anchor: boundaries
    sources: [s1]
    basis: source-report
    limits: 标准 MD5 是作者对 hook 明文的判断。时间串的闭合脚本不在正文，且 SO 与 trace 曾不一致。
relations:
  - type: derived_from
    target: ./xfq-20251214-01.md#32-继续分析
tags: [fenbi-leo, request-encoder, md5, source-report]
---

# 小猿口算 3.93.2 的五轮 MD5 顺序

这份参考卡回答：`com.fenbi.android.leo` 3.93.2 的 `zcvsd1wr2t` 在讲义里被分成哪几轮标准 MD5，以及那串随时间变化的数字从哪个函数出来。它不复述固定 key、证书字节或长数字串，也不是可运行的签名实现。来源是 [小猿口算讲义](./xfq-20251214-01.md#32-继续分析)。

<a id="interfaces"></a>
## 调用面

目标是 `sign`，定位方式是 `搜"sign"就行`。Smali 签名是 `zcvsd1wr2t(Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;`。模板写明 `com.fenbi.android.leo`、`3.93.2.apk`、`com.fenbi.android.leo.utils.e`、`RequestEncoder`。

JNI 日志把 `zcvsd1wr2t` 登记在 `0x61bd4`。另一个 native 名是 `sdwioxccsd`，地址 `0x607f0`。日志还出现 `PackageInfo.signatures` 和 `toChars()[C`，作者注明 `这里在做签名校验`。`resolveClass("[C")` 这条返回 `经过测试用不了`，作者改用自己的 CharArray。证书内容不进入本卡。

主动调用的返回会变。来源写过了一段时间结果就不一样，所以后面才去固定 `rand` / `time`。固定值只说明那次 unidbg 把时间钉死了。

<a id="parameters"></a>
## 五轮顺序

作者把 `0x64980` 当作输入 MD5，`0x65604` 当作输出 MD5，`分别对应update和digest`。digest 的第二参 `约定使用x8`，并且是 `usercall`。输入缓冲 `内存结构很像是std::string`。对照之后作者写 `很好,标准的`。

五轮里，第一轮 `发现好像后续没用到`。从第二轮起，顺序是来源的项目符号，不是本轮推出来的：

- m2 输入：`路径,第一位/换成-`，再加来源所谓的固定 key。
- m3 输入：`处理后的路径,第一位/换成-`、固定 key、`m2`、再一段 `处理后的路径`。来源另写 `然后再加路径`。
- m4 输入：`m3输入`、`m3输出`、以及 `一长串字符串`。
- m5 输入：`m4输入`、`m4输出`、再加 `key`。作者把第五轮输出当成当次签名。

那一长串 `怎么来的` 被指到 `657A4`，入参是 `a4(-3)`。讲义贴出的注释写 `timer = (timer + a2) / 60`，并说明除以 60 得到分钟级时间，后面还有移位、查表和 `ostream` 写入。这是注释里的桶，不是已经展开的逐项公式。

<a id="boundaries"></a>
## 验证与限制

`很好,标准的` 只覆盖作者 hook 到的那几段明文是否像标准 MD5。时间串后来靠捕获 `operator<<`，作者先说捕获是对的，换测试后又写 `有几个不对`。结尾写 `看的so和unidbg trace不太一样`，调整后才分析出来；附件名是 `sub_65784_reverse.py`，与正文里的 `657A4` 不是同一个写法，脚本本身不在正文。因此分钟串的展开不能从本篇复原。本轮没有跑 unidbg，也没有重算五轮。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 方法签名是 `zcvsd1wr2t(Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;`，类是 `com.fenbi.android.leo.utils.e`。 | s1 第 90、1171 行 | source-report | 3.93.2 模板 | 未重载 APK |
| C2 | `zcvsd1wr2t` 登记在 `0x61bd4`；`sdwioxccsd` 在 `0x607f0`。 | s1 第 1376–1376 行 | source-report | 该次 JNI 日志 | 基址未重核 |
| C3 | 签名字符走 `PackageInfo.signatures` 与 `toChars()[C`，`这里在做签名校验`。 | s1 第 1486、1501、1503 行 | source-report | 第一轮输入的来源 | 证书字节不入卡 |
| C4 | `64980是输入md5,65604是输出md5`，digest `约定使用x8`。作者写 `很好,标准的`。 | s1 第 1562、1576 行 | source-report | 作者钉死时间后的五次调用 | 未独立计算 MD5 |
| C5 | m2 起于 `路径,第一位/换成-`。m4 吃进 `一长串字符串`。m5 最后再加 `key`。 | s1 第 1719、1747、1762 行 | source-report | 讲义列出的拼接顺序 | key 与长串原文不入卡 |
| C6 | 长串由 `657A4` 处理，`a4(-3)`。注释给出 `timer = (timer + a2) / 60`。 | s1 第 1769、1831 行 | source-report | 讲义中的分钟桶 | 注释不是闭合公式 |
| C7 | 作者发现 `so和unidbg trace不太一样`，附件只留下 `sub_65784_reverse.py`。 | s1 第 2047 行 | source-report | 时间串纯算的结尾 | 脚本不在正文 |
