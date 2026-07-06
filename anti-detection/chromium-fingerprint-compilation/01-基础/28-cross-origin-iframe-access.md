
### 一、iframe下的#document是什么

*   `#document` 是一个特殊的 HTML 元素，表示 `<iframe>` 元素内部的文档对象。
*   当你在 HTML 页面中嵌入一个 `<iframe>` 元素时，浏览器会创建一个新的文档对象来表示 `<iframe>` 内部的内容。这 个文档对象就是 `#document`。

### 二、如何获取#document下的内容

##### 1. 使用 contentDocument 属性

```js
var iframe = document.getElementById('myIframe');
var iframeDocument = iframe.contentDocument;
// 现在可以访问 iframe 文档中的元素了
var heading = iframeDocument.getElementsByTagName('h1')[0];
console.log(heading.textContent);
```

##### 2. 使用 contentWindow.document

```js
var iframe = document.getElementById('myIframe');
var iframeDocument = iframe.contentWindow.document;
// 访问 iframe 文档中的元素
var heading = iframeDocument.getElementsByTagName('h1')[0];
console.log(heading.textContent);
```

> 注意：如果 iframe 加载的页面与父页面不同源（即协议、域名或端口任一不同），则出于安全考虑，浏览器的同源政策会阻止你访问 iframe 的内容。这种情况下，`contentDocument`会返回null。

### 三、如何获取跨域iframe的#document里的内容

*   这里提供一个修改chromium源码的方案。
*   这里假设你已经可以熟练编译chromium源码。

###### 1.找到源码：

*   打开：`\third_party\blink\renderer\core\html\html_iframe_element.idl`

```c
[CheckSecurity=ReturnValue] readonly attribute Document? contentDocument;
```

###### 2.替换为：

```c
//[CheckSecurity=ReturnValue] readonly attribute Document? contentDocument;
readonly attribute Document? contentDocument;
```

> 注意，这里就是把`[CheckSecurity=ReturnValue]`这段注释掉了，意思是忽略掉安全隔离。

###### 3.编译：

```c
ninja -C out/Default chrome
```

##### 4.启动时加上参数（必须）

```
--disable-site-isolation-trials
```

> 操作完后，就可以发现，跨域iframe的#document里的内容也可以获取到啦。

### 四、风险

*   1.取消跨域隔离有一定安全风险。
*   2.有些站会做安全隔离检测，可能会被识别到。
