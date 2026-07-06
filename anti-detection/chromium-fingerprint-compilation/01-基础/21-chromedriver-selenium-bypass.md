
*   有小伙伴说使用selenium没能绕过机器人检测，盘他。
*   selenium机器人检测有2种，一是cdp检测，二是webdriver特征检测。cdp检测前面的博客已写过，这里就提下webdriver特征检测。

### 一、selenium简介

*   Selenium 是一个强大的工具，用于Web浏览器自动化，更常被用于爬虫。
*   但selenium需要通过webdriver来驱动chrome，每次运行selenium时，都要先找到对应版本的chromedriver.exe。
*   chromedriver自动化会对浏览器的部分属性进行修改，非常容易被识别为机器人。
*   pypeeteer却没有这种烦恼，它不需要中间驱动，所以还是建议大家使用pyppeteer。但如果你已经写了上万行selenium代码了，那还是编译一个驱动吧。

### 二、机器人识别网站

*   1.https://www.browserscan.net/bot-detection  
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/9f84644c0b544f5eb4ff26ebbbd1debc.png)
*   2.https://fingerprintjs.github.io/BotD/main/

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/7b493097f2b746d280561a20ec5d0aa0.png)

> 很明显，常规网站都能检测到selenium机器人。

### 三、 检测原理

*   将下面的js代码复制粘贴进F12控制台：

```js
// 定义正则表达式
let regex = /^([a-z]){3}_.*_(Array|Promise|Symbol|JSON|Object|Proxy)$/;
// 获取window对象的所有属性名称
let allProps = Object.getOwnPropertyNames(window);
// 过滤出符合正则表达式的属性名称
let filteredProps = allProps.filter(prop => regex.test(prop));
// 输出匹配的属性名
console.log(filteredProps);
```

*   正常浏览器会打印

```js
[]
```

*   被selenium控制的浏览器会打印

```js
(6) ['cdc_adoQpoasnfa76pfcZLmcfl_Array', 'cdc_adoQpoasnfa76pfcZLmcfl_Object', 
'cdc_adoQpoasnfa76pfcZLmcfl_Promise', 'cdc_adoQpoasnfa76pfcZLmcfl_Proxy', 
'cdc_adoQpoasnfa76pfcZLmcfl_Symbol', 'cdc_adoQpoasnfa76pfcZLmcfl_JSON']
```

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/e8476218c35240f99696f385078af5b2.png)

> 注意：这就是这2个站检测selenium机器人的核心逻辑。pypeeteer机器人已经不用担心，网站检测不到。

### 四、编译crhomedriver.exe

*   打开chromium源码文件：`\chrome\test\chromedriver\chrome\devtools_client_impl.cc`

###### 1.找到：

```c
std::string script =
        "(function () {"
        "window.cdc_adoQpoasnfa76pfcZLmcfl_Array = window.Array;"
        "window.cdc_adoQpoasnfa76pfcZLmcfl_Object = window.Object;"
        "window.cdc_adoQpoasnfa76pfcZLmcfl_Promise = window.Promise;"
        "window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy = window.Proxy;"
        "window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol = window.Symbol;"
        "window.cdc_adoQpoasnfa76pfcZLmcfl_JSON = window.JSON;"
        "}) ();";
    params.Set("source", script);
```

###### 2.替换为：

```c
std::string script =
        "(function () {"
        //"window.cdc_adoQpoasnfa76pfcZLmcfl_Array = window.Array;"
        //"window.cdc_adoQpoasnfa76pfcZLmcfl_Object = window.Object;"
        //"window.cdc_adoQpoasnfa76pfcZLmcfl_Promise = window.Promise;"
        //"window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy = window.Proxy;"
        //"window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol = window.Symbol;"
        //"window.cdc_adoQpoasnfa76pfcZLmcfl_JSON = window.JSON;"
        "}) ();";
    params.Set("source", script);
```

###### 3.编译：

```c
ninja  -C  out/Default chromedriver
```

> 注意：编译完后，会在out/Default目录下生成一个chromedriver.exe文件，这就是驱动。

### 五、验证

*   将生成的chromedriver.exe拿过来，运行下面的python代码：

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

# 指定chromedriver的路径
s = Service(r"chromedriver.exe")  # 请将这里替换为你的chromedriver路径

# 初始化Chrome选项
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = r"C:\Users\Administrator\AppData\Local\Chromium\Application\chrome.exe"  # 请将这里替换为你的Chrome浏览器路径
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--fingerprints=11111111")

# 使用Service对象初始化driver
driver = webdriver.Chrome(service=s, options=chrome_options)
driver.delete_all_cookies()

# driver.get("https://www.browserscan.net/bot-detection")
driver.get("https://fingerprintjs.github.io/BotD/main/")
time.sleep(99999)
```

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d9085c124ddc4e4b8cb2718359c1652e.png)

> 可以看到，依旧是自动化控制，官网却已经检测不到了。browserscan也一样。
