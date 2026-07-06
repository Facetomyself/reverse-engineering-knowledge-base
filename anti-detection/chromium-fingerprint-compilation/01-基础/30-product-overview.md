
关于成品
----

#### 主要功能：

每次启动chrome.exe时， 浏览器 随机生成一个新指纹。

#### 可选参数：

`--fingerprints=12341234`（随机数种子,最大9个9），可以固定住指纹，每个种子对应一个不同指纹。  
`--timezone=Asia/Hong_Kong` 修改时区。  
`--ignores=webrtc,fonts` 保留原生的webrtc和fonts指纹，多值用逗号分隔，可选值有：`--ignores=fonts,webgpu,webgl,webrtc,canvas,audio,clientrects,screen,tls,useragent,video,svg`

#### 指纹修改：

*   canvas指纹
*   fonts指纹
*   webGL指纹
*   webRTC禁用
*   audio指纹
*   ClientRects指纹
*   tls/ja4指纹
*   video指纹
*   svgRect指纹
*   webGPU指纹
*   浏览器屏幕信息
*   浏览器版本信息
*   时区
*   可绕过cdp检测
*   可绕过常见无头检测

#### 指纹检测站点：

*   https://iphey.com/
*   https://www.browserscan.net/
*   https://abrahamjuliot.github.io/creepjs/
*   https://demo.fingerprint.com/playground

#### 注意：

*   成品仅供个人使用，请勿传播，如需商用，请联系作者授权。
*   请在法律允许的范围内合理使用，尊重法律的权威。

#### 版本：

*   当前版本为116。
