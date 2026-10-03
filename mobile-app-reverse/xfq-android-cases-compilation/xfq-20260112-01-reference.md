---
schema_version: 2
id: njxmxbank-744-native-ciphertext-reference
document_type: reference
original_date: '2026-01-12'
archived_date: '2026-10-02'
scope:
  targets:
    - cn.com.njxmxbank.mbank
    - 南银法巴消金
  client: Android
  version: '7.4.4'
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260112-01.md#11-apk扫描"
    basis: source-report
  - id: s2
    ref: "./xfq-20260112-01.md#21-java层"
    basis: source-report
  - id: s5
    ref: "./xfq-20260112-01.md#31-处理反调试"
    basis: source-report
  - id: s3
    ref: "./xfq-20260112-01.md#32-算法分析"
    basis: source-report
  - id: s4
    ref: "./xfq-20260112-01.md#33-固定keyiv然后py纯算"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s5]
    basis: source-report
    limits: 只保留扫描日志里的包名、版本、梆梆 soname，以及来源点名的 JNI 类、方法描述和 so 名。不收录脱壳附件、内存 dump 脚本或调用样例。
  - name: parameters
    anchor: parameters
    sources: [s3, s4]
    basis: source-report
    limits: 只保留来源对三段布局和 AES-CBC 的说法。钉死的 key/iv、模数、请求样例和密文不收录。作者自称对上，没有对照打印。
relations:
  - type: derived_from
    target: "./xfq-20260112-01.md#32-算法分析"
tags:
  - njxmxbank
  - aes-cbc
  - source-report
---

# 南银法巴消金 7.4.4：native 密文入口和三段布局

这张卡只回答：7.4.4 里请求字段走到哪个 JNI，以及来源把返回值说成哪三段。不提供可运行复现，也不把钉死 key 之后的纯算当成已定位的线上密钥。

来源没有可公开定位的原文 URL，只自述知识星球。作者写下的成功保持 source-report。样例参数、模数、钉死的 key/iv 和密文不进入本卡。

<a id="interfaces"></a>
## 入口

扫描日志把目标写成包名 `cn.com.njxmxbank.mbank`、版本名 7.4.4、版本号 157。加固命中写的是梆梆企业版，soname 包括 `lib/arm64-v8a/libDexHelper.so`。同一份日志还扫到 `classes.dex` 里的 TracerPid 字符串；作者接着只说要注意梆梆。证书行写着 `META-INF/NJBANK.RSA` 解析失败，没有后续。

抓包只点名两个字段：请求体里的 `pdddata`，响应体里的 `passworddata`。没有 URL、没有明文结构。

Java 层来源点名 `com.csii.njaesencryption.PEJniLib.getNativeValue`，描述是 `getNativeValue(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`。unidbg 模板里的 so 名是 `csii_AESTelecomModule_v1_0`。调用样例不收录。

so 段说来源文件是加密的，要先从内存拉下来再修。动态注册之后来源说实际走了跳板。这些是定位顺序，不是 dump 或修复步骤。

<a id="parameters"></a>
## 参数机制

来源把返回值收成一句：`RSA加密的AESKey(Base64)|AES密文(Base64)|MD5(Base64)`。第三段被说成明文 MD5 的二进制再做 Base64。第二段被说成标准 AES-CBC。加解密由传入的最后一个标志位区分。第一段被说成对 AES key 做标准 RSA 公钥加密，再 Base64。

这句不能当成已闭合的密钥调度：

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 包名是 cn.com.njxmxbank.mbank | s1，扫描日志 | source-report | 来源贴出的 7.4.4 扫描 | 未对照安装包 |
| C2 | 版本名 7.4.4 | s1，同一日志 | source-report | 同上 | 未对照安装包 |
| C3 | JNI 为 PEJniLib.getNativeValue(String,String) | s2 | source-report | 来源贴出的 smali 描述 | 不收录调用样例 |
| C4 | so 名 csii_AESTelecomModule_v1_0 | s5 | source-report | 来源的 unidbg 模板 | 模板类初始化失败后改用旧版 so 的说法只是转述 |
| C5 | 输出被说成 RSA(AESKey)、AES 密文、MD5 三段 Base64 | s3 | source-report | 来源对本次加密方向的归纳 | IDA 没找到 result 的赋值，反编译被作者自己标成有问题 |
| C6 | 纯算段是把 AES key 和 IV 钉死后的结果 | s4 | source-report | 只说明来源怎么得到第二段 | 钉死的材料不收录，文末没有对照打印 |

反编译片段把 `getValue` 和 `sigaction`、`rand` 写在一起。作者写 result 没有合理赋值，于是改用 Binary Ninja。因此不能从这段反编译读出线上 key 的生成规则。纯算节明确写 key 和 IV 是固定住的；对应的 unidbg 片段是在库调用处改写，不是从随机缓冲推导。字面量不收录。

旧版算法相同，来源写的是转述，不是本篇的对照。包内 so 的类初始化被写成直接报错，后面改看旧版。

## 验证与限制

- 没有本地运行，也没有把作者的纯算输出和抓包结果并排核对。文末停在两张未贴出的图号上。
- 不把 `maps` 打不开就 `exit(0)`、HookZz 触发检测、Binary Ninja 基址要去掉 `0x400000` 写成绕过步骤。偏移 `0x446d54` 到来源说的 `0x46d54` 只保留为图像基址差，hook 代码不收录。
- 脱壳只写了网站、fart、`56.al` 三个名字，没有壳的定位过程。
- 近邻查询里，`cn.com.njxmxbank.mbank` 和「南银法巴消金」的 parameters、interfaces 都没有已有卡片。不把这篇补进别的 AES 或 unidbg 卡。
- 前提、步骤、输出、验收、失败出口五段不齐，尤其没有可观察的验收记录，所以不是流程。
