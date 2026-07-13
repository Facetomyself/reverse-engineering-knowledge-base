# Chrome开发者工具指南-反Hook检测与对抗篇

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-03-30
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 在上一期Hook实操指南中，我们掌握了使用Hook来帮我们快速的分析网站。本期我们进入更深层的攻防领域：当网站开始 检测Hook行为本身 时，我们如何识别这些检测，并进行安全、合规的对抗性研究。

在上一期Hook实操指南中，我们掌握了使用Hook来帮我们快速的分析网站。本期我们进入更深层的攻防领域：当网站开始  ** 检测Hook行为本身  **
时，我们如何识别这些检测，并进行安全、合规的对抗性研究。

本文将继续严格遵循  ** 仅用于授权测试、安全研究与学习  **
的前提，所有示例均在可控的测试环境（如JSONPlaceholder、本地搭建的Demo）中进行。请务必遵守《网络安全法》及测试目标的授权协议。

## 一、 为什么网站要检测Hook？理解攻防升级

当普通反爬参数（如sign、token）被轻易Hook获取后，网站防御会升级到  ** 第二层  **
：检测运行时环境是否被修改过，就比如某宝，加密参数中就会有检查代码是否被修改。

** 核心检测目标  ** ：

  1. ** 环境真实性  ** ：确认前端代码是否在原生浏览器中执行，而非被自动化工具（Selenium）或调试脚本篡改。

  2. ** 代码完整性  ** ：验证关键函数（如加密函数、环境检测函数）是否被重写（即被Hook）。

  3. ** 行为一致性  ** ：监控API调用时序、函数执行痕迹是否出现异常模式。


###  ** 二、 4大反Hook检测核心场景与对抗策略（代码思路详解）  **

###  **
**

####  ** 场景1：函数完整性校验  **

** 检测原理  ** ：

网站会保存关键函数的“原始指纹”并与运行时对比，例如通过  ` Function.prototype.toString()  `
获取函数源码字符串进行比对。

** 对抗策略：隐形Hook - 不改变“指纹”  **

核心思路：确保Hook后，函数的“外观”（如  ` toString  ` 的结果、  ` name  ` 、  ` length  `
属性）与原始函数完全一致，从而通过校验。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 策略A：使用Proxy进行隐式Hook，这是应对`toString`检测的最优解const originalGenerateSign = window.generateSign;
    Object.defineProperty(window, 'generateSign', {  configurable: true,  enumerable: true,  get: function() {    // 【设计思路】我们不在`window`上直接覆盖函数，而是定义一个getter。    // 当网站代码读取`window.generateSign`时，才动态返回一个Proxy代理。    // 这本身就增加了一层间接性，使得简单的引用对比(`window.generateSign === 原始引用`)失效。    return new Proxy(originalGenerateSign, {      apply: function(target, thisArg, argumentsList) {        // 【核心Hook逻辑】在这里插入我们的监听代码。所有调用都会经过此`apply`陷阱。        console.log('generateSign被调用，参数:', argumentsList);        const result = Reflect.apply(target, thisArg, argumentsList);        console.log('生成结果:', result);        return result;      },      // 【关键防御点】处理属性访问，确保`toString`等检测点返回原始值      get(target, prop) {        if (prop === 'toString') {          // 当网站调用`func.toString()`检测时，我们返回原始函数的字符串。          // 这是对抗“代码比对”检测的核心。          return function() {            return originalGenerateSign.toString();          };        }        // 对于`name`、`length`等属性，也直接转发给原始函数对象        return Reflect.get(target, prop);      }    });  },  set: function(newValue) {    // 防止其他代码（或网站的自我修复逻辑）覆盖我们的Hook    return false;  }});// 【应用场景】此方法适用于防御**主动的代码完整性检查**。当网站怀疑关键函数被篡改，并执行`func.toString()`与预留的源码进行字符串比对时，此策略可完美绕过。它保持了“指纹”不变，但行为已被我们监听。

策略B：底层劫持 - 修改Function原型方法

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 【设计思路】这是一种更激进、更全局化的方案。我们不Hook特定函数，而是Hook所有函数调用的“必经之路”：`Function.prototype.apply` 和 `call` 方法。// 在此处进行过滤，只对我们关心的函数调用进行监听。const originalApply = Function.prototype.apply;
    Function.prototype.apply = function(thisArg, argsArray) {  // 通过`this`判断当前正在调用哪个函数  if (this === window.generateSign || this.name === ‘generateSign’) {    // 【应用场景】此方法适用于防御那些不依赖`toString`，但可能监控函数**执行流程**的检测。    // 优点：对函数对象本身没有任何修改，`toString`检测100%通过。    // 缺点：影响范围是全局的，需要精确过滤，否则可能影响页面其他正常逻辑，并可能被检测`Function.prototype.apply`本身是否被修改。    console.log(‘generateSign.apply被调用‘, { args: argsArray });    const result = originalApply.call(this, thisArg, argsArray);    console.log(‘结果:‘, result);    return result;  }  // 其他函数正常执行  return originalApply.call(this, thisArg, argsArray);};

####  ** 场景2：环境属性一致性检测  **

** 检测原理  ** ：检查多个环境属性（如  ` userAgent  ` 、  ` plugins  ` 、屏幕尺寸）之间是否合乎逻辑。

** 对抗策略：环境同步与合理化  **

核心思路：伪造环境属性时，必须确保  ** 整个环境套件  ** 的逻辑自洽，而不是单独修改某一个值。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 【设计思路】定义一个完整、自洽的虚假环境配置文件，确保所有属性值来自同一“剧本”。const fakeProfile = {  userAgent: ‘Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36…‘,  platform: ‘Win32‘,  hardwareConcurrency: 8,};// 1. 修改`userAgent`Object.defineProperty(navigator, ‘userAgent‘, {  get: () => fakeProfile.userAgent,  configurable: false // 【关键】设置为不可配置，防止网站后续用`Object.getOwnPropertyDescriptor`检测描述符是否被篡改});// 2. **同步**修改相关的屏幕属性Object.defineProperty(screen, ‘width‘, {   get: () => 1920, // 与Windows 10+Chrome的常见分辨率匹配  configurable: false });Object.defineProperty(screen, ‘availWidth‘, {   get: () => 1920 - 20, // 留出任务栏空间，使`availWidth < width`，符合真实情况  configurable: false });// 【应用场景】此策略用于对抗**环境指纹碰撞检测**。当网站发现你的`userAgent`声称是Windows Chrome，但`plugins`为空、或屏幕可用大小异常时，就会触发警报。因此，我们必须提供一套逻辑一致的、完整的虚拟环境数据。

####  ** 场景3：执行时序与性能分析  **

** 检测原理  ** ：监控函数执行耗时，被Hook的函数因增加了额外逻辑，执行时间通常会长于原生函数。

** 对抗策略：时序伪装与性能补偿  **

核心思路：先测量原始函数的执行耗时基准，然后在Hook函数中，通过“空转”或“延迟”将总耗时补偿到基准水平。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const originalEncrypt = window.encryptData;let performanceBaseline = 0.1; // 单位：毫秒
    // 【设计思路】首先，我们需要一个“基准”。在纯净环境下多次执行原函数，统计其耗时中位数。function measureBaseline() {  const samples = [];  for (let i = 0; i < 100; i++) {    const start = performance.now();    originalEncrypt(‘test_data‘);    samples.push(performance.now() - start);  }  samples.sort();  performanceBaseline = samples[Math.floor(samples.length / 2)]; // 取中位数，排除极端值}measureBaseline(); // 在Hook前调用
    // 带性能补偿的Hookwindow.encryptData = function(…args) {  const startTime = performance.now();  // … 这里执行我们的监听代码（应尽可能高效）…  const result = originalEncrypt.apply(this, args);  const actualTime = performance.now() - startTime;
      // 【核心对抗逻辑】性能补偿  if (actualTime < performanceBaseline) {    const delayNeeded = performanceBaseline - actualTime;    // 通过一个空循环，同步地“忙等”一段时间，将总耗时拉高到基准水平。    const waitUntil = performance.now() + delayNeeded;    while (performance.now() < waitUntil) { /* 空循环 */ }  }  return result;};// 【应用场景】此策略专门用于对抗**基于性能分析的检测**。当网站通过`performance.now()`前后差值判断`encryptData`函数的执行时间是否在合理范围内时，我们的补偿机制可以使其耗时曲线与正常情况吻合，避免因执行“过快”（无Hook）或“过慢”（低效Hook）而暴露。

####  ** 场景4：堆栈追踪与调用链分析  **

** 检测原理  ** ：分析  ` Error().stack  ` ，检查调用栈中是否包含可疑函数名（如  ` Proxy  ` 、  `
console.log  ` ）。

** 对抗策略：栈清洗与调用链伪装  **

核心思路：将我们的监听代码从主调用链中剥离，或清理堆栈字符串中的敏感信息。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 方法2：通过异步任务剥离调用栈function createCleanCall(fn, …args) {  return new Promise((resolve) => {    // 【设计思路】利用`setTimeout`（或`setImmediate`、`postMessage`）的异步特性，创建一个全新的调用栈。    // 当回调执行时，其调用栈起点是“事件循环（Event Loop）”，而非我们注入的Hook代码。    setTimeout(() => {      const result = fn(…args);      // 此时，在这里打印`new Error().stack`，将看不到外层Hook函数的痕迹。      resolve(result);    }, 0);  });}// 使用方式window.encryptData = async function(…args) {  // 将主要的日志记录也放在异步任务中，确保它不出现在加密函数的直接调用栈里。  setTimeout(() => console.log(‘[安全日志] 调用发生‘), 0);  // 通过`createCleanCall`调用原函数，切断调用链关联  return await createCleanCall(originalEncrypt, …args);};// 【应用场景】此策略用于对抗**调用栈分析检测**。当网站在加密函数内部捕获堆栈，并发现堆栈顶层是`Proxy.apply`或包含`@user_script`（Chrome扩展脚本标记）时，即可判定被Hook。通过异步跳板，我们将堆栈“清洗”干净，使其看起来像是直接从事件循环发起的正常调用。

###  ** 总结：代码设计原则  **

通过以上详解，可以看出反Hook代码的设计始终围绕几个核心原则：

  1. ** 保持透明  ** ：尽可能不改变被Hook对象的原始属性（  ` toString  ` ，  ` name  ` ，  ` length  ` ）。

  2. ** 逻辑自洽  ** ：伪造环境或行为时，确保整个逻辑是完整且合理的，避免特征矛盾。

  3. ** 模仿正常  ** ：在行为（如执行时序）和痕迹（如调用栈）上，无限接近未被干扰时的状态。

  4. ** 分层防御  ** ：针对不同粒度的检测（代码、环境、行为、痕迹），使用不同的对抗策略，组合使用效果最佳。


**
**

##  三、 综合实战：构建一个“隐形”的Hook框架


1\. 框架顶层设计：状态管理与沙盒化

  *   *   *   *   *   *   *


    class StealthHook {  constructor() {    this.originalReferences = new Map(); // 核心：备份所有原始函数    this.performanceBaselines = new Map(); // 核心：存储性能基准数据    this.activeHooks = new Set();         // 核心：跟踪当前生效的Hook  }}

** 设计意图  ** ：将Hook行为“沙盒化”。所有由框架产生的修改都被记录在实例内部，而不是污染全局空间。这带来了两个核心优势：

  1. ** 可逆性  ** ：通过  ` cleanup()  ` 方法，可以一键将所有被Hook的函数恢复到原始状态，确保测试环境干净，避免对网站后续功能或后续测试产生不可预知的影响。

  2. ** 可管理性  ** ：清晰知道当前Hook了哪些函数，避免自我冲突或重复Hook


####  ** 2\. 核心方法  ` hookFunction  ` ：Proxy驱动的多层防御  **

这是框架的“心脏”，它整合了多个隐形策略。

** 步骤1：状态检查与原始引用保存  **

  *   *   *


    if (this.activeHooks.has(`${target}.${funcName}`)) { ... }const original = target[funcName];this.originalReferences.set(funcName, original);

** 设计意图  ** ：确保操作的幂等性和安全性。防止对同一函数多次Hook造成调用栈混乱或内存泄漏。  ** 保存原始引用是任何Hook操作的“生命线”
** ，是后续恢复和代理调用的基础。

** 步骤2：性能基线测量  **

  *   *   *   *   *   *


    measurePerformanceBaseline(funcName, fn) {  // ...多次执行原函数...  samples.sort();  const median = samples[Math.floor(samples.length / 2)];  this.performanceBaselines.set(funcName, median);}

** 设计意图  ** ：主动量化目标函数的“正常”执行时间。  ** 取中位数而非平均值  **
，是为了排除垃圾回收、系统调度等偶然因素造成的极端值干扰，得到一个更稳定、更具代表性的性能标尺。这是进行精准“性能补偿”的前提，对抗  ** 时序检测
** 的关键准备工作。

** 步骤3：创建Proxy代理（隐形核心）  **

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const proxy = new Proxy(original, {  apply: (targetFn, thisArg, argsList) => {    const startTime = performance.now();    const result = Reflect.apply(targetFn, thisArg, argsList);    // 异步执行回调日志    Promise.resolve().then(() => { callback(original, argsList, result); });    // 性能补偿逻辑    this.compensateDelay(performanceBaseline - (performance.now() - startTime));    return result;  },  get(target, property) {    if (property === 'toString') { ... } // 返回原始toString    // ... 处理`name`, `length`, `prototype` ...    return Reflect.get(target, property);  }});

apply陷阱的设计：

同步调用，异步记录  ：使用 Reflect.apply同步调用原函数，保证网站业务逻辑立即得到结果。而将我们的研究回调callback包装在
Promise.resolve().then()中异步执行。这有两个巨大好处：(1) 不阻塞主线程，不影响原始执行时序；(2)
我们的日志代码不会出现在原函数的调用栈（Call Stack） 中，有效对抗了堆栈溯源检测。

即时性能补偿  ：在获取结果后，立即计算实际耗时，并调用 compensateDelay进行补偿，使总耗时贴近基线。这整个流程是同步的，对调用方透明。

get陷阱的设计：

这是对抗toString检测的灵魂所在。当检测代码访问 func.toString属性时，我们返回一个返回原始字符串的函数。这确保了
func.toString()的结果与原始代码一字不差。对 name、length等属性的转发，则保证了函数“身份信息”的完全一致。

步骤4：属性部署与反检测加固

  *   *


    Object.defineProperty(target, funcName, { value: proxy, ... });this.installAntiDetection(funcName, original, proxy);

** 设计意图  ** ：  ` Object.defineProperty  ` 提供了比直接赋值更精细的控制。随后调用的  `
installAntiDetection  ` 是一个深度防御点，它特别加固了针对  ` Function.prototype.toString  `
的检测：即使检测代码直接访问  ` Function.prototype.toString.call(func)  ` ，我们也能确保返回原始字符串。

####  ** 3\. 辅助方法详解：细节决定成败  **

  * **` compensateDelay(delayMs)  ` 方法  **

  *   *   *   *   *   *   *   *   *   *


    if (delayMs > 10) {  // 使用 MessageChannel 模拟延迟  const channel = new MessageChannel();  channel.port1.postMessage('');  channel.port2.onmessage = () => {};} else {  // 短延迟用微任务空循环  let end = performance.now() + delayMs;  while (performance.now() < end) { Promise.resolve().then(() => {}); }}

** 设计意图  ** ：实现延迟，但不能用容易被监测的  ` setTimeout  ` 。这里提供了两种策略：

    1. ** 长延迟用  ` MessageChannel  ` ** ：这是一个优先级较高的宏任务，比  ` setTimeout  ` 更隐蔽，常用于模拟异步延迟而不易被针对性地检测。

    2. ** 短延迟用微任务空循环  ** ：对于几毫秒的补偿，通过快速产生和消耗微任务来“忙等”，精度更高。这种方法是  ** 高性能代码中常见的技巧  ** ，将其用于补偿，能使性能特征更接近原生密集计算。  **`
` **


**` getTestArguments(funcName)  ` 方法  ** **
**

** 设计意图  ** ：自动化地根据函数名猜测测试参数。这是一个  ** 用户体验优化和安全性设计  **
。在测量性能基线时，使用合理（而非随机或空）的参数进行调用，可以确保测量出的是函数在“典型工作状态”下的性能，使基线数据更有参考价值。同时，避免了因传入非法参数导致函数抛出异常，干扰基线测量。


将上述策略组合，创建一个用于研究的最小化隐形Hook框架


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    /** * StealthHook - 隐形Hook框架（仅用于授权安全研究） */class StealthHook {  constructor() {    this.originalReferences = new Map();    this.performanceBaselines = new Map();    this.activeHooks = new Set();  }
      /**   * 隐形Hook函数   * @param {object} target - 目标对象（如window）   * @param {string} funcName - 函数名   * @param {function} callback - 回调函数，接收(originalFn, args, result)   */  hookFunction(target, funcName, callback) {    if (this.activeHooks.has(`${target}.${funcName}`)) {      console.warn(`函数 ${funcName} 已被Hook`);      return false;    }
        const original = target[funcName];    if (typeof original !== 'function') {      console.error(`${funcName} 不是函数`);      return false;    }
        // 保存原始引用    this.originalReferences.set(funcName, original);
        // 测量性能基准    this.measurePerformanceBaseline(funcName, original);
        // 创建代理函数    const proxy = new Proxy(original, {      apply: (targetFn, thisArg, argsList) => {        const startTime = performance.now();
            // 调用原函数        const result = Reflect.apply(targetFn, thisArg, argsList);
            // 异步执行回调，避免阻塞和留下调用栈痕迹        Promise.resolve().then(() => {          try {            callback(original, argsList, result);          } catch (e) {            // 静默失败，不暴露Hook存在            if (window.DEBUG_MODE) {              console.error('Hook回调错误:', e);            }          }        });
            // 性能补偿        const elapsed = performance.now() - startTime;        const baseline = this.performanceBaselines.get(funcName) || 0;        if (elapsed < baseline * 0.8) {          // 轻微延迟，使时间接近基线          this.compensateDelay(baseline - elapsed);        }
            return result;      },
          // 保持所有属性访问透明      get(target, property) {        if (property === 'toString') {          return () => original.toString();        }        if (property === 'name') {          return original.name || funcName;        }        if (property === 'length') {          return original.length;        }        if (property === 'prototype') {          return original.prototype;        }        return Reflect.get(target, property);      }    });
        // 使用Object.defineProperty确保属性描述符一致    Object.defineProperty(target, funcName, {      value: proxy,      writable: true,      enumerable: true,      configurable: true    });
        this.activeHooks.add(`${target}.${funcName}`);
        // 安装反检测保护    this.installAntiDetection(funcName, original, proxy);
        return true;  }
      /**   * 测量性能基准   */  measurePerformanceBaseline(funcName, fn) {    const samples = [];    const testArgs = this.getTestArguments(funcName);
        for (let i = 0; i < 50; i++) {      const start = performance.now();      try {        fn(...testArgs);      } catch (e) { /* 忽略错误 */ }      samples.push(performance.now() - start);    }
        samples.sort();    const median = samples[Math.floor(samples.length / 2)];    this.performanceBaselines.set(funcName, median);
        if (window.DEBUG_MODE) {      console.log(` ${funcName} 性能基准:`, median.toFixed(3), 'ms');    }  }
      /**   * 延迟补偿   */  compensateDelay(delayMs) {    if (delayMs <= 0) return;
        if (delayMs > 10) {      // 长延迟用setTimeout，但用postMessage避免被检测为定时器Hook      const channel = new MessageChannel();      channel.port1.postMessage('');      channel.port2.onmessage = () => {};    } else {      // 短延迟用微任务      let end = performance.now() + delayMs;      while (performance.now() < end) {        // 微任务 yielding        Promise.resolve().then(() => {});      }    }  }
      /**   * 安装反检测保护   */  installAntiDetection(funcName, original, proxy) {    // 保护toString    const originalToString = original.toString;    Object.defineProperty(proxy, 'toString', {      value: function() {        return originalToString.call(original);      },      writable: false,      enumerable: false,      configurable: true    });
        // 防御Function.prototype.toString检测    const originalProtoToString = Function.prototype.toString;    Function.prototype.toString = function() {      if (this === proxy) {        return originalToString.call(original);      }      return originalProtoToString.call(this);    };  }
      /**   * 获取测试参数（根据函数名推测）   */  getTestArguments(funcName) {    // 根据常见函数名返回合适的测试参数    const argMap = {      'encrypt': ['test'],      'encode': ['data'],      'sign': [{}, 'key123'],      'hash': ['input']    };
        for (const [key, args] of Object.entries(argMap)) {      if (funcName.toLowerCase().includes(key)) {        return args;      }    }
        return []; // 默认无参数  }
      /**   * 清理所有Hook   */  cleanup() {    for (const hookKey of this.activeHooks) {      const [targetName, funcName] = hookKey.split('.');      const target = targetName === 'window' ? window : eval(targetName);      const original = this.originalReferences.get(funcName);
          if (target && original) {        target[funcName] = original;      }    }
        this.activeHooks.clear();    this.originalReferences.clear();
        if (window.DEBUG_MODE) {      console.log(' 所有Hook已清理');    }  }}
    // 使用示例/*const stealth = new StealthHook();
    // Hook加密函数stealth.hookFunction(window, 'encryptData', (original, args, result) => {  console.log(' 加密调用:', {    参数: args,    结果: result.substring(0, 50) + '...'  });});
    // 使用后清理// stealth.cleanup();*/

**
**

##  四、 研究伦理与注意事项


** 合法边界  ** ：所有技术仅用于  ** 授权测试  ** 。在测试任何网站前，务必：

     * 确认拥有明确书面授权

     * 使用自己完全掌控的测试环境

     * 遵守目标的  ` robots.txt  ` 和服务条款


  * 再次强调：所有操作仅用于合法学习、技术研究，严禁用于商业网站的违规爬取！


##  五、 总结：从对抗到理解


反Hook检测的对抗，本质上是与网站防御方在  ** 可见性  ** 层面的博弈。通过本文的技术，你可以：

  1. ** 识别  ** 网站的检测手段

  2. ** 理解  ** 其背后的防御思路

  3. ** 验证  ** 防御机制的有效性

  4. 记住，最高明的“对抗”不是击败对方，而是完全理解对方的思维，很多时候，站在反爬工程师的角度思考问题会对你解决加密或者风控有很大帮助。


##  码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！
