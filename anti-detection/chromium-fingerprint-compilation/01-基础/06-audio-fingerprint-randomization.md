### 一、什么是audio指纹

*   Audio指纹（音频指纹）是音频内容的独特标识，可以将其看作是沿时间轴的数字摘要。
*   音频指纹技术通过从音频信号中提取显著的特征点来创建指纹。这些特征通常是不易被感知变化所影响的，如音高、节奏、频谱等。
*   audio指纹都是独特性不高。

### 二、如何获取audio指纹

*   有攻才有防，先看看网站是如何通过js获取你的audio指纹的。
*   将下面的代码复制到F12控制台，就可以获取显示你的audio指纹了

```js
let AudioContext = window.OfflineAudioContext || window.webkitOfflineAudioContex
let context = new AudioContext(1, 5000, 44100)
let oscillator = context.createOscillator()
oscillator.type = "triangle"
oscillator.frequency.value = 1000
let compressor = context.createDynamicsCompressor()
compressor.threshold.value = -50
compressor.knee.value = 40
compressor.ratio.value = 12
compressor.reduction.value = 20
compressor.attack.value = 0
compressor.release.value = 0.2
oscillator.connect(compressor)
compressor.connect(context.destination);

async function sha256(message) {
    // 把字符串转换为Uint8Array
    const msgBuffer = new TextEncoder().encode(message);
    // 计算散列值
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    // 转换为数组
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    // 转换为16进制字符串
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
}

oscillator.start()
context.oncomplete = event => {
    // We have only one channel, so we get it by index
    let samples = event.renderedBuffer.getChannelData(0)
    let samples_str = JSON.stringify(samples)
    sha256(samples_str).then(hash => console.log(hash));
};
context.startRendering()
```

*   输出：

```
e336f0bfce56a91fd1fd0a88530f3bf323ad23cf6155769cc89b09092880cde9
```

> 注意: audio指纹唯一性不是特别高，一般都是和其他指纹配合使用才能做到较高的准确性。

### 三、编译随机audio指纹

*   我在第一篇文章写了如何编译chromium的大概流程，网上的教程也一抓一大把，假设你已经编译成功了。
*   打开源码 `third_party/blink/renderer/modules/webaudio/offline_audio_context.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include <random>
```

###### 2.找到下面的代码

```c
OfflineAudioContext::OfflineAudioContext(LocalDOMWindow* window,
                                         unsigned number_of_channels,
                                         uint32_t number_of_frames,
                                         float sample_rate,
                                         ExceptionState& exception_state)
    : BaseAudioContext(window, kOfflineContext),
      total_render_frames_(number_of_frames) {
  destination_node_ = OfflineAudioDestinationNode::Create(
      this, number_of_channels, number_of_frames, sample_rate);
  Initialize();
}
```

###### 替换为

```c
int getRandomIntForFoo6Modern() {
    static std::mt19937 generator(static_cast<unsigned long>(time(NULL))); // 静态以确保只初始化一次
    std::uniform_int_distribution<int> distribution(0, 99);
    return distribution(generator);
}

OfflineAudioContext::OfflineAudioContext(LocalDOMWindow* window,
                                         unsigned number_of_channels,
                                         uint32_t number_of_frames,
                                         float sample_rate,
                                         ExceptionState& exception_state)
    : BaseAudioContext(window, kOfflineContext),
      total_render_frames_(number_of_frames) {
  destination_node_ = OfflineAudioDestinationNode::Create(
      this, number_of_channels, number_of_frames , sample_rate+getRandomIntForFoo6Modern());
  Initialize();
}

```

###### 3.编译

```
ninja  -C  out/Default chrome
```

*   编译后每次刷新时audio指纹都是随机的了。

> 注意：这里可能会对浏览器的声音产生未知影响。

### 四、在线指纹验证网站：

*   https://abrahamjuliot.github.io/creepjs/
*   https://ip77.net/  
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ebe86493fdc451cdc2df00093fc0b18c.png)
