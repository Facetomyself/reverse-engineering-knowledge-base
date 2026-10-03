---
schema_version: 2
id: unoptimized-flatbuf-signature-layout
document_type: reference
original_date: unknown
archived_date: '2026-09-04'
scope:
  targets: [unoptimized-flatbuf-signature]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-undated-01.md#flatbuf-基本结构解析"
    basis: source-report
modules:
  - name: parameters
    anchor: layout
    sources: [s1]
    basis: source-report
    limits: 只保留来源对示例缓冲的读法。样本没有名字，两段 hex 没有在本轮运行。
  - name: decision-flow
    anchor: parse-order
    sources: [s1]
    basis: source-report
    limits: schema 引擎按来源原文写作 flact。解密函数没有名字，嵌套示例的计数不外推。
  - name: validation
    anchor: alignment-check
    sources: [s1]
    basis: source-report
    limits: pad 和 vtable 一致只是来源的对照说法。没有不一致时的停止条件。
relations:
  - type: derived_from
    target: "./xfq-undated-01.md#flatbuf-基本结构解析"
tags: [flatbuf, flatbuffers]
---

# 未优化 flatbuf 的布局对照

这张卡只回答：来源为什么拒绝用 schema 解析它所说的签名缓冲，以及它如何读 root、vtable、倒序 data 和自动 pad。不提供编码实现，也不把示例 hex 当成已复核的抓包。

<a id="layout"></a>
## 布局

来源把缓冲分成 `[root] [vtable] [data] [ref_data]`。最小示例里，root_ptr 的 4 字节按小端读成偏移，来源写这 4 字节大小是固定的。vtable 前两项是 vtable_size 和 obj_size，后面是各槽相对偏移。root_node 向前移动它写出的 `0xc` 指向 vtable。data 与写入顺序相反；字符串槽里的值是相对当前的偏移，不是字符串本身。ref_data 按长度、值和 pad 来读。

嵌套示例把 `StartObject` 的参数写成最大容量，来源说可以随便写，所以 `99` 不是字段个数。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C3 | 四段名称 | [root] [vtable] [data] [ref_data] | s1 :41 | source-report | 后文还拆出 root_node 和 child_obj |
| C4 | root_ptr 小端偏移 | root_ptr: [10000000] -> le_hex 0x10 | s1 :68 | source-report | 只对应最小示例 |
| C5 | 由 root_node 回看 vtable | 向前移动 0xc 位指向 vtable | s1 :77 | source-report | 0xc 同时是该例的 vtable_size |
| C6 | data 倒序 | 储存的顺序和我们写入的顺序相反 | s1 :79 | source-report | 来源归因于推栈 |
| C7 | 对象容量不是字段数 | builder.StartObject(99) | s1 :102 | source-report | 同段注释写可以随便写 |

<a id="parse-order"></a>
## 何时不用 schema

来源的结论是：它写的 flact 会自动优化结构，而样本签名用的是未优化结构，所以不能用 schema 解析。encode 只用 python 的 flatbuffers；decode 交给一个没有命名的解密函数。嵌套对象仍按 root_ptr、root_node、vtable 再读 data。来源对那一份嵌套缓冲写的是从 root_ptr 往后数到 root_node，这个数不外推到别的缓冲。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 未优化结构不用 schema | 所以不能用schema解析。 | s1 :37 | source-report | 引擎名保持原文 flact；样本无名 |
| C2 | encode 与 decode 分开 | 只能使用python库flatbuffers来encode | s1 :38 | source-report | 解密函数没有名字 |
| C8 | 嵌套示例的起点算法 | root_ptr 往后数6个找到 root_node | s1 :122 | source-report | 只描述这一份缓冲 |

<a id="alignment-check"></a>
## 对齐与版本对照

pad 由对齐自动出现。来源写格式对上就一定会有这块 pad，并且不能手改；int64 旁边多出来的 pad 可以当对照，不能当输入。更新签名版本时，照真实包的 vtable 填 slot 索引，来源把完全一致当成做完。结构体和 enum 也是往回对。来源没有写不一致时停在哪里。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C9 | 对齐 pad 用来确认格式 | 如果你格式对得上就一定会有这个pad | s1 :126 | source-report | 没有不对上的分支 |
| C10 | pad 不能手改 | 这个pad由序列化后的结构决定，不可人为控制 | s1 :138 | source-report | 紧挨一份 int64 读法 |
| C11 | 版本对照的完成说法 | 能完全一致就完事了 | s1 :156 | source-report | 没有失败出口 |

## 验证与限制

样本产品、版本和解密函数都不在来源里。两段 hex 是来源打印的 Builder 输出，本轮没有运行。末尾的分区名单把 root_node、root_data 和 child_obj 又列了一次，不增加新的通过条件。
