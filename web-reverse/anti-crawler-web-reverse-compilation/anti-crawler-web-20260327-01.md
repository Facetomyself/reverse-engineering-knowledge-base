# Chrome开发者工具指南-Hook篇

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-03-27
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 大家好～ 之前分享了Chrome断点调试的实操。今天带来更高效的进阶技巧——Hook实战。全程基于Chrome开发者工具，无需安装任何插件，话不多说，直接上干货。

大家好～
之前分享了Chrome断点调试的实操。今天带来更高效的进阶技巧——Hook实战。全程基于Chrome开发者工具，无需安装任何插件，话不多说，直接上干货！

##   重要免责声明（必看）

本文所分享的Hook技巧，仅用于合法的  ** 技术研究、学习交流、安全测试  ** ，且必须在  ** 拥有明确授权的测试环境  ** 或  **
个人搭建的模拟环境  ** 中进行。

严禁用于破解商业网站反爬、非法采集数据、侵犯网站权益等违规违法操作。实操前请务必：

  1. 遵守《网络安全法》及相关法律法规

  2. 尊重网站的  ` robots.txt  ` 协议与服务条款

  3. 仅在合法授权的范围内进行研究

任何违规使用导致的法律责任，均由使用者自行承担。

##  一、Hook核心原理：理解“偷梁换柱”的艺术


Hook（钩子）本质是通过JavaScript的  ** 函数重写  **
能力，在网站原有函数执行前插入自定义逻辑。它不是“破解”加密算法，而是“监听”函数的输入输出。

** 通俗比喻  **
：Hook就像在快递配送站安装监控摄像头。你不用拆开快递包裹（加密算法），就能知道“谁寄的、寄给谁、什么时候寄的”（函数参数和返回值）。

** 核心价值  ** ：避开复杂的算法逆向，直击反爬参数的生命周期节点。

##  二、前置准备：Chrome开发者的三板斧


无需额外插件，只需Chrome基础功能：

  1. ** 访问测试环境  ** ：打开Chrome浏览器，访问目标网站（用于学习测试的网站推荐使用JSONPlaceholder公开API测试站）

  2. ** 打开开发者工具  ** ：  ` F12  ` 或右键→检查

  3. ** 熟悉两个核心面板  ** ：

     * ** Console面板  ** ：执行Hook脚本、查看拦截结果

     * ** Sources → Snippets  ** ：保存常用Hook脚本，长期使用

     * ** Sources → Overrides  ** ：永久覆写网站JS文件（高级用法）

** 关键提示  ** ：所有Hook脚本必须在页面JS加载  ** 后  ** 、相关函数调用  ** 前  **
执行。通常在页面加载完成后，在Console中粘贴执行。


##  三、4个实战场景：从基础到进阶


###  场景1：参数签名拦截 - 某电商平台签名生成分析

** 背景  ** ：某电商商品列表接口需携带动态签名  ` _sign  ` ，由  ` generateSignature(params)  `
函数生成。

** Hook目标  ** ：获取签名生成前的原始参数和生成的签名值。

** 实战步骤  ** ：

  1. ** 定位签名函数  ** （多种方法组合）：

     * 方法A：全局搜索  ` _sign  ` 、  ` signature  ` 、  ` generateSign  `

     * 方法B：XHR断点捕获请求，在Call Stack中向上查找

     * 方法C：监控  ` JSON.stringify  ` ，签名函数通常会先序列化参数

  2. ** Hook脚本  ** ：

     *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *     // 保存原函数引用const originalGenerateSignature = window.generateSignature ||                                  window.sign ||                                 window.getSign;
    if (originalGenerateSignature) {  // 重写函数  const hookedFunction = function(...args) {    console.group(' 签名函数被调用');    console.log(' 原始参数:', args);    console.log(' 调用时间:', new Date().toISOString());    console.log(' 调用栈:', new Error().stack.split('\n').slice(1, 6).join('\n'));
        // 执行原函数    const result = originalGenerateSignature.apply(this, args);
        console.log(' 生成的签名:', result);    console.groupEnd();
        // 可选：将结果存储到全局变量，方便后续使用    if (!window._interceptedSignatures) {      window._interceptedSignatures = [];    }    window._interceptedSignatures.push({      params: args,      sign: result,      timestamp: Date.now()    });
        return result;  };
      // 替换原函数  if (window.generateSignature) window.generateSignature = hookedFunction;  if (window.sign) window.sign = hookedFunction;  if (window.getSign) window.getSign = hookedFunction;
      console.log(' Hook安装成功！');}

**
**

     *

     *

     *

     *

     *

     *

     *

     *

     *

     *

  3. ** 高级技巧 - 条件过滤：  **

  *   *   *   *   *   *   *   *


    // 只拦截特定参数的签名生成const conditionalHook = function(params) {  // 只关心包含"product"关键词的签名  if (JSON.stringify(params).includes('product')) {    console.log(' 商品相关签名参数:', params);  }  return originalGenerateSignature.apply(this, arguments);};

###  场景2：时间戳动态化 - 应对  ` t  ` 、  ` _t  ` 参数反爬


** 背景  ** ：多数接口使用  ` t  ` 、  ` timestamp  ` 、  ` _t  ` 等参数防止重放攻击，值通常是13位毫秒时间戳。

** Hook思路  ** ：不直接修改时间戳（容易被检测），而是记录其生成规律。

** Hook脚本  ** ：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // Hook Date.now() 和 performance.now() 两种常见时间戳来源const originalDateNow = Date.now;const originalPerformanceNow = performance.now;
    let timestampCounter = 0;const timestampRecords = [];
    Date.now = function() {  const result = originalDateNow();  timestampCounter++;
      if (timestampCounter % 10 === 0) { // 每10次记录一次    timestampRecords.push({      type: 'Date.now()',      value: result,      offset: result - originalDateNow(),      callCount: timestampCounter    });
        if (timestampRecords.length > 100) {      console.table(timestampRecords.slice(-10));    }  }
      return result;};
    // 监控setTimeout/setInterval中的时间戳使用const originalSetTimeout = window.setTimeout;window.setTimeout = function(fn, delay, ...args) {  if (delay < 1000 && delay > 0) { // 短延时可能是反爬检测    console.log('⏱ setTimeout检测:', { delay, stack: new Error().stack });  }  return originalSetTimeout.call(this, fn, delay, ...args);};

** 数据分析  ** ：运行后查看  ` timestampRecords  ` ，可分析出：

  * 时间戳的更新频率

  * 是否存在固定偏移

  * 是否与其它参数联动


###  场景3：反debugger检测绕过 - 应对无限debugger


** 背景  ** ：部分网站通过  ` debugger  ` 语句或定时器检测开发者工具。

** 反检测Hook：  **

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 1. 禁用无限debuggerconst originalDebugger = window.debugger;window.debugger = function() {  console.log(' debugger调用被拦截');  return null;};
    // 2. Hook Function构造函数，防止动态注入debuggerconst originalFunction = Function;Function = function(...args) {  const source = args[args.length - 1];  if (typeof source === 'string' && source.includes('debugger')) {    console.log(' 检测到动态debugger注入');    args[args.length - 1] = source.replace(/debugger;?/g, '');  }  return originalFunction.apply(this, args);};Function.prototype = originalFunction.prototype;
    // 3. 监控eval中的debuggerconst originalEval = window.eval;window.eval = function(code) {  if (code.includes('debugger')) {    console.log(' eval中的debugger被拦截');    code = code.replace(/debugger;?/g, 'console.log("eval debugger blocked");');  }  return originalEval.call(this, code);};

** 场景4：浏览器指纹伪装 - 应对高级反爬  **

** 背景  ** ：网站通过多种浏览器属性生成唯一指纹。

** 综合Hook方案：  **

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 1. WebDriver属性Object.defineProperty(navigator, 'webdriver', {  get: () => undefined,  configurable: false,  enumerable: false});
    // 2. 插件列表标准化const originalPlugins = navigator.plugins;Object.defineProperty(navigator, 'plugins', {  get: () => originalPlugins,  configurable: false});
    // 3. Languages标准化Object.defineProperty(navigator, 'languages', {  get: () => ['zh-CN', 'zh', 'en-US', 'en'],  configurable: false});
    // 4. 屏幕参数微调（注意边界值）const getParameter = WebGLRenderingContext.prototype.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {  // 重写UNMASKED_VENDOR_WEBGL等指纹参数  if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL    return 'Intel Inc.';  }  if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL    return 'Intel(R) Iris(TM) Graphics 6100';  }  return getParameter.call(this, parameter);};


##  四、常用Hook脚本汇总（直接复制，即拿即用）


结合前面的实战场景，整理了8个高频常用Hook脚本，覆盖参数拦截、反检测、指纹伪装等核心需求，新手无需修改，复制到Console面板即可执行，高效避坑。

###  1\. 通用参数签名拦截（适配多数网站）

适用于拦截sign、token等核心反爬参数，自动记录参数和结果，无需定位具体函数名。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 通用签名拦截，自动适配常见签名函数名const signFunctions = ['generateSign', 'getSign', 'generateSignature', 'sign', 'getSignature'];let hookedCount = 0;signFunctions.forEach(fnName => {  const originalFn = window[fnName];  if (originalFn && typeof originalFn === 'function') {    window[fnName] = function(...args) {      console.group(` 签名函数 [${fnName}] 被调用`);      console.log(' 原始参数:', args);      const result = originalFn.apply(this, args);      console.log(' 生成结果:', result);      console.groupEnd();
          // 存储所有记录，方便后续分析      if (!window._signLogs) window._signLogs = [];      window._signLogs.push({        fnName: fnName,        params: args,        result: result,        time: new Date().toLocaleTimeString()      });
          return result;    };    hookedCount++;  }});console.log(` 成功Hook ${hookedCount} 个签名函数，可通过 window._signLogs 查看所有记录`);


###  2\. 时间戳参数监听（适配t、timestamp、_t）

自动监听所有生成时间戳的常见方法，记录时间戳规律，无需手动查找函数。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 监听时间戳生成，覆盖常见时间戳来源const originalDateNow = Date.now;const originalNewDate = Date;// Hook Date.now()Date.now = function() {  const timestamp = originalDateNow.call(this);  console.log('⏱ Date.now() 生成时间戳:', timestamp);  return timestamp;};// Hook new Date() 生成时间戳window.Date = function(...args) {  const date = new originalNewDate(...args);  // 监听getTime()调用（多数网站通过此方法获取时间戳）  const originalGetTime = date.getTime;  date.getTime = function() {    const timestamp = originalGetTime.call(this);    console.log('⏱ new Date().getTime() 生成时间戳:', timestamp);    return timestamp;  };  return date;};console.log('⌚ 时间戳监听已开启，所有时间戳生成会自动打印');


###  3\. 无限debugger一键绕过（通用版）

适配所有网站的debugger检测，无需区分反爬方式，一键拦截所有debugger调用。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 通用debugger拦截，覆盖直接调用、动态注入、定时器注入(function() {  // 拦截直接调用的debugger  const originalDebugger = window.debugger;  window.debugger = function() {    console.log(' 直接debugger调用被拦截');  };  // 拦截Function构造函数注入的debugger  const originalFunction = Function;  Function = function(...args) {    const source = args[args.length - 1];    if (typeof source === 'string' && source.includes('debugger')) {      console.log(' 检测到动态注入debugger，已拦截');      args[args.length - 1] = source.replace(/debugger;?/g, 'console.log("debugger blocked");');    }    return originalFunction.apply(this, args);  };  Function.prototype = originalFunction.prototype;  // 拦截eval注入的debugger  const originalEval = window.eval;  window.eval = function(code) {    if (code.includes('debugger')) {      console.log(' eval注入debugger被拦截');      code = code.replace(/debugger;?/g, 'console.log("debugger blocked");');    }    return originalEval.call(this, code);  };  console.log(' 所有debugger检测已绕过');})();


###  4\. 浏览器指纹全量伪装（高级反爬适配）

模拟真实浏览器指纹，避开WebDriver、插件、屏幕参数等多维度检测，适配自动化工具。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 浏览器指纹全量伪装（一键生效，无需修改）(function() {  // 1. 伪装WebDriver（自动化工具核心检测点）  Object.defineProperty(navigator, 'webdriver', {    get: () => undefined,    configurable: false,    enumerable: false  });  // 2. 伪装浏览器语言和地区  Object.defineProperty(navigator, 'languages', {    get: () => ['zh-CN', 'zh', 'en-US', 'en'],    configurable: false  });  // 3. 伪装插件列表（模拟普通用户常用插件）  const originalPlugins = navigator.plugins;  Object.defineProperty(navigator, 'plugins', {    get: () => originalPlugins,    configurable: false  });  // 4. 伪装WebGL指纹（避免唯一指纹检测）  const originalGetParameter = WebGLRenderingContext.prototype.getParameter;  WebGLRenderingContext.prototype.getParameter = function(parameter) {    if (parameter === 37445) return 'Intel Inc.'; // 显卡厂商    if (parameter === 37446) return 'Intel(R) Iris(TM) Graphics 6100'; // 显卡型号    return originalGetParameter.call(this, parameter);  };  // 5. 伪装屏幕参数（避免异常屏幕尺寸检测）  const originalScreen = window.screen;  window.screen = {    ...originalScreen,    width: 1920,    height: 1080,    availWidth: 1920,    availHeight: 1040  };  console.log(' 浏览器指纹伪装完成，可正常进行调试');})();


###  5\. Fetch/XMLHttpRequest请求拦截（全量监听）

无需定位具体接口，一键监听所有网络请求，捕获请求头、参数和响应，适合快速排查反爬参数。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 监听Fetch请求（现代网站常用）const originalFetch = window.fetch;window.fetch = async function(url, options) {  console.group(` Fetch请求拦截: ${url}`);  console.log(' 请求地址:', url);  console.log(' 请求参数:', options);  console.log(' 请求头:', options?.headers);
      try {    const response = await originalFetch.apply(this, arguments);    // 克隆响应，避免影响原请求    const clonedResponse = response.clone();    const responseData = await clonedResponse.json().catch(() => clonedResponse.text());    console.log(' 响应数据:', responseData);    console.groupEnd();    return response;  } catch (error) {    console.error(' 请求失败:', error);    console.groupEnd();    throw error;  }};// 监听XMLHttpRequest请求（传统网站常用）const originalXhrOpen = XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open = function(method, url) {  console.group(` XHR请求拦截: ${method} ${url}`);  console.log(' 请求方法:', method);  console.log(' 请求地址:', url);
      // 监听发送请求  const originalSend = this.send;  this.send = function(body) {    console.log(' 请求体:', body ? JSON.parse(body) : body);    originalSend.call(this, body);  };
      // 监听响应  this.addEventListener('load', () => {    try {      const responseData = JSON.parse(this.responseText);      console.log(' 响应数据:', responseData);    } catch (e) {      console.log(' 响应数据:', this.responseText);    }    console.groupEnd();  });
      originalXhrOpen.call(this, method, url);};console.log(' 所有网络请求监听已开启，请求会自动打印详情');


###  6\. Cookie参数拦截（监听反爬Cookie）

自动监听Cookie的新增、修改，捕获反爬相关Cookie（如token、sessionId），无需手动查找。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 监听Cookie变化，捕获反爬相关Cookieconst originalDocumentCookie = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie');Object.defineProperty(Document.prototype, 'cookie', {  get: function() {    return originalDocumentCookie.get.call(this);  },  set: function(cookie) {    // 过滤反爬相关Cookie（可根据需求添加关键词）    const antiCrawlKeys = ['token', 'session', 'cookieId', 'auth', 'uid'];    const cookieArr = cookie.split(';').map(item => item.trim());
        cookieArr.forEach(item => {      const [key, value] = item.split('=').map(part => part.trim());      if (antiCrawlKeys.some(antiKey => key.toLowerCase().includes(antiKey))) {        console.log(` 反爬Cookie捕获: [${key}] = ${value}`);
            // 存储Cookie记录        if (!window._cookieLogs) window._cookieLogs = [];        window._cookieLogs.push({          key: key,          value: value,          time: new Date().toLocaleTimeString(),          fullCookie: cookie        });      }    });
        return originalDocumentCookie.set.call(this, cookie);  },  configurable: true});console.log(' Cookie监听已开启，反爬相关Cookie会自动打印');

###  7\. 本地存储（localStorage/sessionStorage）监听

监听本地存储的新增、修改，捕获网站存储的反爬标识（如token、验证信息）。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 监听localStorageconst originalSetItem = localStorage.setItem;localStorage.setItem = function(key, value) {  // 过滤反爬相关存储键名  const antiCrawlKeys = ['token', 'auth', 'userInfo', 'sign'];  if (antiCrawlKeys.some(antiKey => key.toLowerCase().includes(antiKey))) {    console.log(` localStorage捕获: [${key}] = ${value}`);
        if (!window._localStorageLogs) window._localStorageLogs = [];    window._localStorageLogs.push({ key, value, time: new Date().toLocaleTimeString() });  }  return originalSetItem.call(this, key, value);};// 监听sessionStorageconst originalSessionSetItem = sessionStorage.setItem;sessionStorage.setItem = function(key, value) {  const antiCrawlKeys = ['token', 'auth', 'tempSign'];  if (antiCrawlKeys.some(antiKey => key.toLowerCase().includes(antiKey))) {    console.log(` sessionStorage捕获: [${key}] = ${value}`);  }  return originalSessionSetItem.call(this, key, value);};console.log(' 本地存储监听已开启');


###  8\. 通用函数拦截（适配未知函数名）

无需知道具体函数名，自动拦截所有可能的反爬相关函数，适合新手快速排查。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 通用函数拦截，自动匹配反爬相关函数(function() {  const antiCrawlKeywords = ['sign', 'token', 'auth', 'encrypt', 'crypto', 'debugger'];
      // 遍历window对象，拦截包含反爬关键词的函数  Object.keys(window).forEach(key => {    const value = window[key];    if (typeof value === 'function' && antiCrawlKeywords.some(keyword => key.toLowerCase().includes(keyword))) {      const originalFn = value;      window[key] = function(...args) {        console.group(` 反爬相关函数 [${key}] 被调用`);        console.log(' 函数参数:', args);        const result = originalFn.apply(this, args);        console.log(' 函数返回值:', result);        console.groupEnd();        return result;      };      console.log(` 已自动Hook反爬函数: ${key}`);    }  });})();


####  脚本使用说明

  * 所有脚本均为通用版，复制后直接粘贴到Chrome开发者工具「Console」面板，回车即可执行；

  * 无需修改任何代码，适配绝大多数网站，新手可直接使用；

  * 脚本仅用于监听，不篡改原有逻辑，不会触发网站反爬检测；

  * 可通过脚本中定义的全局变量（如window._signLogs、window._cookieLogs）查看拦截记录。


##  五、新手避坑指南（重点提醒）


  * Hook脚本仅作用于当前页面，刷新页面后会失效，需重新执行；长期使用可保存到Sources → Snippets中。

  * 不要随意篡改函数返回值（如把sign改成随机字符串），容易触发网站反爬机制，导致IP被封、账号受限。

  * 调试完成后，关闭开发者工具或刷新页面，即可恢复网站原有函数逻辑，避免影响后续正常访问。

  * 再次强调：所有操作仅用于合法学习、技术研究，严禁用于商业网站的违规爬取！


##  码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！
