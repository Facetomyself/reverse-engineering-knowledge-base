# Akamai对抗的隐秘战线——TLS指纹

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2026-07-13
> 归档日期: 2026-07-16
> 分类: anti-detection
>
> 调试 Akamai 站点爬虫时发现，Requests 默认发包极易被风控识别拦截，单纯修改请求头完全无法规避。

调试 Akamai 站点爬虫时发现，Requests 默认发包极易被风控识别拦截，单纯修改请求头完全无法规避。

为搞懂底层识别逻辑，本文从零梳理 TLS 握手、JA3/JA4 指纹核心原理，搭配 Wireshark
抓包对比脚本与浏览器的数据包差异，拆解指纹识别完整链路，最后给出复刻浏览器 TLS 特征、自建请求库的实操方案。

## 背景科普

在动手抓包之前，科普一些名词。

**1\. TLS 握手/ClientHello 是什么？**
访问  ` https://  ` 网站时，在专属数据之前时，客户端会先给服务器发一个  **ClientHello**
的包，里面包含着加密套件，扩展程序这些关键信息，不同版本的客户端携带的内容不一样。

**2\. 为什么能当「指纹」？**
关键在于——这个  **ClientHello** 是  **明文**
发的（加密还没建立起来），任何人都能看到里面全部内容。而且不同客户端（Chrome、Firefox、requests）携带的内容都不一致，但每个客户端携带的内容每次都很相似，所以通过这个可以来进行判断客户端。

**3\. JA3 / JA4 是什么？**
客户端发送  **ClientHello** 时，将 加密套件、 扩展等相关信息按一定的规则来计算成hash，当作这个客户端的  ** 指纹 ID
** 。服务器 / WAF（如 Akamai）手里有一份「已知浏览器指纹库」，来一个请求就算一次指纹去比对：对得上真浏览器就放行，对不上就当成脚本拦掉。

**4\. 那 requests 为什么老是被认出来？**
因为 requests 底层是  **OpenSSL** ，它的 ClientHello 是OpenSSL，对于校验严格会一下识别出来。而且这发生在
**TLS 握手阶段，比 HTTP 请求还早** —所以你就算把  ` User-Agent  ` 改成 Chrome 也没用。

## 指纹检测的流程

    一致

    不一致

    客户端发起 HTTPS 请求TCP 建连发送 ClientHello(明文，未加密)服务器 / WAF提取握手特征计算 TLS 指纹JA3 / JA4计算 HTTP/2 指纹Akamai SETTINGS + 伪头序提取声称身份User-Agent指纹 与 UA是否一致?放行当作真实浏览器拦截 / 挑战403 · 验证码 · 静默降权

## 0\. 版本信息

requests  |  2.34.2
---|---
**firefox** |  **152.0.5**
**chrome** |  **150.0.7871.115**
**wireshark** |  **v4.6.7-0-gb439fb7b47a9**

## 1\. wireshark抓包

一般的抓包软件很难找到相关的请求信息，wireshark作为老牌的网络工具，功能齐全。

打开抓包软件，我在虚拟机进行，捕获的接口为 Ethernet0（以太网）

![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MSxCED1Y9U2eSIo7r9oib4DhPicacicjLY9X75ugiabWE3Hw8iciaLbD6OicJtMSXgAuLsh3dKmjiajIVGOUj1KljgfPaSnMmRDAezckMk/640?wx_fmt=png&from=appmsg)

使用 requests 请求发包

    import requests

    resp = requests.get("https://example.com/").text
    print(resp)

发出请求后，wireshark已经出现  ` Client Hello  ` 相关流量。

![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRqBf4EMy9tlpXmia2zYK4UmBekmJkI1CSibxuleYPfIryiboAjHwpRO5jks01SRHrxGhiaovBGpxibowZziaa5icibicXT2F3bhhBvbnog/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MSAIESovnv1uHhKwLSQl41M7iaTK0rd1GibYIBcgemicBoDtyxyibGpzgicC5OUvhopCJqVwTQ3y2OmvcZ8Wy4JUMlfGrA4UKtMrgc8/640?wx_fmt=png&from=appmsg)

抓包的信息相关解释如下表格

英文（Wireshark 显示）  |  中文名称
---|---
**Frame** |  帧 / 抓包元信息
**Ethernet II** |  以太网（链路层帧头）
**Internet Protocol Version 4** |  网际协议第 4 版（IPv4）
**Transmission Control Protocol** |  传输控制协议（TCP）
**Transport Layer Security** |  传输层安全协议（TLS）重点关注★

重点关注  ` Transport Layer Security  ` 这里。接下来关注  ` firefox  ` 和  ` chrome  ` 的请求

## 2\. Client Hello完整数据包

### 2.1 Python Requests库

    Frame 4: Packet, 1587 bytes on wire (12696 bits), 1587 bytes captured (12696 bits) on interface \Device\NPF_{1B5B72E7-3008-426A-AAC9-250F52762B5E}, id 0
        Section number: 1
        Interface id: 0 (\Device\NPF_{1B5B72E7-3008-426A-AAC9-250F52762B5E})
            Interface name: \Device\NPF_{1B5B72E7-3008-426A-AAC9-250F52762B5E}
            Interface description: Ethernet0
        Encapsulation type: Ethernet (1)
        Arrival Time: Jul  9, 2026 18:43:38.870598400 中国标准时间
        UTC Arrival Time: Jul  9, 2026 10:43:38.870598400 UTC
        Epoch Arrival Time: 1783593818.870598400
        [Time shift for this packet: 0.000000000 seconds]
        [Time delta from previous captured frame: 12.361700 milliseconds]
        [Time delta from previous displayed frame: 12.361700 milliseconds]
        [Time since reference or first frame: 226.679200 milliseconds]
        Frame Number: 4
        Frame Length: 1587 bytes (12696 bits)
        Capture Length: 1587 bytes (12696 bits)
        [Frame is marked: False]
        [Frame is ignored: False]
        [Protocols in frame: eth:ethertype:ip:tcp:tls]
        Character encoding: ASCII (0)
        [Coloring Rule Name: TCP]
        [Coloring Rule String: tcp]
    Ethernet II, Src: VMware_23:87:c9 (00:0c:29:23:87:c9), Dst: XiaomiMobile_ea:55:c4 (50:4f:3b:ea:55:c4)
        Destination: XiaomiMobile_ea:55:c4 (50:4f:3b:ea:55:c4)
            .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
            .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
        Source: VMware_23:87:c9 (00:0c:29:23:87:c9)
            .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
            .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
        Type: IPv4 (0x0800)
        [Stream index: 0]
    Internet Protocol Version 4, Src: <private-ip>, Dst: 172.66.147.243
        0100 .... = Version: 4
        .... 0101 = Header Length: 20 bytes (5)
        Differentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)
            0000 00.. = Differentiated Services Codepoint: Default (0)
            .... ..00 = Explicit Congestion Notification: Not ECN-Capable Transport (0)
        [Total Length: 1573 bytes (reported as 0, presumed to be because of "TCP segmentation offload" (TSO))]
        Identification: 0x2bef (11247)
        010. .... = Flags: 0x2, Don't fragment
            0... .... = Reserved bit: Not set
            .1.. .... = Don't fragment: Set
            ..0. .... = More fragments: Not set
        ...0 0000 0000 0000 = Fragment Offset: 0
        Time to Live: 128
        Protocol: TCP (6)
        Header Checksum: 0x0000 [validation disabled]
        [Header checksum status: Unverified]
        Source Address: <private-ip>
        Destination Address: 172.66.147.243
        [Stream index: 0]
    Transmission Control Protocol, Src Port: 55171, Dst Port: 443, Seq: 1, Ack: 1, Len: 1533
        Source Port: 55171
        Destination Port: 443
        [Stream index: 0]
        [Stream Packet Number: 4]
        [Conversation completeness: Complete, WITH_DATA (31)]
            ..0. .... = RST: Absent
            ...1 .... = FIN: Present
            .... 1... = Data: Present
            .... .1.. = ACK: Present
            .... ..1. = SYN-ACK: Present
            .... ...1 = SYN: Present
            [Completeness Flags: ·FDASS]
        [TCP Segment Len: 1533]
        Sequence Number: 1    (relative sequence number)
        Sequence Number (raw): 2825017551
        [Next Sequence Number: 1534    (relative sequence number)]
        Acknowledgment Number: 1    (relative ack number)
        Acknowledgment number (raw): 133989241
        0101 .... = Header Length: 20 bytes (5)
        Flags: 0x018 (PSH, ACK)
            000. .... .... = Reserved: Not set
            ...0 .... .... = Accurate ECN: Not set
            .... 0... .... = Congestion Window Reduced: Not set
            .... .0.. .... = ECN-Echo: Not set
            .... ..0. .... = Urgent: Not set
            .... ...1 .... = Acknowledgment: Set
            .... .... 1... = Push: Set
            .... .... .0.. = Reset: Not set
            .... .... ..0. = Syn: Not set
            .... .... ...0 = Fin: Not set
            [TCP Flags: ·······AP···]
        Window: 1028
        [Calculated window size: 263168]
        [Window size scaling factor: 256]
        Checksum: 0x2088 [unverified]
        [Checksum Status: Unverified]
        Urgent Pointer: 0
        [Timestamps]
            [Time since first frame in this TCP stream: 226.679200 milliseconds]
            [Time since previous frame in this TCP stream: 12.361700 milliseconds]
        [SEQ/ACK analysis]
            [iRTT: 214.317500 milliseconds]
            [Bytes in flight: 1533]
            [Bytes sent since last PSH flag: 1533]
        [Client Contiguous Streams: 1]
        [Server Contiguous Streams: 1]
        TCP payload (1533 bytes)
    Transport Layer Security
        [Stream index: 0]
        TLSv1.3 Record Layer: Handshake Protocol: Client Hello
            Content Type: Handshake (22)
            Version: TLS 1.0 (0x0301)
            Length: 1528
            Handshake Protocol: Client Hello
                Handshake Type: Client Hello (1)
                Length: 1524
                Version: TLS 1.2 (0x0303)
                    [Expert Info (Chat/Deprecated): This legacy_version field MUST be ignored. The supported_versions extension is present and MUST be used instead.]
                        [This legacy_version field MUST be ignored. The supported_versions extension is present and MUST be used instead.]
                        [Severity level: Chat]
                        [Group: Deprecated]
                Random: 2451d4ff61edf485b8b8accbfdd26a9ef0af2b4c9b6221263336fa6353b02052
                Session ID Length: 32
                Session ID: 38c3f18427ff8ef741e758b6e9298dba7654295b8b651cb5cbda7c5bd6bbe5f6
                Cipher Suites Length: 34
                Cipher Suites (17 suites)
                    Cipher Suite: TLS_AES_256_GCM_SHA384 (0x1302)
                    Cipher Suite: TLS_CHACHA20_POLY1305_SHA256 (0x1303)
                    Cipher Suite: TLS_AES_128_GCM_SHA256 (0x1301)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (0xc02c)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (0xc030)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 (0xc02b)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (0xc02f)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 (0xcca9)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 (0xcca8)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384 (0xc024)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384 (0xc028)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 (0xc023)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256 (0xc027)
                    Cipher Suite: TLS_DHE_RSA_WITH_AES_256_GCM_SHA384 (0x009f)
                    Cipher Suite: TLS_DHE_RSA_WITH_AES_128_GCM_SHA256 (0x009e)
                    Cipher Suite: TLS_DHE_RSA_WITH_AES_256_CBC_SHA256 (0x006b)
                    Cipher Suite: TLS_DHE_RSA_WITH_AES_128_CBC_SHA256 (0x0067)
                Compression Methods Length: 1
                Compression Methods (1 method)
                    Compression Method: null (0)
                Extensions Length: 1417
                Extension: renegotiation_info (len=1)
                    Type: renegotiation_info (65281)
                    Length: 1
                    Renegotiation Info extension
                        Renegotiation info extension length: 0
                Extension: server_name (len=16) name=example.com
                    Type: server_name (0)
                    Length: 16
                    Server Name Indication extension
                        Server Name list length: 14
                        Server Name Type: host_name (0)
                        Server Name length: 11
                        Server Name: example.com
                Extension: ec_point_formats (len=4)
                    Type: ec_point_formats (11)
                    Length: 4
                    EC point formats Length: 3
                    Elliptic curves point formats (3)
                        EC point format: uncompressed (0)
                        EC point format: ansiX962_compressed_prime (1)
                        EC point format: ansiX962_compressed_char2 (2)
                Extension: supported_groups (len=18)
                    Type: supported_groups (10)
                    Length: 18
                    Supported Groups List Length: 16
                    Supported Groups (8 groups)
                        Supported Group: X25519MLKEM768 (0x11ec)
                        Supported Group: x25519 (0x001d)
                        Supported Group: secp256r1 (0x0017)
                        Supported Group: x448 (0x001e)
                        Supported Group: secp384r1 (0x0018)
                        Supported Group: secp521r1 (0x0019)
                        Supported Group: ffdhe2048 (0x0100)
                        Supported Group: ffdhe3072 (0x0101)
                Extension: application_layer_protocol_negotiation (len=11)
                    Type: application_layer_protocol_negotiation (16)
                    Length: 11
                    ALPN Extension Length: 9
                    ALPN Protocol
                        ALPN string length: 8
                        ALPN Next Protocol: http/1.1
                Extension: encrypt_then_mac (len=0)
                    Type: encrypt_then_mac (22)
                    Length: 0
                Extension: extended_master_secret (len=0)
                    Type: extended_master_secret (23)
                    Length: 0
                Extension: post_handshake_auth (len=0)
                    Type: post_handshake_auth (49)
                    Length: 0
                Extension: signature_algorithms (len=54)
                    Type: signature_algorithms (13)
                    Length: 54
                    Signature Hash Algorithms Length: 52
                    Signature Hash Algorithms (26 algorithms)
                        Signature Algorithm: mldsa65 (0x0905)
                            Signature Hash Algorithm Hash: Unknown (9)
                            Signature Hash Algorithm Signature: Unknown (5)
                        Signature Algorithm: mldsa87 (0x0906)
                            Signature Hash Algorithm Hash: Unknown (9)
                            Signature Hash Algorithm Signature: Unknown (6)
                        Signature Algorithm: mldsa44 (0x0904)
                            Signature Hash Algorithm Hash: Unknown (9)
                            Signature Hash Algorithm Signature: Unknown (4)
                        Signature Algorithm: ecdsa_secp256r1_sha256 (0x0403)
                            Signature Hash Algorithm Hash: SHA256 (4)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: ecdsa_secp384r1_sha384 (0x0503)
                            Signature Hash Algorithm Hash: SHA384 (5)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: ecdsa_secp521r1_sha512 (0x0603)
                            Signature Hash Algorithm Hash: SHA512 (6)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: ed25519 (0x0807)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (7)
                        Signature Algorithm: ed448 (0x0808)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (8)
                        Signature Algorithm: ecdsa_brainpoolP256r1tls13_sha256 (0x081a)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (26)
                        Signature Algorithm: ecdsa_brainpoolP384r1tls13_sha384 (0x081b)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (27)
                        Signature Algorithm: ecdsa_brainpoolP512r1tls13_sha512 (0x081c)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (28)
                        Signature Algorithm: rsa_pss_pss_sha256 (0x0809)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (9)
                        Signature Algorithm: rsa_pss_pss_sha384 (0x080a)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (10)
                        Signature Algorithm: rsa_pss_pss_sha512 (0x080b)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (11)
                        Signature Algorithm: rsa_pss_rsae_sha256 (0x0804)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (4)
                        Signature Algorithm: rsa_pss_rsae_sha384 (0x0805)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (5)
                        Signature Algorithm: rsa_pss_rsae_sha512 (0x0806)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (6)
                        Signature Algorithm: rsa_pkcs1_sha256 (0x0401)
                            Signature Hash Algorithm Hash: SHA256 (4)
                            Signature Hash Algorithm Signature: RSA (1)
                        Signature Algorithm: rsa_pkcs1_sha384 (0x0501)
                            Signature Hash Algorithm Hash: SHA384 (5)
                            Signature Hash Algorithm Signature: RSA (1)
                        Signature Algorithm: rsa_pkcs1_sha512 (0x0601)
                            Signature Hash Algorithm Hash: SHA512 (6)
                            Signature Hash Algorithm Signature: RSA (1)
                        Signature Algorithm: SHA224 ECDSA (0x0303)
                            Signature Hash Algorithm Hash: SHA224 (3)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: SHA224 RSA (0x0301)
                            Signature Hash Algorithm Hash: SHA224 (3)
                            Signature Hash Algorithm Signature: RSA (1)
                        Signature Algorithm: SHA224 DSA (0x0302)
                            Signature Hash Algorithm Hash: SHA224 (3)
                            Signature Hash Algorithm Signature: DSA (2)
                        Signature Algorithm: SHA256 DSA (0x0402)
                            Signature Hash Algorithm Hash: SHA256 (4)
                            Signature Hash Algorithm Signature: DSA (2)
                        Signature Algorithm: SHA384 DSA (0x0502)
                            Signature Hash Algorithm Hash: SHA384 (5)
                            Signature Hash Algorithm Signature: DSA (2)
                        Signature Algorithm: SHA512 DSA (0x0602)
                            Signature Hash Algorithm Hash: SHA512 (6)
                            Signature Hash Algorithm Signature: DSA (2)
                Extension: supported_versions (len=5) TLS 1.3, TLS 1.2
                    Type: supported_versions (43)
                    Length: 5
                    Supported Versions length: 4
                    Supported Version: TLS 1.3 (0x0304)
                    Supported Version: TLS 1.2 (0x0303)
                Extension: psk_key_exchange_modes (len=2)
                    Type: psk_key_exchange_modes (45)
                    Length: 2
                    PSK Key Exchange Modes Length: 1
                    PSK Key Exchange Mode: PSK with (EC)DHE key establishment (psk_dhe_ke) (1)
                Extension: key_share (len=1258) X25519MLKEM768, x25519
                    Type: key_share (51)
                    Length: 1258
                    Key Share extension
                        Client Key Share Length: 1256
                        Key Share Entry: Group: X25519MLKEM768, Key Exchange length: 1216
                            Group: X25519MLKEM768 (4588)
                            Key Exchange Length: 1216
                            Key Exchange […]: 3ff925d9d94eeedb2bf897bff6b4a31d107d04176d592aa16b0442e144331809598d3b9db7880ac5a18b5812af16339783470ce0079e65b68664923051f7c65a553a13911775296ecae8b836e12afea2c32f009a7c9c8ee0301866ec6136ea14fa0376d164b5f946be295bb8116
                        Key Share Entry: Group: x25519, Key Exchange length: 32
                            Group: x25519 (29)
                            Key Exchange Length: 32
                            Key Exchange: b09c22d452ad7367b4ceb4aabb72aa94f24fc34ce0e7c2ae15799359e847eb2d
                [JA4: t13d1712h1_ab0a1bf427ad_882d495ac381]
                [JA4_r […]: t13d1712h1_0067,006b,009e,009f,1301,1302,1303,c023,c024,c027,c028,c02b,c02c,c02f,c030,cca8,cca9_000a,000b,000d,0016,0017,002b,002d,0031,0033,ff01_0905,0906,0904,0403,0503,0603,0807,0808,081a,081b,081c,0809,080a,080b,0804,0805,]
                [JA3 Fullstring: 771,4866-4867-4865-49196-49200-49195-49199-52393-52392-49188-49192-49187-49191-159-158-107-103,65281-0-11-10-16-22-23-49-13-43-45-51,4588-29-23-30-24-25-256-257,0-1-2]
                [JA3: 7291ea5e449f2c7b17582541703e549d]

### 2.2 Firefox

    Frame 10: Packet, 1948 bytes on wire (15584 bits), 1948 bytes captured (15584 bits) on interface \Device\NPF_{1B5B72E7-3008-426A-AAC9-250F52762B5E}, id 0
        Section number: 1
        Interface id: 0 (\Device\NPF_{1B5B72E7-3008-426A-AAC9-250F52762B5E})
            Interface name: \Device\NPF_{1B5B72E7-3008-426A-AAC9-250F52762B5E}
            Interface description: Ethernet0
        Encapsulation type: Ethernet (1)
        Arrival Time: Jul  9, 2026 18:41:00.724424600 中国标准时间
        UTC Arrival Time: Jul  9, 2026 10:41:00.724424600 UTC
        Epoch Arrival Time: 1783593660.724424600
        [Time shift for this packet: 0.000000000 seconds]
        [Time delta from previous captured frame: 618.600 microseconds]
        [Time delta from previous displayed frame: 618.600 microseconds]
        [Time since reference or first frame: 1.997454400 seconds]
        Frame Number: 10
        Frame Length: 1948 bytes (15584 bits)
        Capture Length: 1948 bytes (15584 bits)
        [Frame is marked: False]
        [Frame is ignored: False]
        [Protocols in frame: eth:ethertype:ip:tcp:tls]
        Character encoding: ASCII (0)
        [Coloring Rule Name: TCP]
        [Coloring Rule String: tcp]
    Ethernet II, Src: VMware_23:87:c9 (00:0c:29:23:87:c9), Dst: XiaomiMobile_ea:55:c4 (50:4f:3b:ea:55:c4)
        Destination: XiaomiMobile_ea:55:c4 (50:4f:3b:ea:55:c4)
            .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
            .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
        Source: VMware_23:87:c9 (00:0c:29:23:87:c9)
            .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
            .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
        Type: IPv4 (0x0800)
        [Stream index: 1]
    Internet Protocol Version 4, Src: <private-ip>, Dst: 172.66.147.243
        0100 .... = Version: 4
        .... 0101 = Header Length: 20 bytes (5)
        Differentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)
            0000 00.. = Differentiated Services Codepoint: Default (0)
            .... ..00 = Explicit Congestion Notification: Not ECN-Capable Transport (0)
        [Total Length: 1934 bytes (reported as 0, presumed to be because of "TCP segmentation offload" (TSO))]
        Identification: 0x2bcf (11215)
        010. .... = Flags: 0x2, Don't fragment
            0... .... = Reserved bit: Not set
            .1.. .... = Don't fragment: Set
            ..0. .... = More fragments: Not set
        ...0 0000 0000 0000 = Fragment Offset: 0
        Time to Live: 128
        Protocol: TCP (6)
        Header Checksum: 0x0000 [validation disabled]
        [Header checksum status: Unverified]
        Source Address: <private-ip>
        Destination Address: 172.66.147.243
        [Stream index: 2]
    Transmission Control Protocol, Src Port: 55131, Dst Port: 443, Seq: 1, Ack: 1, Len: 1894
        Source Port: 55131
        Destination Port: 443
        [Stream index: 1]
        [Stream Packet Number: 4]
        [Conversation completeness: Incomplete, DATA (15)]
            ..0. .... = RST: Absent
            ...0 .... = FIN: Absent
            .... 1... = Data: Present
            .... .1.. = ACK: Present
            .... ..1. = SYN-ACK: Present
            .... ...1 = SYN: Present
            [Completeness Flags: ··DASS]
        [TCP Segment Len: 1894]
        Sequence Number: 1    (relative sequence number)
        Sequence Number (raw): 468398048
        [Next Sequence Number: 1895    (relative sequence number)]
        Acknowledgment Number: 1    (relative ack number)
        Acknowledgment number (raw): 2400450490
        0101 .... = Header Length: 20 bytes (5)
        Flags: 0x018 (PSH, ACK)
            000. .... .... = Reserved: Not set
            ...0 .... .... = Accurate ECN: Not set
            .... 0... .... = Congestion Window Reduced: Not set
            .... .0.. .... = ECN-Echo: Not set
            .... ..0. .... = Urgent: Not set
            .... ...1 .... = Acknowledgment: Set
            .... .... 1... = Push: Set
            .... .... .0.. = Reset: Not set
            .... .... ..0. = Syn: Not set
            .... .... ...0 = Fin: Not set
            [TCP Flags: ·······AP···]
        Window: 1028
        [Calculated window size: 263168]
        [Window size scaling factor: 256]
        Checksum: 0x2088 [unverified]
        [Checksum Status: Unverified]
        Urgent Pointer: 0
        [Timestamps]
            [Time since first frame in this TCP stream: 192.694400 milliseconds]
            [Time since previous frame in this TCP stream: 618.600 microseconds]
        [SEQ/ACK analysis]
            [iRTT: 192.075800 milliseconds]
            [Bytes in flight: 1894]
            [Bytes sent since last PSH flag: 1894]
        [Client Contiguous Streams: 1]
        [Server Contiguous Streams: 1]
        TCP payload (1894 bytes)
    Transport Layer Security
        [Stream index: 0]
        TLSv1.3 Record Layer: Handshake Protocol: Client Hello
            Content Type: Handshake (22)
            Version: TLS 1.0 (0x0301)
            Length: 1889
            Handshake Protocol: Client Hello
                Handshake Type: Client Hello (1)
                Length: 1885
                Version: TLS 1.2 (0x0303)
                    [Expert Info (Chat/Deprecated): This legacy_version field MUST be ignored. The supported_versions extension is present and MUST be used instead.]
                        [This legacy_version field MUST be ignored. The supported_versions extension is present and MUST be used instead.]
                        [Severity level: Chat]
                        [Group: Deprecated]
                Random: baea10cb62fe88c424360a049ae1152c377f7a6f1dcee31defd273032e56ca17
                Session ID Length: 32
                Session ID: 14fe0ed93b39c185a9dfe9ed87687da9e05fd9486533163322f4676a98eeb8cf
                Cipher Suites Length: 32
                Cipher Suites (16 suites)
                    Cipher Suite: TLS_AES_128_GCM_SHA256 (0x1301)
                    Cipher Suite: TLS_CHACHA20_POLY1305_SHA256 (0x1303)
                    Cipher Suite: TLS_AES_256_GCM_SHA384 (0x1302)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 (0xc02b)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (0xc02f)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 (0xcca9)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 (0xcca8)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (0xc02c)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (0xc030)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA (0xc00a)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (0xc013)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA (0xc014)
                    Cipher Suite: TLS_RSA_WITH_AES_128_GCM_SHA256 (0x009c)
                    Cipher Suite: TLS_RSA_WITH_AES_256_GCM_SHA384 (0x009d)
                    Cipher Suite: TLS_RSA_WITH_AES_128_CBC_SHA (0x002f)
                    Cipher Suite: TLS_RSA_WITH_AES_256_CBC_SHA (0x0035)
                Compression Methods Length: 1
                Compression Methods (1 method)
                    Compression Method: null (0)
                Extensions Length: 1780
                Extension: server_name (len=16) name=example.com
                    Type: server_name (0)
                    Length: 16
                    Server Name Indication extension
                        Server Name list length: 14
                        Server Name Type: host_name (0)
                        Server Name length: 11
                        Server Name: example.com
                Extension: extended_master_secret (len=0)
                    Type: extended_master_secret (23)
                    Length: 0
                Extension: renegotiation_info (len=1)
                    Type: renegotiation_info (65281)
                    Length: 1
                    Renegotiation Info extension
                        Renegotiation info extension length: 0
                Extension: supported_groups (len=16)
                    Type: supported_groups (10)
                    Length: 16
                    Supported Groups List Length: 14
                    Supported Groups (7 groups)
                        Supported Group: X25519MLKEM768 (0x11ec)
                        Supported Group: x25519 (0x001d)
                        Supported Group: secp256r1 (0x0017)
                        Supported Group: secp384r1 (0x0018)
                        Supported Group: secp521r1 (0x0019)
                        Supported Group: ffdhe2048 (0x0100)
                        Supported Group: ffdhe3072 (0x0101)
                Extension: ec_point_formats (len=2)
                    Type: ec_point_formats (11)
                    Length: 2
                    EC point formats Length: 1
                    Elliptic curves point formats (1)
                        EC point format: uncompressed (0)
                Extension: session_ticket (len=0)
                    Type: session_ticket (35)
                    Length: 0
                    Session Ticket: <MISSING>
                Extension: application_layer_protocol_negotiation (len=14)
                    Type: application_layer_protocol_negotiation (16)
                    Length: 14
                    ALPN Extension Length: 12
                    ALPN Protocol
                        ALPN string length: 2
                        ALPN Next Protocol: h2
                        ALPN string length: 8
                        ALPN Next Protocol: http/1.1
                Extension: status_request (len=5)
                    Type: status_request (5)
                    Length: 5
                    Certificate Status Type: OCSP (1)
                    Responder ID list Length: 0
                    Request Extensions Length: 0
                Extension: delegated_credentials (len=10)
                    Type: delegated_credentials (34)
                    Length: 10
                    Signature Hash Algorithms Length: 8
                    Signature Hash Algorithms (4 algorithms)
                        Signature Algorithm: ecdsa_secp256r1_sha256 (0x0403)
                            Signature Hash Algorithm Hash: SHA256 (4)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: ecdsa_secp384r1_sha384 (0x0503)
                            Signature Hash Algorithm Hash: SHA384 (5)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: ecdsa_secp521r1_sha512 (0x0603)
                            Signature Hash Algorithm Hash: SHA512 (6)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: ecdsa_sha1 (0x0203)
                            Signature Hash Algorithm Hash: SHA1 (2)
                            Signature Hash Algorithm Signature: ECDSA (3)
                Extension: signed_certificate_timestamp (len=0)
                    Type: signed_certificate_timestamp (18)
                    Length: 0
                Extension: key_share (len=1327) X25519MLKEM768, x25519, secp256r1
                    Type: key_share (51)
                    Length: 1327
                    Key Share extension
                        Client Key Share Length: 1325
                        Key Share Entry: Group: X25519MLKEM768, Key Exchange length: 1216
                            Group: X25519MLKEM768 (4588)
                            Key Exchange Length: 1216
                            Key Exchange […]: f1a9369202492cb8134c10437901a80e122d5318b79b27baa7d83ffc0543c8a6012fdccd46858a3fda3120b39308b8841604a0a90a72945ab590dcc4f8f7c9176b6335056d4696504b52b6c0b92cfa0b331619695fa77b094b55b2f80891a45c4b5a33d79122f4e12c67d7b771f
                        Key Share Entry: Group: x25519, Key Exchange length: 32
                            Group: x25519 (29)
                            Key Exchange Length: 32
                            Key Exchange: 8e8108092a780cda7aa76a875a9b56094f03d1acc1866cf32ceb08d17d16c60c
                        Key Share Entry: Group: secp256r1, Key Exchange length: 65
                            Group: secp256r1 (23)
                            Key Exchange Length: 65
                            Key Exchange: 045376de4a03592749a1f852bf4b37381bb8c1eb08229a954cf5e29a4003f73211a1ac0f8643c48218a9f45ea5376771475cc6328d49144d8dd6406941138e7a34
                Extension: supported_versions (len=5) TLS 1.3, TLS 1.2
                    Type: supported_versions (43)
                    Length: 5
                    Supported Versions length: 4
                    Supported Version: TLS 1.3 (0x0304)
                    Supported Version: TLS 1.2 (0x0303)
                Extension: signature_algorithms (len=24)
                    Type: signature_algorithms (13)
                    Length: 24
                    Signature Hash Algorithms Length: 22
                    Signature Hash Algorithms (11 algorithms)
                        Signature Algorithm: ecdsa_secp256r1_sha256 (0x0403)
                            Signature Hash Algorithm Hash: SHA256 (4)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: ecdsa_secp384r1_sha384 (0x0503)
                            Signature Hash Algorithm Hash: SHA384 (5)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: ecdsa_secp521r1_sha512 (0x0603)
                            Signature Hash Algorithm Hash: SHA512 (6)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: rsa_pss_rsae_sha256 (0x0804)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (4)
                        Signature Algorithm: rsa_pss_rsae_sha384 (0x0805)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (5)
                        Signature Algorithm: rsa_pss_rsae_sha512 (0x0806)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (6)
                        Signature Algorithm: rsa_pkcs1_sha256 (0x0401)
                            Signature Hash Algorithm Hash: SHA256 (4)
                            Signature Hash Algorithm Signature: RSA (1)
                        Signature Algorithm: rsa_pkcs1_sha384 (0x0501)
                            Signature Hash Algorithm Hash: SHA384 (5)
                            Signature Hash Algorithm Signature: RSA (1)
                        Signature Algorithm: rsa_pkcs1_sha512 (0x0601)
                            Signature Hash Algorithm Hash: SHA512 (6)
                            Signature Hash Algorithm Signature: RSA (1)
                        Signature Algorithm: ecdsa_sha1 (0x0203)
                            Signature Hash Algorithm Hash: SHA1 (2)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: rsa_pkcs1_sha1 (0x0201)
                            Signature Hash Algorithm Hash: SHA1 (2)
                            Signature Hash Algorithm Signature: RSA (1)
                Extension: psk_key_exchange_modes (len=2)
                    Type: psk_key_exchange_modes (45)
                    Length: 2
                    PSK Key Exchange Modes Length: 1
                    PSK Key Exchange Mode: PSK with (EC)DHE key establishment (psk_dhe_ke) (1)
                Extension: record_size_limit (len=2)
                    Type: record_size_limit (28)
                    Length: 2
                    Record Size Limit: 16385
                Extension: compress_certificate (len=7)
                    Type: compress_certificate (27)
                    Length: 7
                    Algorithms Length: 6
                    Algorithm: zlib (1)
                    Algorithm: brotli (2)
                    Algorithm: zstd (3)
                Extension: encrypted_client_hello (len=281)
                    Type: encrypted_client_hello (65037)
                    Length: 281
                    Client Hello type: Outer Client Hello (0)
                    Cipher Suite: HKDF-SHA256/AES-128-GCM
                        KDF Id: HKDF-SHA256 (1)
                        AEAD Id: AES-128-GCM (1)
                    Config Id: 212
                    Enc length: 32
                    Enc: a4539b02d1ce0a4dfff8e9bbff03a1387640e5a6044696293e6a21209c72ff31
                    Payload length: 239
                    Payload […]: d88c4933be6d9404884b32c0fd0a449a372c000430c8d9c182ef9325ff12d6d1b2dfc1190603f9b2919fc3fa85229c64ef0da665788bbc79bf1895feadcbf3fef090aa29bf74414b2a6a8fe85bf9b9d269ddd83f6c642f71a0d84277acf4f0ccd248d43c049154b37da3a27384eafd44
                [JA4: t13d1617h2_86a278354501_3cbfd9057e0d]
                [JA4_r: t13d1617h2_002f,0035,009c,009d,1301,1302,1303,c00a,c013,c014,c02b,c02c,c02f,c030,cca8,cca9_0005,000a,000b,000d,0012,0017,001b,001c,0022,0023,002b,002d,0033,fe0d,ff01_0403,0503,0603,0804,0805,0806,0401,0501,0601,0203,0201]
                [JA3 Fullstring: 771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-34-18-51-43-13-45-28-27-65037,4588-29-23-24-25-256-257,0]
                [JA3: 6447ab086255d194909d4013b1a89e87]

### 2.3 Chrome

    Frame 20: Packet, 1813 bytes on wire (14504 bits), 1813 bytes captured (14504 bits) on interface \Device\NPF_{1B5B72E7-3008-426A-AAC9-250F52762B5E}, id 0
        Section number: 1
        Interface id: 0 (\Device\NPF_{1B5B72E7-3008-426A-AAC9-250F52762B5E})
            Interface name: \Device\NPF_{1B5B72E7-3008-426A-AAC9-250F52762B5E}
            Interface description: Ethernet0
        Encapsulation type: Ethernet (1)
        Arrival Time: Jul  9, 2026 19:07:10.337597800 中国标准时间
        UTC Arrival Time: Jul  9, 2026 11:07:10.337597800 UTC
        Epoch Arrival Time: 1783595230.337597800
        [Time shift for this packet: 0.000000000 seconds]
        [Time delta from previous captured frame: 659.900 microseconds]
        [Time delta from previous displayed frame: 659.900 microseconds]
        [Time since reference or first frame: 2.718532000 seconds]
        Frame Number: 20
        Frame Length: 1813 bytes (14504 bits)
        Capture Length: 1813 bytes (14504 bits)
        [Frame is marked: False]
        [Frame is ignored: False]
        [Protocols in frame: eth:ethertype:ip:tcp:tls]
        Character encoding: ASCII (0)
        [Coloring Rule Name: TCP]
        [Coloring Rule String: tcp]
    Ethernet II, Src: VMware_23:87:c9 (00:0c:29:23:87:c9), Dst: XiaomiMobile_ea:55:c4 (50:4f:3b:ea:55:c4)
        Destination: XiaomiMobile_ea:55:c4 (50:4f:3b:ea:55:c4)
            .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
            .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
        Source: VMware_23:87:c9 (00:0c:29:23:87:c9)
            .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
            .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
        Type: IPv4 (0x0800)
        [Stream index: 0]
    Internet Protocol Version 4, Src: <private-ip>, Dst: 172.66.147.243
        0100 .... = Version: 4
        .... 0101 = Header Length: 20 bytes (5)
        Differentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)
            0000 00.. = Differentiated Services Codepoint: Default (0)
            .... ..00 = Explicit Congestion Notification: Not ECN-Capable Transport (0)
        [Total Length: 1799 bytes (reported as 0, presumed to be because of "TCP segmentation offload" (TSO))]
        Identification: 0x2bfb (11259)
        010. .... = Flags: 0x2, Don't fragment
            0... .... = Reserved bit: Not set
            .1.. .... = Don't fragment: Set
            ..0. .... = More fragments: Not set
        ...0 0000 0000 0000 = Fragment Offset: 0
        Time to Live: 128
        Protocol: TCP (6)
        Header Checksum: 0x0000 [validation disabled]
        [Header checksum status: Unverified]
        Source Address: <private-ip>
        Destination Address: 172.66.147.243
        [Stream index: 5]
    Transmission Control Protocol, Src Port: 62580, Dst Port: 443, Seq: 1, Ack: 1, Len: 1759
        Source Port: 62580
        Destination Port: 443
        [Stream index: 6]
        [Stream Packet Number: 4]
        [Conversation completeness: Incomplete, DATA (15)]
            ..0. .... = RST: Absent
            ...0 .... = FIN: Absent
            .... 1... = Data: Present
            .... .1.. = ACK: Present
            .... ..1. = SYN-ACK: Present
            .... ...1 = SYN: Present
            [Completeness Flags: ··DASS]
        [TCP Segment Len: 1759]
        Sequence Number: 1    (relative sequence number)
        Sequence Number (raw): 603691538
        [Next Sequence Number: 1760    (relative sequence number)]
        Acknowledgment Number: 1    (relative ack number)
        Acknowledgment number (raw): 3355459472
        0101 .... = Header Length: 20 bytes (5)
        Flags: 0x018 (PSH, ACK)
            000. .... .... = Reserved: Not set
            ...0 .... .... = Accurate ECN: Not set
            .... 0... .... = Congestion Window Reduced: Not set
            .... .0.. .... = ECN-Echo: Not set
            .... ..0. .... = Urgent: Not set
            .... ...1 .... = Acknowledgment: Set
            .... .... 1... = Push: Set
            .... .... .0.. = Reset: Not set
            .... .... ..0. = Syn: Not set
            .... .... ...0 = Fin: Not set
            [TCP Flags: ·······AP···]
        Window: 1028
        [Calculated window size: 263168]
        [Window size scaling factor: 256]
        Checksum: 0x2088 [unverified]
        [Checksum Status: Unverified]
        Urgent Pointer: 0
        [Timestamps]
            [Time since first frame in this TCP stream: 229.210600 milliseconds]
            [Time since previous frame in this TCP stream: 659.900 microseconds]
        [SEQ/ACK analysis]
            [iRTT: 228.550700 milliseconds]
            [Bytes in flight: 1759]
            [Bytes sent since last PSH flag: 1759]
        [Client Contiguous Streams: 1]
        [Server Contiguous Streams: 1]
        TCP payload (1759 bytes)
    Transport Layer Security
        [Stream index: 0]
        TLSv1.3 Record Layer: Handshake Protocol: Client Hello
            Content Type: Handshake (22)
            Version: TLS 1.0 (0x0301)
            Length: 1754
            Handshake Protocol: Client Hello
                Handshake Type: Client Hello (1)
                Length: 1750
                Version: TLS 1.2 (0x0303)
                    [Expert Info (Chat/Deprecated): This legacy_version field MUST be ignored. The supported_versions extension is present and MUST be used instead.]
                        [This legacy_version field MUST be ignored. The supported_versions extension is present and MUST be used instead.]
                        [Severity level: Chat]
                        [Group: Deprecated]
                Random: a5608c259e18a38e73c56a836ac1650d03a323ed98e25061f4cf2c4908866cca
                Session ID Length: 32
                Session ID: 4e370f778ac67779d5cb9703b35f95d603c885271c5e37181fc9583c5cfe2d78
                Cipher Suites Length: 32
                Cipher Suites (16 suites)
                    Cipher Suite: Reserved (GREASE) (0xfafa)
                    Cipher Suite: TLS_AES_128_GCM_SHA256 (0x1301)
                    Cipher Suite: TLS_AES_256_GCM_SHA384 (0x1302)
                    Cipher Suite: TLS_CHACHA20_POLY1305_SHA256 (0x1303)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 (0xc02b)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (0xc02f)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (0xc02c)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (0xc030)
                    Cipher Suite: TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 (0xcca9)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 (0xcca8)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (0xc013)
                    Cipher Suite: TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA (0xc014)
                    Cipher Suite: TLS_RSA_WITH_AES_128_GCM_SHA256 (0x009c)
                    Cipher Suite: TLS_RSA_WITH_AES_256_GCM_SHA384 (0x009d)
                    Cipher Suite: TLS_RSA_WITH_AES_128_CBC_SHA (0x002f)
                    Cipher Suite: TLS_RSA_WITH_AES_256_CBC_SHA (0x0035)
                Compression Methods Length: 1
                Compression Methods (1 method)
                    Compression Method: null (0)
                Extensions Length: 1645
                Extension: Reserved (GREASE) (len=0)
                    Type: Reserved (GREASE) (56026)
                    Length: 0
                    Data: <MISSING>
                Extension: extended_master_secret (len=0)
                    Type: extended_master_secret (23)
                    Length: 0
                Extension: application_layer_protocol_negotiation (len=14)
                    Type: application_layer_protocol_negotiation (16)
                    Length: 14
                    ALPN Extension Length: 12
                    ALPN Protocol
                        ALPN string length: 2
                        ALPN Next Protocol: h2
                        ALPN string length: 8
                        ALPN Next Protocol: http/1.1
                Extension: renegotiation_info (len=1)
                    Type: renegotiation_info (65281)
                    Length: 1
                    Renegotiation Info extension
                        Renegotiation info extension length: 0
                Extension: signed_certificate_timestamp (len=0)
                    Type: signed_certificate_timestamp (18)
                    Length: 0
                Extension: server_name (len=16) name=example.com
                    Type: server_name (0)
                    Length: 16
                    Server Name Indication extension
                        Server Name list length: 14
                        Server Name Type: host_name (0)
                        Server Name length: 11
                        Server Name: example.com
                Extension: psk_key_exchange_modes (len=2)
                    Type: psk_key_exchange_modes (45)
                    Length: 2
                    PSK Key Exchange Modes Length: 1
                    PSK Key Exchange Mode: PSK with (EC)DHE key establishment (psk_dhe_ke) (1)
                Extension: signature_algorithms (len=24)
                    Type: signature_algorithms (13)
                    Length: 24
                    Signature Hash Algorithms Length: 22
                    Signature Hash Algorithms (11 algorithms)
                        Signature Algorithm: mldsa44 (0x0904)
                            Signature Hash Algorithm Hash: Unknown (9)
                            Signature Hash Algorithm Signature: Unknown (4)
                        Signature Algorithm: mldsa65 (0x0905)
                            Signature Hash Algorithm Hash: Unknown (9)
                            Signature Hash Algorithm Signature: Unknown (5)
                        Signature Algorithm: mldsa87 (0x0906)
                            Signature Hash Algorithm Hash: Unknown (9)
                            Signature Hash Algorithm Signature: Unknown (6)
                        Signature Algorithm: ecdsa_secp256r1_sha256 (0x0403)
                            Signature Hash Algorithm Hash: SHA256 (4)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: rsa_pss_rsae_sha256 (0x0804)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (4)
                        Signature Algorithm: rsa_pkcs1_sha256 (0x0401)
                            Signature Hash Algorithm Hash: SHA256 (4)
                            Signature Hash Algorithm Signature: RSA (1)
                        Signature Algorithm: ecdsa_secp384r1_sha384 (0x0503)
                            Signature Hash Algorithm Hash: SHA384 (5)
                            Signature Hash Algorithm Signature: ECDSA (3)
                        Signature Algorithm: rsa_pss_rsae_sha384 (0x0805)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (5)
                        Signature Algorithm: rsa_pkcs1_sha384 (0x0501)
                            Signature Hash Algorithm Hash: SHA384 (5)
                            Signature Hash Algorithm Signature: RSA (1)
                        Signature Algorithm: rsa_pss_rsae_sha512 (0x0806)
                            Signature Hash Algorithm Hash: Unknown (8)
                            Signature Hash Algorithm Signature: Unknown (6)
                        Signature Algorithm: rsa_pkcs1_sha512 (0x0601)
                            Signature Hash Algorithm Hash: SHA512 (6)
                            Signature Hash Algorithm Signature: RSA (1)
                Extension: compress_certificate (len=3)
                    Type: compress_certificate (27)
                    Length: 3
                    Algorithms Length: 2
                    Algorithm: brotli (2)
                Extension: ec_point_formats (len=2)
                    Type: ec_point_formats (11)
                    Length: 2
                    EC point formats Length: 1
                    Elliptic curves point formats (1)
                        EC point format: uncompressed (0)
                Extension: supported_versions (len=7) TLS 1.3, TLS 1.2
                    Type: supported_versions (43)
                    Length: 7
                    Supported Versions length: 6
                    Supported Version: Reserved (GREASE) (0x5a5a)
                    Supported Version: TLS 1.3 (0x0304)
                    Supported Version: TLS 1.2 (0x0303)
                Extension: session_ticket (len=0)
                    Type: session_ticket (35)
                    Length: 0
                    Session Ticket: <MISSING>
                Extension: status_request (len=5)
                    Type: status_request (5)
                    Length: 5
                    Certificate Status Type: OCSP (1)
                    Responder ID list Length: 0
                    Request Extensions Length: 0
                Extension: encrypted_client_hello (len=218)
                    Type: encrypted_client_hello (65037)
                    Length: 218
                    Client Hello type: Outer Client Hello (0)
                    Cipher Suite: HKDF-SHA256/AES-128-GCM
                        KDF Id: HKDF-SHA256 (1)
                        AEAD Id: AES-128-GCM (1)
                    Config Id: 58
                    Enc length: 32
                    Enc: 84d00f53aa2ae3aef0c39fa230662993a476da1eb7715d7e5a760e05ed8acb1a
                    Payload length: 176
                    Payload […]: cb02c3d600a8f35d86059a55cd53f6f7416f11deae94ad3e08d037f777e8c17927d2d254d3c96006b1d577c0220c0edf1f5928093335d2ecfa1c40985bbcd374ffa86688d4bfc8f489d8e15b317cabbbe303fc2a7bd5fc99b922211c558d6599e9a9c29e08d964cdc2030b87a1990fb3
                Extension: key_share (len=1263) X25519MLKEM768, x25519
                    Type: key_share (51)
                    Length: 1263
                    Key Share extension
                        Client Key Share Length: 1261
                        Key Share Entry: Group: Reserved (GREASE), Key Exchange length: 1
                            Group: Reserved (GREASE) (19018)
                            Key Exchange Length: 1
                            Key Exchange: 00
                        Key Share Entry: Group: X25519MLKEM768, Key Exchange length: 1216
                            Group: X25519MLKEM768 (4588)
                            Key Exchange Length: 1216
                            Key Exchange […]: bea9c7d4632d4e558f25dc9245b14f8a542b4ba2255f330fbb6b801cc12794a472f4f18ba271cab5745d9d25a89d05136a1135af2b6e13a6c688466d3c1c1eb7c741edb8b2f3c8530f41c08a6bac7d02ab81a114b85c4dd1329f1520bd6791b7d52636d9b624e8371c4f6900287
                        Key Share Entry: Group: x25519, Key Exchange length: 32
                            Group: x25519 (29)
                            Key Exchange Length: 32
                            Key Exchange: c752acf3afd8aefb4e532f1ba66fb344a40b4f807a44dabcba3d73617f9a2e66
                Extension: supported_groups (len=12)
                    Type: supported_groups (10)
                    Length: 12
                    Supported Groups List Length: 10
                    Supported Groups (5 groups)
                        Supported Group: Reserved (GREASE) (0x4a4a)
                        Supported Group: X25519MLKEM768 (0x11ec)
                        Supported Group: x25519 (0x001d)
                        Supported Group: secp256r1 (0x0017)
                        Supported Group: secp384r1 (0x0018)
                Extension: application_settings (len=5)
                    Type: application_settings (17613)
                    Length: 5
                    ALPS Extension Length: 3
                    Supported ALPN List
                        Supported ALPN Length: 2
                        Supported ALPN: h2
                Extension: Reserved (GREASE) (len=1)
                    Type: Reserved (GREASE) (14906)
                    Length: 1
                    Data: 00
                [JA4: t13d1516h2_8daaf6152771_806a8c22fdea]
                [JA4_r: t13d1516h2_002f,0035,009c,009d,1301,1302,1303,c013,c014,c02b,c02c,c02f,c030,cca8,cca9_0005,000a,000b,000d,0012,0017,001b,0023,002b,002d,0033,44cd,fe0d,ff01_0904,0905,0906,0403,0804,0401,0503,0805,0501,0806,0601]
                [JA3 Fullstring: 771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,23-16-65281-18-0-45-13-27-11-43-35-5-65037-51-10-17613,4588-29-23-24,0]
                [JA3: f6c9b33d2cc1d091ec4177e7bd702452]

## 3\. 分析 Transport Layer Security

通过第 2 节的  ` Client Hello 完整数据包  ` 一点点来进行分析。

### 3.1 分析Layer以及Handshake

字段  |  requests  |  Firefox  |  Chrome
---|---|---|---
Version  |  TLS 1.0 (0x0301)  |  TLS 1.0 (0x0301)  |  TLS 1.0 (0x0301)
Handshake Version  |  TLS 1.2 (0x0303)  |  TLS 1.2 (0x0303)  |  TLS 1.2 (0x0303)
Random  |  2451d4...(32 字节)  |  baea10...(32 字节)  |  a5608c...(32 字节)
Session ID  |  32 字节  |  32 字节  |  32 字节
Compression  |  null  |  null  |  null
Length  |  1524  |  1885  |  1750

### 3.2 Cipher Suites（加密套件信息）

## |  requests（17）  |  Firefox（16）  |  Chrome（16，含GREASE）
---|---|---|---
1  |  1302 AES256-GCM  |  1301 AES128-GCM  |  GREASE(0xfafa)
2  |  1303 CHACHA20  |  1303 CHACHA20  |  1301 AES128-GCM
3  |  1301 AES128-GCM  |  1302 AES256-GCM  |  1302 AES256-GCM
4  |  c02c ECDHE-ECDSA-A256  |  c02b ECDHE-ECDSA-A128  |  1303 CHACHA20
5  |  c030 ECDHE-RSA-A256  |  c02f ECDHE-RSA-A128  |  c02b ECDHE-ECDSA-A128
6  |  c02b ECDHE-ECDSA-A128  |  cca9 ECDHE-ECDSA-CHACHA  |  c02f ECDHE-RSA-A128
7  |  c02f ECDHE-RSA-A128  |  cca8 ECDHE-RSA-CHACHA  |  c02c ECDHE-ECDSA-A256
8  |  cca9 ECDHE-ECDSA-CHACHA  |  c02c ECDHE-ECDSA-A256  |  c030 ECDHE-RSA-A256
9  |  cca8 ECDHE-RSA-CHACHA  |  c030 ECDHE-RSA-A256  |  cca9 ECDHE-ECDSA-CHACHA
10  |  c024 ECDHE-ECDSA-A256-CBC384  |  c00a ECDHE-ECDSA-A256-CBC  |  cca8 ECDHE-RSA-CHACHA
11  |  c028 ECDHE-RSA-A256-CBC384  |  c013 ECDHE-RSA-A128-CBC  |  c013 ECDHE-RSA-A128-CBC
12  |  c023 ECDHE-ECDSA-A128-CBC256  |  c014 ECDHE-RSA-A256-CBC  |  c014 ECDHE-RSA-A256-CBC
13  |  c027 ECDHE-RSA-A128-CBC256  |  009c RSA-A128-GCM  |  009c RSA-A128-GCM
14  |  009f DHE-RSA-A256-GCM  |  009d RSA-A256-GCM  |  009d RSA-A256-GCM
15  |  009e DHE-RSA-A128-GCM  |  002f RSA-A128-CBC  |  002f RSA-A128-CBC
16  |  006b DHE-RSA-A256-CBC  |  0035 RSA-A256-CBC  |  0035 RSA-A256-CBC
17  |  0067 DHE-RSA-A128-CBC  |  —  |  —

### 3.3 Extensions（扩展插件）

顺序  |  requests（12，固定序）  |  Firefox（17，固定序※）  |  Chrome（18，每次重组）
---|---|---|---
1  |  renegotiation_info(65281)  |  server_name(0)  |  GREASE(56026)
2  |  server_name(0)  |  extended_master_secret(23)  |  extended_master_secret(23)
3  |  ec_point_formats(11)  |  renegotiation_info(65281)  |  ALPN(16)
4  |  supported_groups(10)  |  supported_groups(10)  |  renegotiation_info(65281)
5  |  ALPN(16)  |  ec_point_formats(11)  |  signed_certificate_timestamp(18)
6  |  encrypt_then_mac(22)  |  session_ticket(35)  |  server_name(0)
7  |  extended_master_secret(23)  |  ALPN(16)  |  psk_key_exchange_modes(45)
8  |  post_handshake_auth(49)  |  status_request(5)  |  signature_algorithms(13)
9  |  signature_algorithms(13)  |  delegated_credentials(34)  |  compress_certificate(27)
10  |  supported_versions(43)  |  signed_certificate_timestamp(18)  |  ec_point_formats(11)
11  |  psk_key_exchange_modes(45)  |  key_share(51)  |  supported_versions(43)
12  |  key_share(51)  |  supported_versions(43)  |  session_ticket(35)
13  |  —  |  signature_algorithms(13)  |  status_request(5)
14  |  —  |  psk_key_exchange_modes(45)  |  encrypted_client_hello(65037)
15  |  —  |  record_size_limit(28)  |  key_share(51)
16  |  —  |  compress_certificate(27)  |  supported_groups(10)
17  |  —  |  encrypted_client_hello(65037)  |  application_settings(17613)
18  |  —  |  —  |  GREASE(14906)

> ※ Firefox 的扩展顺序经 2 次独立抓包验证一致（两次 Random 不同、但 JA3 相同——JA3 不排序扩展，故 JA3
> 相同即证明顺序未变）。注意 NSS 本身带有扩展乱序机制（见 5.5 节的  ` enableChXtnPermutation  `
> ），未来版本或开启该 pref 后顺序可能变化，届时以实际抓包为准。Chrome 则是  **每次请求都重排** （所以其 JA3
> 每次都变，需用会排序的 JA4 才稳定）。

### 3.4 Supported Groups

requests（8）  |  Firefox（7）  |  Chrome（5）
---|---|---
X25519MLKEM768  |  X25519MLKEM768  |  GREASE(0x4a4a)
x25519  |  x25519  |  X25519MLKEM768
secp256r1  |  secp256r1  |  x25519
x448  |  secp384r1  |  secp256r1
secp384r1  |  secp521r1  |  secp384r1
secp521r1  |  ffdhe2048  |  —
ffdhe2048  |  ffdhe3072  |  —
ffdhe3072  |  —  |  —

### 3.5 Signature Hash Algorithms

|  requests（26）  |  Firefox（11）  |  Chrome（11）
---|---|---|---
-mldsa  |  44/65/87  |  —  |  含有 44/65/87
ecdsa 256/384/512  |  含有  |  含有  |  256/384（无521）
ed25519 / ed448  |  含有  |  —  |  —
brainpool tls13 ×3  |  含有  |  —  |  —
rsa_pss_pss ×3  |  含有  |  —  |  —
rsa_pss_rsae ×3  |  含有  |  含有  |  含有
rsa_pkcs1 ×3  |  含有  |  含有  |  含有
sha1 (ecdsa/rsa)  |  含有（sha224系列）  |  含有  |  —
DSA sha224/256/384/512  |  含有  |  —  |  —

### 3.6 ALPN / 其他关键扩展取值

扩展  |  requests  |  Firefox  |  Chrome
---|---|---|---
ALPN  |  http/1.1  |  h2, http/1.1  |  h2, http/1.1
ec_point_formats  |  uncompressed +2 种  |  仅 uncompressed  |  仅 uncompressed
supported_versions  |  1.3, 1.2  |  1.3, 1.2  |  GREASE, 1.3, 1.2
psk_key_exchange_modes  |  psk_dhe_ke  |  psk_dhe_ke  |  psk_dhe_ke
encrypt_then_mac  |  包含  |  —  |  —
post_handshake_auth  |  包含  |  —  |  —
session_ticket  |  —  |  包含  |  包含
status_request(OCSP)  |  —  |  包含  |  包含
signed_certificate_timestamp  |  —  |  包含  |  包含
delegated_credentials  |  —  |  包含  |  —
record_size_limit  |  —  |  包含(16385)  |  —
compress_certificate  |  —  |  zlib+brotli+zstd  |  仅 brotli
encrypted_client_hello (ECH)  |  —  |  包含  |  包含
application_settings (ALPS)  |  —  |  —  |  包含
GREASE  |  —  |  —  |  包含

### 3.7 key_share

requests  |  Firefox  |  Chrome
---|---|---
X25519MLKEM768(1216B)  |  X25519MLKEM768(1216B)  |  GREASE(1B)
x25519(32B)  |  x25519(32B)  |  X25519MLKEM768(1216B)
—  |  secp256r1(65B)  |  x25519(32B)

### 3.8 指纹

|  requests  |  Firefox  |  Chrome
---|---|---|---
JA3  |  7291ea5e449f2c7b17582541703e549d  |  6447ab086255d194909d4013b1a89e87  |  f6c9b33d2cc1d091ec4177e7bd702452
JA4  |  t13d1712h1_ab0a1bf427ad_882d495ac381  |  t13d1617h2_86a278354501_3cbfd9057e0d  |  t13d1516h2_8daaf6152771_806a8c22fdea

> **JA3 与 JA4 的关键区别：JA3 保留扩展的原始顺序，JA4 会先把扩展排序再计算。**
>
> 这直接影响到对 Chrome 的识别：Chrome  **每次请求都会重排扩展顺序** （还带随机 GREASE），所以它的  ** JA3
> 每次都变  **；而** JA4 因为排了序，对 Chrome 依然稳定  ** 。反过来，Firefox 扩展顺序固定， JA3 完全相同（见
> 3.3 节注※）。

破绽  |  requests  |  浏览器（Chrome/Firefox）
---|---|---
encrypted_client_hello  |  —  |  有
ALPN  |  ` http/1.1  ` |  ` h2, http/1.1  `
application_settings  |  —  |  Chrome 特有
签名算法  |  26 个，含 mldsa/ed25519/brainpool/DSA/SHA224 一大堆  |  精简 11 个
x448 群  |  有  |  —
独有扩展  |  encrypt_then_mac、post_handshake_auth  |  —

通过github的源码分析，requests 的请求最终是通过 openssl 来握手、发送的（调用链：requests → urllib3 →
Python 标准库 ssl → OpenSSL）。所以上面像
encrypted_client_hello、ALPN(h2)、application_settings 这些，  **
requests（urllib3）默认没有去启用它们  **；再加上套件/扩展/签名算法用的都是 OpenSSL 的出厂默认排列，所以**
ClientHello  ** 数据包一眼就能看出不是浏览器的发包。用  ` curl_cffi  `
这类开源的tls库，可以避免这些问题，如果开源的被检测了，可以看最后一节，直接动手封装专属自己的库。

## 5\. 打造自己的请求库

在前面几个环节分析了requests与浏览器之前的请求差别。而且在第三节分析中，chrome的扩展插件的顺序并不是固定的，所以本次根据firefox来进行封装。

### 5.1 下载firefox源码

firefox源码地址，我使用的是
firefox151的版本，下载链接：https://ftp.mozilla.org/pub/firefox/releases/151.0.4/source/firefox-151.0.4.source.tar.xz

### 5.2 定位源码发包位置

![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MR3Bh7ad1MuHOro71lAFUJ2wSeVicAtibc6JHiaWqD5UicAUZva4gojZm9oy7ZvxZTLd85oNBqoccjSuN9NMRB50JD0EZNb8k9yjR0/640?wx_fmt=png&from=appmsg)
netwerk里是firefox的请求地方
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MSQd7ErXU9xp4A2kt1C37PFJXUlgHk3qYxUnC1Bx8TjtI9AusL9jlAu1j5TxhiavJib8pfqkfJTUwQk3YWH5VkHlXs1A2KUHdodg/640?wx_fmt=png&from=appmsg)
security/nss里是握手相关指纹核心。

### 5.3 指纹

指纹要素  |  文件 : 行  |  关键符号  |  说明
---|---|---|---
**ClientHello 主构造** |  ` security/nss/lib/ssl/ssl3con.c:5505  ` |  ` ssl3_SendClientHello()  ` |  组装 legacy_version / random / session_id / cipher / compression / 扩展
**Cipher suites 顺序** (JA3 密码段)  |  ` security/nss/lib/ssl/sslenum.c:57  ` |  ` SSL_ImplementedCiphers[]  ` |  NSS 全集,发送序 = 数组序;Firefox 实际发子集(prefs 过滤)
↳ 一致性校验表  |  ` ssl3con.c:213  ` |  ` cipherSuites[]  ` |  必须与上表同序(源码 assert)
**扩展列表 + 顺序** (JA4)  |  ` security/nss/lib/ssl/ssl3ext.c:128  ` |  ` clientHelloSendersTLS[]  ` |  ClientHello 扩展发送顺序
↳ 扩展构造入口  |  ` ssl3ext.c:779  ` |  ` ssl_ConstructExtensions()  ` |  遍历 senders 表逐个 append
↳ 扩展  **乱序** 机制  |  ` ssl3ext.c:793  ` /  ` :1159  ` |  ` enableChXtnPermutation  ` /  ` tls_ClientHelloExtensionPermutationSetup()  ` |

**TLS1.2 扩展编码** |  ` security/nss/lib/ssl/ssl3exthandle.c  ` |  ` ssl3_ClientSend*Xtn  ` |  SNI/ALPN/EMS/renego/point_formats/status_request…
**TLS1.3 扩展编码** |  ` security/nss/lib/ssl/tls13exthandle.c  ` |  ` tls13_ClientSend*Xtn  ` |  key_share/supported_versions/PSK/psk_modes/cookie/early_data
**supported_groups** (曲线)  |  ` security/nss/lib/ssl/sslgrp.c  ` |  ` ssl_SendSupportedGroupsXtn  ` |

**key_share 曲线** |  ` security/manager/ssl/nsNSSIOLayer.cpp:1600  ` |
|

**signature_algorithms** |  ` security/nss/lib/ssl/tls13signature.c  ` \+  ` ssl3con.c ssl3_SendSigAlgsXtn  ` |
|  sigalg 列表
**ECH** (encrypted_client_hello)  |  ` security/nss/lib/ssl/tls13ech.c  ` /  ` tls13echv.c  ` |  ` tls13_ClientHandleEchXtn  ` |  ECH 握手
**TLS1.3 握手状态机** |  ` security/nss/lib/ssl/tls13con.c  ` |
|  ServerHello 后的 1.3 流程

### 5.4 Cipher suites

NSS  ` SSL_ImplementedCiphers[]  ` 全集(发送即此序)。  **TLS 1.3 三个恒在最前** :

序  |  Cipher  |  Hex
---|---|---
1  |  TLS_AES_128_GCM_SHA256  |  ` 0x1301  `
2  |  TLS_CHACHA20_POLY1305_SHA256  |  ` 0x1303  `
3  |  TLS_AES_256_GCM_SHA384  |  ` 0x1302  `
4  |  TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256  |  ` 0xc02b  `
5  |  TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256  |  ` 0xc02f  `
6  |  TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305  |  ` 0xcca9  `
7  |  TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305  |  ` 0xcca8  `
8  |  TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384  |  ` 0xc02c  `
9  |  TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384  |  ` 0xc030  `
10  |  TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA  |  ` 0xc00a  `
11  |  TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA  |  ` 0xc009  `
12  |  TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA  |  ` 0xc013  `
13  |  TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA  |  ` 0xc014  `
…  |  (后续 DHE / ECDH / RSA / 3DES / RC4 / NULL 等大量老套件)  |

尾  |  TLS_RSA_WITH_AES_128_GCM_SHA256 / …256_GCM / 128_CBC_SHA / 256_CBC_SHA …  |  ` 0x009c  ` ` 0x009d  ` ` 0x002f  ` ` 0x0035  `

### 5.5  ** 扩展顺序

序  |  扩展  |  序  |  扩展
---|---|---|---
1  |  ` tls13_grease  ` (空 GREASE)  |  12  |  ` key_share  `
2  |  ` server_name  ` (SNI)  |  13  |  ` early_data  `
3  |  ` extended_master_secret  ` |  14  |  ` supported_versions  `
4  |  ` renegotiation_info  ` |  15  |  ` signature_algorithms  `
5  |  ` supported_groups  ` |  16  |  ` cookie  `
6  |  ` ec_point_formats  ` |  17  |  ` psk_key_exchange_modes  `
7  |  ` session_ticket  ` |  18  |  ` post_handshake_auth  `
8  |  ` application_layer_protocol  ` (ALPN)  |  19  |  ` record_size_limit  `
9  |  ` use_srtp  ` |  20  |  ` certificate_compression  `
10  |  ` delegated_credentials  ` |  21  |  ` tls13_grease  ` (1 字节 GREASE)
11  |  ` signed_certificate_timestamp  ` (SCT)  |  22  |  ` pre_shared_key  ` (必须最后)

### 5.6 总结

现在有AI的话，直接让AI阅读源码动手封装。我直接使用的是 Rust +
PyO3封装好NSS和请求顺序、加密套件等相关指纹信息，然后通过python进行调用即可，目前成功绕过akamai的校验，稳定过。

提示词如下：

    /goal 根据firefox的源码阅读请求的握手和发送请求的地方，来进行模拟浏览器发包，使用Rust + PyO3来进行封装给Python调用，Api参考requests的风格来进行调用，在请求时，不断的比对akamai指纹和ja3/4的指纹信息，与浏览器同源，直到可以进行生产使用。

### 本文由  小卢 投稿
