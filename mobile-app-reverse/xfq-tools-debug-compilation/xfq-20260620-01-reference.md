---
schema_version: 2
id: libcore-xfcryptohook-capture-reference
document_type: reference
original_date: '2026-06-20'
archived_date: '2026-10-02'
scope:
  targets: ["libcore XfCryptoHook capture"]
  client: Android libcore/ROMManager
  version: feature/crypto-hook-structured
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20260620-01.md#51-两级门禁
    basis: source-report
  - id: s2
    ref: ./xfq-20260620-01.md#52-算法路由
    basis: source-report
  - id: s3
    ref: ./xfq-20260620-01.md#53-json-字段
    basis: source-report
  - id: s4
    ref: ./xfq-20260620-01.md#61-cipher
    basis: source-report
  - id: s5
    ref: ./xfq-20260620-01.md#64-参数来源
    basis: source-report
  - id: s6
    ref: ./xfq-20260620-01.md#八测试-apk
    basis: source-report
  - id: s7
    ref: ./xfq-20260620-01.md#三整体数据流
    basis: source-report
  - id: s8
    ref: ./xfq-20260620-01.md#一功能目标
    basis: source-report
  - id: s9
    ref: ./xfq-20260620-01.md#十踩坑与后续维护规则
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s6, s7, s8, s9]
    basis: source-report
    limits: 放行顺序和类优先路由是 2026-06-20 笔记对 XfCryptoHook 的描述。用户可见开关已由 2026-06-22 的 UI 卡改为大类属性，本卡不把 hook_* 当成当前门禁。
  - name: parameters
    anchor: parameters
    sources: [s3]
    basis: source-report
    limits: 只保留 jsonl 字段和 mode 词表。不重列已被 UI 卡替换的细粒度属性表。
  - name: interfaces
    anchor: interfaces
    sources: [s4, s5]
    basis: source-report
    limits: 只保留 AAD、wrap 可导出性和 PBE 不明文这三条记录边界。其余类名清单不单独成模块。
relations:
  - type: derived_from
    target: ./xfq-20260620-01.md#51-两级门禁
  - type: derived_from
    target: ./xfq-20260620-01.md#52-算法路由
  - type: derived_from
    target: ./xfq-20260620-01.md#53-json-字段
  - type: derived_from
    target: ./xfq-20260620-01.md#61-cipher
tags: [libcore, jca, cryptohook]
---

# libcore XfCryptoHook 的放行顺序和事件字段

这张卡回答 bootclasspath 上的 Java 算法采集何时允许打日志、类和算法名冲突时归谁，以及 `crypto.jsonl` 里有哪些字段。用户看到的大类开关、派生 `java_trace` 和刷机后的 2110 行结果已经在 `../../signature-algorithms/xfq-crypto-notes-compilation/xfq-20260622-01.md`。本卡不另建那套 UI，也不把旧的 `hook_*` 键写成当前门禁。

<a id="decision-flow"></a>
## 先轻量预检，再按类路由

采集是按应用打开的：目标应用的 `java_trace` 不为 1 就不进逻辑；只开主开关、不开算法范围也不落算法数据。热路径先调用 `appTraceMaybeEnabled()`，只做 uid、包名和属性判断；`emit()` 确认应用、主开关、范围和过滤条件之后才写日志。调用栈在确认会输出之后才采。数据流把这条路径限制在 uid 大于等于 10000 的应用进程。

`algKey` 先看类，再看算法名。`SecretKeySpec` 归密钥生成，不能因为名字里有 AES 就进对称算法。参数类归参数。`Signature` 优先于哈希，避免 `SHA256withRSA` 被当成摘要。这些桶名是本篇的路由标签；2026-06-22 的笔记已经声明旧细粒度键不再是 UI 语义。

测试包只作为普通应用安装。若构建把 `XfCryptoHookTest` 放进 system 分区的暂存目录，打镜像前要删掉。只刷 product 时要带同一构建的 vbmeta，否则 AVB 可能不一致。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 主开关按应用打开 | 不开目标 App 的 `java_trace` 不采集。 | s8，第 60 行 | source-report | 应用 opt-in | 后一卡把该键改成由大类派生 |
| C2 | 没开算法范围就不落数据 | 只开主开关但没开算法按钮时不落算法数据。 | s8，第 61 行 | source-report | 算法范围 | “算法按钮”是本篇 UI，不是后一卡的 chip |
| C3 | 只处理应用 uid | 目标 App 进程（uid >= 10000） | s7，第 142 行 | source-report | 数据流 | 未给出判断代码 |
| C4 | 第一级只做轻量判断 | `appTraceMaybeEnabled()`：轻量预门禁，只做 uid/package/prop 快速判断。 | s1，第 206 行 | source-report | 热路径 | 未给出属性读取实现 |
| C5 | 第二级确认后才写日志 | `emit()`：最终门禁，确认 app、主开关、算法范围、过滤条件后才生成日志。 | s1，第 207 行 | source-report | 热路径 | 过滤条件的文法不在本篇 |
| C6 | 调用栈延后采集 | 在 `emit()` 确认会输出后再采，避免无效开销。 | s1，第 215 行 | source-report | callstacks | 未说明栈深度 |
| C7 | 路由先看类 | `algKey(alg, cls)` 先看 class，再看算法名： | s2，第 219 行 | source-report | 分类 | 桶名是 06-20 标签 |
| C8 | 密钥规格不能被 AES 抢走 | `SecretKeySpec` 必须归 `hook_keygen`，不能因为算法名是 AES 就被 `hook_aes` 接管。 | s2，第 221 行 | source-report | SecretKeySpec | 不是当前 UI 键名 |
| C9 | 带 SHA 的签名仍是签名 | Signature 类优先归 `hook_sig`，避免 `SHA256withRSA` 被误判为 hash。 | s2，第 223 行 | source-report | Signature | 未列出全部签名算法 |
| C10 | 测试包不能进系统镜像 | `XfCryptoHookTest` 只作为普通 `/data/app` 安装验证，不进入 system image。 | s8，第 64 行 | source-report | 测试 APK | 后一卡已写普通安装 |
| C11 | 镜像暂存目录要删 | 生成 system image 前要删除该 staging 目录，避免误内置。 | s6，第 380 行 | source-report | system/app 暂存 | 路径在上一节，本卡不抄设备号 |
| C12 | product 刷机要配 vbmeta | 否则可能 AVB 不一致。 | s9，第 453 行 | source-report | Pixel 7 product 分区 | 未给刷机命令 |

<a id="parameters"></a>
## crypto.jsonl 的字段和 mode

文件一行一个事件。来源列出的核心字段是时间、编号、包名、类、方法、算法、mode，以及 key、iv、aad、输入、输出、tag 长度和调用栈，另加参数来源类字段。mode 词表分成加解密与包装、摘要与签名、密钥与参数、编码与压缩。logcat 用给人读的分块；文件保留完整 JSON。具体键值不收录。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C13 | 一行一个事件 | `crypto.jsonl` 一行一个事件，核心字段： | s3，第 228 行 | source-report | /data/misc/rommgr/<pkg>/ | 目录权限不在本篇展开 |
| C14 | 字段包含材料和调用栈 | ts, id, pkg, cls, method, alg, mode, | s3，第 231 行 | source-report | 事件对象 | 下一行列出 key/iv/aad/in/out |
| C15 | 加解密 mode | encrypt / decrypt / wrap / unwrap | s3，第 240 行 | source-report | mode 词表 | 未说明 init 是否单独成行 |
| C16 | 编码和压缩 mode | encode / decode / zip / unzip | s3，第 243 行 | source-report | mode 词表 | 上层 zip 是否都落到 deflate 只在后文 |

<a id="interfaces"></a>
## 三条容易记错的记录边界

GCM 的附加数据不在 `doFinal` 参数里，要从 `updateAAD` 累积。wrap 和 unwrap 记录包装密钥和被包装密钥，但只有 `getEncoded()` 可导出时才记材料。PBE 不记密码明文，只记长度和派生参数。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C17 | GCM 的 AAD 要另累积 | GCM 的 AAD 不在 `doFinal()` 参数里，需要从 `updateAAD()` 累积。 | s4，第 279 行 | source-report | Cipher | 未给出累积字段名 |
| C18 | 不可导出的密钥不记材料 | 只有 `getEncoded()` 可导出时记录 key material，否则标记不可导出。 | s4，第 280 行 | source-report | wrap/unwrap | 未定义标记的具体字符串 |
| C19 | PBE 不记密码明文 | PBE password 默认不记录明文，只记录长度和派生参数。 | s5，第 310 行 | source-report | PBEKeySpec | 口令本身不进入卡片 |

## 验证与限制

关闭范围后 0 行、全开后 2110 行以及模式覆盖表，是作者的设备自述，而且后一卡已经记录了打开七个新大类之后的同一行数。本卡不把这些数字当成新的验收模块。没有“预检失败就停止后续结论”的出口，不建流程。
