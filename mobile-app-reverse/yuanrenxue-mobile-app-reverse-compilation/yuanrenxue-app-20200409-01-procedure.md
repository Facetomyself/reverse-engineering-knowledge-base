---
schema_version: 2
id: yuanrenxue-app-20200409-android7-https-capture-procedure
document_type: procedure
original_date: '2020-04-09'
archived_date: '2026-07-16'
scope:
  targets: [android-7-https-capture]
  client: Android
  version: Android 7.0+ as cited
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-app-20200409-01.md#android-70-https抓包单双向验证解决方案汇总"
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: 只保留来源写明的系统信任、证书目录和权限。示例哈希、折行命令和占位包名不进入可执行步骤。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 分支按来源的四层现象分流。证书提取实例暂略，双向只有原理，签名校验没有位置。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 通过句只有重打包和 DroidSSLUnpinning 两句来源自述。本轮没有抓包。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20200409-01.md#android-70-https抓包单双向验证解决方案汇总"
tags: [android, https, certificate, source-report]
---

# Android 7 抓包分支

这张流程只覆盖来源自己划定的排查：Android 7 以后用户 CA 不被信任，以及随后的单向校验、双向校验和不常见校验。它不收录环境搭建卡里的模拟器、MoveCertificates 或另一套证书哈希命令。来源把命令折进同一行，本卡不把它们还原成脚本。

<a id="prerequisites"></a>
## 前提与输入

先有来源描述的现象，而不是先改系统分区。缺现象或缺少该支所需的材料，就停在 F1。

必需输入：

- 一台出现 Android 7 信任变化的测试机。来源写默认只信任系统级 CA。
- 用户级证书来自 `chls.pro/ssl`。来源用它说明 Charles 此时拦不到流量。
- 系统证书支需要 Root。免 Root 支需要能改 `AndroidManifest` 并重新签名；来源点名 apktool、keytool、jarsigner。
- 单向 Hook 支需要能区分 JustTrustMe 所依赖的 Xposed，或 DroidSSLUnpinning 所用的 frida。来源要求先看 CPU ABI。具体服务器文件名不进入本卡。
- 不把另一张环境卡的 `subject_hash_old` 或权限 644 混进来。本篇写的是 `subject_hash` 和 `chmod 664`。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 默认信任边界 | app 只信任系统级别的 CA | s1 :42 | source-report | 未在设备上核对信任库 |
| C3 | 文件名来自 subject_hash | -noout -subject_hash | s1 :52 | source-report | 不记录该行示例哈希 |
| C4 | 系统证书目录 | /system/etc/security/cacerts/ | s1 :53 | source-report | 推送和挂载写在同一行 |
| C5 | 本篇权限是 664 | chmod 664 | s1 :54 | source-report | 不是另一张卡的 644 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 先判断拦在哪一层：用户 CA 不被系统信任，应用自己校验，双向校验，或来源称为不常见的校验 | 一个分支名 | 只是系统信任走 S2 或 S3；单向走 S4；双向走 F6；不常见走 S6；现象不清走 F1 |
| S2 | 有 Root 且没有 Root 检测时，按来源把 Charles CA 装成系统 CA：用 subject_hash 做成带 `.0` 的文件名，放进系统 CA 目录，权限 664，然后重启 | 证书位于来源写的系统目录 | 目标有 Root 检测则改走 S3，不要停在这一支 |
| S3 | 免 Root 或存在 Root 检测时，apktool 解开清单，把 `platformBuildVersionCode` 从 26 改成 23，再打包签名 | 一份重签安装包 | 装上后用来源的抓包句验收；若还有签名校验走 F3 |
| S4 | 单向校验不要走「取出证书」：来源写实例暂略。只在 JustTrustMe 与 DroidSSLUnpinning 之间选择 | 所选工具名 | Xposed 检测或新版本失效走 F4；选择 DroidSSLUnpinning 时，脚本正文不在文字里则走 F5 |
| S5 | 双向不进入操作。来源只写应用把 Charles 当服务端、服务端把 Charles 当客户端 | 两句原理的对照 | 一律走 F6 |
| S6 | 不常见校验只记录来源的机制：钩底层 `ssl_read` 和 `ssl_write`，并且不用配置代理 | 机制分类，不是抓包结果 | 没有来源的通过句，不能拿图片当验收；材料不够走 F1 |

来源把系统 CA 写成全局生效且需要 Root，把清单降级写成只针对单个应用且无需 Root。`platformBuildVersionCode>=24` 是它给出的分界。示例清单里的包名是占位，不进入目标。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C2 | 系统 CA 需要 Root | 将 Charles CA 安装为系统级 CA | s1 :45 | source-report | 同段写明需 Root |
| C6 | Root 检测改走降级 | 目标APP 有设备 Root 检测时适用 | s1 :59 | source-report | 未看到具体检测点 |
| C7 | 示例级别 | platformBuildVersionCode=26改成 23 | s1 :62 | source-report | 示例包名是占位 |
| C9 | 签名校验没有位置 | 如果有签名校验，jadx分析修改smali绕过 | s1 :79 | source-report | 没有校验函数 |
| C10 | 取证书未写完 | 实例暂略 | s1 :97 | source-report | 搜索词不是步骤 |
| C13 | 双向第一点 | APP 以为 Charles 是服务端 | s1 :146 | source-report | 没有 Hook 点 |
| C14 | 双向第二点 | 服务端以为 Charles 是客户端 | s1 :147 | source-report | 没有证书位置 |
| C15 | 底层读写机制 | hook 底层 ssl_read 和 ssl_write 两个方法 | s1 :151 | source-report | 同段写不用代理；没有通过句 |

<a id="outputs"></a>
## 输出

只交付来源写明了完成句的两支：

- 清单降级并重签之后，来源写可以正常抓包。
- DroidSSLUnpinning 那一支，来源写 Charles 抓包恢复正常。示例进程和 `hooks.js` 正文不在文字里，不作为输出的一部分。

系统证书支停在「文件按来源放进系统目录并重启」。双向和 ssl_logger 没有完成句，输出是未验收，不是抓包结果。

<a id="acceptance"></a>
## 验收

通过只认两句来源自述，并且各管各的支：

- 重打包支：就可以正常抓包了。
- DroidSSLUnpinning 支：charles 抓包恢复正常。

反例：JustTrustMe 已勾选并重启，但来源同时写新版本会失效，也写 Xposed 检测会引出新问题。勾选本身不是通过。系统证书装完、双向原理抄完、或只看到 ssl_logger 的图片，都不是通过。编辑本卡不代替来源的那两句。本轮没有抓包。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C8 | 重打包通过句 | 就可以正常抓包了 | s1 :63 | source-report | 来源自述，本轮没有抓包 |
| C11 | JustTrustMe 不能当通过 | 在某些 App 的新版本已失效 | s1 :105 | source-report | 未复现失效版本 |
| C12 | Unpin 通过句 | charles 抓包恢复正常 | s1 :133 | source-report | 示例脚本不在文字里 |

<a id="failure-exits"></a>
## 失败出口

F1：还没有 Android 7 的系统信任现象，或所选分支缺来源点名的材料。停止该支，不改分区，也不补写脚本。

F2：目标有 Root 检测。来源写清单降级就是给这种情况用的。离开系统证书支。

F3：重打包后仍有签名校验。来源只写 jadx 分析并改 smali。没有函数位置时停止，不发明补丁。

F4：JustTrustMe 依赖 Xposed。来源写目标若检测 Xposed 会引出新问题，并且在某些新版本已失效，只能看旧版本或等更新。停止把该模块写成已经通过。

F5：单向「取出证书」在来源里实例暂略。assets 和扩展名只是线索。DroidSSLUnpinning 的脚本正文也不在文字里。两条都停止，不补步骤。

F6：双向只有两句原理。证书未定位时停止，不把「导入 Charles」写成已完成。
