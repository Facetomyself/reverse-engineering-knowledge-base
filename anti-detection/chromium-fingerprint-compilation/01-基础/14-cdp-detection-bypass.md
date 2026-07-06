#### 一、cpd检测是什么

*   开发者工具协议（Chrome DevTools Protocol，就简称CDP）
*   cdp检测(`Chrome DevTools Protocol Detection`)，是许多网站常用的机器人检测手段之一。通常是利用浏览器开发者工具的进行的功能检测或漏洞探测。
*   当每次打开F12控制台，或者使用selenium，puppeteer之类的自动化工具打开网页，都会被识别成机器人。这种情况基本就是因为有cpd检测。

#### 二、cdp 检测原理

*   cdp检测的原理一般是利用`console.debug()`函数来实现，当你打开consle控制台时，`console.debug()`才会真正的被调用。
*   一旦`console.debug()`函数被触发，我们就可以认定你打开了F12控制台。

#### 三、代码实现cdp检测

*   编写一个html文件，随便取名111.html。

```html
<!DOCTYPE html>
<html>

<head>
	<title>Detect Chrome DevTools Protocol</title>
	<script>
		function genNum(e) {
			return 1000 * e.Math.random() | 0;
		}
		function catchCDP(e) {
			if (e.chrome) {
				var rng1 = 0;
				var rng2 = 1;
				var acc = rng1;
				var result = false;
				try {
					var errObj = new e.Error();
					var propertyDesc = {
						configurable: false,
						enumerable: false,
						get: function () {
							acc += rng2;
							return '';
						}
					};
					Object.defineProperty(errObj, "stack", propertyDesc);
					console.debug(errObj);
					errObj.stack;
					if (rng1 + rng2 != acc) {
						result = true;
					}
				} catch {

				}
				return result;
			}
		}
		function isCDPOn() {
			if(!window)
				return;
			const el = document.querySelector('span#status');
			if(!el)
				return;
			el.innerText = catchCDP(window) ? "yes":"no";
		}
		function init() {
			isCDPOn();
			setInterval(isCDPOn, 100);
		}
		document.addEventListener("DOMContentLoaded", init);
	</script>
</head>

<body>
	<p>CDP Detected: <span id="status">-</span></p>
</body>

</html>

```

*   这个检测页面可以有效识别，每次打开F12，或者使用selenium，puppeteer之类的自动化工具打开这个页面，都会被识别成机器人。

#### 四、修改源码绕过cdp检测

*   第一篇文章写了如何编译chromium，假设你已经编译成功了。
*   找到源码：`\v8\src\inspector\v8-console.cc`

###### 1.找到下面的代码

```c
void V8Console::Debug(const v8::debug::ConsoleCallArguments& info,
                      const v8::debug::ConsoleContext& consoleContext) {
  TRACE_EVENT0(TRACE_DISABLED_BY_DEFAULT("v8.inspector"), "V8Console::Debug");
  ConsoleHelper(info, consoleContext, m_inspector)
      .reportCall(ConsoleAPIType::kDebug);
}
```

###### 2.替换为

```c
void V8Console::Debug(const v8::debug::ConsoleCallArguments& info,
                      const v8::debug::ConsoleContext& consoleContext) {
  //TRACE_EVENT0(TRACE_DISABLED_BY_DEFAULT("v8.inspector"), "V8Console::Debug");
  //ConsoleHelper(info, consoleContext, m_inspector)
  //    .reportCall(ConsoleAPIType::kDebug);
}
```

###### 3.编译

```
ninja  -C  out/Default chrome
```

#### 五、在线指纹验证网站：

*   https://fingerprint.com/products/bot-detection/
*   https://www.browserscan.net/bot-detection
