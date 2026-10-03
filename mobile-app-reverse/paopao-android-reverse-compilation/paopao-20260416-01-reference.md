---
schema_version: 2
id: unidbg-env-response-model-reference
document_type: reference
original_date: '2026-04-16'
archived_date: '2026-10-02'
scope:
  targets: [unidbg-env-response-model]
  client: unidbg
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260416-01.md#四层响应模型so-的四种外部交互
    basis: source-report
  - id: s2
    ref: ./paopao-20260416-01.md#优先级原则能不补就不补
    basis: source-report
  - id: s3
    ref: ./paopao-20260416-01.md#决策树补什么值
    basis: source-report
  - id: s4
    ref: ./paopao-20260416-01.md#真正危险的补错了不知道
    basis: source-report
  - id: s5
    ref: ./paopao-20260416-01.md#如何避免补错
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s3]
    basis: source-report
    limits: 四通道和取值顺序只复述来源的思维框架。syscall 比例、默认文件路径和后续篇号都未在本地核对。
  - name: parameters
    anchor: parameters
    sources: [s3, s4]
    basis: source-report
    limits: 示例分辨率和版本字符串是作者给出的合理值，不是某一台设备的测量。设备标识只保留“必须取真机”的规则，不收录示例数字。
  - name: validation
    anchor: validation
    sources: [s2, s4, s5]
    basis: source-report
    limits: 对照步骤是作者建议。没有样本数以外的通过阈值，也没有“缺真机结果就停止”的失败出口，因此不建流程。
relations:
  - type: derived_from
    target: ./paopao-20260416-01.md#四层响应模型so-的四种外部交互
  - type: derived_from
    target: ./paopao-20260416-01.md#决策树补什么值
  - type: derived_from
    target: ./paopao-20260416-01.md#如何避免补错
tags: [unidbg, jni, env-patch, source-report]
---

# Unidbg 补环境先分流再决定返回值

这张卡只回答：SO 的外部请求落在哪一类，以及返回值该推理、该抄真机，还是可以先给空。JNI 包装、IOResolver 三返回和具体模板分别在同系列后续笔记，不在这里展开。已有的 unidbg 卡片是 APK v2 签名数组为空，以及哈希明文扫描，目标不同，不把本篇补进去。

<a id="decision-flow"></a>
## 四通道与最小干预

来源把补环境收成四种外部交互，并要求先让 Unidbg 自己跑。JNI 未实现时抛出带签名的 `UnsupportedOperationException`，由 `AbstractJni` 接手。syscall 只有报 `not implemented` 或怀疑返回值时才介入。文件访问交给 `IOResolver`。带符号的 libc / liblog / libdl 调用才考虑 Hook。`gettimeofday` 的例子用来说明：默认实现能用就不要先改成固定时间。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 外部交互被说成只有四种 | 答案是四种。  ** 所有补环境工作都落在这四种之一  ** 。 | s1，第 92 行 | source-report | 本篇框架 | 没有穷尽列表的证明 |
| C2 | JNI 默认抛出未实现并带上签名 | ** Unidbg 默认行为  ** ：抛  ` UnsupportedOperationException  ` ，把签名告诉你。 | s1，第 111 行 | source-report | JNI 通道 | 未核对当前 Unidbg 异常文本 |
| C3 | syscall 的触发被写成 svc | SO 代码（或它调用的 libc 函数）执行  ` svc  #0  ` 指令。 | s1，第 120 行 | source-report | 系统调用通道 | 内置比例“约 30%”未复核 |
| C4 | 文件通道的工作是 IOResolver | 实现一个  ` IOResolver  ` ，对 SO 关心的路径返回伪造的内容。 | s1，第 160 行 | source-report | 文件通道 | 实现在后续篇，本卡不写 |
| C5 | 能默认处理的不要动手 | 能让 Unidbg 默认处理的事情，绝对不要手动干预。 | s2，第 184 行 | source-report | 干预顺序 | 没有反例实验 |
| C6 | 时间函数先用内置实现 | 什么都不做，让 Unidbg 用内置实现（返回宿主机系统时间）。如果发现签名结果和 Frida 不一致，再回头处理。 | s2，第 209 行 | source-report | gettimeofday 例子 | 作者称 90% 情况如此，未测 |
| C7 | 口诀是跑、看、判、补、验 | 跑、看、判、补、验 | s2，第 218 行 | source-report | 工作顺序 | 不是带失败出口的流程 |

<a id="parameters"></a>
## 返回值从哪来

方法名能解释时，来源允许直接给一个语义上合理的值。解释不了，或者值会进入签名，就要求用 Frida 抄真机，字段很多时改用 r0tracer。先返回 null 只适用于跑完且最终结果仍正确的非关键调用。包信息要看 flags：`GET_SIGNATURES` 和 metadata 不是同一个空对象能应付的。设备标识不能自造一串数字。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C8 | 能看懂方法名就直接给合理值 | 只要方法名能看懂含义，就直接推理一个合理值返回 | s3，第 249 行 | source-report | 有语义的 API | 合理值不等于签名输入 |
| C9 | 看不懂就抄真机返回值 | Frida hook 真机，把真实返回值复制下来 | s3，第 281 行 | source-report | 混淆名或不确定的字段 | 不收录示例标识数字 |
| C10 | 不可推理的值禁止猜 | 不要瞎猜不可推理的值 | s3，第 300 行 | source-report | Step 2 | 与 C8 的分界由方法名是否可解释决定 |
| C11 | 只有结果仍正确才能一直返回 null | 如果 SO 继续跑且最终结果正确 → 这就是非关键路径，永远 null | s3，第 335 行 | source-report | Step 4 | “最终结果正确”依赖对照，本篇没有样本 |
| C12 | 设备标识自造会导致对照失败 | 两边 IMEI 不一致 → 签名结果不一致 → 你的对照验证会失败 | s3，第 408 行 | source-report | getDeviceId 这类标识 | 只保留规则，不写示例串 |
| C13 | getPackageInfo 要看 flags | getPackageInfo  ` 的第二个参数是  ` flags  ` 。如果 SO 传的是  ` GET_SIGNATURES  ` | s4，第 445 行 | source-report | PackageInfo | 原文继续区分 metadata，本行只点出 flags |

<a id="validation"></a>
## 不报错不算补对

错的字符串不会让 SO 停。来源要求每次补完用同一组入参对 Frida，并且至少用多组入参，避免一组碰巧通过。还可以把两边的 JNI 调用序列做 diff。这些是作者写下的检查，不是本次运行结果。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C14 | 标识拌进签名后不会当场报错 | 算签名时把这个 ID 拌进去了，最终签名和真机不一致 | s4，第 56 行 | source-report | 错误返回值 | 行文在讲被动模式的后果 |
| C15 | 每次补完就和 Frida 对照 | 每次补完立刻和 Frida 对照 | s5，第 456 行 | source-report | 作者的方法 1 | 没有给出 diff 工具 |
| C16 | 至少多组入参 | 建议至少抓 3-5 组不同入参的真机结果 | s5，第 480 行 | source-report | 作者的方法 2 | 3 组通过仍被写成“基本是对的” |
| C17 | JNI 调用序列可以做 diff | 把 Unidbg 和 Frida 在同一组入参下的 JNI 调用日志都打印出来，做 diff。 | s5，第 484 行 | source-report | 作者的方法 3 | Frida 侧只给了 JNI_OnLoad 挂点骨架 |

## 验证与限制

本篇自己写明没有新 API。Unidbg 版本未知。示例设备标识不进入本卡。没有“缺真机对照就停止结论”的出口，所以不建流程。第七篇以后的 JNI、文件和 syscall 细节不在本卡补完。
