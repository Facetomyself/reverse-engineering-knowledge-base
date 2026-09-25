# 方法论：VMP 先钩宿主原语，再决定要不要纯算

> 来源: `workspace/cv-cat`（DouYin_Spider `secsdk_web_sign.py` 的定位路径，对照窗口 2026-08-16）
> 原始发布时间: 2026-08-16
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 认定目标是 stack VM 之后，先在哈希、编码和 WebCrypto 入口读明文，用换 Cookie 探针把常量池和会话材料分开，只移植已经闭合的边界。opcode 解释不是完成门。抖音 `webSignUrl` 是这条方法的完整工作样例。

工作样例的字段规则见 [webSign 案例](./douyin-secsdk-websign-case.md)。本篇不收录盐、字母表和 opcode 表。

## 何时用

请求在发出前被一段解释器改写，业务代码里搜不到返回签名的函数，静态阅读停在 `switch (opcode)`。同时调用栈或 hook 能看到它最终进入下面之一：

- `CryptoJS.MD5` / `SHA256` / `HmacSHA256`
- `SubtleCrypto.digest` / `sign` / `encrypt`
- `encodeURIComponent`、`btoa`、`JSON.stringify`
- `sm3`、`md5` 等页面自己挂到 `window` 的函数

这四类入口就是宿主原语。明文在进原语之前已经排好，VM 只是在调度它们。

## 真实流程：抖音 webSign

源码文件头记录的顺序：

1. CDP hook `XMLHttpRequest.prototype.open`，调用栈落到 security SDK。策略行是 `webSignUrl(url)` 把整条 URL 重写后再发出。
2. `webSignUrl` 本体是 stack VM，opcode 负责外部调用。静态读到这里停。
3. 在 `window.CryptoJS.MD5` 入口读明文，形状是 `{uifid}_{timestamp}_{VM_CONST}_{canonical_query}`。
4. 探针：换 `uifid`、清空 Cookie 和 storage。盐不变，且不出现在 Cookie、localStorage、策略配置里。盐归入常量池，记名 `VM_CONST`，不写进长期 SDK。
5. 只复刻规范化：原序、value 先解码再按 `encodeURIComponent` 重编码、key 只解码、裸参数补 `=`、`timestamp` 追加到末尾。
6. 与浏览器内 `webSignUrl` 对拍空格、`+`、`%`、中文、重复参数、已有签名字段。源码注释称 5 条抓包逐字节命中、20 组以上边界一致。本知识库没有重跑这组回归。
7. 发送函数返回的 URL。服务端按收到的 query 校验，HTTP 客户端再编码一次就作废。

```text
hook XHR.open / fetch
→ 找到改写 URL 的函数
→ 若函数体是 stack VM:
      hook MD5 / SM3 / SubtleCrypto / encodeURIComponent
      记录明文模板和字段顺序
      换 Cookie、清 storage:
          变的段 = 会话材料，记 provenance
          不变且不在存储里的段 = VM 常量，只记名字
      移植规范化 + 标准哈希
      oracle 对拍边界，不要求拆 opcode
      发送签名函数返回的字节
```

## 探针表

| 动作 | 若输出变了 | 若输出不变 |
|------|------------|------------|
| 换 Cookie / 清 storage | 该段是会话材料 | 继续看它是否出现在存储或策略 JSON |
| 该段出现在 Cookie 或配置 | 从那里取，不要硬编码 | — |
| 该段不在任何存储里 | — | VM 常量池。可以参与当前窗口的纯算，不能当跨版本 SDK |
| 换 UA / 屏幕 | 指纹槽，必须和当前画像绑定 | 与环境无关 |
| 换 query 一个字符 | 确认它进了明文 | 这条链可能不签 query，另找入口 |

只换一个变量。一次换 Cookie 又换 query，就分不清盐和规范化。

## 完成门

| 状态 | 含义 |
|------|------|
| 钩到明文模板 | 定位完成，还不是纯算 |
| 规范化与 oracle 逐边界一致 | 边界格式闭合，可以纯算这一层 |
| 业务 JSON 读回 | 这一层过了服务端。其它链仍要单独验收 |
| 拆完 opcode | 只有明文钩不到、或原语本身被改写时才需要 |

原语本身被改写时，钩到的「MD5」可能不是标准 MD5。这时对拍一组已知输入。标准库对得上就继续纯算；对不上就先记录差分轮次，不要把标准库结果当 oracle。

## 反面

把巨型 DOM stub 加冻住的 canvas data URL 当成已经纯算。抖音 acrawler 走的是另一条路：页面 VM 隔离执行，provenance 记 `node_page_js`，失败不写随机签名。那是预言机，不是宿主原语纯算。分流见 [纯算与预言机](./purecalc-vs-oracle-cost.md)。
