---
schema_version: 2
id: unidbg-jni-override-reference
document_type: reference
original_date: '2026-04-17'
archived_date: '2026-10-02'
scope:
  targets: [unidbg-jni-override]
  client: unidbg
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260417-01.md#三个维度把一个-jni-补环境请求拆成三个问题
    basis: source-report
  - id: s2
    ref: ./paopao-20260417-01.md#六种返回模式的代码模板
    basis: source-report
  - id: s3
    ref: ./paopao-20260417-01.md#维度二返回什么值--信息收集工具箱
    basis: source-report
  - id: s4
    ref: ./paopao-20260417-01.md#四种处理策略
    basis: source-report
  - id: s5
    ref: ./paopao-20260417-01.md#验证闭环--跑通不等于跑对
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s3, s4]
    basis: source-report
    limits: 三维拆分和四种逻辑策略是来源的操作顺序。成本排序没有计时数据。
  - name: parameters
    anchor: parameters
    sources: [s2]
    basis: source-report
    limits: 只保留签名后缀和包装类型的对应。示例机型、标识和签名字节不写入。
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3]
    basis: source-report
    limits: AbstractJni 方法名规则来自来源对栈顶帧的拆法。未对照 unidbg 源码确认是否总走带 V 的重载。
  - name: validation
    anchor: validation
    sources: [s1, s5]
    basis: source-report
    limits: “两个结果一致才算通”是作者标准。没有失败即停止的出口，不建流程。
relations:
  - type: derived_from
    target: ./paopao-20260417-01.md#三个维度把一个-jni-补环境请求拆成三个问题
  - type: derived_from
    target: ./paopao-20260417-01.md#六种返回模式的代码模板
  - type: derived_from
    target: ./paopao-20260417-01.md#验证闭环--跑通不等于跑对
tags: [unidbg, jni, source-report]
---

# Unidbg JNI override 的类型、取值和逻辑

这张卡回答一次 JNI 补环境要拆开的三个问题：栈顶方法决定包装类型，真机工具决定具体值，JDK、JADX 或简化实现决定要不要执行逻辑。它不覆盖 unidbg 自己 `vm.getSignatures()` 在仅有 v2 签名时返回空数组的那条诊断；那是另一张卡的目标。

<a id="decision-flow"></a>
## 三个问题不要一次答完

来源要求先答返回类型，再答值，最后才处理“这是一段动作”。取值工具从轻到重：系统属性用 adb，单个动态方法用 Frida，整类用 r0tracer，仍不够再看 Java。逻辑侧同样先绑定 JDK，再抄 App 类，再手写 Framework 的简化行为，最后才试 null。null 能过就留下；出现 NPE 或走错分支再回到前三策。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 每次 override 被拆成三个问题 | 任何一次 JNI override，本质上都在回答三个独立的问题 | s1，第 68 行 | source-report | JNI 通道 | 作者称 JNI 占工作量 90%，未计量 |
| C2 | 三维互相独立 | 类型不对，取值再对也白搭；取值不对，类型正确也会让签名错 | s1，第 79 行 | source-report | 三维模型 | 逻辑维被写成少数方法 |
| C3 | 全局属性优先 adb | 凡是可以从系统属性直接读出来的，优先 adb shell | s3，第 279 行 | source-report | 工具一 | 拿不到 App 内部状态和需权限的标识 |
| C4 | Frida 适合单个方法 | 抓单个方法、单个字段的返回值，精确可控 | s3，第 337 行 | source-report | 工具二 | 来源同时写了被动 hook 和主动 call |
| C5 | r0tracer 用来摸一整类 | 一次补一整个类、一整个包、一个复杂样本的首轮 | s3，第 385 行 | source-report | 工具三 | 调用栈开关的具体配置未逐行核对 |
| C6 | 有些调用要的是动作而不是常量 | 有时候 SO 调的不是一个"getter"，它调的是一段"动作" | s4，第 407 行 | source-report | 维度三 | 例子包括格式化时间和 Map |
| C7 | JDK 集合让后续 put/get 走真实现 | 后续 put/get 全部由 JDK 处理 | s4，第 431 行 | source-report | 策略 1 | 只说明 HashMap 这个例子 |
| C8 | App 类从 JADX 抄逻辑 | 策略 2：App 自定义类 → JADX 反编译后复制逻辑 | s4，第 441 行 | source-report | 策略 2 | 未给可编译的复刻 |
| C9 | Framework 类做简化实现 | 策略 3：Framework 类 → 手动简化实现 | s4，第 468 行 | source-report | 策略 3 | Base64 分支只处理了来源点名的常见 flag |
| C10 | 复杂调用可以先返回 null | 策略 4：复杂逻辑 → 降级返回 null | s4，第 499 行 | source-report | 策略 4 | 通过条件在下一行 |
| C11 | null 失败再回到前三策 | 先返回 null 跑一下，如果 SO 能过，这就是最省力的选择；如果 SO 报 NPE 或者拿到 null | s4，第 510 行 | source-report | 策略 4 的退回 | 该行在 “拿到 null” 处截断，后文才写回策略 1/2/3 |

<a id="parameters"></a>
## 签名后缀对应哪种包装

基本整数直接返回。字符串用 `StringObject`。字节数组用 `ByteArray`。难构造的对象用 `ProxyDvmObject`。JDK 类用 `resolveClass().newObject()`。装箱类型用 `DvmInteger` 一类，不能把 `Integer` 当成原始 int。示例设备和签名字节不收录。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C12 | 基本整数直接返回 | 模板 1：基本类型（int / long / boolean）— 直接返回数值 | s2，第 129 行 | source-report | I / J / Z | 示例 SDK 整数不收录 |
| C13 | 字符串用 StringObject | 模板 2：字符串 — 用 StringObject 包装 | s2，第 148 行 | source-report | Ljava/lang/String; | 示例机型字符串不收录 |
| C14 | 字节数组用 ByteArray | // 签名字节数组, 必须包成 ByteArray | s2，第 171 行 | source-report | [B | 示例字节不收录 |
| C15 | 装箱整数用 DvmInteger | 不是 int, 所以要用 DvmInteger 包装 | s2，第 210 行 | source-report | Ljava/lang/Integer; | 同行的示例整数不收录 |

<a id="interfaces"></a>
## 认栈顶方法名，只重写带 V 的重载

来源把栈顶方法拆成 call/get/set/new、可选 Static、返回类型、Method 或 Field，以及可选的 V。Unidbg 内部几乎总走带 V 的版本；不带 V 的重载被要求忽略。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C16 | callObjectMethodV 与不带 V 的不是同一个方法 | callObjectMethodV  ` 和  ` callObjectMethod  ` 是  ** 两个不同的方法 | s1，第 117 行 | source-report | AbstractJni 重载 | 该行在句中截断；后文才写 ARM va_list |

<a id="validation"></a>
## 值错了不会抛异常

类型错会崩，值错不会。来源把验收写成：同一输入下 Unidbg 的结果和真机 Frida 打出的 native 输出一致才算通，不一致就回到 r0tracer。这是 source-report，不是本次对照。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C17 | 值错只让结果错，不抛异常 | 值错了 → 代码不崩，但最终签名 / 加密结果是错的，你看不到任何报错 | s1，第 235 行 | source-report | 维度二 | 未定义哪些输出算签名 |
| C18 | 没报错不等于成功 | 千万不要以为"没报错 = 成功" | s5，第 519 行 | source-report | 验证闭环 | 要求做值对照 |
| C19 | 一致才算通 | 两个结果一致 → 真通了 | s5，第 523 行 | source-report | 作者的第 3 步 | 不一致时只说回到 r0tracer |
| C20 | 不对照就不能确认占位字符串 | 只有对照通过的补环境才是真的补环境 | s5，第 526 行 | source-report | 全篇 | 占位字符串的例子不收录 |

## 验证与限制

Unidbg 与 r0tracer 版本未知。主动调用签名字节的脚本只说明收集方式，不替代“v1 解析不到 v2 签名”那条已有诊断。没有缺样本即停止的失败出口，不建流程。
