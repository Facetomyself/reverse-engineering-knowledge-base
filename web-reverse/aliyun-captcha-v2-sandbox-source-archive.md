---
schema_version: 2
id: web-reverse-aliyun-captcha-v2-sandbox-source-archive
document_type: archive
original_date: unknown
archived_date: "2026-10-13"
scope:
  targets: [aliyun-captcha]
  client: web
  version: "V2"
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s/FuTVmBa7DOu59FJ2O-NV8w"
    basis: source-report
source_completeness: partial
relations: []
tags: [aliyun-captcha, V2, Node-vm, FeiLin, sg, source-report]
---

# AliyunCaptcha V2 滑块补环境单站分析（来源归档）

## 清洗与完整性说明

原文件没有 H1；标题按已审输入文件名与正文主题补入。导出里有 1 个 1×1 SVG 占位图，没有原图附件。原文中的 Base64 目标网址保持未解码并替换为脱敏标记；本归档不带入目标 host、真实 token、设备指纹、密钥、请求体或运行时样值。所见代码与结果只保留来源报告身份，不代表本轮复现。 来源可定位到 metadata 中的原文链接；链接只按来源材料记录，本轮未访问原站。该 `archive` 只归档 pending 可见内容，`source_completeness: partial` 不替代原文以外的图片、附件或原始 runtime 证据。

<a id="source-body"></a>
## 来源正文

#### 声明

###### 本文章中所有内容仅供学习交流使用，不用于其他任何目的，不提供完整代码，抓包内容、敏感网址、数据接口等均已做脱敏处理，严禁用于商业用途和非法用途，否则由此产生的一切后果均与作者无关！

#### 一、前言

上期讲这个站的 v2 cookie（AST 解混淆那篇）[Python爬虫进阶：acw\_sc\_v2加密AST解混淆全流程](https://mp.weixin.qq.com/s?__biz=MzI1MjE1NjIyMw==&mid=2650862084&idx=1&sn=87089f7f28fee89e20a97132bd38968f&scene=21#wechat_redirect)  ，结尾挖了个坑：**采 5 页左右就会出 v2滑块**。v2滑块是某里验证码之一：`AliyunCaptcha` 主 SDK + `FeiLin` 设备指纹 + `sg` 行为采集，三个混淆包接力。本期就把这个坑填了。

网站（同上期）：

`[目标 URL 已脱敏；原文为 Base64 编码]`

先说清前提：v2 按上期 AST 方案过（直接 vm 跑质询页自身 IIFE 也一样），业务接口带一套五段式 md5 签名头（`X-Timestamp / X-Nonce / X-Sign / X-Sign-Version`，盐在站点自己的 js 里，纯算对拍全等即可），这两样都不在本文展开。本文只回答一个问题——**怎么补动态的feilin算法**。

思路一句话：InitCaptchaV2 的签名是 `HMAC-SHA1(key, params)`，密钥藏在主 SDK bundle 内部的解密链里（`gr/vt/dt` 三段、控制流扁平化）；deviceToken 里嵌着当轮毫秒时间戳，旧 token 重放直接被拒（实测证伪）；轨迹是自定义加密。三个硬点全在混淆包内部，静态解的代价没有上限，而让 SDK 自己跑的成本是固定的——所以把三个 SDK 原封不动丢进 Node vm 沙箱，环境补到位，签名、设备凭证、加密全由 SDK 自产，站点升级 SDK 时零成本跟版。

#### 二、滑块的入口：惩罚页

v2 过了、签名对了，正常翻几页之后，POST 会突然返回 200 + 一段 HTML——**惩罚页**。注意它不是 4xx，就是 200，不按形态分流根本发现不了。

核心是 textarea 里一段 `requestInfo`：

```
{"data":"<原POST体的base64>", "region":"cn", "sceneId":"19xx…lo", "token":"<32位hex>", "traceid":"<30位>", "type":"POST", "userId":"<44b64>", "userUserId":"<44b64>"}
```

三个字段先吃透：

*   `data`
    
     base64 解开就是**原 POST body 本身**，逐字节一致（对拍过），重发时原样带上；
    
*   `token`
    
     就是回传用的 `u_atoken`，**不用算**；
    
*   `traceid`
    
     是本轮滑块的会话锚，后面 InitCaptchaV2 的 `UserCertifyId` 就填它。
    

惩罚页 script 里还带着成功回调的源码，大意是：

```
initCaptcha.success = function (certifyId) {  // REMOVE_KEYS: 清掉质询类 cookie  // 组 url = reGenUrl + "?u_atoken=" + requestInfo.token + "&u_asig=" + certifyId  // 原 body 原样重发 → 业务 JSON}
```

还有一个行为特征要记下：**每个被惩罚的请求独立一轮**——token/traceid 单次有效，滑块没过就再 POST 一次业务接口，拿到的就是全新 token、全新滑块实例。这个特征后面救了大命。

#### 三、滑块链协议全景

抓包把一轮滑块的请求序全部拉出来，秩序非常规矩：

| 
#

 | 

请求

 | 

要点

 |
| --- | --- | --- |
| 

1

 | 

GET AliyunCaptcha.js

 | 

~220KB 主 SDK

 |
| 

2

 | 

POST InitCaptchaV2

 | 

SDK 自签 HMAC-SHA1（下文明细）；响应回 CertifyId/StaticPath/DeviceConfig

 |
| 

3

 | 

GET feilin / sg

 | 

文件名按响应下发，**每轮轮换**（feilin 带 sha：`feilin032.d833…`；sg 带版本：`3.29.0/sg.067.…`）

 |
| 

4

 | 

POST UploadLog

 | 

INIT\_SUCCESS / DYNAMICJS\_LOADED 埋点

 |
| 

5

 | 

POST Log2 / Log3

 | 

FeiLin 设备数据（加密体）

 |
| 

6

 | 

拖滑块

 | 

sg 采集行为

 |
| 

7

 | 

POST VerifyCaptchaV2

 | `CaptchaVerifyParam={sceneId, certifyId, deviceToken, data}` |
| 

8

 | 

响应 VerifyCode

 | 

T001=通过；F001=行为不过；F008=格式不过

 |

InitCaptchaV2 的表单字段值得单独看一眼，后面补环境时每一条都要对上：

```
AaduaneId      = <KEY_ID 常量，bundle 内置，形如 111jdk****201>SceneId        = 19xx…lo                    ← 惩罚页 requestInfo 里带来的UserCertifyId  = traceid                    ← 同上UserId         = <44b64>                    ← 同上UserUserId     = <44b64>                    ← 同上DeviceData     = <192b64>                   ← FeiLin 采集的设备配置密文SignatureNonce = <uuid>Signature      = <HMAC-SHA1, base64>        ← Cr(sortedParams, KEY_SECRET)Timestamp / Format / Version …
```

签名算法面在主 SDK 里能定位到（`Signature=Cr(params, KEY_SECRET)` 一带），但 `KEY_SECRET` 本体要经过那条 `gr/vt/dt` 扁平化解密链才拿得到——到这一步就可以收手了，因为**根本不需要拿**：补环境里 SDK 自己会算。

响应也很有信息量：

```
{"CertifyId":"<== traceid 原样返回>", "Code":"Success", "LimitFlow":false, "StaticPath":"3.29.0/sg.067.0fca1…", "CaptchaType":"SLIDING", "DeviceConfig":"<192b64>"}
```

`StaticPath` 决定接下来拉哪个版本的 sg，`DeviceConfig` 喂给 FeiLin 做设备配置解密——**每轮都变，所以版本和配置都不能缓存**。

两个跨轮稳定的"规律"，是校验沙箱产出是否同构的最好锚点：

*   **deviceToken 结构**
    
    ：base64 解开是 `WEB#<32位指纹哈希>-h-<毫秒时间戳>-<hex>`。指纹哈希跨轮恒定（同设备同值），时间戳每轮变——所以它既能当形状锚，也宣告了"缓存 token"这条路是死的；
    
*   **Log2/Log3 的 Data 首段**
    
    ：跨轮完全一致（`0YBJkdVP…` 打头），只有后段随载荷变。这就是"动态 key 有规律"的那个规律：key 是会话级稳定、按轮换载荷，不用破，拿它对拍即可。
    

#### 四、沙箱骨架

Node 单进程 `vm.createContext`，900 行上下手写环境，**不用 jsdom**——jsdom 太重而且指纹面不受控，宁可手写。

四个核心件：

**1\. XHRShim（灵魂）。** SDK 里所有请求走 `XMLHttpRequest`，我们接到后直接转 Node `https` 出网——签名、加密、参数顺序一个字节都不用手拼：

```
XHRShim.prototype.send = function (body) {  requestLog.push({ url: this._url, method: this._method, body: String(body || '') });const u = newURL(this._url);if (!ALLOW_HOSTS.some(h => u.host === h || u.host.endsWith('.' + h)))    returnrespond(0, '');                       // 白名单外直接断const req = https.request({ hostname: u.hostname, path: u.pathname + u.search,    method: this._method, headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',      Origin: 'https://<站点域>', Referer: 'https://<站点域>/', 'User-Agent': UA, ...this._headers } },    res => { const chunks = []; res.on('data', c => chunks.push(c));             res.on('end', () =>respond(res.statusCode, Buffer.concat(chunks).toString())); });  req.on('error', e =>respond(0, ''));  req.end(payload);};
```

`requestLog` 同时是**结果源**（第五节讲为什么回调不可信）。另配一个自检探针，进程退出前打印关键状态，一眼定位卡在哪层：

```
[PROBE] FEILIN= object | z_um.getToken()= string len=1276[PROBE] slider listeners= mousedown,touchstart[PROBE] reqs= 5 → Init/UploadLog/Log2/Log3/Verify 全齐
```

**2\. script 元素加载器。** SDK 动态插 `<script>` 拉 feilin/sg，我们在 `createElement('script')` 挂钩，按当轮 URL 实时下载，拉回来的代码丢回同一个 vm context 执行。这一步不做白名单限定，SDK 让拉什么拉什么会很危险。

**3\. realm 语义对齐。** 三件套：DOM 元素挂原型链（`HTMLElement → Element → Node → EventTarget`）让 `instanceof` 能过；options 等 object 参数在 realm 内重建；`Function.prototype.toString` 伪装（SDK 会抽查函数原生性）：

```
const orig = Function.prototype.toString;function toString() {  if (map.has(this)) return 'function ' + map.get(this) + '() {\n    [native code]\n}';  return orig.call(this);}Object.defineProperty(Function.prototype, 'toString', { value: toString, configurable: true });
```

#### 五、补环境踩坑实录

**1\. 跨 realm 陷阱。**`initAliyunCaptcha(options)` 的 options 如果在宿主侧 `JSON.parse` 出来再传进去，SDK 校验 `slideStyle` 等 object 参数时 `constructor === Object` 判假——跨 realm 的构造函数不是同一个。报错形态是参数校验三连败（element/button/slideStyle 逐个"不合法"）。解法：

```
vm.runInContext('globalThis.__mkOpt = s => JSON.parse(s)', ctx);const options = sandbox.__mkOpt(JSON.stringify(opts));   // realm 内 parse
```

**2\. 5 字符假 certifyId。** 有一版沙箱忘挂 `sandbox.XMLHttpRequest = XHRShim`，Init 根本没发出去，SDK 内部走了限流 stub 路径——**照样回调 `success(certifyId)`**，但那是 5 位随机串（正常是 30 位）。表象一切正常，重放必然被拒。排查手法就是看 requestLog：说好的 Init 呢？一条都没有。教训：**success 回调 ≠ 请求真发出去了**。

**3\. feilin 静默不导出（最大的坑，值一整节）。** 现象：`eval` 成功、零报错、`window.FEILIN` 永远不出现，主 SDK 等到 30 秒超时才绑滑块。这个坑跟了两三天，定位分四步：

*   **模块级插桩**
    
    ：包一层 webpack 模块加载器，357 个模块每个注入一行日志 → 356 个全部执行，唯一没跑的是"找不到模块"的桩。说明 **bootstrap 整体跑完了**，不是加载问题；
    
*   **导出点设陷阱**
    
    ：对 `window.FEILIN` 挂 `defineProperty` setter，全程零触发——导出语句从来没被执行过。回源码找导出点：在某个门禁函数里，if/else 两个分支都导出，但这个函数在我们环境里**是死代码**；
    
*   **和真浏览器对表**
    
    ：把真浏览器里这个 SDK 的函数调用序列按列位拉出来，和沙箱对比——模块求值顺序完全一致，分叉在"求值全部完成后的第一个业务函数调用"：真浏览器里，指纹采集驱动器启动了，沙箱里没有；
    
*   **根因链**
    
    （四层）：采集器的状态机没启动 → 29 个指纹 getter 没注册进注册表 → 初始化器查注册表拿到 `undefined` → 一个按**字符串长度**计算索引的解码器（`n[r-=9]` 这种）越界返回 undefined → 环境探测函数读到半路就死，且异常被扁平化的 try 静默吞掉。
    

也就是说 feilin 在用"采集到的东西"决定"要不要继续初始化"，环境缺什么它不说。解法就是螺旋补面，每轮跑一遍看新报错/新死点：

*   navigator 撒谎面：plugins（5 个 PDF）、`mediaDevices.enumerateDevices`、webgl `getParameter` 参数表（37445/37446/33901…）、connection、permissions、storage.estimate；
    
*   window 方法批：`resizeTo/scrollTo/structuredClone/requestIdleCallback/createImageBitmap/structuredClone`……按探测报错逐个补；
    
*   DOM 面：iframe 的 `contentWindow/contentDocument`（`readyState` 要 `'complete'`，它轮询这个）、indexedDB 的 `onupgradeneeded` 事件、`DOMTokenList`/`Location` 等类批。
    

**补到位的标志非常清晰**：Log2/Log3 真实发出，`window.FEILIN` 导出，deviceToken 长度 1332 与真浏览器一致。这三条全绿之前，所有滑块问题都别先怀疑轨迹。

**4\. sg 滑块。** slider 元素 `style.left` 没有初值，内部某处对它 `slice` 直接抛错（报错栈只有混淆列位）。补上 `left:'0px' / position:absolute / top` 就过。另外 sg 的滑动进度依赖 mousemove——事件要同时送到 slider、document、window 三层监听器，只派发给元素本层它会收不到。

**5\. 别只盯回调。** Verify 回 F001 时 `success/fail` 都不会触发，Promise 只能干等超时。结果源要放在"Verify 响应本身"上：轮询 requestLog 里 `Action=VerifyCaptchaV2` 的响应抽 `VerifyCode`，回调只是 T001 时的加分通道，两条通道互为备份。

#### 六、轨迹与环境分：行为验证是两场考试

环境全通之后，Verify 回的是 **F001**——注意这不是失败，这是签名、设备凭证全过之后，行为分没过。此时最能说明问题的是 Verify 提交的行为密文 `data` 的长度：

| 
来源

 | 

data 长度

 | 

结果

 |
| --- | --- | --- |
| 

真人手拖（饱满的一次拖动，约 2.5s）

 | **1104** | 

T001

 |
| 

同一真人同一页面的前一次（拖得太急，610ms）

 | 

848

 | 

F008

 |
| 

真人轨迹回放 + 沙箱环境（环境面未对齐时）

 | 

恒 732

 | 

F001

 |
| 

真人轨迹回放（补上 pointer 通道后）

 | 

848~1276

 | 

F001

 |
| 

真人轨迹回放（**环境面对齐后**）

 | **936** | **T001** |

这张表里有三个反直觉的结论，都是拿真浏览器全流程无侵入采集对出来的：

**其一，"行为体累积"是错的。** 我们曾以为真人第 7 次才过是因为行为体随拖动累积（那次 T001 的 data=1808 是其余的 2.4 倍）。后来在沙箱里连拖五轮实测：848→1048→**732**→860→840——第三轮掉回基线。sg 在每轮重臂时会**清空行为缓冲**（它和 FeiLin 之间有一对 `clearEventDataListeners` 自定义事件专门干这个）。所以过验考的是**单次拖动自身的信息量**：拖多急、悬停多久、有没有犹豫停顿，别指望多拖几轮攒厚度。

**其二，判分是"行为质量 × 环境一致性"的合分。** 最有说服力的一组数字：环境面对齐之前，data=1256 照样 F001；对齐之后，data=**936** 反而 T001。行为体大小只是合分里的一项，另一项是 sg 顺手采集的环境信号与你冒充的浏览器是否自洽。

**其三，真人首拖也会挂。** 真浏览器里那次 F008（data=848）就是真人拖的——拖太急连真人都过不了。所以沙箱 F001 不代表"环境还有洞"，先看行为体质量再怀疑环境，别来回横跳。

#### 七、环境面对齐：把"缺什么"从猜变成查表

行为体质量推到超过真人过验线之后，仍然 F001——这说明判分里还有环境一致性这项，而它没法靠手感补。最后这一段的做法是把"sg 到底探测了什么、真浏览器怎么答的"全部从真浏览器的无侵入采集中查表：

给浏览器挂上一套无侵入采集（JS 调用树、DOM 读写、事件监听、HTTP 报文全量记录，外加对"全局缺失、接口存在性"这类环境探测的应答监控），真人正常拖一遍滑块，拿到的是"真浏览器对 sg 每一次环境探测的真实应答"。这次抓出来两张表：

*   **缺席表 ×135**
    
    ：真浏览器 window 上不存在的全局——一半是反自动化武器库（selenium/phantom/webdriver 全家桶的各种历史标记、`$cdc_` 开头的 chromedriver 痕迹、`chrome`、`navigator` 之外的 `webdriver`），另一半是运行时 tell（`process`、`setImmediate`、`global`、`__dirname`、`SharedArrayBuffer`……**每一个都是"你是 Node 不是浏览器"的自白**）；
    
*   **接口表 ×75**
    
    ：真浏览器暴露的构造器清单（73 present + 2 disabled）。
    

沙箱侧一行代码 dump 全局名→typeof，做同表 diff，结果两极：

*   **泄漏 0**
    
    ——vm 新领域天然没有 Node 全局，之前担心的 `process` 泄漏根本不存在；
    
*   **缺 37 个接口**
    
    ——`TextDecoder/TextEncoder/URL/Headers/Request` 这类 vm 新领域默认没有、而 sg 真会用的构造器。
    

补齐原则：能借 Node 真实现的直接借（解码、编码、URL、Headers、Request、File、Blob——这些 sg 可能实际调用），纯探测型的给命名类桩。复测 0 泄漏 0 缺失之后，live 第四拖、data 只有 936（比之前被拒的 1256 还小），**VerifyCode 翻成 T001**。

这一段的方法论价值大于技巧价值：补环境补到深处，"还缺什么"是完全无法靠跑报错得知的——SDK 静默吞掉所有探测分歧。而真浏览器的无侵入采集把每次探测的应答都摆在桌上，补环境从"螺旋试错"变成"查表作业"。

#### 八、端到端

最终分职架构：**Python发包，Node 补环境**，两边 UA 保持同族。Python 遇到惩罚页就把 `requestInfo` 写给沙箱，沙箱实弹跑完滑块链把 `certifyId` 递回来，Python 换票重放：

```
Python: POST queryPage → 惩罚页 ──requestInfo──▶ Node 沙箱Node:   Init → UploadLog → Log2/Log3 → 注入轨迹 → Verify ──certifyId──▶ PythonPython: POST queryPage?u_atoken=…&u_asig=… → success:true
```

两个工程细节：**u\_atoken 重放也会撞 v2 质询**（重放请求和普通业务请求一样可能被质询拦截，解掉 cookie 原样重试即可，别在这里翻车）；滑块证书与惩罚 token 绑定会话，取到后尽快重放，别攒。最终这条沙箱路线 live 实测：**VerifyCode=T001 → 换票重放 → success:true 拿到业务 JSON**，全程无浏览器参与。至此这个站 v2 + v3 全链路补环境+纯算。

#### 九、结果展示

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

####   

###### 本文章未经许可禁止转载，禁止任何修改后二次传播，擅自使用本文讲解的技术而导致的任何意外，作者均不负责，若有侵权，请在公众号联系作者立即删除！

本文转自 <https://mp.weixin.qq.com/s/FuTVmBa7DOu59FJ2O-NV8w>，如有侵权，请联系删除。

## 复用边界

来源中的分析过程、代码片段、样值和成功 / 失败结果均为作者自述，依据统一标记为 `source-report`。本轮只做文字清洗和脱敏；未运行目标代码、未请求目标服务、未复现来源结果，也不把来源结论升级为 `runtime-observation`、`local-parity` 或 `server-accepted`。
