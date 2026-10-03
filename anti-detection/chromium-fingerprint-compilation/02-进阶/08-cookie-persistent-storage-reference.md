---
schema_version: 2
id: chromium-cookie-expiry-override-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-cookie-expiry]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./08-cookie-persistent-storage.md#2修改位置"
    basis: unknown
  - id: s2
    ref: "./08-cookie-persistent-storage.md#1加入头部引用"
    basis: unknown
  - id: s3
    ref: "./08-cookie-persistent-storage.md#3编译"
    basis: unknown
  - id: s4
    ref: "./08-cookie-persistent-storage.md#四成果测试"
    basis: unknown
  - id: s5
    ref: "./08-cookie-persistent-storage.md#二为什么要设置cookie的持久化存储"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3]
    basis: unknown
    limits: 只记录来源贴出的文件和插入点。没有 Chromium 版本，两个新增头文件在替换块里没有被引用。本轮没有源码树可对照。
  - name: parameters
    anchor: parameters
    sources: [s1, s5]
    basis: unknown
    limits: 代码赋值是 Time::Max()，正文和测试叙述是 1 年。来源没有解释 ValidateAndAdjustExpiryDate 是否改写该值。不记录任何 Cookie 样值。
  - name: validation
    anchor: validation
    sources: [s4]
    basis: unknown
    limits: 关浏览器后仍保持登录是作者自述。配图未审。不能外推到当前分支、具体站点或后续请求。
relations:
  - type: derived_from
    target: "./08-cookie-persistent-storage.md#2修改位置"
tags: [Chromium, CanonicalCookie, cookie-expiry, unknown]
---

# Chromium CanonicalCookie 过期时间覆盖

这张卡只回答一个检索问题：来源把 Cookie 过期时间改写插在 `net/cookies/canonical_cookie.cc` 的哪一次赋值上，以及哪些说法还对不齐。它不覆盖启动 switch 写入 `CookieManager::SetCanonicalCookie` 的那条链；那条链在 [Chromium 启动 CookieManager 参考](../../chromium-startup-cookie-manager-reference.md#interfaces)，并且明确没有持久化回读。

来源要求读者已会编译 Chromium，但没有版本号，也没有「改完仍按 session 过期」时的失败出口，所以这里不是 procedure。

<a id="interfaces"></a>
## 接口边界

来源打开的文件是 `net/cookies/canonical_cookie.cc`。对照片段先调用 ParseExpiration，马上交给 `ValidateAndAdjustExpiryDate`，再把 `cookie_expires` 送进 CanonicalCookie 构造函数。替换片段保持同一构造，只在两次调用之间插入赋值。

来源同时加入 `iostream` 和 `base/command_line.h`。贴出的替换块没有使用这两个头。编译命令只有 `ninja -C out/Default chrome`。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 改动文件是 cookie 实现里的 canonical_cookie.cc | `/net/cookies/canonical_cookie.cc` | s1 08-cookie-persistent-storage.md:40 | unknown | 无版本，未对当前树 |
| C2 | 覆盖之后仍进入有效期调整，再交给构造函数 | `ValidateAndAdjustExpiryDate(cookie_expires, creation_time, source_scheme);` | s1 08-cookie-persistent-storage.md:80 | unknown | 调整函数正文不在来源里 |
| C3 | 来源要求增加的头文件没有出现在替换逻辑中 | `#include "base/command_line.h"` | s2 08-cookie-persistent-storage.md:46 | unknown | 不能当成命令行开关已经接上 |

<a id="parameters"></a>
## 参数机制

替换块里唯一的新赋值是 `cookie_expires = base::Time::Max()`。动机段另写「把过期时间强制设置成 1 年」。这两个说法都在来源里，但来源没有给出从 `Time::Max()` 到 1 年的换算，也没有给出 `ValidateAndAdjustExpiryDate` 的上界。本卡只把它们记成互相未闭合的来源陈述。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C4 | 插入点上的赋值是时间上界，不是字面量 1 年 | `cookie_expires = base::Time::Max();` | s1 08-cookie-persistent-storage.md:76 | unknown | 随后仍会进入有效期调整 |
| C5 | 动机段把目标说成 1 年 | `把过期时间强制设置成1年` | s5 08-cookie-persistent-storage.md:35 | unknown | 与 C4 的关系未知 |

<a id="validation"></a>
## 验证边界

作者称运行 `./chrome.exe` 后，Cookie 过期时间全部变成 1 年后，关闭再打开仍保持登录。该段有一张未审插图。没有「过期时间未变」或「重新打开后会话丢失」时的分支。作者的成功叙述保持 source-report。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C6 | 作者把肉眼结果说成 1 年后 | `cookie的过期时间全部变成1年后了` | s4 08-cookie-persistent-storage.md:102 | unknown | 配图未审，未复现 |
| C7 | 作者把关闭再打开后的登录保持当作结果 | `将浏览器关闭后重新打开，依然可以**正常保持登录状态**了` | s4 08-cookie-persistent-storage.md:104 | unknown | 未指定站点，未读回存储 |

## 验证与限制

缺失的是版本、`ValidateAndAdjustExpiryDate` 的实现，以及两个头文件的用途。不适用启动注入、明文落盘或任意站点的登录保持。需要重验时应在标明版本的源码树上看插入点是否仍在 `ParseExpiration` 与有效期调整之间，并单独记录存储回读；本卡不提供该步骤。
