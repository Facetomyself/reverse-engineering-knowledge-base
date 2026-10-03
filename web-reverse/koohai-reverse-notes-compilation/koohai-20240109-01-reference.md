---
schema_version: 2
id: koohai-fart-dex-dump-points
document_type: reference
original_date: '2024-01-09'
archived_date: '2026-09-06'
scope:
  targets: [fart]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20240109-01.md#fart源码分析以及改进"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录作者点名的脱壳点和 ArtMethod 上的 DexFile 范围。aospxref 链接没有对应到本地行号，youpk 只被当作合并时的参照。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: ClassLoader 遍历和“与 Frida 同用时注释 ActivityThread”是作者的改进笔记。自定义方法名不在上游 AOSP 里，本文不补实现。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 目录、cookie 字段和 jar 命令按原文保留，含作者写错的 jar 名。没有样本 dex，不能把这些路径当成已经导出的文件。
relations:
  - type: derived_from
    target: "./koohai-20240109-01.md#fart源码分析以及改进"
tags: [fart, android, source-report]
---

# FART 抽取壳的脱壳点与目录开关

这张卡只回答：作者把 FART 的脱壳点放在哪些 DexFile 入口，ClassLoader 怎么往父链走，以及用哪个目录决定要不要脱。依据停在 source-report。`fart` 与 `youpk` 的 interfaces、decision-flow、parameters、validation 都没有已发布卡片。反射演示和文末的 dex2c、vmp 两个名字没有步骤，不单列模块。

<a id="interfaces"></a>
## 脱壳点

作者用 android-13.0.0_r3 的交叉引用当阅读入口，并把脱壳收成“找到 DexFile”。`DexFileLoader::openCommon` 被单独标成脱壳点。整体加固时，解释器 `Execute` 在方法名含 `<clinit>` 时取出 `Begin()` 和 `Size()`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 源码阅读入口是 `http://aospxref.com/android-13.0.0_r3/`。 | s1 ./koohai-20240109-01.md:37 | source-report | fart | 只有链接，没有本地树 |
| C2 | `DexFileLoader::openCommon` 被写成一个脱壳点。 | s1 ./koohai-20240109-01.md:110 | source-report | fart | 没有函数体行号 |
| C3 | 脱壳的本质就是找到 DexFile。 | s1 ./koohai-20240109-01.md:116 | source-report | fart | 作者概括，不是文件格式说明 |
| C4 | `Execute` 里若方法名含 `<clinit>`，就调用 `savedexfileByExecute`。 | s1 ./koohai-20240109-01.md:160 | source-report | fart | 只覆盖作者插入的分支 |
| C5 | 取出范围的两行是 “begin_=dex_file->Begin()” 和 “size_=dex_file->Size()”。 | s1 ./koohai-20240109-01.md:178-180 | source-report | fart | 没有对应的内存转储 |

<a id="decision-flow"></a>
## ClassLoader 与调用时机

抽取型从 `ActivityThread` 走到应用 ClassLoader，再沿 parent 调用，跳过 `BootClassLoader`。`loadClass` 被写成不会执行方法体。函数体若仍是另一段加密函数，不执行就还不是最终内容。加固后的 PathClassLoader 加载到的可能是壳。和 Frida 一起用时，作者要求注释掉 `ActivityThread` 里的自动调用，改由 Frida 收集 ClassLoader。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | “loadClass(eachclassname);  这样调用不会运行”。 | s1 ./koohai-20240109-01.md:350 | source-report | fart | 没有对照主动 invoke 的结果 |
| C7 | 某些函数体是另一个加密函数，不执行就还不是最终函数。 | s1 ./koohai-20240109-01.md:528 | source-report | fart | 没有点名是哪一个壳 |
| C8 | 有加固时 PathClassLoader 加载的是壳的 dex。 | s1 ./koohai-20240109-01.md:534 | source-report | fart | 没有壳的代际判定 |
| C9 | 要用 Frida 动态获取所有 ClassLoader，再调用 `fartwithclassloader`。 | s1 ./koohai-20240109-01.md:536 | source-report | fart | 方法名是作者加进镜像的 |
| C10 | 为了和 Frida 一起用，就注释掉 `activityThread.java` 里的调用。 | s1 ./koohai-20240109-01.md:543 | source-report | fart | 原文把 Frida 写成了 frdai |

<a id="parameters"></a>
## cookie、指令片段和目录开关

类名列表用的 cookie 是 `DexFile.mCookie`，作者也写了 `mInternalCookie`。指令片段落到应用数据目录下的 bin，再交给一个 jar 填回 dex。是否脱壳由 `/data/local/tmp/koohai/<包名>/saveDex` 是否存在决定，白名单和黑名单是该目录下两个文本文件。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | “DexFile.mCookie  实际上openDex的返回值就是mcookie”。 | s1 ./koohai-20240109-01.md:332 | source-report | fart | 字段代际差异未写 |
| C12 | 指令片段路径写在 “/data/data/%s/koohai/%d_ins_%d.bin”。 | s1 ./koohai-20240109-01.md:507 | source-report | fart | 没有实际文件 |
| C13 | 修复命令原文是 “java -jar dexifxer-main.jar a.dex a.bin out.dex”。 | s1 ./koohai-20240109-01.md:523 | source-report | fart | jar 名与上文 dexfixer 不一致 |
| C14 | 开关是 “new File("/data/local/tmp/koohai",curPackName+"/saveDex").exists()”。 | s1 ./koohai-20240109-01.md:653 | source-report | fart | 这是开关，不是脱壳成功条件 |
| C15 | 白名单文件是 “saveDex/includeClassName.txt”，黑名单是 “saveDex/filterClassName.txt”。 | s1 ./koohai-20240109-01.md:671-675 | source-report | fart | 路径引号在原文里是断的 |

## 验证与限制

jadx 打不开时，作者只说关掉右下角插件里的验证，并提醒很多类仍是空壳，然后用类名前缀写进白名单。这不是通过条件。崩溃类名被手工追加到过滤文件，也没有“补采后如何判断已经完整”的标准。反射打印构造方法的演示、以及文末单独列出的 dex2c 和 vmp，都没有可复用步骤。因此不建流程。
