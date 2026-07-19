# Qidian 请求签名与 Fock SDK 结论更新

> 来源: `workspace/qidian`
> 原始发布时间: 2026-06-27
> 归档日期: 2026-07-05
> 分类: signature-algorithms
>
> 样本: 起点读书 7.9.464 ｜ 更新: 2026-07-15
>
> 证据: 28 MB 流量、126 条 QDSign、jadx/IDA、3DES 独立解密复核、公开实现交叉验证

## 技术摘要

起点读书通过 `FockUtil.addRetrofitH/getH` 向请求注入 QDSign、borgus、cecelia、gorgon、ibex、tstamp 等字段。早期文章把 QDSign 推测为 RSA/HMAC，并把 `libfock.so` 的 AES/Hash 链当作最终签名算法；126 条真实样本复核已推翻该判断。

当前样本的 QDSign 是固定 24-byte key 与 8-byte IV 下的 3DES-CBC 字段密文。`libfock.so` 内确实存在 AES、DES、Hash 与 CRC 代码，但其业务归属需要重新沿 JNI 调用链确认。

## 请求注入结构

~~~text
OkHttp request
  -> FockUtil.addRetrofitH(request)
     -> FockUtil.getH(...)
        -> QDSign / borgus / cecelia / gorgon / ibex / tstamp
  -> QDRequestAddKnobsInterceptor
     -> sora
~~~

Java 层负责组装和调度，Native/Fock runtime 负责部分字段生成。不能再概括为“所有签名逻辑全部位于 `libfock.so`”，因为当前 QDSign 已可由独立字段链闭环，而 `libfock.so` 中相关函数尚未完成一一映射。

## QDSign 已验证算法

### 字段与加密

~~~text
plaintext =
  marker |
  timestamp_ms |
  0 |
  QIMEI |
  1 |
  app_version |
  0 |
  MD5(payload.lower()) |
  certificate_md5

QDSign = Base64(
  3DES-CBC(
    PKCS#7(plaintext),
    STATIC_KEY_24,
    STATIC_IV_8
  )
)
~~~

`payload` 的取值随请求类型变化：

- GET 通常对应 query string；
- 无参数请求通常对应空字符串；
- POST 通常对应 body 或经过 canonicalization 的请求数据；
- 不能只凭缓存 key 猜测，需与实际 call-site/抓包关联。

### 本地复核结果

对 `analysis/qdsign_db.json` 的 126 条样本逐条执行 Base64 解码、3DES-CBC 解密和 PKCS#7 校验：

| 检查项 | 结果 |
|--------|------|
| 可正确解密并通过 padding | 126 / 126 |
| 明文为 9 个管道字段 | 126 / 126 |
| 版本字段为 `7.9.464` | 126 / 126 |
| query 小写 MD5 直接匹配 | 104 / 126 |
| QIMEI 长度 | 16 或 36 |
| 密文长度 | 128 或 144 bytes |
| 唯一首密文块数量 | 1 |

剩余 22 条不应判为算法失败，优先检查 POST body、空参数、参数排序和项目缓存 key 是否丢失了原始 canonicalization 信息。

### 固定前缀的正确解释

所有样本共享固定 Base64 前缀，原因是：

- 首个明文字段固定；
- 3DES key 和 IV 固定；
- CBC 的第一个密文块因此固定。

这不是 RSA 公钥指纹，也没有证据证明它是 FockKey ID。密文长度会随 QIMEI/字段长度从 128 bytes 变化到 144 bytes，也与固定长度 RSA 签名不符。

## 其他请求头的验证状态

以下结论来自匿名排行榜接口的重放实验，不自动外推到登录、付费、内容解密或风控接口。

| 字段 | 样本行为 | 当前解释 |
|------|----------|----------|
| `QDSign` | 删除后返回签名错误 | 排行榜样本中的必需字段 |
| `borgus` | 删除后仍成功 | 该批 endpoint 未独立校验 |
| `cecelia` | 删除后仍成功 | 该批 endpoint 未独立校验 |
| `gorgon` | 多请求中保持不变，删除后仍成功 | 更像设备/注册态材料；并非该批 endpoint 的必需字段 |
| `ibex` | 删除后仍成功 | Nib 设备指纹，在其他风控接口可能仍有意义 |
| `tstamp` | 删除后仍成功 | QDSign 明文内部仍有 timestamp；服务端是否校验取决于 endpoint |
| `QDInfo` | 删除后仍成功 | 设备信息密文，不是该批 endpoint 的必需字段 |
| `sora` | Knobs interceptor 注入 | 需按目标 URL 单独验证 |

## 重放与时效性

历史测试中，旧 QDSign 在 27 个排行榜分类接口上仍被接受。这说明这些 endpoint 没有严格执行 QDSign 内部 timestamp 的短时窗口，但不能写成“所有 QDSign 永不过期”。

正确边界：

- 已验证：指定版本、指定设备字段和排行榜 endpoint 的旧样本可重放；
- 待验证：登录、付费章节、内容 key、用户态请求和新版 App；
- 任何服务端策略变更都可能使缓存失效。

## Native/Fock 组件关系

| 组件 | 已确认 | 待确认 |
|------|--------|--------|
| `FockUtil` | 请求头注入入口、Java bridge | 不同 endpoint 对 Native 方法的选择 |
| `libfock.so` | JNI 注册、AES/DES/Hash/CRC/hex 函数 | 哪条函数链对应当前 QDSign、QDInfo 或其他 Fock 功能 |
| `libfockrt.so` | QuickJS runtime、远端配置/数据接口 | 与当前 QDSign 静态 3DES 字段链的直接关系 |
| `libnib.so` | `ibex` 设备环境链 | 服务端按 endpoint 的校验强度 |
| `libknobs.so` | `sora` / Knobs | URL 命中与配置内容语义 |

`libfock.so` 的 AES-256-CBC、自定义 sponge、SHA1 风格 Hash、MD5 和 CRC32 分析仍有价值，但现在只能作为“库内算法能力”记录，不能继续命名为最终 QDSign 算法。

## 当前复现边界

生成 QDSign 至少需要：

- 当前版本的字段 marker；
- timestamp；
- 与目标设备/会话一致的 QIMEI；
- App version；
- payload 的准确 canonicalization；
- certificate MD5；
- 对应版本的 static key/IV。

Public 知识库不保存真实设备 QIMEI、流量 Cookie、用户 token 或测试账号材料。实现中使用 `QIMEI`、`CERT_MD5`、`STATIC_KEY_24`、`STATIC_IV_8` 占位，并从项目本地 fixture 注入。

## 结论矩阵

| Claim | 状态 |
|-------|------|
| 当前 QDSign 是 RSA/HMAC | 已推翻 |
| 当前 QDSign 是 3DES-CBC 管道字段 | 已验证 |
| 固定前缀是 FockKey 标识符 | 已推翻 |
| 排行榜 endpoint 只独立校验 QDSign | 已验证于当前样本 |
| 所有 endpoint 都忽略其他头 | 未验证 |
| `libfock.so` 的 AES 链就是 QDSign | 未验证，现有网络证据相冲突 |

## 关联资料

- [Qidian Native SO 分析与结论纠偏](../native-analysis/qidian-so-analysis.md)
- [360 Jiagu VIP 绕过与脱壳能力](../packing-bypass/jiagu-bypass-analysis.md)
- [GodKeawa/AppApiCrack](https://github.com/GodKeawa/AppApiCrack)
