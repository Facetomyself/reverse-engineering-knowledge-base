---
schema_version: 2
id: android-framework-permission-gid-reference
document_type: reference
original_date: '2019-01-14'
archived_date: '2026-09-06'
scope:
  targets: [android-framework-permission]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./softard-20190114-01.md#0010-packageslist--packagesxml
    basis: source-report
  - id: s2
    ref: ./softard-20190114-01.md#android-filesystem-configh
    basis: source-report
  - id: s3
    ref: ./softard-20190114-01.md#fs_configc
    basis: source-report
  - id: s4
    ref: ./softard-20190114-01.md#0100-android-app-permission
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只保留来源点名的行格式、AID 宏和 permission 到 gid 名。7.0 得到 1015 是作者自述。不收录证书字段，也不把某一串系统 gid 当成所有平台签名包的固定集合。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s4]
    basis: source-report
    limits: 扫描、protectionLevel 删除和写回 packages.list 只有入口和作者概述。uid 生成、gid 填入进程和动态权限代码被写明不在本篇。
  - name: validation
    anchor: validation
    sources: [s2, s3, s4]
    basis: source-report
    limits: ls 与 /proc/status 是作者写下的结果。普通应用能访问 sdcard 但 Groups 没有存储 gid，撤销后 1015 仍在，来源自己标成未闭合。
relations:
  - type: derived_from
    target: ./softard-20190114-01.md#0100-android-app-permission
tags: [android-permission, packages-list, platform-xml, source-report]
---

# Android permission 名怎样对到 Linux gid

这张卡用来读 `packages.list` 的 uid、seinfo 和 gid 列，以及 `/proc/<pid>/status` 的 Groups：permission 字符串先落到 gid 名，gid 名再落到 `android_filesystem_config.h` 里的 AID 数字。来源是 [Android Framework 权限底层实现概览](./softard-20190114-01.md#0100-android-app-permission)。存储权限在 6.0 之后的摘录里没有 gid，作者称 7.0 实际看到的是 `sdcard_rw`（1015），但同文的进程 Groups 又对不上。没有前提到验收的完整路径，所以不是 procedure。依据保持 source-report。

<a id="parameters"></a>
## packages.list 列、AID 与 permission 映射

普通安装样本一行是包名、uid、一个数字、数据目录、seinfo、gid 列。来源只明确把 10052 叫 uid，并写明 uid 怎么生成要到下一篇。系统应用样本的 uid 变成 1000，seinfo 从 default 变成 platform，gid 列变成一串数字；同一次 `packages.xml` 写着 `sharedUserId="1000"`。

头文件用宏定义这些数字。`AID_SYSTEM` 的注释是 system server。`AID_APP` 的注释是 first app user。同一文件还有把数字映射成名字的结构体数组。来源用这张表把系统应用那串数字读成名字，其中 1015 对到 `sdcard_rw`，3003 对到 `inet`。

目录默认模式在 `fs_config.c`。来源摘出的 `data/data` 是 `00771`，属主和属组都是 `AID_SYSTEM`。

permission 名到 gid 名在 `platform.xml`。摘录里 `android.permission.INTERNET` 的组是 `inet`。同一段较新摘录里，`READ_EXTERNAL_STORAGE` 和 `WRITE_EXTERNAL_STORAGE` 没有 `<group>`。来源的解释是 6.0 之后存储权限要用户确认，所以这里不映射，动态权限代码本篇不分析。旧摘录则是 `<group gid="sdcard_r" />`。来源把 `sdcard_r` 对到 1028，并写 7.0 上实际得到的是 1015。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 普通安装行以 uid 10052、seinfo default、gid 列 none 结尾 | `com.softard.test 10052 1 /data/user/0/com.softard.test default none` | s1 ./softard-20190114-01.md:99 | source-report | 中间那个 1 没有字段名 |
| C2 | 10052 被认作 uid，生成规则不在本篇 | `这里10052是uid，至于其怎么生成的后面第二篇再详谈。` | s1 ./softard-20190114-01.md:102 | source-report | 没有分配算法 |
| C3 | 系统应用样本的 uid 为 1000，seinfo 为 platform，并带 gid 列表 | `com.softard.test 1000 0 /data/user/0/com.softard.test platform 3009,3002,1023,1015,3003,3001,1021,1000,2002,2950,1010,1007` | s1 ./softard-20190114-01.md:123 | source-report | 只这一次样本 |
| C4 | 同一次记录的 sharedUserId 是 1000 | `sharedUserId="1000"` | s1 ./softard-20190114-01.md:129 | source-report | 不提取证书字段 |
| C5 | system 用户的宏是 AID_SYSTEM | `#define AID_SYSTEM` | s2 ./softard-20190114-01.md:380 | source-report | 1000 与注释在同一行，中间有不间断空格 |
| C6 | 第一个应用用户的宏是 AID_APP | `#define AID_APP` | s2 ./softard-20190114-01.md:559 | source-report | 10000 在同一行 |
| C7 | 数字之外还有名字映射表 | `每个权限组都是由一串数字代表的。除了数字，该文件还定义了一个结构体数组，映射数字对应的字符串：` | s2 ./softard-20190114-01.md:581 | source-report | 不补来源没印出的名字 |
| C8 | 来源把系统应用 uid 归到 1000 | `所以，当我指定应用为系统应用时，就将uid指定为了1000。` | s2 ./softard-20190114-01.md:776 | source-report | gid 赋值被留到后文 |
| C9 | data/data 的表项是 00771 system:system | `{ 00771, AID_SYSTEM, AID_SYSTEM, 0, "data/data" }` | s3 ./softard-20190114-01.md:1014 | source-report | 未对照当前 AOSP 树 |
| C10 | INTERNET 的 gid 名是 inet | `<group gid="inet" />` | s4 ./softard-20190114-01.md:1153 | source-report | 权限名在上一行 |
| C11 | 较新摘录的读存储权限没有 group | `android.permission.READ_EXTERNAL_STORAGE` | s4 ./softard-20190114-01.md:1299 | source-report | 写存储的下一行同样没有 group |
| C12 | 空映射被解释成 6.0 后的动态存储权限 | `6.0之后存储权限变成动态，需要用户确认才可以获取权限，所以这里不作处理。` | s4 ./softard-20190114-01.md:1408 | source-report | 没有动态授权代码 |
| C13 | 旧摘录把读存储映射到 sdcard_r | `<group gid="sdcard_r" />` | s4 ./softard-20190114-01.md:1413 | source-report | 旧文件没有版本号 |
| C14 | sdcard_r 被对到 1028，7.0 被写成实际得到 1015 | `数值是1028。实际上在7.0上得到的是` | s4 ./softard-20190114-01.md:1419 | source-report | 同一行以即1015结束，没有构建号 |

<a id="decision-flow"></a>
## 从 Manifest 到 packages.list

来源的顺序是：开机扫描已安装应用的 Manifest，把信息和权限写入 packages 文件；这件事放在 PackageManagerService 启动之后。`protectionLevel` 里，normal 只在 Manifest 注册，dangerous 要动态申请，signature|privileged 被写成系统签名应用才有。三方应用若申请 signature|privileged，来源称 PMS 会把该权限从申请列表删掉，应用实际上没有得到它。

留下来的 permission 按 `platform.xml` 带上 gid。来源称 PMS 解析每个 permission 时做这步关联，gid 进入数组后，对应设备文件才可访问，但具体代码放到下一篇。给的入口是 `grantRequestedRuntimePermissions`。摘录末尾注释说可能动过 GID membership，然后调用 `mSettings.writePackageListLPr()` 把 `packages.list` 写出去。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C15 | 开机扫描 Manifest 并保存应用信息和权限 | `Android开机阶段会扫描所有App，从Manifest文件中把App信息和权限存到` | s1 ./softard-20190114-01.md:91 | source-report | 文件名被拆行 |
| C16 | 扫描解析发生在 PackageManagerService 启动之后 | `PackageManagerService在启动后会扫描所有已经安装的App，然后加载和解析他们的Androidmanifest文件，生成` | s4 ./softard-20190114-01.md:1031 | source-report | 生成物名字在后面 |
| C17 | normal 不需要动态申请 | `normal是一般权限，即不需要动态申请，直接在Manifest里注册即可获得的权限。` | s4 ./softard-20190114-01.md:1078 | source-report | dangerous 在同一行后半 |
| C18 | 三方应用申请后者时，PMS 会从申请列表删除该权限 | `PMS就会将其从申请权限的列表里将该权限删除。` | s4 ./softard-20190114-01.md:1081 | source-report | 整句还写了 signature 与 privileged 的组合级别；没有删除函数名 |
| C19 | 解析 permission 时带上文件里关联的 gid | `PMS在解析每个Permission时会根据这个文件将Permission关联的gid` | s4 ./softard-20190114-01.md:1421 | source-report | 下一行才写进数组，并声明代码不在本篇 |
| C20 | 入口函数名是 grantRequestedRuntimePermissions | `grantRequestedRuntimePermissions` | s4 ./softard-20190114-01.md:1425 | source-report | 只有签名开头 |
| C21 | 写回函数是 writePackageListLPr | `mSettings.writePackageListLPr();` | s4 ./softard-20190114-01.md:1442 | source-report | 不能证明每次授权都改 gid |

<a id="validation"></a>
## 哪些对照对上了，存储权限哪里没对上

`packages.list` 的设定被来源说成 0640、属主 system、属组 package_info。作者写下的 `ls` 是 `-rw-r----- 1 system package_info`，这一条对得上。`/sdcard` 的 `ls` 是 `drwxrwx--x`，属主 root、属组 sdcard_rw。来源由此说，拿到 `sdcard_rw` 的应用才能访问内置存储。

进程凭证对不上。普通应用加上存储权限后，Groups 只有 `9997 50053`。来源写 Groups 没有对应 gid，但程序仍能访问 sdcard。系统签名样本的 Groups 含 `1015`。从设置关掉存储权限后，应用不能读文件，再次查看 gid，1015 还在。来源把这标成 7.0 与 5.0 不同、尚未填上的坑。因此不能用「Groups 里有 1015」单独判断存储权限仍有效，也不能用「Groups 里没有 1015」单独判断不能读存储。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C22 | 作者看到的 packages.list 是 system:package_info 且属主可写 | `-rw-r----- 1 system package_info` | s2 ./softard-20190114-01.md:799 | source-report | 未复看 ls |
| C23 | 该模式被说成 0640 system:package_info | `它给packages.list文件赋予了0640的权限，权限隶属于system，权限组为package_info。` | s2 ./softard-20190114-01.md:792 | source-report | 来源写这是由参数作出的推测 |
| C24 | /sdcard 的属组被写成 sdcard_rw | `drwxrwx--x 27 root sdcard_rw` | s4 ./softard-20190114-01.md:1454 | source-report | 未复看 ls |
| C25 | 普通样本的补充组只有 9997 和 50053 | `9997 50053` | s4 ./softard-20190114-01.md:1488 | source-report | 只这一次 status |
| C26 | 来源称没有对应 gid 时仍然能访问 sdcard | `Groups没有对应的gid，但是程序的确可以访问` | s4 ./softard-20190114-01.md:1491 | source-report | 没有读文件的记录 |
| C27 | 系统签名样本的 Groups 含 1015 | `1000 1007 1010 1015 1021 1023 2002 2950 3001 3002 3003 3009 9997 41000` | s4 ./softard-20190114-01.md:1522 | source-report | 不能外推到其他系统应用 |
| C28 | 关掉存储权限后读失败，但 1015 仍在 | `从设置里手动关掉存储权限，App无法读取文件，再次检查gid发现这个1015依旧存在。` | s4 ./softard-20190114-01.md:1525 | source-report | 作者没有解释，也没有 5.0 对照数据 |

## 验证与限制

不把目录模式表里的某一行改写当成可执行步骤：来源没有构建、刷入、验收或失败出口。不把系统应用那串 permission 名称或证书片段当作映射表。`shell` 对 `data/data` 只有执行位，与 00771 的属主属组一致，但这只解释目录列表，不解释存储权限的进程组。7.0 与 5.0 的差别、动态权限如何改 gid，都还是未知。没有本地运行证据。
