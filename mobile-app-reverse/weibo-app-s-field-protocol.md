---
schema_version: 2
id: weibo-app-s-field-protocol
document_type: archive
original_date: "2021-02-13"
archived_date: "2026-10-30"
scope:
  targets: [weibo]
  client: app
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: https://www.52pojie.cn/thread-1370540-1-1.html
    basis: source-report
relations:
  - type: supplements
    target: ../web-reverse/weibo-request-planes.md#interfaces
source_completeness: partial
tags: [weibo, generateS, sha512, native, source-report]
---

# 微博极速版 s 字段（Null_Null，2021-02-13）

作者 Null_Null 于 2021-02-13 22:00 编辑。帖子标题是「从零开始逆向分析APP系列----微博APP协议分析」。作者本来想看微博 APP，后来改看体积更小的极速版，包名写成 `com.sina.weibolite`。准备工具是 JADX、Frida、IDA Pro。

PC / 移动网页请求面和上传校验在 [微博请求面](../web-reverse/weibo-request-planes.md)。那篇不覆盖极速版 `generateS`。本文只补这篇 2021 年来源里的 s 字段叙述，不把两套请求面合成一个结论。

## 清洗与完整性说明

- 登录包整段不入库。不保留会话头原值、账号字段里的手机号、口令密文样值，以及论坛附件令牌。
- 来源有 8 张截图（1.png 至 8.png），只有附件链接，没有本地图片。缺图处不补结论。
- Hook 日志里的账号与口令拼接、其余参数样值、两次 SHA-512 摘要原值都不入库。
- 因此完整性为 partial。作者的 hook 输出和「算法基本就是这样」都是 source-report。本次没有装包、没有 hook、没有对拍 so。

## 来源正文

### 作者要查的字段

作者在调用微博极速版接口时，修改参数不能通过校验，服务端返回：

```json
{"errmsg":"客户端身份校验失败","errno":-105,"errtype":"DEFAULT_ERROR","isblock":false}
```

登录请求的主机和路径是 `POST https://api.weibo.cn/2/account/login`。作者点名要查的是 `s`。作者认为它不像一般哈希的长度。请求里同时出现的字段名包括 `c`、`i`、`s`、`u`、`p`、`getuser`、`getoauth`、`getcookie`、`lang`、`aid`、`from`。这些字段的原值不入库。`User-Agent` 被写成 `okhttp/3.12.1`。

### 从字符串搜到 calculateS / generateS

JADX 搜索字符串 `s` 后，作者注意到 `calculateS`，再转到 Frida。实际 hook 的类是 `com.sina.weibo.security.WeicoSecurityUtils`，方法是 `generateS(a, b, c, d, e)`。作者的脚本在实现里调用原方法，并打印 `b, c, d, e` 和返回值。启动命令写成：

```text
frida -U -f com.sina.weibolite -l js/hookWeibo.js
```

作者还写了主动调用：用 `android.app.ActivityThread.currentApplication().getApplicationContext()` 取 context，再调用 `generateS`。四个字符串参数的角色，按作者叙述是账号与口令的拼接、第二个字符串、一个渠道类参数、第四个数字串。样值不入库。作者称除拼接串以外，有的参数能在提交参数里找到，有的是固定值，没有再展开。

### so 里的分流

作者把 apk 改后缀取出 `libnative-lib.so`。导出符号是 `Java_com_sina_weibo_security_WeicoSecurityUtils_generateS`。缺图，下面只保留作者反编译里写明的调用和分支，不把寄存器临时名收成新的算法，也不补作者没有贴出的 `aa4` 实现。

作者描述的顺序是：

1. 取出四个字符串参数。第四个字符串交给 `verify(env, context, fourth)`。
2. `FindClass("com/weico/international/mvp/v2/AboutActivity")`，调用静态方法 `forVerify()Ljava/lang/String;`，再 `strcmp` 返回值与 `"#*123321"`。
3. 作者注释里的条件是：`strcmp` 结果为 0 时，再要求 `verify` 的结果为 1，并且第三个字符串的首字节非 0。作者认为这组判断是在确认客户端，避免别人打包后直接调这个 so。
4. 条件成立时，回调 Java `WeicoSecurityUtils.aa4(String, String, String)`，把这个返回值当作 `generateS` 的结果。
5. 否则 `sprintf("%s%s", first, second)`，再调用 `WeicoSecurityUtils.aa3(String)`。

### 两次 SHA-512 之后怎样取字符

作者接着 hook `com.weico.international.utility.KotlinUtilKt.sha512`，打印入参和结果。两次摘要的十六进制原值不入库。作者用文字描述的取字符方式是：

- 取第二次 SHA-512 十六进制的当前字符，在 `"0123456789abcdef"` 里找作者所谓的对应位置，再用这个位置去第一次 SHA-512 里取字符。
- 作者举的第一步写成：第二个摘要的第 0 个字符，对应位置是 11，于是取第一个摘要的第 11 位。
- 然后把偏移累加，用第二个摘要的下一字符继续。作者称当再次取到的字符使位置为 0 时，后面的字符串不再变化。

作者让读者对照 Java 代码理解，但帖子没有再贴出 `aa4` 的 Java 源码。缺图，本文不把「位置 11」改成另一种下标，也不把这段口述补成可运行实现。

作者的收尾是：极速版把核心放在 Java 里，so 这边更多是客户端判断后回调 `aa4` 或 `aa3`。这是作者当时的判断。

## 复用边界

类名、so 名、`#*123321`、`aa3` / `aa4` 分流和 SHA-512 取字符的口述，都只属于这篇 2021-02-13 的 source-report。登录材料、会话、手机号、参数密文和附件令牌已去掉。8 张图没有审。不能据此认为当前微博客户端仍是这条 `generateS`，也不能把作者日志里的返回值当成已对拍的 `s`。
