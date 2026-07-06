### 一、什么是webRTC

*   WebRTC（Web Real-Time Communication）是一种支持网页浏览器进行实时语音通话（voice）、视频聊天（video chat）和点对点文件分享的技术。该技术由世界各地的工程师和研究人员共同开发，广泛应用于视频会议、在线教育等。

### 二、webRTC指纹原理

*   WebRTC 指纹（WebRTC Fingerprinting）是指利用 WebRTC 从用户的浏览器中获取信息，并构建一个可辨识该用户的唯一标识（即"指纹"）的行为。
*   但是 WebRTC 获取的信息有限，且其中最重要最有用的的部分，就是**获取用户的真是IP**。
*   即使用户使用 VPN 或代理服务，隐藏其公网 IP 地址，也依旧能够被探测到。

### 三、通过webRTC获取自己的局域网ip

*   有攻才有防，先看看网站是如何通过webRTC获取你信息的。
*   将下面的代码复制到F12控制台，就可以获取显示你的真实ip了，加了代理也没有

```js
function getLocalIPAddress(callback) {
    // 创建一个RTCPeerConnection对象
    let rtc = new RTCPeerConnection({
        iceServers: [
            {urls: "stun:stun.miwifi.com"},
            {urls: 'stun:stun.l.google.com:19302'},
            {urls: 'stun:stun1.l.google.com:19302'},
            {urls: 'stun:stun2.l.google.com:19302'},
            {urls: 'stun:stun3.l.google.com:19302'},
            {urls: 'stun:stun4.l.google.com:19302'},
        ]
    });
    // 监听本地ice候选的事件
    rtc.addEventListener('icecandidate', function handleCandidate(evt) {
        if (evt.candidate) {
            // let ipAddress = evt.candidate.address;
            // 获取IP地址
            let ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;
            let match = ipRegex.exec(evt.candidate.candidate);
            if (match) {
                let ipAddress = match[1];
                callback(ipAddress);
            }
            // 关闭peer connection并且移除监听
            // rtc.close();
        }
    });

    // 创建一个伪数据通道来触发ice事件
    rtc.createDataChannel('');
    // 创建并且触发offer来开始收集ice候选
    rtc.createOffer().then(offer => rtc.setLocalDescription(offer)).catch(console.error);
}

// 使用函数
getLocalIPAddress(ip => console.log('your real IP is:', ip));
```

*   输出：

```
your real IP is: 192.168.xxx.xxx
```

> tips：也可以通过一些在线网站查看自己的暴露的真实ip，如：https://browserleaks.com/webrtc

#### 四、编译chromium源码来随机webRTC的返回值

*   第一篇文章写了如何编译chromium，假设你已经编译成功了。
*   打开文件`third_party/blink/renderer/modules/peerconnection/rtc_ice_candidate.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include <iostream>
#include <cstdlib> // 包含rand()和srand()
#include <ctime> // 包含time()
```

###### 2.找到下面的代码

```c
String RTCIceCandidate::candidate() const {
  return platform_candidate_->Candidate();
}
```

###### 替换为

```c
std::string generateRandomIP() {
    srand(static_cast<unsigned int>(time(0))); // 为了每次运行生成不同的随机数
    int ip_part = rand() % 256;
    std::string ip = "192.168.1.";
    ip += std::to_string(ip_part);
    return ip;
}

String RTCIceCandidate::candidate() const {
  //return platform_candidate_->Candidate();
  return String(generateRandomIP());
}
```

###### 3.编译

```
ninja  -C  out/Default chrome
```

> 既然网站从evt.candidate.candidate里获取我们的ip，我直接将其给篡改。  
> 注意：返回空也是可以的，这2种方式都相当于禁用了webRTC的部分功能，可能导致webRTC不可用。

*   再次访问https://browserleaks.com/webrtc，发现真实ip已被隐藏

#### 五、还有高手？

*   还有其他网站可以获取到我的真实ip啊，如：https://www.browserscan.net/  
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/3a086e8bedfa9bd2bd630f96ad90f774.png)
