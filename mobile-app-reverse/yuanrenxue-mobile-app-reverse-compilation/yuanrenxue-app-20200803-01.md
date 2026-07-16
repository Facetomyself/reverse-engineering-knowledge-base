# 安卓逆向之Luac解密反编译

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-08-03
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> lua文件大概分3种。lua是明文代码，直接用ide能打开，luac是lua编译后的字节码，文件头特征为0x1B 0x4C 0x75 0x61 0x51。 lua虚拟机直接解析lua和luac脚本文件，luaJIT是另一个lua的实现版本，采用即时解析运行机制，luaJIT更高效，文件头特征为0x1B 0x4C 0x4A。

本文阐述针对Cocos2dx-lua提供的轻量级加密方案的反编译。
本文demo对象：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceUWPW8IHqOPtga4wctvahInbf0sZibzib0gyoWNcvFefbvQ6lsb7kMlDGBOQvnqk3sON7h93HTaKUA/640?wx_fmt=png)
lua文件大概分3种。lua是明文代码，直接用ide能打开，luac是lua编译后的字节码，文件头特征为0x1B 0x4C 0x75 0x61 0x51。
lua虚拟机直接解析lua和luac脚本文件，luaJIT是另一个lua的实现版本，采用即时解析运行机制，luaJIT更高效，文件头特征为0x1B 0x4C
0x4A。

### 加密流程

** 一篇文章搞定Cocos2dx-lua正向开发打包流程：
CSDN文章【Cocos2dx-lua 3.11.1】打包lua项目为安卓apk
https://blog.csdn.net/lannan91/article/details/67637373/
加密指令：cocos luacompile -s 未加密源码目录 -d 加密后源码目录 -e -k 加密key -b 加密sign --disable-
compile
``

### 解密逻辑

lua官方加解密实现方式很容易就能查找资料得到，根据得到key和sign就可以利用xxtea算法来对脚本进行解密，只需要三个条件，文件路径&加密sign&加密key就能解密。
加密和解密算法在这：
https://github.com/cocos2d/cocos2d-x-3rd-party-libs-bin/tree/v3/xxtea

### 实现过程

#### 加密sign的找寻方法

sign在.luac文件头中
随机打开一个项目内的.luac文件，找第一个字符串。
![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEceUWPW8IHqOPtga4wctvahICDZF9zbtJbgelhXo8c7CBOmoJy8IJoHyGQm1iasE0ho56sqjLsshDXA/640?wx_fmt=jpeg)

#### 加密key的找寻方法

** key在打包后的cocos的lib库的libcocos2dlua.so中
1.第一种方法是libcocos2dlua.so使用IDA pro打开，全局查找加密sign。点击进入查找结果，在该结果的上方3行能够发现加密key。
2.第二种方法，由于写作的电脑已经升级到10.15.5 (19F101)，IDA pro运行有问题。所以用osx自带的strings工具查找。
2-1.终端运行 strings -a libcocos2dlua.so
2-2.ctrl+f 查找sign，观察sign上方的字符串，即为key。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceUWPW8IHqOPtga4wctvahIqEPHppRATBRnyngicVf1iaicFheLuHoLVNicYRMwZcXezEWScrlXSt1e7A/640?wx_fmt=png)

### 解密实现

** OSX实现脚本：
https://github.com/dengxiaochun/luac_decodeTool  win实现工具：
https://www.jb51.net/softs/575428.html  OSX演示：
将解密脚本放在项目assets目录下
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceUWPW8IHqOPtga4wctvahIkubjnIicSCNNbeefmqCDO8CQwJJ6kZgwPeycqicbHO3g4SIDbwib7kxDg/640?wx_fmt=png)
修改decode.sh的SIGN&KEY变量，并保存。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceUWPW8IHqOPtga4wctvahIlTP0hYaAiabgcFPXjxOGp1paHDl4uxOSPcYAfia4IP4r1VxQSIAQl5NA/640?wx_fmt=png)
终端执行：sh ./decode.sh src
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceUWPW8IHqOPtga4wctvahINeyOFtfEib3ib1T7nibn2MK292R8YZjAMpYhNeO4gmejnVUIEyU3biamOA/640?wx_fmt=png)
执行结果：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceUWPW8IHqOPtga4wctvahIHGicIyYrKNyKFk4ATmeK7Saf7s948CzXoq3LRNsZX0ApGKicoibFpeU0A/640?wx_fmt=png)

执行后脚本将自动备份luac源代码（src_backup）
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceUWPW8IHqOPtga4wctvahI4xhAX6tQmEJuoPf42PYic9ib6bXdniahz1hfd3c3iaOVFJicW6l2OzDPF5g/640?wx_fmt=png)
解密后的.lua文件在src目录中，ide打开，源代码反编译成功，可以进一步研究程序的客户端源码实现。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceUWPW8IHqOPtga4wctvahIFFH7buTsKu0nyvibLia4rQhREQG2AGlRSjfhtN0XJdEIycE10r9ycuZw/640?wx_fmt=png)
本篇来自小伙伴，ID：学徒 的投稿
