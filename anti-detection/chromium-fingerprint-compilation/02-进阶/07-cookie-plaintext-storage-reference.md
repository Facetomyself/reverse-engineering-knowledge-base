---
schema_version: 2
id: chromium-cookie-plaintext-storage-reference
document_type: reference
archived_date: '2026-10-02'
scope:
  targets: [chromium-cookie-plaintext]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./07-cookie-plaintext-storage.md#一目标"
    basis: unknown
  - id: s2
    ref: "./07-cookie-plaintext-storage.md#二浅析cookie存储方式"
    basis: unknown
  - id: s3
    ref: "./07-cookie-plaintext-storage.md#三修改chromium源码"
    basis: unknown
  - id: s4
    ref: "./07-cookie-plaintext-storage.md#四成果测试"
    basis: unknown
  - id: s5
    ref: "./07-cookie-plaintext-storage.md#五安全提醒"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3]
    basis: unknown
    limits: 只定位 sqlite 文件角色和 `sqlite_persistent_cookie_store.cc` 里两处 `crypto_` 判断。不转写替换块，不补能够写入明文列的实现，也不讨论密钥导出。
  - name: parameters
    anchor: parameters
    sources: [s3]
    basis: unknown
    limits: 粘贴包含 command line 头文件，但两处替换都没有读取开关。可见条件只有 `cur_version == 23` 和 `crypto_`。没有字段样值。
  - name: validation
    anchor: validation
    sources: [s3, s4, s5]
    basis: unknown
    limits: 作者关于 value 列和异地登录的句子保持作者自述。静态对照下，替换块仍调用加密函数，不能把该自述当成已闭合结果。图片未审。没有失败出口。
relations:
  - type: derived_from
    target: "./07-cookie-plaintext-storage.md#三修改chromium源码"
tags: [Chromium, CookieStore, sqlite, unknown]
---

# Chromium Cookie 库加密接缝与一篇未闭合的明文改写

这张卡记录来源把 Cookie 持久化加密放在哪，以及粘贴的改写为什么还不能当成明文存储实现。它不提供可用的明文写入，不包含任何 Cookie、密钥或账号材料。已有的启动 CookieManager 卡是另一条注入链，不覆盖这个 sqlite 加密点。

<a id="interfaces"></a>
## 存储角色与两处判断

作者把 Cookie 库放在用户数据目录下的 `Network/Cookies`，并说明它是没有后缀的 sqlite。密钥材料被描述为 `Local State` 里的 `encrypted_key`；换环境会换密钥，所以复制数据库不能直接沿用。这是作者对默认存储的说明，不是本轮打开的数据库。

改写文件是 `/net/extras/sqlite/sqlite_persistent_cookie_store.cc`。第一处在 `cur_version == 23` 的迁移里，原条件 `if (crypto_)` 被收成空块，紧接着写成 `if (!crypto_)`。第二处在 `PendingOperation::COOKIE_ADD`，同样先收起 `if (crypto_)`，再进入 `if (!crypto_)`，但块内仍然调用 `crypto_->EncryptString(...)`。可见替换没有展示把明文绑到 value 列的语句。因此这篇粘贴不能复用为“跳过加密”的实现。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 作者把默认库放在用户数据目录的 Network/Cookies，并称其为 sqlite | user-data-dir/Default/Network/Cookies | s2 07-cookie-plaintext-storage.md:32 | unknown | 作者描述的默认路径 | 本轮未打开该文件 |
| C2 | 作者把密钥字段放在 Local State 的 encrypted_key | 秘钥的位置在`user-data-dir/Local State` | s2 07-cookie-plaintext-storage.md:37 | unknown | 作者描述的 JSON 字段角色 | 不记录字段内容 |
| C3 | 改写点文件是 sqlite persistent cookie store | *   打开：`/net/extras/sqlite/sqlite_persistent_cookie_store.cc` | s3 07-cookie-plaintext-storage.md:46 | unknown | 所示路径 | 未核对当前树 |
| C4 | 迁移块只包住版本 23 |   if (cur_version == 23) { | s3 07-cookie-plaintext-storage.md:60 | unknown | 第一处粘贴 | 其他版本未出现 |
| C5 | 第一处替换把后续逻辑放进 `!crypto_` |     if (!crypto_) { | s3 07-cookie-plaintext-storage.md:88 | unknown | 迁移替换的开头 | 空 `crypto_` 上的后续调用未在该行闭合 |
| C6 | 第二处替换内部仍调用 EncryptString |             if (!crypto_->EncryptString( | s3 07-cookie-plaintext-storage.md:137 | unknown | COOKIE_ADD 替换块 | 与“不再加密”的目标句不一致 |

<a id="parameters"></a>
## 没有新的开关合同

两处替换都没有读取命令行。作者包含了 command line 头，但本篇没有对应的 `HasSwitch`。能从粘贴里定位的条件只有数据库版本 23 和 `crypto_` 是否为空。不把任何列值、域名或密钥写进本卡。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C7 | 粘贴引入了 command line 头，但所示替换不用它做分支 | #include "base/command_line.h" | s3 07-cookie-plaintext-storage.md:52 | unknown | 头部引用块 | 两处替换都没有 HasSwitch |

<a id="validation"></a>
## 作者自述没有被粘贴闭合

作者称运行后记录进入 value 列而不再是加密列，并把 A 点的数据库复制到 B 点后仍保持登录。这两句保持作者自述。静态上看，COOKIE_ADD 的替换仍走 `EncryptString`，所以不能把“已经明文”写成代码形态已经证明的事。图片未审。安全段只提醒明文有泄密风险，没有写迁移失败、加密失败或版本不是 23 时怎么退出。缺失败出口，且输出与粘贴不一致，因此不是 procedure。

启动期 CookieManager 注入卡覆盖的是另一条 `SetCanonicalCookie` 链，不包含这个 sqlite 条件。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C8 | 作者称结果落在 value 列且变为普通文本 | cookie全部存到了value列 | s4 07-cookie-plaintext-storage.md:158 | unknown | 作者的运行叙述 | 与 C6 的粘贴不一致，本轮未复现 |
| C9 | 作者称复制数据库后另一环境仍保持登录 | B端发现可以直接**正常保持登录状态**了。 | s4 07-cookie-plaintext-storage.md:160 | unknown | 作者的 A/B 叙述 | 没有请求或账号材料，未复现 |
| C10 | 作者提醒明文存储有泄密风险 | 但需注意明文存储存在泄密风险。 | s5 07-cookie-plaintext-storage.md:165 | unknown | 作者的安全提醒 | 不是失败出口 |

未知：当前树的 schema 版本、`crypto_` 为空时 `EncryptString` 那一行是否还能编过，以及 value 列与 encrypted value 列哪一个会被后续读取。本卡不补这些缺口。
