---
schema_version: 2
id: cocos2dx-lua-xxtea-luac-reference
document_type: reference
original_date: '2020-08-03'
archived_date: '2026-10-02'
scope:
  targets:
    - Cocos2dx-lua
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s0
    ref: "./yuanrenxue-app-20200803-01.md#安卓逆向之luac解密反编译"
    basis: source-report
  - id: s1
    ref: "./yuanrenxue-app-20200803-01.md#加密流程"
    basis: source-report
  - id: s2
    ref: "./yuanrenxue-app-20200803-01.md#解密逻辑"
    basis: source-report
  - id: s3
    ref: "./yuanrenxue-app-20200803-01.md#加密sign的找寻方法"
    basis: source-report
  - id: s4
    ref: "./yuanrenxue-app-20200803-01.md#加密key的找寻方法"
    basis: source-report
  - id: s5
    ref: "./yuanrenxue-app-20200803-01.md#解密实现"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s0, s1, s2]
    basis: source-report
    limits: 只保留文件头、luacompile 参数和 xxtea 的三项输入。算法实现与脚本正文都在外链，不在本卡。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3, s4, s5]
    basis: source-report
    limits: sign 与 key 的位置来自来源叙述。IDA 不能运行时只改走 strings，正文没有解密失败的停止条件。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20200803-01.md#加密key的找寻方法"
tags:
  - cocos2dx-lua
  - xxtea
  - source-report
---

# Cocos2dx-lua：luac 头里的 sign 和 so 里的 key

这张卡只回答：来源如何区分 lua、luac、luaJIT，以及这套轻量加密的 sign 和 key 写在哪里。不收录 xxtea 实现，也不收录外部解密脚本正文。

<a id="parameters"></a>
## 文件头和加解密输入

来源把脚本分成三种。明文 `.lua` 可以用 IDE 打开。luac 的文件头是 `0x1B 0x4C 0x75 0x61 0x51`。luaJIT 的文件头是 `0x1B 0x4C 0x4A`，后一个字节在正文里被换行拆开，导语里写在同一句。

正向命令是 `cocos luacompile`，带 `-e`、`-k`、`-b` 和 `--disable-compile`。`--disable-compile` 在来源里拆成两行。`-k` 是加密 key，`-b` 是加密 sign。

解密被写成 xxtea。来源称只需要文件路径、加密 sign、加密 key。实现指向 Cocos 第三方库里的 xxtea 目录，步骤不在正文。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | luac 头为 0x1B 0x4C 0x75 0x61 0x51 | s0 第 38 行「文件头特征为0x1B 0x4C 0x75 0x61 0x51」 | source-report | 来源区分的三种 lua 文件 | 没有样本文件 |
| C2 | luaJIT 头为 0x1B 0x4C 0x4A | s0 第 33 行「文件头特征为0x1B 0x4C 0x4A」 | source-report | 同上 | 该句在导语，后文把末字节拆到下一行 |
| C3 | 加密用 luacompile 的 -e -k -b | s1 第 47 行「cocos luacompile -s 未加密源码目录 -d 加密后源码目录 -e -k 加密key -b 加密sign --disable-」 | source-report | Cocos 这套打包命令 | 下一行才把 flag 补成 compile |
| C4 | 解密输入是路径、sign、key，算法名为 xxtea | s2 第 53 行「只需要三个条件，文件路径&加密sign&加密key就能解密」 | source-report | 来源称为官方轻量加密 | 算法源码不在正文 |

<a id="decision-flow"></a>
## sign 和 key 放在哪

sign 在 `.luac` 文件头里。来源的找法是打开项目中的一个 `.luac`，取第一个字符串。

key 在打包后的 `libcocos2dlua.so`。第一条路：用 IDA 全局搜索刚才的 sign，命中结果上方 3 行是 key。第二条路：来源写 IDA 在 macOS 10.15.5（19F101）上无法运行，改执行 `strings -a libcocos2dlua.so`，再查找 sign，其上方字符串就是 key。

外部脚本的用法只到命令：把脚本放在 assets，修改 `decode.sh` 的 `SIGN` 和 `KEY`，执行 `sh ./decode.sh src`。来源称 luac 会备份到 `src_backup`，解密后的 `.lua` 在 `src`，用 IDE 打开即看到源码。脚本正文和 Windows 工具只有链接。

IDA 不能启动时来源改走 strings，这仍是找 key 的成功分支。正文没有写第一个字符串不是 sign、或解密结果不是 lua 源码时如何停止，所以不建流程。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | sign 是 .luac 里的第一个字符串 | s3 第 61 行「sign在.luac文件头中」；第 62 行「找第一个字符串」 | source-report | 来源打开的项目内 luac | 没有给出该字符串 |
| C6 | IDA 中 sign 命中上方 3 行是 key | s4 第 68 行「在该结果的上方3行能够发现加密key」 | source-report | libcocos2dlua.so | 依赖已从 luac 读出的 sign |
| C7 | IDA 不可用时用 strings -a，sign 上方即 key | s4 第 70 行「strings -a libcocos2dlua.so」；第 71 行「观察sign上方的字符串，即为key」 | source-report | 来源的 OSX 环境 | 没有样本输出 |
| C8 | 脚本入口是 sh ./decode.sh src，备份目录为 src_backup | s5 第 83 行「sh ./decode.sh src」；第 88 行「src_backup」 | source-report | 来源演示的 assets 目录 | 脚本正文不在来源 |

## 验证与限制

demo 的产品名只在图片中。样本 sign 和 key 都没有写入正文。xxtea 实现和 `decode.sh` 都不在本卡。顶象 DXRisk 的 parameters 是 riskToken 线格式，并且写明不收录 XXTEA key，不覆盖这里的 luac 定位。本次没有运行 strings 或解密脚本。
