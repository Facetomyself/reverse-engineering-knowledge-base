---
schema_version: 2
id: native-analysis-qidian-so-analysis
document_type: reference
scope:
  targets:
  - qidian
  client: Android native
  version: source report 7.9.464; exact target build unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: '`本地项目分析材料（定位不公开）`'
  reason: 出处来自原归档来源字段；本地路径已省略，原始材料未随本文公开，本轮未重跑来源实验。
- id: s2
  ref: ../signature-algorithms/qidian-fock-signature.md#fock-request-injection
  basis: source-report
source_completeness: unknown
modules:
- name: parameters
  anchor: qdsign-3des-pipeline
  sources: [s1]
  basis: source-report
  limits: 126 条样本和字段结论均来自来源报告；本轮未运行解密、未做服务端回读。
- name: validation
  anchor: qdsign-3des-pipeline
  sources: [s1, s2]
  basis: source-report
  limits: 来源报告中的样本复核不能升级为本轮 runtime 或 serverAccepted。
- name: request-chain
  anchor: fock-request-assembly
  sources: [s2]
  basis: source-report
  limits: 仅补充来源报告中的 FockUtil/Knobs 请求装配、canonicalization 和排行榜样本边界；未运行目标 App、未验证其他 endpoint。
relations:
  - type: supplements
    target: ../signature-algorithms/qidian-fock-signature.md#fock-request-injection
tags:
- libfock.so
- libfockrt.so
- ARM64
- JNI动态注册
- 3DES-CBC
- AES-256-CBC
- QuickJS
- Unicorn
- 结论纠偏
original_date: '2026-06-27'
archived_date: '2026-07-05'
---

# Qidian Native SO 分析与结论纠偏

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: `workspace/qidian`
> 原始发布时间: 2026-06-27
> 归档日期: 2026-07-05
> 分类: native-analysis
</details>
>
> 样本: 起点读书 7.9.464 ｜ 分析区间: 2026-06-27 至 2026-07-05 ｜ 更新: 2026-07-15
>
> 工具: radare2 6.1.8、IDA Pro 9.3、Unicorn 2.1.4、jadx 1.5.5

## 技术摘要

早期分析正确识别了 Fock SDK 的 Native 组件、JNI 动态注册、QuickJS runtime 和 `libfock.so` 内的自实现 Hash/AES 代码，但把 QDSign 的密文长度直接解释为 RSA-1024，并将一条 AES/Hash 函数链归因于当前版本 QDSign。后续对 126 条真实 QDSign 样本完成解密复核，已确认当前样本使用 3DES-CBC 与管道字段，不是 RSA，也没有证据表明 `libfock.so` 的 AES 链就是线上 QDSign。

本文保留已经验证的 Native 结构结论，同时明确撤销过度推断。

<a id="qdsign-3des-pipeline"></a>
## 可复用提炼：QDSign 的来源报告边界

来源报告将当前样本描述为 3DES-CBC 与九段管道字段，并明确撤销“RSA-1024”以及把 `libfock.so` AES 链直接归因于线上 QDSign 的旧推断。报告还称 126 条样本中 104 条可直接匹配 URL query 的小写 MD5，其余需要继续关联 POST body、空参数和 canonicalization。

这些数字和算法归属均是 `source-report`，本轮没有运行解密或服务端回读。复用时应先固定目标 build、请求 canonicalization 和 QIMEI 变体，再分别确认网络字段与 Native 算法调用归属；不能把库内存在 AES/DES 实现当成 QDSign 使用证据。

<a id="fock-request-assembly"></a>
## 可复用提炼：FockUtil/Knobs 请求装配与排行榜边界

这段只补充 [Qidian 请求签名与 Fock SDK 归档](../signature-algorithms/qidian-fock-signature.md#fock-request-injection)中独立于 3DES/QDSign 算法的调用链和 endpoint 范围，不重复其字段密文公式。

### 请求链与 canonicalization

来源报告给出的装配顺序是：

```text
OkHttp request
  -> FockUtil.addRetrofitH(request)
  -> FockUtil.getH(...)
  -> QDSign / borgus / cecelia / gorgon / ibex / tstamp
  -> QDRequestAddKnobsInterceptor
  -> sora
```

其 payload 边界按来源描述分开记录：GET 通常关联 query，无参数请求关联空字符串，POST 则可能关联 body 或请求数据的 canonicalization。来源报告明确还有 22 条样本不能直接用 query 的小写 MD5 解释；不能把上述概括扩写成统一的 GET/POST 算法。

### 头字段删除探针

下表只记录来源报告对匿名排行榜样本的逐头删除结果，不外推到登录、付费、内容 key 或风控接口：

| 探针 | 来源报告结果 | 适用边界 |
|---|---|---|
| 删除 `QDSign` | 返回签名错误 | 当前排行榜样本中为必需字段 |
| 删除 `borgus`、`cecelia` | 仍成功 | 该批 endpoint 未独立校验 |
| 删除 `gorgon`、`ibex`、`tstamp`、`QDInfo` | 仍成功 | 不能因此判定其他接口不需要；`ibex` 更像设备/注册态材料 |
| `sora` | 由 Knobs interceptor 注入 | 仍需按目标 URL 单独验证 |

### 排行榜重放范围

来源报告称旧 QDSign 样本曾在 27 个排行榜分类接口上被接受。可复用的边界只有“指定版本、设备字段和该组 endpoint 的历史重放范围”；它不等于所有 QDSign 永不过期，也不覆盖登录、付费章节、内容解密、用户态或新版 App。

## 文件清单

| 文件 | 大小 | 架构 | 已确认角色 |
|------|------|------|------------|
| `libfock.so` | 154 KB | ARM64 | Fock Native 函数、JNI 动态注册；与当前 QDSign 的精确函数映射仍需补证 |
| `libfockrt.so` | 1.2 MB | ARM64 | 内嵌 QuickJS runtime，承载 Fock runtime 脚本与配置处理 |
| `libnib.so` | 138 KB | ARM64 | 设备环境与 `ibex` 指纹链 |
| `libknobs.so` | 150 KB | ARM64 | `sora` / Knobs 配置链 |
| `libcrypto.so` | 1.6 MB | ARM64 | APK 内 OpenSSL 组件；`libfock.so` 未直接导入其 EVP/RSA 符号 |

## QDSign 结论纠偏

### 已撤销的旧判断

| 旧判断 | 新证据 | 当前结论 |
|--------|--------|----------|
| 128 bytes 等于 1024 bit，因此是 RSA-1024 | 126 条样本密文长度分为 128 bytes 和 144 bytes，随字段长度变化 | 密文长度来自分组加密与 PKCS#7 padding，不能据此判断 RSA |
| 固定 Base64 前缀是 FockKey 标识符 | 126 条样本的首个 3DES-CBC 密文块完全相同，明文首字段、key 和 IV 固定即可产生该现象 | 固定前缀是固定首明文块的 CBC 结果，不是 key ID 证据 |
| `libfock.so` 的 AES/Hash 链就是 QDSign | 126/126 样本可被另一条 3DES-CBC 字段链正确解密 | AES/Hash 链确实存在，但业务归属待重新映射 |

### 当前已验证格式

~~~text
QDSign = Base64(
  3DES-CBC(
    PKCS#7(
      marker | timestamp_ms | 0 | QIMEI | 1 |
      app_version | 0 | MD5(payload.lower()) | certificate_md5
    ),
    STATIC_KEY_24,
    STATIC_IV_8
  )
)
~~~

公开实现 `GodKeawa/AppApiCrack/Qidian/crypto.py` 提供了该字段链。本地使用项目捕获的 126 条 QDSign 做独立复核：

- 126/126：Base64 解码、3DES-CBC 解密和 PKCS#7 padding 均有效；
- 126/126：明文均为 9 个管道字段，版本字段均为 `7.9.464`；
- 104/126：第 8 字段直接匹配 URL query 的小写 MD5；
- 其余 22 条需要继续关联 POST body、空参数和请求 canonicalization，不能只按缓存 key 反推；
- QIMEI 长度有 16 和 36 两类，对应密文长度 128 和 144 bytes。

因此，当前版本 QDSign 的网络格式已经闭环；`libfock.so` 内 AES/Hash 代码的真实调用用途需要单独分析，二者不能再混写成同一结论。

## `libfock.so` 已确认结构

### 关键函数

| 函数 | 地址 | 大小 | 已确认程度 |
|------|------|------|------------|
| `JNI_OnLoad` | `0x9690` | 892 B | 高：执行 RegisterNatives |
| `fock_uksf` | `0xad60` | 800 B | 中：参与 Fock key/sign 相关处理，具体线上字段待动态映射 |
| `fock_lk` | `0xac58` | 264 B | 中：文本/数据加密包装 |
| `fock_35775553` | `0x16f60` | 160 B | 高：引用 hex 表的编码函数 |

### 密码函数证据

`libfock.so` 未导入 OpenSSL 的 RSA/HMAC/EVP 接口，但静态代码中存在：

- 标准 MD5 结构；
- 自定义 sponge Hash；
- SHA1 风格变体；
- 标准 CRC32 选择器；
- AES-256-CBC 与 DES-CBC 风格实现；
- hex 编解码表 `0123456789abcdef` / `fedcba9876543210`。

这些证据只能证明库内具备相应算法，不能仅凭函数存在就把它们绑定到 QDSign。正确做法是继续沿 JNI 注册表、Java bridge 参数、调用 xref 和运行时输入输出做归属确认。

## `libfockrt.so` 与 QuickJS

已确认：

- `libfockrt.so` 内嵌 QuickJS；
- 存在 `Java_com_yuewen_fockrt_vm_QuickJS_*` JNI 方法族；
- runtime 会访问 `fockrt.yuewen.com/files?t=1` 一类配置/数据接口；
- 返回字段包含 Base64 包装的加密数据。

尚未闭环：

- `/files?t=1` 的 `Sign` 公式；
- 返回数据与当前 3DES QDSign 的直接关系；
- QuickJS 字节码中的具体 key/config 派生逻辑。

早期文档把该接口直接串成“bootstrap key → FockKey → QDSign”的唯一链路，证据不足。当前应将其记录为 Fock runtime 子链，等待调用点和真实数据流闭合。

## Jiagu 与运行时边界

| 时间 | 结果 | 准确定性 |
|------|------|----------|
| 2026-07-02 | Frida spawn 成功，拦截 `raise(SIGKILL)` 后进程继续存活 | 已验证，但会话约 5 秒后断开 |
| 2026-07-05 | 阻断 `PR_SET_PTRACER`、`PR_SET_DUMPABLE`、`PR_SET_SECCOMP` 后进程持续存活 | 已验证，但 Frida transport 仍约 2 秒断开 |
| 2026-07-05 | ARM64 `libfock.so` 在 LDPlayer x86_64 native bridge 下 JNI 注册失败 | 已验证，动态 QDSign hook 需 ARM64 环境复核 |

这不是“Frida 持久绕过完成”。目前只证明终止路径和部分 `prctl` 链可被压制，仍存在 direct syscall、transport close、watchdog 或匿名执行段中的第二检测链。

## DEX 与 SO 分工结论

对起点读书 7.9.464 的原始 APK 与设备安装版 APK 做逐 DEX SHA-256 对比，12 个 DEX 全部一致。因此该样本的 Java/Kotlin 业务代码原本就是明文，Jiagu 重点保护位于 Native 反调试、反注入和运行时解密段；“先脱 DEX 再分析业务”并不是必要前提。

2026-07-14 的 panda 实测又从运行进程导出 13 个标准 DEX。这证明 whole-DEX 导出路线可运行，但不能反推原始 12 个 DEX 曾被加密。两类证据应分别表述：

- APK 对比回答“磁盘 DEX 是否被壳加密”；
- 运行时 dump 回答“进程内能否恢复标准 whole DEX”；
- 方法体是否被抽取、动态回填或迁移到 Native，仍需单独检查。

## 当前结论矩阵

| Claim | 状态 | 证据 |
|-------|------|------|
| 当前 QDSign 使用 3DES-CBC 管道字段 | 已验证 | 126/126 捕获样本可解密 |
| 固定 QDSign 前缀代表 RSA/FockKey ID | 已推翻 | CBC 首块解释 + 可变密文长度 |
| `libfock.so` 内存在 AES/Hash/CRC 实现 | 已验证 | IDA/Unicorn 静态与模拟证据 |
| AES/Hash 链就是当前 QDSign | 待验证 | 与 3DES 网络格式冲突，缺少调用链映射 |
| `libfockrt.so` 内嵌 QuickJS | 已验证 | JNI 符号与 runtime 结构 |
| 起点 7.9.464 的 12 个 DEX 被 Jiagu 加密 | 已推翻 | 安装前后 SHA-256 全一致 |
| Jiagu Frida 持久绕过完成 | 未完成 | 进程存活但会话仍断开 |

## 后续验证

1. 在 ARM64 真机或可靠 ARM64 runtime 中，从 `FockUtil.getH/addRetrofitH` 追到实际 JNI 注册函数，重新给 `fock_uksf/fock_lk` 定义业务角色。
2. 对 22 条非直接 query-MD5 样本关联请求 body 和 canonicalization，补齐 GET/POST 统一规则。
3. 对 `libjiagu_vip.so` 的运行时解密段、匿名 RX/memfd 和 direct syscall 做 dump/fix 后分析，不继续只叠加 Frida survival hook。
4. 将 `qidian-fock-signature.md` 与本结论保持一致，避免旧的 RSA/AES 推测继续进入新项目。

## 关联资料

- [Qidian 请求签名分析](../signature-algorithms/qidian-fock-signature.md)
- [360 Jiagu VIP 绕过与脱壳能力](../packing-bypass/jiagu-bypass-analysis.md)
- [P4nda0s/panda-dex-dumper](https://github.com/P4nda0s/panda-dex-dumper)
- [GodKeawa/AppApiCrack](https://github.com/GodKeawa/AppApiCrack)

## 提炼说明（559）
retain existing reference。QDSign/Fock 边界已在本文。
不扩卡，不升 runtime。
