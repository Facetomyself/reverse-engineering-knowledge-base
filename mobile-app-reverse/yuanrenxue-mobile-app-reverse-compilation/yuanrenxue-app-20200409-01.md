# Android 7.0 Https抓包单双向验证解决方案汇总

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-04-09
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 汇总 Android 7.0 以后用户 CA 不受信任、SSL Pinning 与单双向 TLS 认证下的抓包排查、证书导入和 Hook 方案。

## 因为App对设备限制的原因，换了一台 Android 7
的测试机，在这期间又遇上了几种棘手的检测与验证。感觉采用防抓包技术的厂商越发多了起来。解决完这些问题，写一篇日志来记录一下，作为日后排查手册。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfLa0sEbiaHbO5uqWpxdGwn5QILuVl5vB6PVWspHge0yzl2J0n8Fx24vTTW96pibj8qNC4LLaMImsJQ/640?wx_fmt=png)

### 系统校验证书

Android 7.0 之后，默认情况下 app 只信任系统级别的 CA 。从 chls.pro/ssl 安装的证书是在用户级，这导致了 Charles
无法拦截应用流量。有两种方法可以绕过：

（一）将 Charles CA 安装为系统级 CA ，需要修改 /system 权限，全局 APP 生效，需 Root

（二）修改 APP 包 Androidmanifest 文件并重打包，仅针对单一APP生效，无需 root

#### 第一种操作，基于 ADB shell 安装证书，需要 Root ：

    # 1.从Charles取出证书charles-proxy-ssl-proxying-certificate.pem
    # 2.获取证书hash，并修改证书文件名为hash+后缀''.0'' 。本例为fc0dd2c8.0    iMac:~ imac$ openssl x509 -in ./charles-proxy-ssl-proxying-certificate.pem   -noout -subject_hash    # 执行结果：fc0dd2c8
    # 3.连接测试机，adb shell 修改/system权限，adb push fc0dd2c8.0证书到/system/etc/security/cacerts/    mount -o rw,remount /system
    # 4.修改证书权限为664，重启设备    cd /system/etc/security/cacerts/    chmod 664 ./fc0dd2c8.0    reboot

#### 第二种操作，基于修改 Manifest 重新打包 APK，免Root :

原理是当 platformBuildVersionCode>=24 时候，App 就只信任系统级别的CA。修改 apk 中的AndroidManifest
强行降底运行环境的 API Level ，虽然麻烦，但这种方案的存在意义是，目标APP 有设备 Root 检测时适用。

运行 Apktool 反解，Android Studio 打开 AndroidManifest.xml ，目标 API 级别会在文件的 “manifest”
元素的 “platformBuildVersionCode” 属性中指定。将 platformBuildVersionCode=26改成 23 ，使用
apktool 重新打包签名安装，就可以正常抓包了。

    <manifest xmlns:android="http://schemas.android.com/apk/res/android" \android:versionCode="55" android:versionName="8.3" platformBuildVersionName="8.0.0" \platformBuildVersionCode="26" package="com.test.test001">

流程：

  1. apktool反解

  2. 修改AndroidManifest.xml

  3. apktool 打包

  4. keytool 生成证书

  5. jarsigner apk签名

  6. 如果有签名校验，jadx分析修改smali绕过

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcfLa0sEbiaHbO5uqWpxdGwn59hAtzKzTqt9htc4AlNveSjrKYn4Nrky0YOmxspzvia2wEF10WTRBe5w/640?wx_fmt=jpeg)

### APP校验证书

### （一）App单向验证

APP 内置校验证书，即厂商将证书文件或证书值内置在 APK 安装包内，通信请求时 app 自身通过代码来校验证书和服务器的关系，即 SSL Pinning
。有2种解决方案：

#### 1.逆向 App 取出证书，导入到抓包程序中

  * 证书通常在 /assets 里

  * jadx 反编译后搜索 .p12 .pem .cer ssl 等关键词

  * Hook 监听证书读取位置
\-------实例暂略，有空另起一篇专门写扣证书-------

#### 2\. Hook 绕过证书的校验逻辑

JustTrustMe（Root+Xposed）
DroidSSLUnpinning(Root/免Root+Frida)

JustTrustMe 在测试过程中并不顺利，首先安装时需要依赖 Xposed 框架，如果目标采用xposed 检测，会引发新的问题。并且
JustTrustMe 在某些 App 的新版本已失效，只能分析旧版本 app 或等待作者更新。用法简单，安装后 xposed 勾选启动，重启手机。

    # xposed-->https://repo.xposed.info/module/de.robv.android.xposed.installer# JustTrustMe-->https://github.com/Fuzion24/JustTrustMe/releases/tag/v.2# TrustMePlus(魔改)-->https://github.com/langgithub/JustTrustMePlus

DroidSSLUnpinning 在 Root 和非 Root 环境下都可以工作，Root 环境下操作更方便一些：

确认本地环境已安装frida&frida-tools

确认测试机 cpu 架构，https://github.com/frida/frida/releases 下载对应的frida-server-->

    adb shellgetprop ro.product.cpu.abi#执行结果 arm64-v8a

部署到手机并执行-->

    adb push ./frida-server-12.8.20-android-arm64 /data/local/tmp/cd /data/local/tmpchmod 777 frida-server-12.8.20-android-arm64./frida-server-12.8.20-android-arm64

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfLa0sEbiaHbO5uqWpxdGwn5IlNsLwvXn66pMKELCibbxy5ibfwYbjAM0kXe2ic13NhDrqAJpKjCjL10Q/640?wx_fmt=png)

tcp 转发，用于与frida-server通信,之后的每个端口对应每个注入的进程

    adb forward tcp:27042 tcp:27042adb forward tcp:27043 tcp:27043

本地 DroidDrops 目录下执行

    frida -U com.zhiliaoapp.musically --no-pause -l hooks.js

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfLa0sEbiaHbO5uqWpxdGwn5vtRSk44UeGwV23X4H6UzO6xzcAExLd8ChOl8qTM3iagdc0V4KgVGtRQ/640?wx_fmt=png)

启动 App，charles 抓包恢复正常。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfLa0sEbiaHbO5uqWpxdGwn51H4k1qEMbbSuJ3YQ4MATX92pHARAR32pDicqyL25g8479vxM0ZmP2vw/640?wx_fmt=png)

### （二）App双向验证

APP 双向校验，即服务器要认证请求涞源是否真实客户端（来自真实证书），大概原理这样：

app -->服务端（证书）---- ok
app（证书）<\--服务端---- ok

解决两个技术点：

APP 以为 Charles 是服务端（ Hook 绕过）
服务端以为 Charles 是客户端 （逆向 APP ，获得证书导入到 charles ）

### 非常见证书校验技术的通杀解决方案

ssl_logger 的作用原理是 hook 底层 ssl_read 和 ssl_write 两个方法，完全不用配置代理，不用理解 APP
客户端和服务端的证书校验问题。

    _大黑阔5alt发布过一个魔改版本，精品中的精品。
     https://github.com/5alt/ssl_logger_

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfLa0sEbiaHbO5uqWpxdGwn5yPWTSvJ0JAXNmZqltN41CZfaUmyBTZgMwttKAjqbo8ZPZn9wOsXkicg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfLa0sEbiaHbO5uqWpxdGwn5wKh6lx1JOBlia3sGAcJQzUYYs6p44UUiazeMk9WSos3hAvFvXuHGfEOA/640?wx_fmt=png)
