---
schema_version: 2
id: zuiyou-573-netcrypto-sign-shape
document_type: reference
original_date: '2025-12-06'
archived_date: '2026-10-02'
scope:
  targets: [cn.xiaochuankeji.tieba]
  client: Android
  version: '5.7.3'
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20251206-01.md#unidbg辅助-算法分析
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 包名、类名和 0x4a28d 来自讲义里的模板与日志。样本 APK 在正文中上传失败，本轮未打开 SO。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留输出形状、第二参角色，以及“魔数被改”这一判断。四个魔数不在正文。
  - name: validation
    anchor: boundaries
    sources: [s1]
    basis: source-report
    limits: “正好对上了”指向未收录的 py 附件。不能把这句话当成可复核的验收。
relations:
  - type: derived_from
    target: ./xfq-20251206-01.md#unidbg辅助-算法分析
tags: [zuiyou, net-crypto, md5, source-report]
---

# 最右 5.7.3 NetCrypto.sign 的形状

这份参考卡回答：讲义把 `cn.xiaochuankeji.tieba` 5.7.3 的 `sign(String, byte[])` 落在哪，以及作者为什么说它不是标准 MD5。它不补魔数，也不把附件脚本复述出来。来源是 [最右讲义](./xfq-20251206-01.md#unidbg辅助-算法分析)。

<a id="interfaces"></a>
## 调用面

目标句是 `sign(String, byte[])`，SO 名写的是 `libnet_crypto.so`。模板里的样本是 `cn.xiaochuankeji.tieba`、`apks/zuiyou/5.7.3.apk`、`com.izuiyou.network.NetCrypto`、`net_crypto`。JNI 签名写成 `sign(Ljava/lang/String;[B)Ljava/lang/String;`。

unidbg 日志把该函数放在 `sign 函数地址0x4a28d`。重打包分支被作者跳过：`由于我们不关心重打包，所以跳过`。这只说明作者没分析那个 if，不是“没有签名检查”。

<a id="parameters"></a>
## 摘要形状

输出 `是一个v2-开头的,后面都是十六进制字符串,32长`。作者换第一个字符串参数后 `结果发现值不变,说明第一个参数可能没起到关键计算`，并写明 `当然也不一定`。更换第二个参数后 `说明第二个参数起到了关键作用`，而且 `这里不是标准的`。

倒追时作者纠正过读法：`r0实际上要偏移20再读指针`。短输入走 `std::string` 的 `short存储`，`入参偏移24的地方是内容`，`24字节出存储字符串内容或者指针`。

32 次循环被当成 MD5。`65484` 被怀疑是 digest，`65540` 里还有 init，`6533A` `猜测是update`。旁边 `有点像md5的4个魔数`，结论是 `感觉就是把魔数改了导致是标准md5计算的不对`。四个数字本身没有写出来。

<a id="boundaries"></a>
## 验证与限制

后文只写 `修改md5源码的魔数`，然后 `正好对上了`，附件名是 `zuiyou_sign.py`。魔数、修改点和脚本都不在这篇正文里。样本压缩包还写着上传失败。因此这里只能检索“v2- 加 32 hex、第二参是消息、初始化魔数被改”，不能当签名实现。本轮没有运行模板，也没有重算那次输出。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 目标是 `libnet_crypto.so` 的 `sign(String, byte[])`，类为 `com.izuiyou.network.NetCrypto`。 | s1 第 49、107 行 | source-report | 讲义中的 5.7.3 模板 | APK 未随正文提供 |
| C2 | JNI 为 `sign(Ljava/lang/String;[B)Ljava/lang/String;`，地址写作 `0x4a28d`。 | s1 第 114、229 行 | source-report | 作者那次 unidbg 日志 | 未重核基址 |
| C3 | 结果 `是一个v2-开头的,后面都是十六进制字符串,32长`。 | s1 第 224 行 | source-report | 该次样例输出的形状 | 不收录样例摘要本身 |
| C4 | 换第一参 `结果发现值不变`；第二参 `起到了关键作用`，且 `这里不是标准的`。 | s1 第 224、226、227 行 | source-report | 作者换过的两次输入 | 作者自己写了“也不一定” |
| C5 | 短串走 `short存储`，内容在 `入参偏移24`。`65484` 被怀疑是 digest。 | s1 第 280、290 行 | source-report | 作者对 std::string 和调用的判断 | 偏移没有在本文用内存图闭合 |
| C6 | 作者 `感觉就是把魔数改了`，但正文只有 `正好对上了` 和文件名 `zuiyou_sign.py`。 | s1 第 292、300、302 行 | source-report | 讲义结尾的自述 | 魔数不在正文，不能复核 |
