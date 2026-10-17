---
schema_version: 2
id: web-reverse-yuanrenxue-match-31-aes-memory-scan-source-archive
document_type: archive
original_date: unknown
archived_date: "2026-10-13"
scope:
  targets: [yuanrenxue-match-31]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s/QW-pPE1ae1lBOiyrtbv8Xw"
    basis: source-report
source_completeness: partial
tags: [yuanrenxue, match-31, WASM, AES-128, key-schedule, source-report]
---

# 别逆 wasm 里的 VM，扫一遍内存就拿到 AES key

## 清洗与完整性说明

保留来源关于 WASM AES key-schedule、CBC 首块和跨会话前缀的分析结构及通用方法；确切 AES key、IV、token、明文 / 密文样值与对应输出已脱敏。来源中的通用扫描代码保留为来源报告原文，不代表本轮已对目标执行；来源称其为公开练习题，本轮未访问目标。由于样值删节，标记 `partial`。

<a id="source-body"></a>
## 来源正文

本文目标为公开逆向练习靶站猿人学 match/31，仅供学习交流；文中复现代码已逐字节验证，不用于任何其他用途。

* * *

`match/31` 的 `token` 是 64 个 base64 字符，解出来 48 字节，正好 3 个 16 字节块。它跟上一题 match/30 是一套题面：JSVMP 外壳 + wasm 做密码。

但 31 挖了个坑等着你。它的 wasm 里反编译出来，标准 AES 的 S-box 被拆散了、找不到，连 wasm 自己都被**二次虚拟化**成了一台解释器。明摆着在诱你：这看着像魔改算法，来逐 op 逆我这台 VM 吧。

别上当。这一篇讲怎么绕开那台 VM，**扫一遍 wasm 的内存，几秒钟把 AES key 捞出来**。文中复现我都跑过，byte-exact。

* * *

一、先看 token 形状，不用碰代码
-------------------

两次独立会话的 token 并排一放，信息就出来了：

`[两个独立会话的 token 样值已脱敏]`

**前 21 个字符两次完全相同，后面全变。** 21 个 base64 字符差不多就是第一个 16 字节块。一个密文第一块恒定、后面随时间变的分组密码，基本就是：**固定 IV 的 CBC，而且明文第一块是常量。**`/api/question/31` 恰好 16 字节，后面证实了它就是第一块。

跨会话比一下公共前缀，分组大小、加密模式、明文首块是不是常量，三个问题一次回答。这是上来最便宜的一步。

二、认清形状：壳拼明文，wasm 做加密
--------------------

`31.js` 是 JSVMP 外壳加一个内嵌 wasm 的加载器：JSVMP 负责把明文拼出来，wasm 负责加密。加密包装还原后长这样：

`function a(plaintext) {  const len = utf8len(plaintext);  const r = w.exports.encrypt(w.write(D, plaintext), len, H);   // 调 wasm  return utf8decode(w.read(H, r));                              // 读输出（已经是 base64）   }`

把那段 wasm 反编译出来，关键在这儿：它的 `encrypt` 不是直接做 AES，而是 `f_lb(字节码地址, 寄存器区, …)` 加一个 `br_table` 大循环。**wasm 自己也被虚拟化了**，`f_lb` 是台解释器，在跑数据段里的小程序。28 个函数、548 个数据段，里面**搜不到**标准 AES 的 S-box（`63 7c 77 7b…`）、逆 S-box、Te0、rcon，一个都没有。表被拆了。

到这一步，坑就露出来了：**它想让你以为这是魔改 AES，于是你去提升这台 wasm 里的 VM、逐 op 把算法抠出来。** 那是好几天的工程。

三、破法：别逆 VM，扫内存捞 key
-------------------

关键的一个认识：**不管表怎么拆、wasm 怎么虚拟化，只要它真的在跑标准 AES，轮密钥扩展的结果运行时一定完整地躺在线性内存里。**

AES-128 的 key schedule 是 176 字节、11 组轮密钥，各组之间有**固定的递推关系**：第 `i` 个 4 字节字 `w[i] = w[i-4] ⊕ g(w[i-1])`，其中每 4 个字做一次 `g`（循环移位 + S-box 代换 + 异或 rcon）。这个结构骗不了人，而且**你根本不用事先知道 key**：内存里只要有一段 176 字节自己满足这个递推，它就是一把 AES key schedule，头 16 字节就是原始 key。这就是 aeskeyfind 的原理。

### 具体怎么扫

第一步，在 DevTools 里 `encrypt` 返回之后那个断点停下，把 wasm 的整块线性内存拿出来，它就挂在 `w.memory.buffer` 上：

`const mem = new Uint8Array(w.memory.buffer);   // 整块 wasm 内存，几十万字节`

第二步，对 `mem` 每个偏移验一遍上面那个递推。下面这段可以直接贴进控制台跑：

`// 现场生成标准 AES S-box（不用从内存里找表，表被拆了也不影响）   const SBOX = (() => {  let p=1, q=1, s=new Uint8Array(256);  do {       p = p ^ (p<<1) ^ ((p&0x80)?0x11b:0);       q^=q<<1; q^=q<<2; q^=q<<4; q&=0xff; if(q&0x80) q^=0x09;       s[p] = (q ^ (q<<1|q>>7) ^ (q<<2|q>>6) ^ (q<<3|q>>5) ^ (q<<4|q>>4) ^ 0x63) & 0xff;     } while (p!==1);     s[0]=0x63; return s;   })();   const RCON = [0,1,2,4,8,16,32,64,128,27,54];      function findAesKey(mem) {  const hits = [];  for (let o=0; o+176<=mem.length; o++) {    let ok = true;    for (let i=4; i<44 && ok; i++) {      let a=mem[o+(i-1)*4], b=mem[o+(i-1)*4+1], c=mem[o+(i-1)*4+2], d=mem[o+(i-1)*4+3];      if (i%4===0) [a,b,c,d] = [SBOX[b]^RCON[i/4], SBOX[c], SBOX[d], SBOX[a]];   // g()      for (let k=0;k<4;k++)        if (mem[o+i*4+k] !== (mem[o+(i-4)*4+k] ^ [a,b,c,d][k])) { ok=false; break; }       }    if (ok) hits.push([o, [...mem.slice(o,o+16)].map(x=>x.toString(16).padStart(2,"0")).join("")]);     }  return hits;   }      console.log(findAesKey(mem));`

几十万字节扫完也就几秒，噪声里几乎不会误命中（要连续 160 字节都恰好满足 10 轮递推，概率极低）。这题的结果：

`[key schedule 扫描输出中的偏移 / key 样值已脱敏]`

来源称在 WASM 线性内存中发现了满足 AES-128 key-schedule 递推关系的候选区；目标偏移和 key 字节已脱敏。

（顺带一提：那 36 个环境探针，设计意图是"环境不对就让 key 不对、静默给你错 token"。但真实浏览器里最终 key 就是这个常量，离线复现根本不用算那些探针。它吓唬你的成分，比实际拦你的成分多。）

四、反推 IV：key 和 IV 只差一个字母
-----------------------

有了 key，直接 AES-ECB 加密明文去对，**对不上**。说明不是 ECB，是带 IV 的 CBC。IV 不用猜，一对已知的明文密文就能反推：CBC 第一块是 `c0 = E_k(p0 ⊕ IV)`，反过来 `IV = D_k(c0) ⊕ p0`。

`iv = AES_ECB_decrypt(key, c0) ^ p0    # → b'[CBC IV 样值已脱敏]'`

来源称其依据 CBC 首块关系推算 IV，并指出 key 与 IV 不应默认相同；具体差异值已脱敏。

五、明文模板，和逐字节验证
-------------

断点读到的明文拼起来是这个模板：

`[challenge-specific path prefix redacted] + now + [challenge-specific constant redacted] + page + [suffix redacted]`

`now` 是本地 `Date.now()`，和 query 里的 `now` 同一个值。我把复现器跑了一遍对拍，不是空口说还原了：

`KEY = b'[AES key 样值已脱敏]'   IV  = b'[CBC IV 样值已脱敏]'    # IV 样值差异已脱敏      token([原始明文样值已脱敏])   # [token 样值已脱敏]   # 和真实抓包逐字节一致（两个独立会话 2/2）`

端到端也通：离线算的 token，page=1 用本机时间发请求，`200 {"data":[...]}`；page=2 把尾巴改成 `21` 也 200。负对照：尾巴故意写成 `99`、`12`、`2`，一律 `403`。请求头只带 UA 和 Referer，没 cookie、没登录，这题的门就是 token 本身。

诚实交代边界：明文的**拼接逻辑**我没逆，`[challenge-specific constant redacted]` 和末尾那个 `1` 是从样本读出来的、不是从 JSVMP 字节码里读的；只测过 `pageSize=10`、`kw` 为空，换搜索词明文可能变。环境探针对 key 的影响、`now` 的时效窗口，也都没测。

六、三条能复用的方法
----------

1.  1. **wasm 里的 AES，先扫内存，别先逆 VM。** 不管 S-box / T 表怎么拆、wasm 怎么虚拟化，标准 AES 的 key schedule 运行时一定完整出现在线性内存。断点落在 `encrypt` 返回之后扫一遍，几秒出 key。**数据段里搜不到标准表，不等于魔改了 AES。**
    
2.  2. **CBC 的 IV 用第一块反推**：`IV = D_k(c0) ⊕ p0`，只要一对已知的明文密文。
    
3.  3. **跨会话 token 的公共前缀**，直接告诉你分组大小、加密模式（ECB 还是固定 IV 的 CBC）、以及明文第一块是不是常量。这是不碰代码就能做的定性。
    

* * *

和 match/30 是同一个判断：**JSVMP 常常只是壳，真算法在 wasm 里；而"看着像魔改"往往是障眼法，先确认它是不是标准算法，别一上来就逐 op 逆整台 VM。** 这一题把障眼法做到了极致，连 wasm 都虚拟化了，可只要 AES 还是标准 AES，key 就躲不过内存里那把尺子。

**延伸阅读**

*   • 姊妹题《猿人学 match/30：JVM1 字节码壳套一个 wasm，token 完整还原》，同一套壳，wasm 里换成自写的 SPN 加密。
    
*   • 想从零系统学 JSVMP：《JSVMP 从入门到入土》系列，从手写一台 VM 开始，一路讲到脱壳、拆套娃这些硬活。
    

* * *

**你碰到过"表全被拆散、看着像魔改、其实是标准算法"的目标吗？最后是硬逆下来的，还是扫内存绕过去的？评论区聊聊。**

本文转自 <https://mp.weixin.qq.com/s/QW-pPE1ae1lBOiyrtbv8Xw?scene=1&click_id=849819225>，如有侵权，请联系删除。

## 复用边界

来源作者报告其做过逐字节对拍与目标请求；原始夹具未提供，本轮没有运行目标或复核 AES 模式。该材料不证明其它 WASM 实现会保留同样的轮密钥布局，也不提供可复用的目标 token / key / IV。
