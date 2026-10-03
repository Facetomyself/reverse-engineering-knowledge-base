---
schema_version: 2
id: libnative-getas-frida-rpc-reference
document_type: reference
original_date: '2019-11-13'
archived_date: '2026-10-02'
scope:
  targets:
    - libnative-lib getAS
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-app-20191113-01.md#不还原token算法抓取app最简单的hook方法"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 Unicorn、AndServer 和 Frida rpc 的取舍，以及本地调用边界。没有版本，也没有对照实验。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: App 未命名。类名和脚本只在图里。文本只定位 getAS、libnative-lib.so 和 Python 侧的 getas。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录 Context 与 String 两个类型。没有构造方式、字符串内容或重载。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20191113-01.md#不还原token算法抓取app最简单的hook方法"
tags:
  - frida-rpc
  - getAS
  - source-report
---

# 不还原算法时的 getAS 调用边界

这张卡只回答来源在不还原 signature 时怎么取舍工具，以及它为一个未点名 App 写下的 getAS 形状。不补脚本，也不把它写成可远程调用的服务。

来源没有可公开定位的原文 URL。出处只保留为微信公众号自述。

<a id="decision-flow"></a>
## 工具取舍

来源先承认生成代码可能在 Java 或 Native，再把 Unicorn 和 AndServer 判为繁复，最后选 Frida rpc。调用范围停在本地。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 有的生成sig/token的代码写在Java层里，有的写在Native层里。 | s1 第 39 行 | source-report | 来源的一般陈述 | 无样本计数 |
| C2 | 如果token是在so文件里，最强大的工具莫过于Unicorn | s1 第 44 行 | source-report | so 内 token | 无加载步骤 |
| C3 | 不过这两种形式，我认为对于爬虫选手来说，还是比较繁复，配置和使用麻烦，可能还要自己编译apk，在开发调试阶段费时。 | s1 第 46 行 | source-report | Unicorn 与 AndServer | 作者判断 |
| C4 | 还有一种直接调用app里so代码或java代码的方式是Frida rpc。 | s1 第 48 行 | source-report | 来源选中的调用方式 | 无 Frida 版本 |
| C9 | 上述写好的获取signature代码，还只能本地调用，不能远程调用。 | s1 第 74 行 | source-report | 这篇里写好的调用 | 远程包装没有路径或验收 |

<a id="interfaces"></a>
## getAS 与 getas

图中的类名没有进入正文。这里只保留正文写明的方法、库和 Python 侧名字。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 从上图可以看到需要调用getAS方法，它会返回一个字符串，这个字符串就是signature。  但是getAS在libnative-lib.so文件里。 | s1 第 60 行 | source-report | 来源图中的未点名 App | 无类名、无偏移 |
| C6 | 我们不用去分析这个so文件，当作一个黑匣子，直接使用frida rpc来调用getAS方法即可。 | s1 第 61 行 | source-report | 同一 getAS | 未证明 so 无额外校验 |
| C7 | 用Python直接调用getas这个函数，即可驱动frida调用该APP的getAS方法，返回signature。 | s1 第 65 行 | source-report | Python 侧名字 getas | 脚本只在图里 |

<a id="parameters"></a>
## 形参类型

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | getAS需要传入两个参数，一个Context类型，一个String，你需要构造出这两个类型的参数传入getAS。 | s1 第 70 行 | source-report | 来源图中的 getAS | 无构造方式 |

## 验证与限制

本次只读到文本，没有运行证据。作者说几行代码即可搞定，这是 source-report，不是验收。JS 与 Python 不在正文里，Hook 点找错时也没有失败出口，所以不是流程。75 到 76 行只点名再包一层 Python web server，没有路由，不建请求链。本卡不并入 MTOP InnerSignImpl，也不并入目标写成 unknown 的 Frida 技术选择卡。
