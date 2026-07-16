# 使用 AI 实现最新版本 Flutter HTTPS 明文抓包

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2026-03-24
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 结合 IDA Pro MCP 与 eCapture 定位新版 Flutter libflutter.so 的 ssl_read/ssl_write 偏移，覆盖已解压 SO 与 APK 内嵌 SO 两种部署形态。

Flutter 抓包一直是个难题，常见方案都有明显局限：  代理抓包（Charles / Burp Suite）：  Flutter
默认不走系统代理，也不信任用户安装的 CA 证书。需要 Frida Hook 或修改代码才能让它走代理，操作复杂，遇到 SSL Pinning 更难处理。
VPN 抓包（HttpCanary 等）：  通过本地 VPN 做中间人，同样依赖 App 信任 CA 证书，遇到证书绑定会 失败。  Frida
Hook：  直接  Hook libflutter.so  的认证相关函数，取消证书的校验，这个方案也需要找到对应 的函数，定位依然比较繁琐，并且使用
frida，会引入额外的检测。  这些方案的根本困难在于：Flutter 内嵌了自己的 BoringSSL  不用系统 SSL 库，且 stripped
binary 让函数定位极为困难。
借助 AI 实现 Flutter  本方案使用  eBPF uprobe  \+  修改版 ecapture  配合  AI（Codex + IDA-Pro
MCP）  自动定位函数地址：

  * eBPF 在内核层

Hook SSL_write  /  SSL_read  ，不修改 App，App 无法感知，也不依赖证书

  * AI 自动分析  stripped 的  libflutter.so  ，解决了最难的函数地址定位问题

  * 偏移确定后，同一 Flutter 版本可复用，换 App 只需重新跑一遍 AI 分析

基础搭建
工具安装

  * AI 工具（Codex）

    npm i -g @openai/codex

然后，可以查看一下，是否安装成功，这里默认大家电脑装了新版本的 node，对于 node 以及 npm 的安
装，网上资料有很多，可以自行查找，然后查看一下安装的效果。
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRhribATZ5u19xd3gbzrv5Zq9j14RacbHJ3NkOPdLfGDdrXPJ1hIevibbaphZKTDpHGQgOgHkrNRzeOYibtFww3uHnOwnIS4evpEQ/640?wx_fmt=png&from=appmsg)

  * ida-pro-mcp

    git clone https://github.com/mrexodia/ida-pro-mcp.gitcd ida-pro-mcpuv sync

这里，默认大家已经会使用 git 以及 python，对于 python 包管理工具，这里我选择了
uv，这俩工具的安装，相信难不倒各位读者，进入项目目录（推荐安装到项目目录，不要全局安装）  在  .codex/config.toml  中添加：

    [mcp_servers."ida-pro-mcp"]command = "/opt/homebrew/bin/uv"args = ["--directory", "你下载的路径", "run", "ida-pro-mcp"]

将插件项目复制到 IDA 的插件目录，这里演示的是 mac 的位置，对于 windows，在 ida 的安装目录，路 径应该差不多。
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQIhMvUoTIr4FBwE0eGLib7J3fxaWj0s5xNXztFrIFdf7GbWYQ75dNFdsoJmMdqp5DaE5sKQO1W3OnvYRDh4KNjMJic2NMo39pjs/640?wx_fmt=png&from=appmsg)
用  idapyswitch  确认 IDA 使用的 Python。
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQsNa0Rbu9Pt0YsDYoViacPvWzqgicBE61cZQ1Xc4DulMgvS5FTXOiaG9HXS0GfxCb0GNsIxtiaGbENicGDNaX2kOZdoBqQcV08mYBk/640?wx_fmt=png&from=appmsg)
这里，要注意 python 的版本要求，需要大于 3.11，要自己选一个大于 3.11 的版本。
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MSZbJGb48nBHkiap7GMNgQvSVP2IBqJ1HfXhgt7ibiayxKQnMFMPY5l5bsDexWJaw4QlKsalaJIvLqwbhnz07HbuC0icXxslDhDA1k/640?wx_fmt=png&from=appmsg)
开启插件  打开目标 so 文件，启动插件。
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MSMvIZ3bpIPTV3fUW41lf3ibRRVPGIssk1NWkzIVXMib70xlticynZ8ibZ4AQBuRt2FBhq6QBQSoybocTK6yICrn5BGs9KQahJiaHxE/640?wx_fmt=png&from=appmsg)
现在，就已经开启成功了，看到如下内容。
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MSoRia4HQ42G7MYIyutTqmcGDEoTvpUgC5NYTD3mEVGuNzv665gfhkPTYib9GgLUk2UX43j5YwicMoVolOOVrRG4ogh1ndWw5lRfo/640?wx_fmt=png&from=appmsg)
然后，来测试一下，mcp 是不是好用，进入终端，开启  codex
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRaq0amr0gIr61oLhoh2pLicudCb8LEkiaU63GjwQAicnJqD4WlO8pUQn0TaJVpoiaicMZkgJMJrh381z1DE1e9fv4dSY57wGwwKzGI/640?wx_fmt=png&from=appmsg)
如果不报错，就证明加载成功了，然后在 ida 里面，会看到如下输出。
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTdqBB85jnKZ2QRXPcMdwiazc3uPYicD1PYEbYzrg0fd9mhSFT3Gl2AmjFz851L5kqZxkpuzKTZIQRum4qlEtvBJ4LnJPmFMv4Do/640?wx_fmt=png&from=appmsg)
不用太在意输出内容，有了输出就行，按照正常步骤到这里，一定会有输出的。  到这里，我们工具配置就结束了  接下来，我们要利用这个来获取  ssl_write
和  ssl_read  的偏移。
用 AI 获取函数偏移  接下来，我们要使用 AI 进行函数偏移的获取。  首先我们已知 flutter 网络通信协议要基于 boringssl ，为
了提升模型的处理效率。  使用一个处理过的标准提示词来处理，该提示词是我根据源码辅助来找特征定位
的标准化流程抽象出来的，经测试多个版本都是准确的，可以直接复用。

    ## 任务在 Flutter Android ARM64 的 libflutter.so（stripped）中定位 BoringSSL 的 SSL_write、SSL_read 函数地址及 ssl_read_inner_offset。

    ## ⚠️ 关键：IDA 地址 ≠ 文件偏移ecapture 的 `--ssl_write_addr` / `--ssl_read_addr` 需要 **ELF 文件偏移**，不是 IDA 虚拟地址。libflutter.so 的 `.text` PT_LOAD 段通常满足：`VirtAddr = FileOffset + 0x1000`，因此：**`file_offset = IDA_VA - 0x1000`**验证方法（IDA Python）：```pythonimport idaapiprint(hex(idaapi.get_fileregion_offset(0xYOUR_VA)))````ssl_read_inner_offset` 是相对偏移（BL_VA - SSL_read_VA），两地址在同一段内相减，偏差自动消除，**无需减 0x1000**。---## 已知条件- 架构：ARM64，IDA base=0x0- Flutter 使用内嵌 BoringSSL（非系统 libssl）- 调用链：SSLFilter::ProcessAllBuffers → SSL_write/SSL_read- SSLFilter 成员布局：- `ssl_` @ offset 0x18- `socket_side_` @ offset 0x20- `buffers_[0..3]` 从 offset 0x30 开始，每 8 字节一个---## 定位策略（按步骤执行）### Step 1：找 __errno PLT用 `mcp0_imports` 或 `mcp0_list_funcs(filter="*errno*")` 找到 `.__errno` 的地址。### Step 2：找 ERR_clear_system_error用 `mcp0_xrefs_to` 找 `.__errno` 的所有调用者。筛选条件：函数体 ≤ 4 条指令，仅调用 `.__errno` 并 `STR WZR, [X0]`。### Step 3：找 ssl_reset_error_state用 `mcp0_xrefs_to` 找 `ERR_clear_system_error` 的调用者。筛选条件：- 函数体 ≤ 10 条指令（~28 字节）- 包含 `STR WZR, [X0, #0xXX]`（清 ssl->s3->rwstate）- 调用 `ERR_clear_error`（另一个辅助函数）- 调用 `ERR_clear_system_error`### Step 4：找 ssl_reset_error_state 的所有调用者用 `mcp0_xrefs_to(ssl_reset_error_state_addr)`，通常 3–5 个。### Step 5：识别 SSL_write

    从调用者中找：- 较小的函数（200–350 字节）- 调用 `ssl_reset_error_state` 后，检查 `[ssl, #0xXX]` 是否为 nullptr（CBZ，对应 `do_handshake` 检查）- 内部有 BLR（vtable 间接调用 `write_app_data`）- 有一个内嵌的循环调用另一个中等大小函数（SSL_do_handshake）### Step 6：识别 SSL_read从调用者中找：- 较大的函数（> 1000 字节）- 调用 `ssl_reset_error_state` 后进入复杂 switch/loop（有跳转表 `jpt_xxx`）- 函数体对应 `ssl_read_impl`（内联了 SSL_peek 和 ssl_read_impl）### Step 7：通过调用点验证搜索 `ProcessAllBuffers` 函数（包含 `"Out-of-bounds internal buffer"` 或 `"SecureSocket"`字符串引用的函数）：- 找 `BL SSL_write_candidate` 的前几条指令- 验证：`LDR X0, [SSLFilter, #0x18]`（ssl_），`LDR Xn, [SSLFilter, #0x38]`（buffers_[kWritePlaintext]）- 同理验证 `SSL_read_candidate` 使用 `[SSLFilter, #0x30]`（buffers_[kReadPlaintext]）### Step 8：确认行号反编译 SSL_write 候选函数，找 `ERR_put_error` 调用（`sub_70FXXX`），其 W3 参数（立即数）应约等于 BoringSSL ssl_lib.cc 中 SSL_write 的行号（~940–980）。---### Step 9：找 ssl_read_inner_offset**目标**：找到 SSL_read 内部调用 memcpy 封装桩的 BL 指令偏移量，用于 ecapture inner probe。**封装桩特征**（仅 2 条指令）：```asmMOV X2, X ; 把 size 放入 X2（ARM64 memcpy 第 3 参数）B .memcpy ; 尾调用真正的 memcpy``` 不同版本 size_reg 不同：旧版（de8c7af5）用 `X24`，新版用 `X22`。**在 SSL_read 中定位该 BL**（在 SSL_read 成功路径末尾）：```asm; 识别特征序列（示例来自新版 libflutter.so）：LDR X9, [X8, #0x88] ; X9 = ssl3_state->rbuf.len（可读字节数）MOV W10, W ; W10 = num（用户请求字节数，来自 SSL_read 第 3 参数）CMP X9, W, UXTW ; 比较 avail vs numCSEL X, X9, X10, CC ; X = min(avail, num) ← 就是 size_regCBZ X,  ; 若 0 字节则跳过LDR X1, [X8, #0x80] ; X1 = ssl3_state->rbuf.buf（明文源，C++ heap）MOV X0, X ; X0 = 目标缓冲区BL sub_memcpy_stub ; ← inner probe 就在这里

    **步骤**：1. 用 `mcp0_callees(ssl_read_va)` 列出 SSL_read 的所有被调函数。2. 过滤大小 ≤ 8 字节（2 条指令）的函数，逐一反汇编确认 `MOV X2, Xreg; B .memcpy`。3. 用 `mcp0_xrefs_to(stub_addr)` 找到从 SSL_read 内部调用它的 BL 指令地址（`BL_VA`）。4. 通过反汇编 BL_VA 前后确认上述特征序列（LDR X1 = plaintext src，CSEL = size）。**计算**：```ssl_read_inner_offset = BL_VA - SSL_read_entry_VA```无需减 0x1000（相对偏移，偏差自动消除）。---## 输出格式```SSL_write IDA VA : 0xXXXXXXSSL_read IDA VA : 0xXXXXXXssl_read_inner_offset : 0xXXX (= BL_VA - SSL_read_entry_VA, 无需减 0x1000)# ecapture 实际传参（file offset = IDA VA - 0x1000）：--ssl_write_addr 0xXXXXXX (= SSL_write_IDA_VA - 0x1000)--ssl_read_addr 0xXXXXXX (= SSL_read_IDA_VA - 0x1000)--ssl_read_inner_offset 0xXXX (与 IDA 偏移相同)```> 验证 file offset：在 IDA Python 中执行

![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MSjTyfCyhfFEYibBLeWT4HFwU3SbcDqgicsvCJcvzomiaR3DKX5XthTWiaiculcRRgJRKfR3cWIxglsEWDdhtfKJsibQPFOxOjTAx7icY/640?wx_fmt=png&from=appmsg)
等待 IDA 分析出结果。
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MS0vibmBVQqsSuEIUiaUlhicY65a2aV1415mxnObPEYlZpWsQAic5EVBVxk82wJpslQPXvdnXibIh1oaFiajR6zgcDNGV8XibTWaF0qek/640?wx_fmt=png&from=appmsg)
这里，差不多 10 分钟左右，就能出结果，其他输出不需要关注，看到红框里面的有就行了，其他的并不重要，其他输出是有要兼容不同版本补进去的，不影响。
这里其他模型的效果自行尝试，大模型输出本身有随机性，目前测试  codex  效果相对稳定，如果发现他给你胡乱输出其他内容，考虑一下自己的模型来源。
实验验证  现在有了偏移，我们就可以来看一下这个的实际效果了  注意这里手机要能支持原版的 ecapture 跑起来，也就是内核版本要满足要求。  验证环境
这里我采用的环境和内核版本如下，理论上大于 5.15 的应该都没啥问题  Android ARM64（Linux localhost
6.6.30-android15-8-gdd9c02ccfe27-ab11987101-4k  #1  SMP PREEMPT Tue Jun 18
20:50:32 UTC 2024 aarch64 Toybox），root 权限  推送工具并确定 so 路径  将修改版  ecapture
推送到设备（注意：此版本只能抓 Flutter，其他流量请用原版）：

    bash adb push ecapture /data/local/tmp/ecapture adb shell dumpsys package com.yrx.flutternet | grep -E "codePath|resourcePath|dataDir"

![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRBnNPhWwn0s4dtj5UU0F0KYm5rp19Kmd9ibibeoHm4rYd6siaRtKDT2UQIPyzO6aTCbb4qTDG9ccJlFobmmxHtq5sSCDasrorhso/640?wx_fmt=png&from=appmsg)
情况一：so 已解压（默认）  多数App会将  libflutter.so  解压到  /data/app/.../lib/arm64/
目录，可直接使用该路径。
情况二： extractNativeLibs = false  部分App 在  AndroidManifest.xml  中设置了
android:extractNativeLibs="false"  。  此时  libflutter.so  不会解压到文件系统，而是以未压缩方式保留在
APK 内部。
判断方法：

    # 检查 so 是否存在于文件系统adb shell ls /data/app/~~xxx/com.example-xxx==/lib/arm64/libflutter.so# 若不存在，获取 APK 路径adb shell pm path com.example.app# 输出示例：package:/data/app/~~xxx/com.example-xxx==/base.apk

![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MS3IPkIeg6ARrXPjfK9gTKcesqWx5dXD80c4WrYqVJllxp4VbBEbuBU7jMFyH4r4HdpEEc4voj9lE96uOM8y3O9pCteKN2uIJs/640?wx_fmt=png&from=appmsg)
提取 so 用于 IDA 分析：

    # 把 APK 拉到本地adb pull /data/app/~~xxx/com.xxx-xxx==/base.apk ./base.apk# 从 APK 解出 libflutter.sounzip -p base.apk lib/arm64-v8a/libflutter.so > libflutter.so

用解出的  libflutter.so  按相同流程做 IDA + AI 分析，得到文件偏移。  ecapture 命令：  将 APK 路径传给
\--libssl  ，ecapture 会自动找到 APK 内 so 的数据偏移并叠加到地址上：

    /data/local/tmp/ecapture tls \--libssl /data/app/~~xxx/com.xxx-xxx==/base.apk \--ssl_write_addr 0x73DB50 --ssl_read_addr 0x73D348 \--ssl_version 'boringssl 1.1.1'

> \--ssl_write_addr  /  \--ssl_read_addr  传的始终是相对于  libflutter.so  文件本身的偏移 （
> IDA VA - 0x1000  ），与情况一相同。传入 APK 路径时，ecapture 会自动加上 so 在 APK 内的数据偏移，无需手动计算。

ecapture 捕获命令

    /data/local/tmp/ecapture tls \--libssl /data/app/.../lib/arm64/libflutter.so \--ssl_write_addr 0x73DB50 --ssl_read_addr 0x73D348 \--ssl_version 'boringssl 1.1.1'

![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTvcTpdQOfcvkeHevVoSoyjvIicknHE73gXQe75SCLFG9vtaUId2ic6iaWwASdnLzACFcuENf9cYwdZX3AictAJm1IzWibjpq6GOtUg/640?wx_fmt=png&from=appmsg)
成功获取明文的请求和响应数据，这个应用是用最新的 flutter 打包的，可以发现正常拿到了抓包数据。  然后，我们设置
extractNativeLibs=false  ，再来看一下效果。
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRwzibB0OhTlSeQWE2FZpTRYuneZOkiaG7SVnyMkCD5NAHK4R81r5CX5lYCpibM5PwNaCFR3Ryc763l0AKK4hT6m4NWUQqCib9UxU0/640?wx_fmt=png&from=appmsg)
可以发现，这块依然是没有问题的，成功获取到了数据包。  最后，我们再来随机的挑选一位受害者，这里就不具体透露名字了，方法完全一样，提示词不用换，拿到
偏移地址即可，AI 会自己分析：
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTAXZDYm8biakImXKibKm9JZuVsRC6ujQKAhvIxvPQzfib3IfCTCT71ukydlbMTICAIjibY6AEUJT3CmMSsAymrOBaicHsZGCYS8K00/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MT0OqOOGyibEHApy6ic8Cibdp057gsoibX3SfkFOM7bkdPv0cgJUTC6rllTn8oNj6Y0VpP3dPUm1XnicWkfSFRib1BpnF2nQo4EiaZjWY/640?wx_fmt=png&from=appmsg)
结论  通过 AI + IDA-Pro MCP  自动完成了 stripped libflutter.so 中关键函数的定位  解决了新版 Flutter
抓包难题。同一 Flutter 版本的不同 App 可以复用偏移，后续新版本也可以按相同思路处理。
参考资料

  * ecapture 项目：  https://github.com/gojue/ecapture

  * cilium/ebpf 文档：  https://pkg.go.dev/github.com/cilium/ebpf

  * BoringSSL 源码：  https://boringssl.googlesource.com/boringssl

  * 修改后的实现:  https://github.com/Litt1eQ/ecapture
