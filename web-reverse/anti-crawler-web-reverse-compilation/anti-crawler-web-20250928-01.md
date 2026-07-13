# Akamai难点第三弹：ffs参数的混淆解密思路

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-09-28
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 上一篇我们完成了的ajr参数的解密。 [ Akamai难点第二弹：ajr参数得混淆解密 ](https://mp.weixin.qq.com/s?biz=MzU2NTI5MTU5OA==&mid=2247483729&idx=1&sn=b58a96889b4f8080412ff3d2fc966852&scene=21#wechatredirect) 这一篇我。

上一篇我们完成了的ajr参数的解密。 [ Akamai难点第二弹：ajr参数得混淆解密
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483729&idx=1&sn=b58a96889b4f8080412ff3d2fc966852&scene=21#wechat_redirect)
这一篇我们来搞定Akamai参数得ffs参数。  回顾 [ 被 Akamai 反爬虐到哭？Akamai 反爬 JS 逆向：从抓包到解密，四步拆穿加密套路！
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483672&idx=1&sn=a59f56b139dd1a0db63389022a593d50&scene=21#wechat_redirect)
的内容，我们来解析

tHK参数的生成逻辑。  第一步，我们依旧是进行全局查找，搜索tHK  的位置  ：

接下来就在这里打断点，我们可以看到tHK是由VSK()函数生成的。我们单步进函数看看：

通过对这个函数解混淆我们可以发现，函数的主要逻辑其实是获取页面html的input元素的各个属性值进行加密，解混淆之后的函数就是：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var VSK = function(input_list) {    var SvK = "";    var FSK = -1;    var X3K = input_list;    for (var dwK = 0; qV(dwK, X3K['length']); dwK++) {        var x5K = X3K[dwK];        var fLK = T4K(x5K['name']);        var FLK = T4K(x5K['id']);        var xHK = x5K['required'];        var ZVK = c3(xHK, null) ? 0 : 1;        var kZK = x5K['type'];        var QZK = c3(kZK, null) ? -1 : qsK(kZK);        var lEK = x5K['autocomplete'];        if (c3(lEK, null))            FSK = -1;        else {            lEK = lEK['toLowerCase']();            if (MH(lEK, 'off'))                FSK = hh[5];            else if (MH(lEK, 'on'))                FSK = hh[2];            else                FSK = fr;        }        var dhK = x5K['defaultValue'];        var d5K = x5K['value'];        var tEK = hh[5];        var k5K = 0;        if (dhK && S6(dhK['length'], hh[5])) {            k5K = 1;        }        if (d5K && S6(d5K['length'], GT['zQQ']()) && (HO(k5K) || S6(d5K, dhK))) {            tEK = 1;        }        if (S6(QZK, hh[28])) {            SvK =''['concat'](BO(SvK, QZK), ',')['concat'](FSK, ',')['concat'](tEK, ',')['concat'](ZVK, ',')['concat'](FLK, ',')['concat'](fLK, ',')['concat'](k5K, ';');        }    }    var rgK;    return rgK = SvK,    rgK;};

我这里直接对VSK函数进行可改写，因为要使用python调用，我们没办法直接通过js获取到html的input属性，所以这里直接传入一个dict，传入的参数是input元素的各个属性值。而我们则可以使用python去获取原始页面html的input属性。我这里写一个例子：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    from bs4 import BeautifulSoupdef extract_input_attributes(html_content):    """    从HTML内容中提取所有input标签及其属性，返回字典列表        参数:        html_content (str): HTML源码字符串            返回:        list: 包含所有input标签属性的字典列表    """    soup = BeautifulSoup(html_content, 'lxml')  # 也可以使用 'html.parser'    input_tags = soup.find_all('input')        result = []    for input_tag in input_tags:        # 获取所有属性并转换为字典        attrs = dict(input_tag.attrs)        result.append(attrs)        return result# 示例用法if __name__ == "__main__":    html_example = """    <html>        <body>            <input type="text" name="username" id="user" class="form-control" placeholder="Enter username">            <input type="password" name="password" required>            <input type="submit" value="Login">            <div>                <input type="hidden" name="csrf_token" value="abc123">            </div>        </body>    </html>    """        inputs = extract_input_attributes(html_example)    for i, input_dict in enumerate(inputs, 1):        print(f"Input {i}:")        for attr, value in input_dict.items():            print(f"  {attr}: {value}")        print()

这样我们就解决了ffs参数的混淆加密，同时  inf参数的值跟ffs一样，所以这两个参数的加密都解决了。就是验证页面的input元素的属性值。
如果你们在实操时碰到问题，欢迎在评论区留言，咱们一起拆解！后续还会出 “各个参数的实战案例”，教你用 Python 完整复现 Akamai 加密逻辑，
这里是爬虫虐我千百遍，我待爬虫如初恋的爬虫任。  点赞关注，下次实战不迷路～，


关注该公众号

[ 知道了 ](javascript:;)


宋来自广东
