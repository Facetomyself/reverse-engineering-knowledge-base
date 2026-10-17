---
schema_version: 2
id: wechat-windows-sendmsg-static
document_type: archive
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [wechat-windows]
  client: windows
  version: "4.1.13.65"
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: "微信 4.1.13.65 Windows 发送消息链路 —— 逆向笔记"
    reason: "原始材料未提供作者名或可公开定位的链接"

source_completeness: partial
relations: []
tags: [wechat, sendmsg, ilink, static]
---

# 微信 4.1.13.65 Windows 发送消息链路 —— 逆向笔记

来源自称只做了静态阅读：文件、进程模块表和本机 localhost 端口表。它写明没有注入、没有 hook、没有发消息。构建日期按原文是 2025-09-17，观察日不另填。

## 清洗与完整性说明

复现命令里的本机解释器绝对路径已换成 `<local-python>`，原值不进入本文。`Weixin.dll` 的安装路径、地址、端口和字符串锚点按原文保留。无缺图声明；原文没有图。

<a id="source-body"></a>
## 来源正文

> 本文只记录**静态**分析结论（读文件、读进程模块表、读 localhost 端口表）。
> 全程未向微信进程注入任何代码、未 hook、未发消息。
> 分析对象：微信 `4.1.13.65`（2025-09-17 构建），OS Windows 11 (26100)。

---

## 1. 架构总览：这不再是一个单体程序

早期微信 Windows 版是一个大 `WeChat.exe`。4.x 完全重构成**模块化 + 运行时下发插件**：

- 安装目录只放一个 3 MB 的启动器 `Weixin.exe`。
- 真正的运行时按需从 `.bin` **ZIP 包**解压到
  `%APPDATA%\Tencent\xwechat\xplugin\plugins\<组件>\<build>\extracted\`。
- 主进程 PID 25756 一共只加载了 **17 个腾讯模块，合计 307 MiB**。

### 主进程实际加载的腾讯模块

| 模块 | 大小 | 作用 |
|---|---|---|
| `Weixin.dll` | 198 MB | 主模块：Skia + ICU + Qt + Cronet + 微信自身逻辑 |
| `XNet.dll` | 41 MB | 长连接网络栈，5435 个导出 |
| `VoipEngine.dll` | 22 MB | 音视频 |
| `ilink2.dll` | 11 MB | **消息传输层**（zidl 会话 RPC） |
| `mmcronet.dll` | 8 MB | Cronet（Chromium 网络栈）封装 |
| `wcprobe.dll` | 7.8 MB | 探针/安全组件 |
| `shared_andromeda.dll` | 6.7 MB | 共享运行时 |
| `libGLESv2.dll` | 5.4 MB | ANGLE GL |
| `mmmojo_64.dll` | 2.6 MB | Tencent Mojo IPC |
| `owl.dll` | 1.5 MB | 异步运行时（`owl::promise2`） |
| `ilink_stream.dll` / `ilink_wrapper.dll` | 1.3 MB / 0.25 MB | ilink 分片/包装 |
| `ConfSdk.dll` | 1.3 MB | 配置 |
| `Weixin.exe` | 3 MB | 启动器 |
| `RadiumWMPF\...\wmpf_host_export_x64.dll` | 6.4 MB | 小程序宿主 |
| `XPlayer\...\xplayer.dll` | 4 MB | 播放器 |

### 关键结论：`Weixin.dll` 的 189 MB 不是业务逻辑

`Weixin.dll` 只有 **1,277 个 RTTI 类**，且全部是第三方库：

```
189 std     161 icu     114 SkSL     69 skgpu     27 skia     17 SkShaper
```

即 **Skia（2D 渲染）+ ICU（Unicode）+ SkSL（着色器语言）+ Qt + Cronet**。

**`mmui::` 一个 RTTI 类都没有** —— 腾讯对自己写的代码关闭了 RTTI
（`/GR-`），所以 `dynamic_cast` / RTTI 扫描对微信自身逻辑完全无效。

但 `mmui::` 的**类名字符串**仍然存在于 `.rdata`（例如 `mmui::MainWindow`、
`mmui::ChatSessionCell`、`mmui::ChatBubbleItemView`、`mmui::XTextView`），
所以可以用字符串定位，只是不能靠 RTTI。

### 一个可用的替代品：`.pdata`

`.pdata` 段保存 `RUNTIME_FUNCTION` 数组（每个函数一条：起始 RVA、结束 RVA、unwind RVA）。

```
.pdata  5,963,264 bytes -> 496,938 条记录
零重叠，覆盖 .text 的 114.5 MB / 120.8 MB（95%）
中位函数长度 64 字节，最长 181 KB
```

**这是符号被剥离后唯一可靠的函数边界来源**，也是本项目所有定位工作的基础。

---

## 2. 工具链

`tools/re/` 下四个只读工具，全部可复现：

| 工具 | 作用 |
|---|---|
| `recon.py` | PE 头/节表/导出/导入/RTTI/字符串 |
| `modules.py` | 枚举运行中进程的已加载模块（base + size） |
| `xref.py` | **交叉引用查找**（见下）+ 函数表查询 |
| `disasm.py` | 反汇编单个函数，内联解析字符串引用 |

### `xref.py` 的两个核心技巧

**技巧一：不用反汇编器就能找到引用。**

x86-64 中任何使用 RIP 相对寻址的指令，`disp32` 都是指令的**最后一个字段**。
若该字段位于虚拟地址 `V`，则指令结束于 `V+4`，于是：

```
target = (V + 4) + disp32(V)
```

所以只要扫描可执行段里每一个 4 字节窗口并检验这个恒等式，就能一次向量化
（numpy）扫描找出**所有**引用。对 `call rel32`（`E8 disp32`）同样成立——
因为 `disp32` 也是最后 4 字节。这让"找调用者"变成一次内存扫描。

**技巧二：用 `.pdata` 精确还原指令，剔除巧合。**

上面的恒等式会**误报**：某个立即数恰好落在别的指令中间时也可能满足。
所以对每个命中点，我们用 `.pdata` 查出它属于哪个函数，**从函数真正入口
向前反汇编**，再要求

```
disp_va == insn.address + insn.size - 4
```

即"disp32 必须正好是指令最后四个字节"。这条判据可以同时排除
（a）落在指令中间的巧合，（b）`rel8` 短跳转（根本没有 disp32）。

---

## 3. 发送消息链路（已定位）

### 3.1 字符串锚点

在 `Weixin.dll` 中扫描到这些明文锚点：

```
micromsg.SendMsgRequestNew / SendMsgResponseNew      <- 发送消息的 protobuf 类型
<cgi reqid="2"   respid="1000000002">sendmsg</cgi>   <- 经典发送 CGI
<cgi reqid="107" respid="1000000107">sendappmsg</cgi>
<cgi reqid="237" respid="1000000237">newsendmsg</cgi>
send_message_failed: MessageManager is unavailable
Unsupported message type:
Base64 decode failed; content_xml_base64 is invalid
ZYXWVUTSRQPONMLKJIHGFEDCBA9876543210123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ   <- 自定义 base64 字母表
```

### 3.2 调用链

用 `xref.py --calls-only` 逐层向上追，得到一条**单调用者**的干净链路：

```
0x182ee2e10  (87 B)   注册用 thunk：add rcx,0x20；把 r9 指向的对象 move 出去
      |
      v
0x182ee2e70  (670 B)  解析 JSON 参数；失败时打印 "Invalid arguments JSON"
      |
      v
0x1854b5260  (986 B)  业务校验层
      |
      v
0x1854b7a00  (5745 B) 真正的发送实现：
                        - "Contact not found"          解析目标会话
                        - 自定义 base64 解码 content_xml
                        - "Unsupported message type: " 按类型分派
                        - "send_message_failed: MessageManager is unavailable"
```

`0x1854b7a00` 的字符串构成说明了它的**签名形态**：它接收
*（目标会话 + base64 编码的 content_xml + 消息类型）*，
解码后交给 `MessageManager` 发出。

### 3.3 上层是一个 JSON 命令注册表

`0x182ee2e10` **没有任何直接调用者**（`call rel32` 命中 0 条），说明它是被
**间接注册**的。它的地址由 `0x182ee2cd0` 通过 `lea rdx, [rip+0x101]` 取出：

```
0x182ee2cd0  (183 B)
    mov ecx, 0x28                  ; operator new(0x28)
    call 0x1871659ec
    lea rdx, [0x182ee2e10]         ; handler
    lea r8,  [0x18000bdd0]         ; deleter
    call 0x180104d60               ; 包装成 std::function 风格对象
    ...
    call 0x1854b4b00               ; 该函数引用 "content_xml_base64"
    ...
    call 0x182ec8940               ; 注册 (2028 B)
```

而 `0x1854b4b00` 中引用了 JSON 键名 **`content_xml_base64`**，
说明注册表里存的是 **(命令名, handler, 参数 schema)** 三元组。

命令名锚点 **`message::send_message`**（`namespace::action` 风格）位于
`0x189172470`，唯一引用点是函数 `0x182ec76a0` —— 与注册函数
`0x182ec8940`、`0x182ee2cd0` 同在 `0x182ec7xxx`–`0x182ee3xxx`
这一片区域，即**命令注册表模块**。

### 3.4 JSON 参数键名（已在 `.rdata` 中确认存在）

```
to_user_name        content_xml_base64     content_xml
msg_type            session_id             chat_id
room_id             local_id               create_time
msg_id              username
```

**结论：微信 4.x 内部存在一个 JSON 命令接口，其中
`message::send_message` 命令接受 `to_user_name` + `content_xml_base64` +
`msg_type` 等字段来发送消息。**

### 3.5 传输层（另一条路）

`ilink2.dll` 导出的是 `ilink::zidl_export::*` —— 腾讯 zidl 生成的会话 RPC：

```
NetworkManager::SendRequest       (IlinkRequestInfo)      <- 传输层发送
NetworkManager::SendRequestAsync
NetworkManager::OnReceiveAppMessage / OnReceiveSyncMessage
CloudSession::OnSendCloudCgiRequest
AppSession / CloudSession / DeviceSession / SingletonSession（各有 NoPB 孪生类）
```

这是 Windows 上对应 macOS 版 `mars` `req2buf` 的位置。

---

## 4. 外部可达性排查（结论：不可外部调用）

主进程 PID 25756 监听了 5 个 localhost 端口：

```
127.0.0.1:14013  127.0.0.1:14016  127.0.0.1:14019  127.0.0.1:14022  127.0.0.1:14023
```

逐个发 HTTP 请求（`/`、`/json/version`）**全部无响应**。结合已加载的
`mmmojo_64.dll`，这些是 **Tencent Mojo** 的内部 IPC 通道
（浏览器进程 ↔ 子进程），有私有分帧协议，**无法从外部直接驱动**。

所以 `message::send_message` 这个 JSON 接口是**进程内**的，
要从外面用只能注入。

---

## 5. 建议的下一步：抓包-回放（而非盲猜 schema）

不要试图逆向 JSON schema 或自己拼 protobuf。更可靠的顺序是：

1. 注入后 **hook `0x1854b7a00`**（发送实现），只读地打印入参寄存器
   （`rcx/rdx/r8/r9` + 栈）以及它们指向的内存。
2. **手动**在微信里给目标群发一条消息。
3. 观察真实调用时参数的形态（字符串类型、长度、指针布局）。
4. 用同样的参数形态，把文本换成测试内容，**调用**该函数。

这样完全绕开 schema 猜测，也不需要自己构造 `SendMsgRequestNew` protobuf。

### 风险（必须知情）

- **账号风险**：向运行中的微信注入代码属于非官方行为。客户端带有
  `wcprobe.dll` 探针，无法排除检测与风控的可能。这是用户真实账号。
- **崩溃风险**：`0x1854b7a00` 依赖 `MessageManager` 与已登录的 ilink 会话。
  参数形态错误会导致整个客户端崩溃，而崩溃时数据库正在被写入。
- **版本不可移植**：所有地址都是 4.1.13.65 专属；客户端一升级即全部失效。

### 更保守的替代方案

若不愿承担账号风险，可以只做到"**只读观测**"：hook `0x1854b7a00`
仅打印参数、不调用，用于验证链路理解是否正确。这仍有注入风险，
但不会发出任何消息、不会改变客户端状态。

---

## 6. 复现命令

```bash
PY="<local-python>"
DLL="C:/Program Files/Tencent/Weixin/4.1.13.65/Weixin.dll"

# 架构
"$PY" tools/re/recon.py info "$DLL"
"$PY" tools/re/modules.py --sort size --limit 45

# 锚点
"$PY" tools/re/recon.py strings "$DLL" --pattern "SendMsg|content_xml_base64" --enc both

# 交叉引用：找调用者
"$PY" tools/re/xref.py "$DLL" --va 0x1854b7a00 --calls-only
"$PY" tools/re/xref.py "$DLL" --string "MessageManager is unavailable"

# 读函数
"$PY" tools/re/disasm.py "$DLL" --va 0x1854b7a00 --strings-only
```

## 7. 已知限制

- `xref.py --string` 的 `^`/`$` 锚点作用于整个文件而非单条字符串
  （`recon.py strings` 则是逐条匹配，行为不同）。用 `xref.py` 时不要加锚点。
- 部分字符串在 `.rdata` 中是**加密/混淆**的（形如 `\x25\x00\xC2...`），
  静态读不出内容，只能在运行时解密后读取。
- `ilink2.dll` 的导出是 zidl **代理**层，真实实现通过 `ResetImplStub`
  注册；hook 导出函数不一定能截到真实发送，需要再确认。

## 复用边界

地址只属于来源写下的 4.1.13.65。localhost 无 HTTP 响应是该次端口探测的自述。本文不把“建议下一步注入”写成已完成实验，也不把它升级成可复用流程。
