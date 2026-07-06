
一、进阶简介：
-------

*   之前的博客已经和小伙伴们编译了一个简单的指纹浏览器。
*   进阶篇就是在之前的基础上继续做优化。
*   请确保你已经可以独立编译一个正常运行的指纹浏览器了，进阶内容相对之前要复杂不少。

二、webrtc简介
----------

*   之前的博客简单介绍过webrtc，js可以通过它获取用户的真实IP，插眼传送：

1.  **如何改ip过browserleaks**: [https://blog.csdn.net/w1101662433/article/details/138001797](https://blog.csdn.net/w1101662433/article/details/138001797)
2.  **如何禁用webrtc**: [https://blog.csdn.net/w1101662433/article/details/139476789](https://blog.csdn.net/w1101662433/article/details/139476789)

*   小伙伴们说想传参指定webrtc的ip。之前的修改过不了`browserscan`，这里我们来深挖一下

三、browserscan如何通过webrtc的获取用户ip
------------------------------

*   我先把`browserscan`的webrtc的获取原理给出来
*   将下面的代码复制到F12控制台，就可以获取显示你的真实ip了。

```js
let gevt = [];
let goffer;
function getLocalIPAddress(callback) {
    // 创建一个RTCPeerConnection对象
    let rtc = new RTCPeerConnection({
        iceServers: [
            {urls: "stun:stun.voipbuster.com:3478"},
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
            let candidate_string = JSON.stringify(evt.candidate);
            gevt.push(evt)
            // let ipAddress = evt.candidate.address;
            // 获取IP地址
            let ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;
            let match = ipRegex.exec(candidate_string);
            if (match) {
                let ipAddress = match[1];
                if(! ipAddress.startsWith("192.")){callback(ipAddress);}
            }
            // 关闭peer connection并且移除监听
            // rtc.close();
            let candidate = event.candidate.candidate;
        }
    });
    
    rtc.onicecandidate = e => {
      gevt.push(e)
      if (e.candidate) {
        // 直接从 Candidate 中提取 IP（如非 mDNS 掩码）
        const ip = e.candidate.candidate.split(' ')[4];
        //console.log('Detected IP:', ip);
        if(! ip.startsWith("192.")){console.log('Detected IP:', ip);}
      }
    };

    // 创建一个伪数据通道来触发ice事件
    rtc.createDataChannel('sctp');
    // 创建并且触发offer来开始收集ice候选
    rtc.createOffer().then(offer => {goffer=offer;rtc.setLocalDescription(offer)}).catch(console.error);
}

// 调用函数
getLocalIPAddress(ip => console.log('your real IP is:', ip));

```

*   输出：

```
your real IP is: 114.xx.162.172
Detected IP: 114.xx.162.172
```

四、核心逻辑
------

> browserscan这里的核心就是`JSON.stringify(evt.candidate)`;

*   这里最好玩的地方，就是我们之前改了`evt.candidate`里的值，但是一旦加上`JSON.stringify()`包起来后，就发现我们之前改`evt.candidate`好像失效了。
*   原因是chromium源码中单独给`evt.candidate`写了一个函数方法`RTCIceCandidate::toJSONForBinding`来做`JSON.stringify()`。

五、修改源码
------

> \*目标：传入参数`--webrtc-ip=114.114.114.114`，就可以将webrtc检测的ip替换成114.114.114.114

*   打开文件: `\third_party\blink\renderer\modules\peerconnection\rtc_ice_candidate.cc`

##### 1.加入头

```c
#include <iostream>
#include <string>
#include <regex>
#include "base/command_line.h"
```

##### 2.自建一个函数：

*   这个函数是将字符串中的所有ip替换成传进来的ip

```c
// 追加函数 ===========================
std::string replaceIP(const std::string& input) {
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string webrtc_ip = base_command_line->GetSwitchValueASCII("webrtc-ip"); 
  std::cerr <<  "调用replaceIP(): "<< webrtc_ip << std::endl;
  
  if (base_command_line->HasSwitch("webrtc-ip")) {
    std::regex ip_pattern(
        R"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.)"
        R"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.)"
        R"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.)"
        R"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9]))"
    );
    return std::regex_replace(input, ip_pattern, webrtc_ip);   
  }else{
    return input;
  }
}
// 结束追加 ===========================
```

##### 3.修改下面的4个地方：

```c
String RTCIceCandidate::candidate() const {
  //return platform_candidate_->Candidate();
  // 开始修改 =======================
  //return platform_candidate_->Address();
  String tmp = platform_candidate_->Candidate();
  std::string res = tmp.Utf8();
  res = replaceIP(res);
  return String(res);
  // 结束修改 =======================
}

String RTCIceCandidate::address() const {
  // 开始修改 =======================
  //return platform_candidate_->Address();
  String tmp = platform_candidate_->Address();
  std::string res = tmp.Utf8();
  res = replaceIP(res);
  return String(res);
  // 结束修改 =======================
}

String RTCIceCandidate::relatedAddress() const {
  // 开始修改 =======================
  //return platform_candidate_->RelatedAddress();
  String tmp = platform_candidate_->RelatedAddress();
  std::string res = tmp.Utf8();
  res = replaceIP(res);
  return String(res);
  // 结束修改 =======================
}

ScriptObject RTCIceCandidate::toJSONForBinding(ScriptState* script_state) {
  V8ObjectBuilder result(script_state);

  // 开始修改 =======================
  //result.AddString("candidate", platform_candidate_->Candidate());
  String tmp = platform_candidate_->Candidate();
  std::string res = tmp.Utf8();
  res = replaceIP(res);
  result.AddString("candidate", String(res));
  // 结束修改 =======================
  
  result.AddString("sdpMid", platform_candidate_->SdpMid());
  if (platform_candidate_->SdpMLineIndex())
    result.AddNumber("sdpMLineIndex", *platform_candidate_->SdpMLineIndex());
  result.AddString("usernameFragment", platform_candidate_->UsernameFragment());
  return result.ToScriptObject();
}
```

##### 4.最后再`render`进程中加上参数传递：

*   打开文件：`\content\browser\renderer_host\render_process_host_impl.cc`

```c
command_line->AppendSwitchASCII(switches::kProcessType,
                                  switches::kRendererProcess);
                                  
  // 开始追加 =====================================
  const base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string key;

  if (base_command_line->HasSwitch("webrtc-ip")) {
      key = base_command_line->GetSwitchValueASCII("webrtc-ip");
      command_line->AppendSwitchASCII("webrtc-ip", key);
  }

//结束追加 ===================================

```

##### 5.编译：

```
ninja -C out/Default chrome 
```

六、检测站点：
-------

*   https://www.browserscan.net/zh
*   https://pixelscan.net/

七、测试成果
------

> \*注意，如果以前你修改过webrtc相关内容，请注意是否需要还原。

*   运行命令：

```
./chrome.exe --webrtc-ip=114.114.114.114
```

> 可以看到，`browserscan`站的webrtc检测我们可以随意修改了。我们已经过了。  
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/827de91cf2804eb3bef2e160926a4a31.png)

> 再看看`pixelscan`的webrtc指定ip我们也过了

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0f7f66256ffa40c5961476822cf3332b.png)

八、过browserleaks
---------------

*   打开文件`/third_party/blink/renderer/modules/peerconnection/rtc_session_description.cc`

```c
#include <iostream>
#include <string>
#include <regex>
#include "base/command_line.h"
```

*   找到函数

```c
String RTCSessionDescription::sdp() const {
  return platform_session_description_->Sdp();
}
```

*   替换为：

```c
// 追加函数 ===========================
std::string replaceIP2(const std::string& input) {
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string webrtc_ip = base_command_line->GetSwitchValueASCII("webrtc-ip"); 
  std::cerr <<  "调用replaceIP(): "<< webrtc_ip << std::endl;
  
  if (base_command_line->HasSwitch("webrtc-ip")) {
    std::regex ip_pattern(
        R"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.)"
        R"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.)"
        R"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.)"
        R"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9]))"
    );
    return std::regex_replace(input, ip_pattern, webrtc_ip);   
  }else{
    return input;
  }
}
// 结束追加 ===========================


String RTCSessionDescription::sdp() const {
  // 开始修改 ================================
  //return platform_session_description_->Sdp();
  String tmp = platform_session_description_->Sdp();
  std::string res = tmp.Utf8();
  res = replaceIP2(res);
  return String(res);
  // 结束修改 ================================
}
```

*   编译后测试结果：  
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/e44da7a2f62b4b09ba3ffe11307e4009.png)

