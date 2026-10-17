---
schema_version: 2
id: apatch-source-note-07-superkey
document_type: archive
original_date: "2026-09-06"
archived_date: "2026-10-08"
scope:
  targets: [apatch, kernelpatch]
  client: Android
  version: "APatch main@6ec140e; KernelPatch 0.13.8 bcc8498"
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s?__biz=MzI5NDkwNTAyOQ%3D%3D&mid=2247484826&idx=1&sn=3d31a3388ebf8fce10c1f15b4bd61b78&chksm=ec5af030db2d79265750ad86f0cc1fd44ac1c3482de3dacf179f03635b210cc7bdff98de4f49#rd"
    basis: source-report

source_completeness: partial
relations: []
tags: [apatch, kernelpatch, source-report]
---

# APatch 源码笔记（七）：SuperKey——一把钥匙的安全模型

吴见午公开笔记，发布日 2026-09-06。来源把结论绑在 APatch `main@6ec140e` 与 KernelPatch `0.13.8`（`bcc8498`）。归档不把作者读源码的结论升级成刷机或运行时验收。

## 清洗与完整性说明

正文用已导出的 Markdown，没有从同伴 HTML 重抽。MD 中的 mmbiz 图为 2 张远程 URL，HTML 中不重复的 mmbiz URL 为 14 个；差额未逐张鉴定，可能含页面装饰，也可能含未进入 MD 的图。缺图没有用文字补。MD 表格分隔行 2，HTML `<table>` 2。远程图未本地化。代码围栏、行号和「源码明确行为 / 作者推测」的原词保留。

<a id="source-body"></a>
## 来源正文

![](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBdueYzl7iaiaBhbQW3THtXPUm29EeI2GBjFVdlsxmW3F558N1nUfwlFm42bdh9lSvCfLzib4PHKhkyv8jJgDK2dbklDy1jnEwqhN3kDs/640?wx_fmt=png&from=appmsg)

本文基于双仓库交叉核实：**APatch** `main@6ec140e` + **KernelPatch** `tag 0.13.8`（HEAD `bcc8498`）。所有结论附 `仓库:文件:行号`。

## 01 这一篇我们要解决什么问题？

第 3 篇解剖 supercall 门禁时，我们认识了两个布尔量：`trusted`（有资格说话）和 `authed`（密钥持有者）。第 4 篇看到密钥在打补丁那一刻被写进内核镜像。第 6 篇的授权表解决了"哪些 App 能 su"，但还有一个更根本的问题悬着：**SuperKey 这把钥匙，到底保护什么、存在哪、怎么防偷、为什么新版本敢完全不用它？**

具体拆成四个问题：

1. `-s` 明文和 `-S` 哈希两种打补丁方式，内核里的鉴权逻辑有什么不同？
2. "旧密钥能换新密钥"是怎么实现的——不知道明文也能升级？
3. 内核是怎么验证一个 APK 的签名的——它又没有包管理器。
4. 管理器源码里那句 *"the only way is don't use superkey"* 的 TODO，到底是什么意思？

## 02 为什么从这里开始？

因为这是安全模型的总账页。第 3 篇的分水岭（`if (!is_authed) return -EPERM`）把命令分成"密钥前"和"密钥后"两段，SuperKey 是后半段的唯一通行证；第 4 篇的 `-S` 是这把钥匙的"铸模"；第 6 篇的授权表则是绕过它的旁路之一。看完这篇，"谁在什么条件下能拿到 root"就不再有任何黑箱。

## 03 密钥的一生：从打补丁到开机

密钥的出生地在 kptools（第 4 篇第 03 节）：`-s` 把明文写进 `setup_preset.superkey[0x40]`，`-S` 把 SHA-256 写进 `root_superkey[0x20]`，什么都不传则两个都空。开机后 `predata_init`（`KP:kernel/base/predata.c:332+`）接管：

```
    superkey = (char *)start_preset.superkey;
    root_superkey = (char *)start_preset.root_superkey;
    superkey_is_user_set = lib_strnlen(superkey, SUPER_KEY_LEN) > 0;
    ...
    enable_root_key = false;

    // random key
    if (!superkey_is_user_set) {
        enable_root_key = true;
        int len = SUPER_KEY_LEN > 16 ? 16 : SUPER_KEY_LEN;
        len--;
        for (int i = 0; i < len; ++i) {
            uint64_t rand = rand_next() % (sizeof(bstr) - 1);
            superkey[i] = bstr[rand];
        }
    }
```

**不设密钥 ≠ 没有密钥**：内核会自己生成一个 15 位字母数字"随机密钥"（`int len = SUPER_KEY_LEN > 16 ? 16 : SUPER_KEY_LEN; len--;`——先取 16 再自减，循环只写 15 个字符，第 16 字节留在 kptools 清零的缓冲上当 NUL 终止符），同时打开 `enable_root_key`。这个随机数发生器的种子来自 `kernel_va`（KASLR 基址）、内核版本号、kp 版本号、镜像区域边界、编译时间和密钥区内容（`:343-350`）——全是运行期才能确定的量，但**不是**密码学安全的熵源（这是源码明确事实；为什么这样"够用"，思考题 2）。

"随机密钥 + 哈希模式"这两个机制服务于同一个目标：**让"知道明文密钥"的人集合尽可能小**。随机密钥是"没有任何人知道"（包括用户自己）；哈希模式是"只有设定者知道"。

## 04 auth_superkey：双通道鉴权与"自动晋升"

每次 supercall 门禁都要过一遍的 `auth_superkey`（`KP:kernel/base/predata.c:42-69`），全文不到三十行，却装了两个通道：

```
int auth_superkey(const char *key)
{
    int rc = 0;
    for (int i = 0; superkey[i]; i++) {
        rc |= (superkey[i] ^ key[i]);          // 通道一：明文 XOR 比较
    }
    if (!rc) goto out;

    if (!enable_root_key) goto out;

    BYTE hash[SHA256_BLOCK_SIZE];
    ...
    sha256_update(&ctx, (const BYTE *)key, lib_strnlen(key, SUPER_KEY_LEN));
    sha256_final(&ctx, hash);
    int len = ...;
    rc = lib_memcmp(root_superkey, hash, len); // 通道二：SHA-256 与哈希模式比对

    static bool first_time = true;
    if (!rc && first_time) {
        first_time = false;
        reset_superkey(key);                   // 晋升！
        enable_root_key = false;
    }

out:
    return !!rc;
}
```

**通道一**逐字符 XOR 累积比对明文。**通道二**是哈希模式的救生索：把用户给的密钥做 SHA-256，与 `root_superkey` 比对。妙处在晋升分支——**哈希模式下，第一次有人拿对密钥，内核就把明文"请"了进去**（`reset_superkey(key)` 写入明文，关闭哈希通道）。

这就兑现了 kptools 帮助文本里那句承诺（`KP:tools/kptools.c`）：*"-S, --root-skey KEY — Set the root-superkey useing hash verification, and the superkey can be changed dynamically."*——哈希模式的意义不是永远不存明文，而是**镜像里只留哈希，用户手里的明文首次使用时才进驻内核**。此后明文通道接管，动态换密钥（`SKEY_SET`）才有操作对象。

## 05 一段考古：hash_key() 是个装饰品

`scdefs.h:9-16` 里躺着一个看起来很像鉴权核心的函数：

```
static inline long hash_key(const char *key)
{
    long hash = 1000000007;
    for (int i = 0; key[i]; i++) {
        hash = hash * 31 + key[i];
    }
    return hash;
}
```

1000000007 基数、×31 累加——经典的多项式字符串哈希。**源码明确行为**：内核全部 `.c` 文件里没有任何调用者（全仓库检索确认）。它是 UAPI 头文件里的 inline 函数，用途是给**调用方**（历史版本的客户端）自hash用的遗存，真正在内核里执行鉴权的是第 04 节的 `auth_superkey`。读源码时看到"名字最像核心逻辑"的代码，先搜调用者再下结论——这条考古记入本专栏的"彩蛋收藏夹"。

## 06 钥匙的管理台：SKEY 三命令

密钥自己也有管理接口，全在 supercall 的 `-EPERM` 分水岭之后（第 3 篇的分段，`KP:supercall.c:352` 之后才轮到它们）：

- `SUPERCALL_SKEY_GET 0x100a` → `call_skey_get`（`:155-162`）：**把当前明文密钥原样拷给调用者**；
- `SUPERCALL_SKEY_SET 0x100b` → `call_skey_set`（`:164-171`）：`reset_superkey` 换新密钥（超长返回 `-E2BIG`）；
- `SUPERCALL_SKEY_ROOT_ENABLE 0x100c`（`:173-177`）：开关哈希通道。

组合起来是一条完整的密钥交接链：**旧密钥持有者可以取回明文（GET）、换成新密钥（SET）**——"换了钥匙旧钥匙作废"的安全预期由此实现。同时注意一个推论：在随机密钥模式（第 03 节）下，任何能通过 `authed` 门禁的调用者（比如受信任管理器，下一节）用 GET **可以拿到那把"没人知道"的随机密钥**——机制上是通的，管理器是否使用是产品选择（本仓库未见调用，不下断言）。

## 07 新默认：内核里的 APK 签名验证

现在回答最硬核的问题：**不设密钥时，内核凭什么信任管理器？** 答案在 `KP:kernel/patch/android/userd.c:75-100` 的一张硬编码表：

```
struct trusted_manager_entry {
    const char package[64];
    const uint8_t digest[TRUSTED_MANAGER_DIGEST_LEN];   // SHA-256
};

static const struct trusted_manager_entry trusted_managers[] = {
    {
        "me.bmax.apatch",
        {
            0xd7, 0x1d, 0xad, 0xc0, 0xca, 0x07, 0xbd, 0xf5,
            0x94, 0x38, 0x3b, 0xfb, 0x2a, 0x44, 0x51, 0x34,
            ...
        }
    },
    ...
};
```

**包名 + 证书 SHA-256 摘要，双双硬编码在内核里**。验证逻辑 `apk_matches_trusted_signature`（`userd.c:352+`）直接在内核态解析 APK 文件：找到 APK Signing Block，解析 v2/v3/v3.1 签名块，取出证书 DER 做 SHA-256 与表内摘要比对；同时还有一个专门的 `apk_has_v1_signature`（`:313-344`）扫描 ZIP 中央目录里 `META-INF/*.RSA|DSA|EC` 残留——**v1（JAR）签名一律拒绝**（v1 不绑定文件内容，可被重打包攻击）。验证通过后，该应用的 uid 被缓存在 `trusted_manager_uid`（刷新逻辑 `userd.c:1123-1149`，判定就是一行 `uid == trusted_uid`，`:1152-1160`），第 3 篇 `before()` 的 `is_trusted_manager_uid` 分支随即给它 `trusted + authed` 双开。

所以"新默认"的完整表述是：**镜像里没有可用密钥（随机密钥没人知道）→ 唯一的 authed 通道是受信任管理器签名 → 谁能成为受信任管理器由编译进内核的包名+证书摘要决定 → 伪造成本等于伪造一份通过 SHA-256 比对的官方签名证书**。SuperKey 从"第一道门"降级成了"遗产兼容"。

![图1：supercall 门禁判定树——四条通道、两种等级、两个出口](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueayReZVszr53ZPH80pbibv8u21sNOic0Iib3yJKEsfaQHoIWFsJNKYu0mTpNflS74jEwaU24NlGfsQv9D9WOWeb2GzDu2gwJCqGN8/640?wx_fmt=png&from=appmsg)

图1：supercall 门禁判定树——四条通道、两种等级、两个出口

## 08 管理器侧：钥匙的交接仪式

用户态这边（`APatch:APatchApp.kt:261-281`），`resolveSuperKey` 是每次启动的三级裁决：

```
// Signature authorization (new default).
if (Natives.nativeReady("su")) {
    if (!savedKey.isNullOrEmpty()) {
        APatchKeyHelper.clearConfigKey()
        Log.i(TAG, "signature auth ready, cleared legacy SuperKey")
    }
    return "su"                        // ① 签名通道活着 → 用 "su"，顺手清掉旧钥匙
}

// Legacy kernel patched with a real SuperKey: reuse the stored one.
if (!savedKey.isNullOrEmpty() && Natives.nativeReady(savedKey)) {
    return savedKey                    // ② 老内核 → 掏出加密保存的旧钥匙，帮用户升级
}

return "su"                            // ③ 都不行，也是 "su"
```

先试 `"su"`（签名通道探测，`nativeReady` 底下就是第 3 篇的 HELLO 探针）；活着就**主动清掉本地保存的旧密钥**——注释说得很清楚：签名通道一旦可用，内核不再依赖 SuperKey，陈旧钥匙留着只有风险。只有探测到"老内核 + 本地有旧钥匙"时才走②的升级路径。

旧钥匙在本地也不是明文躺着：`APatchKeyHelper`（`APatchKeyHelper.java:21-37`）用 AndroidKeyStore 里的 `APatchSecurityKey` 做 AES/GCM 加密后存 SharedPreferences，读取时还带一条"旧固定 IV → 新随机 IV"的自动迁移路径（`readSPSuperKey`，`:152-168`）。还有个 `setShouldSkipStoreSuperKey` 开关——连加密存储都可以拒绝。

而整个安全模型最诚实的一句话，写在 `APatchApp.kt:296-298` 的 TODO 里：

```
// TODO: We can't totally protect superkey from be stolen by root or LSPosed-like
// injection tools in user space, the only way is don't use superkey,
// TODO: 1. make me root by kernel
// TODO: 2. remove all usage of superkey
```

作者亲口承认：**用户态永远护不住一把钥匙**——root 进程和注入框架都在你的进程旁边虎视眈眈。唯一的解法不是把钥匙藏得更好，而是让钥匙消失：提权改由内核主动完成（TODO 1，第 5 篇的 execve hook 正是这个思路的完成时态），SuperKey 的使用面清零（TODO 2，本篇的签名通道正是进行时）。两条 TODO，一条已经落地，一条正在落地——读源码读到 TODO 能读出项目的技术路线图，这大概是最有趣的部分。

## 09 安全模型总账

把全系列至今的"准入"收进一张表（全部已核实）：

| 调用者身份 | 能到达的位置 | 依赖什么 |
| --- | --- | --- |
| 普通未授权 App | 真 truncate 原样执行 | 什么都不依赖——被拒之门外 |
| 持正确密钥的任意进程 | 全部命令（含 SKEY/KPM 管理） | SuperKey 明文或其 SHA-256 |
| 受信任管理器（签名验证） | 全部命令 | 内核里硬编码的包名+证书摘要 |
| 已授权 uid（root/shell/授权 App） | 密钥前各段（SU/GRANT/KSTORAGE…） | 授权表（第 6 篇的 CSV→kstorage） |

攻击面也如实列出：密钥可能被同设备的 root/注入框架窃取（官方 TODO 自认）；`auth_superkey` 的 XOR 明文比较非常量时间（源码事实，计时侧信道在 syscall 边界上的实际可行性属作者推测，不在本篇下结论）；随机密钥的 RNG 非密码学安全（第 03 节）。**但每一条都有对应的缓解设计**：签名通道让密钥可整体退役、授权表让普通 App 根本不需要接触密钥、随机密钥让"偷"无从偷起。

## 10 常见误区

1. "`hash_key()` 是鉴权函数"——不是，它在内核侧零调用（第 05 节考古）。
2. **"SuperKey 是加密密钥"**——不是，它是准入口令，不参与任何数据加密。
3. "`-S` 哈希模式 = 内核永远不知道明文"——首次哈希命中即晋升明文（`predata.c:63-66`），此后 `SKEY_GET` 可取回。这是"可动态换钥匙"的代价，不是缺陷。
4. **"签名授权信任所有叫 apatch 的包"**——包名和证书摘要**双比对**，缺一不可。
5. **"不设密钥就不需要鉴权"**——恰恰相反，此时 authed 只剩签名通道一条独木桥，是三种模式里门槛最高的。

## 11 本篇源码地图

| 文件 | 本篇中扮演的角色 |
| --- | --- |
| `KP:kernel/base/predata.c` | `auth_superkey` 双通道 + 首次晋升；`predata_init` 随机密钥与 RNG 种子 |
| `KP:kernel/base/start.h` / `KP:tools/patch.c` | 密钥的出生地：`-s` 明文 / `-S` SHA-256 写入 preset |
| `KP:scdefs.h:9-16` | `hash_key()`：无调用者的 UAPI 遗存（考古） |
| `KP:supercall.c:155-177` | SKEY_GET/SET/ROOT_ENABLE 管理台（分水岭之后） |
| `KP:userd.c:75-100,313-360` | 受信任管理器硬编码表、v1 拒绝、v2/v3 签名块与证书摘要比对 |
| `APatch:APatchApp.kt:261-298` | `resolveSuperKey` 三级裁决 + "don't use superkey" TODO |
| `APatch:util/APatchKeyHelper.java` | 旧密钥的 AES/GCM + AndroidKeyStore 加密存储与迁移 |

## 12 总结与思考题

这一篇把 SuperKey 从"神秘的口令"还原成了工程取舍的标本：**它是准入口令而非加密材料；明文通道与哈希通道双轨，首次命中自动晋升；管理三命令让旧持有者可以换锁；而新默认干脆釜底抽薪——把信任锚从"用户手里的字符串"换成了"编译进内核的官方签名证书"**，并留下两条 TODO 坦白这条路线的终点：内核提权 + 密钥清零。安全设计里最难得的不是防住一切，而是像这段 TODO 一样，把自己护不住什么写明白。

三道思考题，前提均已核实：

1. `-S` 哈希模式下，用户第一次用对密钥后 `reset_superkey` 把明文写进了内核（`predata.c:63-66`）。此后另一个拿到该明文的人调用 `SKEY_GET` 会得到什么？这个"晋升"设计换来了什么、放弃了什么？
2. `predata_init` 的随机密钥 RNG 种子全是运行期可确定量（`predata.c:343-350`），并非密码学熵源——结合"这个密钥的用途是让任何人都不知道，而不是抵抗暴力枚举"（真正的准入在签名通道），推演作者这样写为什么可以接受。
3. `resolveSuperKey` 在签名通道就绪后立刻 `clearConfigKey()`（`APatchApp.kt:266-270`）——结合第 09 节攻击面清单，说明这个"主动扔钥匙"的动作分别降低了哪几条攻击线的风险。

下一篇收尾 Root 权限体系：**《APatch 源码笔记（八）：SELinux——APatch 如何在 enforcing 模式下生存》**。第 5 篇我们见过 `avc_denied` 被替换成"带标记全放行"，第 6 篇的 sepolicy 规则在开机时写进 `/sys/fs/selinux/load`——这两层是什么关系？magiskpolicy 的规则长什么样、apd 内置版本和外部二进制版本经历过什么变迁？模块的 `sepolicy.rule` 又是怎么被逐条执行的？我们把 Android 安全体系里这最后一堵墙看穿。

## 复用边界

文件名和行号属于来源阅读的那两份树。作者标明「作者推测」的句子保持为推测。panther user 镜像把 APatch 收进 ROM 的流程是另一篇，目标不同，不要从本篇推出刷机步骤。
