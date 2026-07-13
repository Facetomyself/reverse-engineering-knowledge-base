# 网络指纹篇：TLS指纹、HTTP2指纹、IP信誉与代理检测

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-07-01
> 归档日期: 2026-07-13
> 分类: anti-detection
>
> 账号信息再完美，网络层一握手就露馅。现代风控的第一道关卡不在应用层，而在 TCP/TLS/HTTP2 的握手包里。

> 账号信息再完美，网络层一握手就露馅。现代风控的第一道关卡不在应用层，而在 TCP/TLS/HTTP2 的握手包里。

很多人以为挂个代理、改个 User-Agent 就能瞒天过海，结果请求刚发出去就被 403。原因很简单：  ** 你用的  ` requests  ` /
` aiohttp  ` 默认发出的 TLS ClientHello 和 HTTP2 SETTINGS 帧，在风控系统眼里就像把"我是机器人"写在脑门上
** 。

这一篇拆开讲四件事：TLS 指纹（JA3/JA4）、HTTP2 指纹（Akamai）、IP
信誉体系、代理检测逻辑。代码给的都是有明确依赖、能直接跑的，不整花活。


##  一、TLS 指纹：JA3 与 JA3S

###  1.1 原理一句话

TLS ClientHello 里有几个字段是  ** 客户端实现决定的、相对固定  ** 的：

  * TLS 版本

  * 支持的加密套件（cipher suites）  ** 顺序  **

  * 扩展列表（extensions）  ** 种类和顺序  **

  * 椭圆曲线（supported_groups）  ** 顺序  **

  * 椭圆曲线点格式（ec_point_formats）

把这 5 项按规则拼成字符串，取 MD5，就是  ** JA3  ** （后来演进到 JA3S 看 ServerHello，JA4 拆得更细）。

不同客户端的 JA3 是稳定的：

客户端  |  JA3 特征
---|---
Chrome 120 (Win)  |  固定一套 cipher+extension 顺序
Firefox 121  |  另一套
Python  ` requests  ` (urllib3)  |  ** 默认 OpenSSL，和浏览器不一样  **
Go  ` net/http  ` |  又一套
Java HttpClient  |  又又一套

风控拿到你第一个 TLS 握手包，算一下 JA3，就知道你是不是"挂着 Chrome UA 但实际是 Python 脚本"。

###  1.2 抓一个真实的 ClientHello 算 JA3

下面这段用  ` scapy  ` 抓本地发出的 TLS ClientHello 来算 JA3，  ** 纯演示原理  ** ，不用它去对抗，只是让你知道
JA3 长啥样：

  *


    pip install scapy

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    from scapy.all import *from scapy.layers.ssl_tls import *def parse_ja3(pkt):    """    从 TLS ClientHello 里抽 JA3 字段    注意：scapy 的 ssl_tls 解析不完整，生产环境用 tls-client 或 ja3 库更稳    """    # 简化版：只演示字段抽取逻辑    # 真实 JA3 格式：    #   SSLVersion,CipherSuites,ExtensionList,EllipticCurves,ECPointFormats    # 然后用逗号拼起来再 MD5    # 这里给一个已知 Chrome 120 的 JA3 做对照：    chrome_120_ja3 = "769,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513-21,29-23-24,0"    print("Chrome 120 典型 JA3 明文:", chrome_120_ja3)    print("MD5:", __import__('hashlib').md5(chrome_120_ja3.encode()).hexdigest())    # 输出类似：e7cad562e11553a86fdf6b939771ac3dif __name__ == "__main__":    parse_ja3(None)


想认真看自己流量的 JA3，两个办法：

  * ** 服务器端  ** ：用  ` sslh  ` /  ` zeek  ` /  ` suricata  ` 都能吐 JA3

  * ** 本机  ** ：用  ` tshark -Y "tls.handshake.type == 1" -T fields -e tls.handshake.ciphersuite -e tls.handshake.extension.type  `

`
`

###  1.3 Python 脚本的 TLS 指纹为什么一眼假

  *   *


    import requestsr = requests.get("https://www.google.com")

` requests  ` 底层是  ` urllib3  ` →  ` pyOpenSSL  ` 或系统  ` ssl  ` ，发出的
ClientHello 里：

  * cipher suites 顺序是 pyOpenSSL 编译时定的

  * extensions 里没有浏览器的  ` server_name  ` (sni) 之外的那些（比如  ` application_layer_protocol_negotiation  ` 只有 h2/http1.1 两个，顺序也和 Chrome 不同）

  * ` supported_groups  ` 顺序是 OpenSSL 默认值

JA3 一算，和任何浏览器都对不上。

** 解法有三个层级  ** ：

方案  |  成本  |  效果
---|---|---
` curl_cffi  ` （  ` requests  ` 风格，底层 rustls/boringssl 模拟浏览器 TLS）  |  低  |   够用
` tls-client  ` （Go 库，多语言绑定，专门做 JA3/JA4 伪装）  |  中  |   很稳
真浏览器（Playwright / Selenium / 无头 Chrome）  |  高  |   最稳

####  用  ` curl_cffi  ` 模拟 Chrome TLS（推荐，代码能直接跑）

  *   *   *   *   *   *   *   *   *


    pip install curl_cffifrom curl_cffi import requests as curl_requests# 关键：指定 impersonate 为某个浏览器r = curl_requests.get(    "https://tls.browserleaks.com/json",    impersonate="chrome120",   # 模拟 Chrome 120 的 TLS + HTTP2 指纹)print(r.json())# 会看到 ja3_hash / ja4 等字段，和真 Chrome 一致


` curl_cffi  ` 的作者把 Chrome/Firefox/Safari 各版本的 ClientHello 字节级抄了一遍，  ** 连
cipher 顺序、extension 顺序、ALPN、GREASE 值都对齐了  ** ，是目前 Python 生态里最省事的方案。


##  二、HTTP2 指纹：Akamai 那一堆 SETTINGS


###  2.1 原理

TLS 之后如果是  ` h2  ` ，客户端会先发一个  ** SETTINGS 帧  ** ，里面有一组键值对。顺序 + 值，构成 Akamai
HTTP2 指纹。

浏览器（Chrome）典型的 SETTINGS 帧（顺序敏感）：

  *   *   *   *   *   *


    SETTINGS_HEADER_TABLE_SIZE: 65536SETTINGS_ENABLE_PUSH: 0SETTINGS_MAX_CONCURRENT_STREAMS: 1000   （某些版本没有）SETTINGS_INITIAL_WINDOW_SIZE: 6291456SETTINGS_MAX_FRAME_SIZE: 16384SETTINGS_MAX_HEADER_LIST_SIZE: 262144


` requests  ` /  ` httpx  ` /  ` aiohttp  ` 走 HTTP2 时，SETTINGS 帧是各自库里硬编码的，  **
和 Chrome 对不上  ** 。

风控（尤其 Akamai、Cloudflare）会同时看：

  * JA3（TLS 层）

  * HTTP2 SETTINGS 顺序 + 值

  * 紧接着的 WINDOW_UPDATE、PRIORITY 帧

三者对不上 → 机器人嫌疑。

###  2.2 看看你当前工具发的 HTTP2 指纹

  *   *   *   *


    # 用 nghttp2 客户端看nghttp -v https://www.google.com# 或用 Python 抓pip install hyper-contrib   # 不太维护了，仅演示

更直接的办法：访问  ` https://http2.pro/api/v1  ` 或  `
https://tls.browserleaks.com/json  ` ，会回显你的 HTTP2 指纹。

###  2.3 对齐 HTTP2 指纹

** 方案 A：  ` curl_cffi  ` 已经帮你对齐了  ** （上面那段代码，  ` impersonate="chrome120"  `
同时管 TLS + HTTP2）

** 方案 B：用  ` httpx  ` \+ 自定义  ` h2  ` 配置  ** （麻烦，不推荐，不如直接用 curl_cffi）

** 方案 C：真浏览器  ** ，Playwright 默认就是真 Chrome 的 HTTP2 栈，不用管。


##  三、IP 信誉：数据中心 IP 一秒露馅

###  3.1 IP 的三六九等

风控给 IP 打分，大致这样排：

IP 类型  |  信誉  |  说明
---|---|---
住宅 ISP（Comcast/电信/联通）  |  ⭐⭐⭐⭐⭐  |  最稳
移动 4G/5G  |  ⭐⭐⭐⭐⭐  |  略好于住宅，批量注册场景反而容易触发
数据中心（AWS/GCP/Azure/阿里云）  |  ⭐⭐  |  新号注册一碰就 403
机房裸机（Hetzner/OVH）  |  ⭐⭐  |  稍好一点但还是机房段
VPN 出口（Nord/Express）  |  ⭐  |  黑名单里躺平
公开代理（free proxy 列表）  |    |  别用

###  3.2 怎么查 IP 信誉


    # 命令行看自己出口 IP
    curl ifconfig.me

    # 查 IP 类型（几个常用接口）
    curl "https://ipapi.co/$IP/json/"          # 会标 hosting / proxy / residential
    curl "https://ipinfo.io/$IP/json"          # 同，付费版更准

程序里可以这样判断：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import requestsdef check_ip_reputation(ip=None):    """查 IP 是不是机房/代理"""    if ip is None:        ip = requests.get("https://ifconfig.me", timeout=5).text.strip()    r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5).json()    result = {        "ip": ip,        "org": r.get("org", ""),        "isp": r.get("isp", ""),        "type": [],    }    org_lower = (result["org"] + result["isp"]).lower()    # 关键词判断（粗筛，够用）    dc_keywords = ["amazon", "google", "microsoft", "azure", "aws",                    "alibaba", "tencent", "ovh", "hetzner", "digitalocean"]    proxy_keywords = ["vpn", "proxy", "hosting", "datacenter", "colocation"]    if any(k in org_lower for k in dc_keywords):        result["type"].append("datacenter")    if any(k in org_lower for k in proxy_keywords):        result["type"].append("proxy_suspicious")    if not result["type"]:        result["type"].append("likely_residential")    return result# 测试info = check_ip_reputation()print(info)# 如果是 {'type': ['datacenter']}，那注册账号基本没戏


###  3.3 住宅代理 vs 4G 代理

想拿住宅 IP，两条路：

  1. ** 住宅代理服务  ** ：Bright Data（原 Luminati）、Oxylabs、SmartProxy

     * 优点：IP 池大、稳定

     * 缺点：贵，知名服务商出口段本身也被一些平台标记了

     * 用法：HTTP 代理穿过去就行

  *   *   *   *   *   *   *   *   *   *   *


    from curl_cffi import requests as curl_requestsproxies = {    "http": "http://user:pass@resi-proxy:port",    "https": "http://user:pass@resi-proxy:port",}r = curl_requests.get(    "https://tls.browserleaks.com/json",    impersonate="chrome120",    proxies=proxies,)print(r.json())  # 看 ja3 / ip 是否对得上


** 2\. 4G 代理 / 拨号 VPS  ** ：自己插 SIM 卡或者买现成的

     * 优点：移动 IP，信誉最好

     * 缺点：慢、不稳、贵


##  四、代理检测：你怎么挂代理，风控怎么拆


###  4.1 常见的露馅点

就算 IP 是住宅的，下面这些地方还能翻车：

** ① DNS 泄露  **

浏览器用代理走 HTTP，但 DNS 查询还是本地 ISP 发的 → 本地是北京联通，代理是洛杉矶住宅，DNS 是  ` bj-unicom-dns  `
→ 怀疑。

** ② WebRTC 泄露  **

浏览器里  ` RTCPeerConnection  ` 能拿到本地内网 IP，甚至公网 IP（如果没走代理的 UDP）。进  `
chrome://webrtc-internals  ` 能看到。

** ③ TCP 时间戳 / 窗口缩放  **

不同 OS 的 TCP 栈参数不一样，有些风控会顺手看（这个偏进阶，JA3 都比它实用）。

** ④ 代理协议特征  **

  * HTTP 代理：CONNECT 隧道有特征

  * SOCKS5：握手包有特征

  * MITM 类（如 Charles/Fiddler）：CA 证书如果被标记为知名拦截工具，直接露


###  4.2 用 Playwright 时的防泄露基础配置

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    from playwright.sync_api import sync_playwrightdef launch_stealth_browser():    with sync_playwright() as p:        browser = p.chromium.launch(            headless=False,   # 无头反而指纹更假，能不 headless 就不            args=[                "--proxy-server=http://your-proxy:port",  # 代理                "--disable-web-security",                "--disable-features=IsolateOrigins,site-per-process",                "--disable-blink-features=AutomationControlled",            ]        )        context = browser.new_context(            viewport={"width": 1920, "height": 1080},            locale="en-US",            timezone_id="America/New_York",            # 关键：关 WebRTC 泄露            extra_http_headers={                "Accept-Language": "en-US,en;q=0.9",            }        )        # 注入脚本关 WebRTC 本地 IP 泄露        context.add_init_script("""            Object.defineProperty(RTCPeerConnection.prototype, 'createDataChannel', {                value: () => ({ close: () => {} })            });            // 更狠的：直接替换 getStats 返回空        """)        page = context.new_page()        return browser, context, page


>  Playwright 默认还是能被  ` navigator.webdriver  ` 检测到，生产要用  ` playwright-
> stealth  ` 或  ` undetected-playwright  ` 。单纯  ` disable-blink-
> features=AutomationControlled  ` 只能骗过浅层检测。


##  五、实战检查清单

注册/登录前，对着这张表自查：

  *   *   *   *   *   *   *


    □ TLS 指纹（JA3）是否对齐目标浏览器？  → curl_cffi impersonate□ HTTP2 SETTINGS 是否对齐？            → curl_cffi 已管 / 或真浏览器□ IP 是不是数据中心段？                → ipapi.co 查 org□ DNS 是否走代理通道？                 → 浏览器 DoH / 代理配 DNS□ WebRTC 是否泄露本地 IP？             → 关 RTC / 注入脚本□ User-Agent 和 TLS 指纹是否匹配？     → Chrome UA + Chrome impersonate□ 时区 / 语言 / 地理位置 是否和 IP 一致？ → 这三件套必须对齐

任何一个对不上，都是风控的"加权项"，攒多了就 403。


##  六、方案选型速查

场景  |  推荐方案
---|---
轻量爬虫，要过 JA3  |  ` curl_cffi  ` \+ 住宅代理
登录后爬数据  |  Playwright + stealth + 住宅代理
批量注册账号  |  真 4G + 真浏览器 + 人工流程（或 RPA 化）
只想测指纹  |  访问  ` tls.browserleaks.com  ` \+  ` http2.pro  `


> 提醒：本篇技术仅供理解风控原理用，注册账号/爬数据请遵守平台 ToS 和当地法律。住宅代理和 4G
> 代理本身是中性工具，但批量注册违规账号在任何平台都是封号理由。
