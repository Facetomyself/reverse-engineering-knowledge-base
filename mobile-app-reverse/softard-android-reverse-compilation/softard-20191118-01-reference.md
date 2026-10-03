---
schema_version: 2
id: grok-mobile-app-reverse-softard-20191118-01
document_type: reference
original_date: "2019-11-18"
archived_date: "2026-10-02"
scope:
  targets: [android-framework-permission]
  client: android
  version: framework notes through Android N; pre23 means targetSdkVersion below 23
  observed_at: unknown
sources:
  - id: s1
    ref: "./softard-20191118-01.md#权限的性质"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源给出的路径、字符串形态和模式常量。未打开 AOSP 树，不收录样例证书字节，也不收录改权限命令。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 授权分支是来源对 protectionLevel 和权限组的整理。默认授予函数体未收进本卡，来源写明源码分析在下一篇。
relations:
  - type: derived_from
    target: "./softard-20191118-01.md#权限的性质"
tags: [android-permission, appops, protection-level]
---

# Android 框架权限的落点与授权分支

这张卡只回答：这份来源把权限字符串、安装记录、保护级别和 AppOps 模式放在哪些路径和常量上，以及它如何用保护级别和权限组决定是否弹窗。范围是这篇归档的文本。不收录把权限先打开再改掉的命令，也不把样例包的证书字节写进来。

<a id="parameters"></a>
## 字符串、文件和模式常量

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 权限被写成一个声明操作类型的字符串。quote: permission（权限）实际上就是一个简单的字串 | s1 ./softard-20191118-01.md:43 | source-report | 来源对 permission 的定义 | 未对照当前 SDK 常量类 |
| C2 | 定义文件写在框架清单。quote: /frameworks/base/core/res/AndroidManifest.xml | s1 ./softard-20191118-01.md:55 | source-report | AOSP 源码树路径 | 来源未给分支或标签 |
| C3 | 生成物写在 Manifest.java。quote: ./out/target/common/R/android/Manifest.java | s1 ./softard-20191118-01.md:57 | source-report | 来源所说的 out 目录 | 来源写已删掉部分代码 |
| C4 | 名字前缀是定义它的包名再加 .permission.。quote: 权限名的前缀是定义它的包名 | s1 ./softard-20191118-01.md:76 | source-report | 来源的命名规则 | 自定义权限可以不遵循这条约定 |
| C5 | 已安装权限列表用 pm list permissions。quote: pm list permissions | s1 ./softard-20191118-01.md:64 | source-report | 来源给出的查询命令 | 未在设备上执行 |
| C6 | 加 -f 会多打出定义包、label、description 和 protection level。quote: protection level | s1 ./softard-20191118-01.md:70 | source-report | pm list permissions -f | 样例输出未整段收录 |
| C7 | 包数据库路径是 /data/system/packages.xml。quote: /data/system/packages.xml | s1 ./softard-20191118-01.md:98 | source-report | 来源所说的安装记录 | 未读取任何设备上的该文件 |
| C8 | 数据库维护安装路径、版本号、签名证书、已拿权限和本机定义的全部权限。quote: 每个package拿到的权限列表 | s1 ./softard-20191118-01.md:94 | source-report | PackageManagerService 的包库 | 证书原值不进入本卡 |
| C9 | 单个 package 里，证书在 cert 标签，权限在 perm 标签。quote: 分配的权限 在 ` <perm> ` 标签下 | s1 ./softard-20191118-01.md:110 | source-report | 来源对 packages.xml 的字段说明 | 样例 uid 和证书索引不收录 |
| C10 | 默认授予 dangerous 权限的类写在 DefaultPermissionGrantPolicy.java。quote: DefaultPermissionGrantPolicy.java | s1 ./softard-20191118-01.md:198 | source-report | frameworks/base/services/core 下的 pm | 只记路径 |
| C11 | 来源点名的核心方法是 grantRuntimePermissionsLPw，并写源码分析在下一篇。quote: grantRuntimePermissionsLPw | s1 ./softard-20191118-01.md:200 | source-report | 该方法名 | 函数体不进入本卡 |
| C12 | AppOps 允许模式常量是 0。quote: MODE_ALLOWED = 0 | s1 ./softard-20191118-01.md:235 | source-report | 来源引用的 AppOpsManager | 未对照后续版本是否改值 |
| C13 | 忽略模式常量是 1，来源写尝试使用会静默失败。quote: MODE_IGNORED = 1 | s1 ./softard-20191118-01.md:236 | source-report | 同上 | 崩溃现象是来源描述 |
| C14 | 错误模式常量是 2，来源写会抛 SecurityException。quote: MODE_ERRORED = 2 | s1 ./softard-20191118-01.md:237 | source-report | 同上 | 未复现异常 |
| C15 | 默认模式常量是 3。quote: MODE_DEFAULT = 3 | s1 ./softard-20191118-01.md:238 | source-report | 来源说它不常用 | 与 appop 标志的配合未展开实现 |
| C16 | 服务把 appops.xml 放在 /data/system/。quote: /data/system/ | s1 ./softard-20191118-01.md:262 | source-report | AppOpsService 启动时创建的文件 | 样例 xml 不收录 |
| C17 | xml 里的 m="0" 被解释成 MODE_ALLOWED。quote: mode=MODE_ALLOWED=0 | s1 ./softard-20191118-01.md:280 | source-report | 来源对属性 m 的读法 | 只此一个样例 op |
| C18 | 悬浮窗操作号写成 24。quote: OP_SYSTEM_ALERT_WINDOW = 24 | s1 ./softard-20191118-01.md:285 | source-report | 来源引用的常量 | 其他 op 编号未列表 |

<a id="decision-flow"></a>
## 保护级别和权限组怎么分支

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C19 | protectionLevel 分成基础级别和附加级别。quote: 可以分为两类 | s1 ./softard-20191118-01.md:140 | source-report | 来源的分类 | 不是框架枚举的正式分组名 |
| C20 | 未写 protectionLevel 时按 normal，不需要用户确认就授予。quote: 不需要用户确认就可以直接赋予应用程序 | s1 ./softard-20191118-01.md:147 | source-report | normal | 来源陈述 |
| C21 | dangerous 不自动授权，由用户在对话框里选择。quote: 由用户进行选择是否授予权限 | s1 ./softard-20191118-01.md:152 | source-report | dangerous | 未覆盖各版本弹窗差异 |
| C22 | 请求方与声明方签名一致时，signature 自动授予，否则用 intent 把用户带到权限界面。quote: 签名一致，系统会自动赋予权限 | s1 ./softard-20191118-01.md:156 | source-report | signature | 未验证 intent 目标 |
| C23 | signatureOrSystem 被写成 signature 与 privileged 的组合。quote: privileged | s1 ./softard-20191118-01.md:162 | source-report | 来源的等价说法 | 同一行还有 signature，竖线不写入表格 |
| C24 | 同一签名的应用可以自动拿到该级别。quote: 拥有相同的签名的应用 | s1 ./softard-20191118-01.md:166 | source-report | signatureOrSystem 的第一支 | 与 C22 同源规则 |
| C25 | /system/priv-app 下的应用是另一支自动授权。quote: /system/priv-app | s1 ./softard-20191118-01.md:168 | source-report | 来源所说的特权系统应用 | 未核对分区布局 |
| C26 | 附加级别必须加在基础级别上，来源看到的搭配基本是 signature。quote: 必须附加在基础权限级别上使用 | s1 ./softard-20191118-01.md:174 | source-report | 来源观察的系统定义 | 不是形式语法 |
| C27 | pre23 在安装时自动授给 targetSdkVersion 低于 23 的应用。quote: targetSdkVersion在23（Android 6.0）以下 | s1 ./softard-20191118-01.md:178 | source-report | 来源列出的附加标志 | 同句还列了 privileged、installer 等，本行只钉 pre23 |
| C28 | 来源对 SYSTEM_ALERT_WINDOW 的组合级别写道：非系统且非预置时，把 targetSdkVersion 调到 23 以下会默认获得。quote: targetSdkVersion调至23以下，来默认获得此权限 | s1 ./softard-20191118-01.md:187 | source-report | 该权限在来源中的 protectionLevel 字符串 | 来源读法，未改包重装验证 |
| C29 | 同组还没有任何权限时，提示用权限组描述，但只授予本次申请的那一个。quote: 系统只会赋予应用之前申请的权限 | s1 ./softard-20191118-01.md:126 | source-report | 运行时权限组 | 提示文案是来源举例 |
| C30 | 同组已有其他权限时，再申请同组权限会自动授予且不再交互。quote: 不需要任何与用户的交互行为 | s1 ./softard-20191118-01.md:128 | source-report | 来源举的联系人读写 | 未覆盖后来按次授权的变化 |
| C31 | checkOp 用来检测某项操作是否允许。quote: 检测应用是否具有该项操作权限 | s1 ./softard-20191118-01.md:295 | source-report | AppOpsManager.checkOp | 来源写多数 API 只面向系统应用 |
| C32 | noteOp 在检查之后会做记录。quote: 在检验后会做记录 | s1 ./softard-20191118-01.md:299 | source-report | 与 checkOp 的差别 | 记录落盘格式未单列 |
| C33 | setMode 的 mode 表示要改成允许、禁止或提示。quote: mode代表要更改成的类型 | s1 ./softard-20191118-01.md:311 | source-report | setMode 的参数含义 | 不收录调用代码 |

## 验证与限制

近邻查询里，android-framework-permission、android-permission、appops、packages-xml 的 parameters 和 decision-flow 都没有命中。target 为 permissions、模块为 risk-control 的命中是浏览器环境探测卡，不是这份框架权限。没有本地运行证据。来源里先授权再用 AppOps 关掉的用法，以及样例包的证书字节，都不进入本卡。grantRuntimePermissionsLPw 的函数体来源自己留到下一篇。
