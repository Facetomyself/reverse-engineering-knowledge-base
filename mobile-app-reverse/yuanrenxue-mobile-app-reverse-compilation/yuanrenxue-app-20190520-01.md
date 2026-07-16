# 爬虫技巧：使用Charles和requests模拟微博登录

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-05-20
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 我们通过模拟微博登录这个例子来看看如何使用Charles分析网站加载流程，顺便把微博模拟登录的Python代码也给实现了。

我们通过模拟微博登录这个例子来看看如何使用Charles分析网站加载流程，顺便把微博模拟登录的Python代码也给实现了。

Charles是一个网络抓包工具，跟Fiddler一样，你哪个用的顺手就用那个。

抓包是写爬虫的必备技能，熟练的使用抓包工具能使分析效率极大提高，当然这过程中也少了分析逻辑。

## 1\. 用Charles记录整个登录过程

首先，我们运行Charles并开始记录。然后打开Chrome浏览器，选择使用Charles代理，打开微博首页
，出现登录页面（如果之前登录过微博，要先退出登录）。输入用户名和密码进行登录，登录成功后就可以停止Charles的记录。这样我们就用Charles完整记录下了微博的登录过程。见图：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtByQII3sND7KMR2d7yPOhTT6nJPO6JE1Bbm3k3whAnVBssg51MRWjpA/640?wx_fmt=png)

我们把整个登录过程写出一个Python类，它的定义为：

    class WeiboLogin:    user_agent = (        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) '        'Chrome/20.0.1132.57 Safari/536.11'    )
        def __init__(self, username, password, cookies_tosave='weibo.cookies'):        self.weibo_user = username        self.weibo_password = password        self.cookies_tosave = cookies_tosave        self.session = requests.session()        self.session.headers['User-Agent'] = self.user_agent

接下来我们分析登录过程，并逐一实现这个类的各个方法。

## 2\. 分析登录过程

把Charles的主窗口切换到“Sequence”标签页，

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtSkISo9t6RvH13R1YOHUMvUDk99jVT0cjxK9InQeUnmJmlm2jVx4prw/640?wx_fmt=png)

我们可以按加载时间顺序观察Charles记录的微博登录过程，我们发现第一个可疑的请求的Host是：

  * login.sina.com.cn

点击该条记录，下方出现该条请求的完整内容，它的路径是：

    GET /sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_=1542456042531 HTTP/1.1

这个GET请求的参数_=1542456042531看起来是个时间戳，这个在ssologin.js（看后面是如何找到的）定义为preloginTimeStart，可以用int(time.time()*1000)得到。

从prelogin.php这个名字看，它是一个预登陆，即在你输入用户名和密码前，它先从服务器拿点东西过来：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtxDWqDgKDPqXUJVjsOzzG0VKo6XKT0wAezMwhibWOCnkXTQ7SnCRjtYw/640?wx_fmt=png)

用Python实现这个prelogin：

        def prelogin(self):        preloginTimeStart = int(time.time()*1000)        url = ('https://login.sina.com.cn/sso/prelogin.php?'               'entry=weibo&callback=sinaSSOController.preloginCallBack&'               'su=&rsakt=mod&client=ssologin.js(v1.4.19)&'               '_=%s') % preloginTimeStart        resp = self.session.get(url)        pre_login_str = re.match(r'[^{]+({.+?})', resp.text).group(1)        pre_login = json.loads(pre_login_str)        pre_login['preloginTimeStart'] = preloginTimeStart        print ('pre_login 1:', pre_login)        return pre_login

这些预先拿过来的东西有什么用呢？目前为止还不知道，继续往下看。

**补充：关于认证码**
昨天最初写这篇教程的时候，没有碰到验证码。今天就碰到验证码跳出来了，真是大快人心，可以把这部分补充上了。

对比昨天的prelogin的URL参数不能发现，今天的多了两个参数：

  * su=xxxxx 就是加密的那个（实为base64编码）用户名

  * checkpin=1 告诉服务器要检查验证码（我去，自己写爬虫绝对不会这么干）

带着这两个参数请求服务器，返回来的也会多了showpin的值：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtOwXKskQPltZDwUhicKDO87WnhFtwD5aOQiaCyibjZOw9SGqpwlOtvQ6icQ/640?wx_fmt=png)

既然要显示pin（验证码），就要下载验证码，它的地址是：

    https://login.sina.com.cn/cgi/pin.php?r=2855501&s=0&p=aliyun-a34a347956ab8e98d6eb1a99dfddd83bc708

这个是怎么来的呢？直接按Ctrl+F 打开“Text to Find”窗口搜索“pin.php”:

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtoUFVzv9UjzRE0GSpfhXCBiaCpofMbv9oMGbjk3v8nkylMqrZcQuqnGQ/640?wx_fmt=png)

这个Find窗口很有用，它让我们可以在记录的所有请求和响应里面查找特定文本，并且它还支持正则表达式、大小写敏感、只找全词。只找全词，对查找su这样的短词很有帮助，可以过滤大量包含它的词，比如super。

这里要特别说明一下，为什么只选在”Response Body”里面查找。
因为我们是要找上面的URL是如何生成的，我们认为它是在某个js文件的某段代码实现的，所以它一定是在 Response Body
里面的，这样也可以过滤掉很多无关信息。

通过上面的过滤，直接就定位了相关代码，双击进去，再稍微一搜，就发现对应的代码了：

    var pincodeUrl = "https://login.sina.com.cn/cgi/pin.php";...return pincodeUrl + "?r=" + Math.floor(Math.random() * 100000000) + "&s=" + size + (pcid.length > 0 ? "&p=" + pcid : "")

有了这个js，用Python来实现就易如反掌了，小猿们可以自己试试看。

有了验证码的URL，我们就用self.session下载它并保存为文件，在POST 所有login数据前，通过  ` <code>pin =
input('>>please input pin:')</code> ` 来获取，加入到POST数据里面一起POST发送即可。

第二条可疑的请求的Host跟第一条一样，路径是：

    POST /sso/login.php?client=ssologin.js(v1.4.19) HTTP/1.1

这是一条POST，我来看看它POST的数据，选择这条记录，点击“Contents”标签，再点击“Form”标签，可以看到它POST的数据：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtRrks1VtnyweXicibY2W7O8xGEdkbv13Fx1hfqOfgxNfZDCick5vTNpMag/640?wx_fmt=png)

这时候我们可以把这写POST的参数和prelogin得到的联系起来了。

**参数：su**
这个看上去是“加密”的username，即用户名。那它是怎么加密的呢？浏览器运行的是JavaScript，所以我们猜测是通过JS加密的，那么是哪段JS呢？看上面login.php路径里给了参数client=ssologin.js(v1.4.19)，那我们就去ssologin.js里面找找，选择加载这个js文件的请求，“Contents”标签下面就会显示JS代码，按Ctrl+F查找username：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtBAnKy5ZgIMgVeKQYnnXGmvRZZlkapq5gdHw008M2hG8CCUBdoNLkUw/640?wx_fmt=png)

果然在这里，其实就是用base64编码了一下，算不上加密，于是我们就有了获得su的方法：

        def encrypt_user(self, username):        user = urllib.parse.quote(username)        su = base64.b64encode(user.encode())        return su

** **参数：sp**  **
跟su同样的思路，还是在ssologin.js里面查找password，我们发现了加密password的算法：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtXSb9HTzCve5BMHDOAkud7my7atGQq0zWJH1YC2j0KzWpJicBVMnyrHg/640?wx_fmt=png)

于是有了获得sp的方法：

        def encrypt_passwd(self, passwd, pubkey, servertime, nonce):        key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))        message = str(servertime) + '\t' + str(nonce) + '\n' + str(passwd)        passwd = rsa.encrypt(message.encode('utf-8'), key)        return binascii.b2a_hex(passwd)

**参数：prelt**
既然ssologin.js就是管登录的，那我们还是在这里找prelt，Ctrl+F 查找到

    request.prelt = preloginTime;

原来prelt就是preloginTime的简称，那我们再搜索preloginTime：

    preloginTime = (new Date()).getTime() - preloginTimeStart - (parseInt(result.exectime, 10) || 0)

这里的preloginTimeStart就是请求prelogin.php时的时间戳，result.exectime就是prelogin请求返回结果里面的exectime。
哈哈哈，又找到了prelt的算法，其实这个prelt就是从请求开始到现在的时间差，似乎也没那么重要，随机一个就可以，不过还是用Python实现一下：

        def get_prelt(self, pre_login):        prelt = int(time.time() * 1000) - pre_login['preloginTimeStart'] - pre_login['exectime']        return prelt

目前，我们已经获得了登录的重要参数，接下来再看看登录请求的流程，在“Sequence”的 “Filter”
输入login，我们可以看到过滤后的请求，其中前三个就是登录的先后顺序：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtH7ASJYkiajUkAEdQF5HYccJ5Caf0iacMArbFnc3niaCz9RthsBycwTsIA/640?wx_fmt=png)

其详细流程就是：

  1. prelogin从服务器获得一些参数

  2. 把加密的用户名密码等参数POST给https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)

  3. 第2步返回的是html代码，html代码里面重定向到另外的url （所以我们代码里面也要实现这个重定向）

  4. 第3步返回的还是html代码，里面通过JS先实现几个跨域设置，最后重定向到另外一个url（我们也要实现这部分操作）

第4步返回的HTTP头里面重定向到另外的URL，request会跟随这个重定向，不用我们实现。
用Python实现html代码里面的JS重定向的方法就是，用正则表达式提取出JS代码里面的重定向URL，然后用requests做GET请求。

完整的登录流程的代码就是：

        def login(self):        # step-1. prelogin        pre_login = self.prelogin()        su = self.encrypt_user(self.weibo_user)        sp = self.encrypt_passwd(            self.weibo_password,            pre_login['pubkey'],            pre_login['servertime'],            pre_login['nonce']        )        prelt = self.get_prelt(pre_login)
            data = {            'entry': 'weibo',            'gateway': 1,            'from': '',            'savestate': 7,            'qrcode_flag': 'false',            'userticket': 1,            'pagerefer': '',            'vsnf': 1,            'su': su,            'service': 'miniblog',            'servertime': pre_login['servertime'],            'nonce': pre_login['nonce'],            'vsnf': 1,            'pwencode': 'rsa2',            'sp': sp,            'rsakv' : pre_login['rsakv'],            'encoding': 'UTF-8',            'prelt': prelt,            'sr': "1280*800",            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.'                   'sinaSSOController.feedBackUrlCallBack',            'returntype': 'META'        }
            # step-2 login POST        login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'        resp = self.session.post(login_url, data=data)        print(resp.headers)        print(resp.content)        print('Step-2 response:', resp.text)
            # step-3 follow redirect        redirect_url = re.findall(r'location\.replace\("(.*?)"', resp.text)[0]        print('Step-3 to redirect:', redirect_url)        resp = self.session.get(redirect_url)        print('Step-3 response:', resp.text)
            # step-4 process step-3's response        arrURL = re.findall(r'"arrURL":(.*?)\}', resp.text)[0]        arrURL = json.loads(arrURL)        print('CrossDomainUrl:', arrURL)        for url in arrURL:            print('set CrossDomainUrl:', url)            resp_cross = self.session.get(url)            print(resp_cross.text)        redirect_url = re.findall(r'location\.replace\(\'(.*?)\'', resp.text)[0]        print('Step-4 redirect_url:', redirect_url)        resp = self.session.get(redirect_url)        print(resp.text)        with open(self.cookies_tosave, 'wb') as f:            pickle.dump(self.session.cookies, f)        return True

代码中打印了很多信息，方便我们过程整个登录过程。

要测试我们的实现就很简单了:

    if __name__ == '__main__':    weibo_user = 'your-weibo-username'    weibo_password = 'your-weibo-password'    wb = WeiboLogin(weibo_user, weibo_password)    wb.login()

修改为你的微博账户和密码就可以测试起来啦。

听说你想学爬虫？点阅读原文看看
