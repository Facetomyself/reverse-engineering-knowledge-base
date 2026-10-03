---
schema_version: 2
id: softard-so-algorithm-constant-identification-reference
document_type: reference
original_date: '2026-06-04'
archived_date: '2026-09-06'
scope:
  targets:
    - Android SO standard algorithm constants in IDA
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./softard-20260604-01.md#三常见特征常量"
    basis: source-report
  - id: s2
    ref: "./softard-20260604-01.md#四静态搜不到时的应对"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留正文里能读到的识别常量。MD5 T 表和若干初始化向量的代码围栏粘成 ounter(line，不把粘连行当成完整表。没有目标 SO 或 IDA 会话。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2]
    basis: source-report
    limits: 只保留来源的分叉：findcrypt 或 Alt+I，再用第五个初值、表首字节或结构分开算法。动态扫描没有地址、时机或命中记录。
  - name: risk-control
    anchor: risk-control
    sources: [s2]
    basis: source-report
    limits: 只说明加固 SO 加密 .rodata 时静态搜常量会失效。没有点名具体壳，也没有解密 stub 的定位。
relations:
  - type: derived_from
    target: "./softard-20260604-01.md#三常见特征常量"
tags:
  - ida
  - findcrypt
  - aes
  - md5
  - sha1
  - source-report
---

# IDA 中用特征常量区分 SO 里的标准算法

这张卡只回答：来源在 IDA 里看到不认识的加密函数时，用哪些常量、表首字节和结构把它收成 MD5、SHA1、AES、HMAC、Base64、CRC32、TEA 或 RC4。它不提供可运行的识别脚本，也不覆盖常量被改写之后的对抗；那是下一篇的范围。来源是 [IDA 逆向 SO 算法的路径](./softard-20260604-01.md#三常见特征常量)。

<a id="parameters"></a>
## 参数机制

来源把识别依据收成一句：`每个主流算法在实现时，都会硬编码一些魔法常量或固定查找表`。下面只列正文里可读的判别值。围栏粘连的整表不抄。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 标准实现靠规范常量，改掉就不再是该算法 | 每个主流算法在实现时，都会硬编码一些魔法常量或固定查找表 | s1 :56 | source-report | IDA 里的 Android SO | 没有证明某份 SO 未改常量 |
| C2 | AES 加密方向看 256 字节表，首字节 0x63 | 大概率就是 AES 加密方向 | s1 :84 | source-report | 数据段为明文时 | 粘连围栏不是完整 S-Box |
| C3 | AES 解密方向的逆 S-Box 首字节是 0x52 | 看表的第一个字节就能判断是加密还是解密 | s1 :86 | source-report | 同一张表的首字节 | 未给出逆表其余字节 |
| C4 | 轮常量 Rcon 共 10 个，用来再确认 AES | 轮常量 Rcon，10 个值 | s1 :88 | source-report | Key Schedule | 数列行的空白不是普通空格，不抄整行 |
| C5 | 四个初值同时出现就按 MD5 记，手搜 0x67452301 | 基本锁定是 MD5 | s1 :104 | source-report | Alt+I 搜立即数 | 前四个值与 SHA1 共用 |
| C6 | IV 和 T 表都命中才不再怀疑 MD5 | 两个都中就不用怀疑了 | s1 :128 | source-report | findcrypt 双命中 | T 表围栏不可抄 |
| C7 | 有第五个值 0xC3D2E1F0 才是 SHA1 | 是 SHA1，没有是 MD5 | s1 :138 | source-report | 前四个初值已经出现时 | 未核对轮函数 |
| C8 | SHA1 四个轮常量配合 80 轮，用来和 MD5 二次分开 | 可以和 MD5 做二次确认 | s1 :145 | source-report | 轮常量交替出现 | 轮常量围栏粘连 |
| C9 | SHA256 的八个初值不会和 MD5/SHA1 混 | 和 MD5/SHA1 完全不同，不会混淆 | s1 :150 | source-report | 8 个 32 位初值 | K 表只给了开头 |
| C10 | 密集的 64 位初值按 SHA512 记 | 看到 64 位大常量密集出现就是 SHA512 | s1 :160 | source-report | 64 位常量 | 只给了两个开头 |
| C11 | HMAC 没有自己的表，靠 0x36 与 0x5C 两次 hash | （ipad）异或 | s1 :169 | source-report | 同一 hash 调用两次 | 未给 key 填充长度 |
| C12 | Base64 补齐符是 ASCII 0x3D | 也是 Base64 特征 | s1 :182 | source-report | MOV 立即数 0x3D | 字母表围栏粘连 |
| C13 | 一个函数加载两张表时，来源按 URL-safe 与标准表并存记 | 同时加载两张表 | s1 :185 | source-report | +/ 与 -_ 互换 | 没有参数位定义 |
| C14 | CRC32 还要看到 0xFFFFFFFF 初值与收尾取反，配 256 项表 | 看到这个常量配合 256 项的表 | s1 :195 | source-report | 表头若干 dword | 表只给了开头 |
| C15 | 0x9E3779B9 再配位移，按 TEA 系列记 | 配合位移操作就是 TEA 系列 | s1 :207 | source-report | 32 轮、v0/v1 | 不区分 TEA、XTEA、XXTEA |

<a id="decision-flow"></a>
## 怎么分支

来源先走常量，常量没有再看结构。插件入口是 findcrypt3：`运行插件会弹出命中列表` 不在本表里单列，手搜原句是 `findcrypt 的原理是搜特征常量`（:72），快捷键写成 Alt+I。命中后按 `X` 看交叉引用。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C16 | 前四个初值不够，必须再看有没有 0xC3D2E1F0 | 是 SHA1，没有是 MD5 | s1 :138 | source-report | MD5 与 SHA1 | 见 C7 |
| C17 | 没有常量时，hash 看 64 或 80 轮和大循环移位 | 64 轮或 80 轮大循环 | s2 :230 | source-report | MD5/SHA 结构 | 来源说深度改造后结构也会变 |
| C18 | 没有常量时，AES 看 16 字节分组和四步 | 固定 16 字节分组处理 | s2 :236 | source-report | AES 结构 | 没有函数边界 |
| C19 | 没有固定常量的 RC4 只看 256 字节顺序初始化和两轮 swap | 结构就是 RC4 | s1 :218 | source-report | 结构，不是立即数 | 没有密钥调度长度 |
| C20 | 结构也看不出时，来源改去等壳解密后再扫内存 | 就要用 | s2 :242 | source-report | 动态分支的入口句 | 后半句在 :243，没有样本命中 |

:242 的后半是 `动态分析`，:243 写 `扫内存就能找到 AES S-Box 或 MD5 的初始化向量`。这是作者给出的下一步，不是已完成的扫描。

<a id="risk-control"></a>
## 静态搜索会停在哪里

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C21 | 特征常量搜索要求数据段没有被加密 | 数据段没有被加密 | s2 :223 | source-report | findcrypt 与立即数搜索 | 未描述解密函数 |
| C22 | 加固把 .rodata 加密后，两种静态搜索都失效 | 这种情况下就还有2个应对方案 | s2 :224 | source-report | 加固 SO | 两个方案是结构，以及 :242 的动态分析 |

## 验证与限制

- 同一目标的 parameters、decision-flow、risk-control 查询没有命中。`xtime in GF(2^8) / AES-style finite-field arithmetic` 的 parameters 是 GF(2^8) 乘 2，不是这张识别表。`IDA/Windows WORD` 的 parameters 是字长，也不是算法常量。
- 没有目标包名、SO 名、IDA 版本，也没有本次打开数据库的交叉引用。
- 代码围栏大量 `ounter(line` 粘连。上表不采用那些行。
- 插件安装被来源写成以后另文，不在本卡。
- 动态扫描若也找不到常量，来源没有写停止条件，所以这不是流程卡。
