# flatbuf 基本结构解析

> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: mobile-app-reverse
>
> 先说结论，由于使用schema的flact引擎会自动优化flatbuf结构，而 样本 签名使用的是未优化的flatbuf结构，所以不能用schema解析。 只能使用python库flatbuffers来encode；decode使用指定的解密函数来解 flatbuf 大概由4个部分组成 [root] [vtable] [data] [ref_data] 生成一个最简单的看下 解析流程: root_ptr: [10000000] le_h

## 正文

先说结论，由于使用schema的flact引擎会自动优化flatbuf结构，而 样本 签名使用的是未优化的flatbuf结构，所以不能用schema解析。
只能使用python库flatbuffers来encode；decode使用指定的解密函数来解

flatbuf 大概由4个部分组成
[root] [vtable] [data] [ref_data]

生成一个最简单的看下
```python
import flatbuffers

def encode_data():
    builder = flatbuffers.Builder(0) # root_obj

    string = builder.CreateString("test1")
    builder.StartObject(4)
    # Slot 表示一个data段的数据槽，
    # args:(vtable 中的索引位置, 数据值，默认值
    builder.PrependInt32Slot(0, 0x1111, 0)  # value
    builder.PrependInt32Slot(1, 0x2222, 0)  # value
    builder.PrependInt32Slot(2, 0x3333, 0)  # value
    builder.PrependUOffsetTRelativeSlot(3, string, 0)  # value
    parent = builder.EndObject()
    builder.Finish(parent)
    return builder.Output()

print(encode_data().hex())

#>>> 100000000c00140010000c00080004000c00000010000000050d0000ae08000057040000050000007465737431000000
```

解析流程: 
root_ptr: [10000000] -> le_hex 0x10 -> 指向root_node, 也就是 encode_data()[4+0x10], where 4 固定的, root_ptr.size

vtable: [0c001400 10000c00 08000400] 从 vtable 指过来，结构是
{
    vtable_size (0xc);
    obj_size (0x14);
    data_ptr [1000 0c00 0800 0400];
}

root_node: [0c000000] 从root_ptr指过来，然后向前移动 0xc 位指向 vtable

root_data: [10000000 33330000 22220000 11110000] 可以看到，储存的顺序和我们写入的顺序相反，flatbuf文档也说了，是推栈然后序列化
这里 [10000000] 并不是一个具体值，而是指向当前位置+0x10 也就是 [7465737431] 开头的位置
然后存了 0x3333, 0x2222, 0x1111

ref_data: [05000000 7465737431 000000] data.len, data.value, pad

# 复杂flatbuf 的逆向

上面看了最基本的flatbuf结构，但实际应用中的flatbuf结构更复杂，下面看嵌套的，带有多种数据类型的结构
```python
import flatbuffers

def encode_data():
    builder = flatbuffers.Builder(0) # root_obj

    # 创建子对象
    child_name = builder.CreateString("Child")
    builder.StartObject(2) # 字段数量
    builder.PrependUOffsetTRelativeSlot(0, child_name, 0)  # name
    builder.PrependInt32Slot(1, 0x9999, 0)   # slot value default
    child = builder.EndObject()

    parent_name = builder.CreateString("Parents")
    builder.StartObject(99)  # 字段数量最大容量，可以随便写
    builder.PrependUOffsetTRelativeSlot(0, parent_name, 0)  # name
    builder.PrependInt32Slot(1, 0x1111, 0)  # value
    builder.PrependInt64Slot(2, 0x3333, 0)  # value
    builder.PrependInt32Slot(3, 0x4444, 0)  # value
    builder.PrependBoolSlot(4, True, 0)  # value
    builder.PrependUOffsetTRelativeSlot(5, child, 0)  # child

    parent = builder.EndObject()

    builder.Finish(parent)
    return builder.Output()

print(encode_data().hex())
# >>> 18000000000000001000240020001c0010000c000b00040010000000340000000000000133330000333300000000000000000000111100000400000007000000506172656e74730008000c0008000400080000009999000004000000050000004368696c64000000
```

回想下之前的解析流程
root_ptr -> root_node -> vtable, 然后解析data

root_ptr 往后数6个找到 root_node
[18000000] 

(pad + vtable) -> vtable
注意这里的pad是自动对齐生成的，无需干涉，如果你格式对得上就一定会有这个pad
[00000000 10002400 20001c00 10000c00 0b000400] -> [10002400 20001c00 10000c00 0b000400] (vtable.size=0x10, obj.size=0x20, data_ptr_list=[1000 0c00 0b00 0400])

root_node 往前数4个找到真实的vtable起点
[10000000] 

data_slot(root_data) 数据槽
[34000000 00000001 44440000 33330000 00000000 00000000 11110000 04000000]

[34000000] 数据指针，指向sub_obj
[00000001] bool 这种一看就是bool类型
[44440000] int32
[33330000 00000000 00000000] 实际上是 [33330000 00000000] int64 + pad[00000000]; 这个pad由序列化后的结构决定，不可人为控制；可以作为对照时的辅助信息
[11110000] int32
[04000000] 数据指针，指向string parent

data_ref 从上面指下来的数据 通常sub_obj, string 会存在这个分区
[07000000 506172656e7473 00] //parent
[08000c0008000400080000009999000004000000050000004368696c64000000] //child_obj

child_obj 解析方法和root_obj 没区别
[08000c00 08000400 08000000 99990000 04000000 05000000 4368696c64 000000] 
vtable.size = 0x8
sub_obj.size = 0xc
data_ptr = [0800 0400]
sub_obj_node = [08000000]

然后是 [99990000] int32
[04000000] 数据指针，指向[4368696c64]

ok，剩下实践就直接照着 样本 对着看就行了，还原结构比较容易；更新签名版本也是同理，往回对照就行，最后照着真实包的vtable填slot的索引，能完全一致就完事了

结构体，enum类似，照着往回对就行了

总结下flatbuf可以分成几块
root_ptr
vtable
root_node
root_data
ref_data(如果有)
child_obj(如果有)
