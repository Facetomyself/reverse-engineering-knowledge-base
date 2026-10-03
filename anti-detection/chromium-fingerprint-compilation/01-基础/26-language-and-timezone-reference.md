---
schema_version: 2
id: chromium-timezone-language-switches-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-02"
scope:
  targets: [chromium]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./26-language-and-timezone.md#三更改语言"
    basis: unknown
  - id: s2
    ref: "./26-language-and-timezone.md#四2025-01-22追加通过读文件方式获取时区参数"
    basis: unknown
  - id: s3
    ref: "./26-language-and-timezone.md#五2025-05-08追加"
    basis: unknown
  - id: s4
    ref: "./26-language-and-timezone.md#二修改源码"
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s4]
    basis: unknown
    limits: 只保留来源写出的开关、相对路径和示例时区字符串。没有 Chromium 版本，也没有语言或时区的读取验收。示例标签不是采集样本。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3, s4]
    basis: unknown
    limits: 按来源出现的先后记录三处插入点。来源没有写三处能否同时保留，也没有写 CommandLine 在这些函数里是否已经可用。
relations:
  - type: derived_from
    target: "./26-language-and-timezone.md#二修改源码"
  - type: derived_from
    target: "./26-language-and-timezone.md#三更改语言"
  - type: derived_from
    target: "./26-language-and-timezone.md#四2025-01-22追加通过读文件方式获取时区参数"
  - type: derived_from
    target: "./26-language-and-timezone.md#五2025-05-08追加"
tags: [chromium, timezone, language]
---

# Chromium 语言开关与时区注入位置

这张卡只回答这篇归档把界面语言和默认时区接到了哪些现成开关、哪个相对路径，以及哪几个函数。它不证明改完后与代理出口地理一致。

来源先写了一条非源码办法：改 Windows 时区设置。源码部分先后出现三套写法：在 `timezone.cpp` 写死时区、启动时把 `--timezone` 写入 `./timezone.txt` 再读回、以及后来在 `InitializeICU` 里 `adoptDefault`。后一处被写成更合适的传参位置，但正文没有要求删掉前两处。

<a id="parameters"></a>
## 参数

语言不改函数，只追加两个已有 Chrome 开关。时区侧有写死字符串、`--timezone` 加相对路径文件，以及同一开关直接交给 ICU 三种形态。文件打不开时的宿主时区回退是该片段的 else，不是操作步骤的失败出口。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 语言被写成追加两个已有开关，没有源码插入点。 | `--lang=en-US`和 `--accept-lang=en-US` | s1 26-language-and-timezone.md:57 | unknown | Chromium 启动参数，版本未知 | 示例语言标签是作者所写，不是采集样本。 |
| C2 | 第一处时区被写成日本时区字面量，其他时区要自行更换。 | TimeZone::createTimeZone(icu::UnicodeString::fromUTF8("Asia/Tokyo")) | s4 26-language-and-timezone.md:42 | unknown | `timezone.cpp` 的第一处替换 | 只是示例字符串，不是某次运行读到的时区。 |
| C3 | 有 `--timezone` 时把开关值写入 `./timezone.txt`，来源用这句话说明文件桥。 | 将`--timezone`获取的值写入`./timezone.txt` | s2 26-language-and-timezone.md:99 | unknown | `PostCreateThreadsImpl` 追加段 | 相对路径的工作目录没有写出。 |
| C4 | 没有该开关时删除这个文件。 | std::filesystem::remove(timeZonePath); | s2 26-language-and-timezone.md:91 | unknown | 同一追加段的 if 分支 | 只看到删除调用，没看到文件如何被创建的完整包含关系。 |

<a id="interfaces"></a>
## 注入位置

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C5 | 第一处文件是 ICU 的 `timezone.cpp`，原调用是宿主时区检测。 | TimeZone *default_zone = TimeZone::detectHostTimeZone(); | s4 26-language-and-timezone.md:36 | unknown | 第一节源码替换 | 来源写这个文件收不到参数，所以它不是传参方案。 |
| C6 | 传参受阻后，来源改成启动时写文件、稍后在这里再读。 | 因为这个文件接收不到参数，所以我的解决方案是：启动时将参数写进一个文件中，后续这里再读文件的。 | s4 26-language-and-timezone.md:53 | unknown | 对 `timezone.cpp` 的约束 | 当时还没给出读写代码。 |
| C7 | 文件桥的读失败分支回到宿主时区检测。 | default_zone = TimeZone::detectHostTimeZone(); | s2 26-language-and-timezone.md:121 | unknown | 2025-01-22 的读文件片段 | 这是代码 else，不是流程失败出口。 |
| C8 | 后一处改在 `icu_util.cc` 的 `InitializeICU`，创建时区后 `adoptDefault`。 | icu::TimeZone::adoptDefault(default_zone); | s3 26-language-and-timezone.md:168 | unknown | 2025-05-08 追加 | 来源称这里更合适，没有写是否仍保留文件桥或写死时区。 |

## 验证与限制

来源没有时区 ID 或语言列表的读取条件，也没有编译失败时停在哪里。`ninja -C out/Default chrome` 只是随文出现的命令字面量。Chromium 版本、三套改动是否同时保留、`./timezone.txt` 的工作目录，以及 `InitializeICU` 执行时命令行是否已解析，都仍然未知。代理 IP 所在地和时区不一致只被写成改时区的动机，不够单独做成风控模块。
