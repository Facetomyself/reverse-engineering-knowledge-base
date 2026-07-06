
一、WebGPU是什么
-----------

*   WebGPU 是一种新的 Web 标准，旨在提供一个具备现代硬件加速能力的图形和计算接口，用于网络应用。
*   WebGPU存在的目的是，允许Web网页应用用户设备上的GPU，从而实现更加高效和强大的图形渲染和计算性能。

二、什么是WebGPU指纹
-------------

*   通过收集如GPU型号、驱动版本、支持的图形特性等信息，hash而成的指纹信息。
*   WebGPU指纹唯一性并不太高，还有很多浏览器是不支持webGPU，所以`WebGPU指纹的风控等级较低`。

三、获取浏览器的WebGPU指纹
----------------

*   有攻才有防，先看看网站是如何通过js获取你的WebGPU指纹的。
*   将下面的代码复制到`F12控制台`，就可以获取显示你的WebGPU指纹了

```js
async function checkWebGPUSupport() {
    if (!navigator.gpu) {
        console.log("当前浏览器不支持WebGPU");
        return;
    }

    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) {
        console.log("当前浏览器不支持WebGPU");
        return;
    }

    const device = await adapter.requestDevice();
    // console.log("GPU Device:", device);

    // 请求设备支持的扩展
    const extensions = Array.from(adapter.features.values());
    console.log("支持的扩展:", extensions);

    // 获取硬件限制信息并手动序列化
    const limits = {};
    for (const key in device.limits) {
	    console.log("key", key)
        limits[key] = device.limits[key];
    }
    console.log("硬件限制信息:");
    console.log(limits);
    
    // 序列化和哈希处理
    const serializedData = JSON.stringify({
        extensions: extensions,
        limits: limits
    });
    console.log('serializedData', serializedData);
		
    // 使用SHA-256计算哈希
    const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(serializedData));
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    
    console.log("hash后得到的webGPU指纹:", hashHex);
}

await checkWebGPUSupport();

```

*   输出：

```
ffa2f3d7b37fd10b2c2eb8c7bb973462443ec1d10040191a399c68fab4d812ee
```

四、编译随机webGPU指纹
--------------

*   第一篇文章写了如何编译chromium，假设你已经编译成功了。
*   找到源码 `/third_party/blink/renderer/modules/webgpu/gpu_supported_limits.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include "base/command_line.h"
```

###### 2.我们注释掉这里的最后一行

```c
#define SUPPORTED_LIMITS(X)                    \
  X(maxTextureDimension1D)                     \
  X(maxTextureDimension2D)                     \
  X(maxTextureDimension3D)                     \
  X(maxTextureArrayLayers)                     \
  X(maxBindGroups)                             \
  X(maxBindGroupsPlusVertexBuffers)            \
  X(maxBindingsPerBindGroup)                   \
  X(maxDynamicUniformBuffersPerPipelineLayout) \
  X(maxDynamicStorageBuffersPerPipelineLayout) \
  X(maxSampledTexturesPerShaderStage)          \
  X(maxSamplersPerShaderStage)                 \
  X(maxStorageBuffersPerShaderStage)           \
  X(maxStorageTexturesPerShaderStage)          \
  X(maxUniformBuffersPerShaderStage)           \
  X(maxUniformBufferBindingSize)               \
  X(maxStorageBufferBindingSize)               \
  X(minUniformBufferOffsetAlignment)           \
  X(minStorageBufferOffsetAlignment)           \
  X(maxVertexBuffers)                          \
  X(maxBufferSize)                             \
  X(maxVertexAttributes)                       \
  X(maxVertexBufferArrayStride)                \
  X(maxInterStageShaderComponents)             \
  X(maxInterStageShaderVariables)              \
  X(maxColorAttachments)                       \
  X(maxColorAttachmentBytesPerSample)          \
  X(maxComputeWorkgroupStorageSize)            \
  X(maxComputeInvocationsPerWorkgroup)         \
  X(maxComputeWorkgroupSizeX)                  \
  X(maxComputeWorkgroupSizeY)                  \
  X(maxComputeWorkgroupSizeZ)                  \
  //X(maxComputeWorkgroupsPerDimension)

```

> 这里注释的`maxComputeWorkgroupsPerDimension`其实是个函数，注释掉是因为我们要给它重新定义一个。

###### 3. 随便一个函数后面追加：

```c
unsigned  GPUSupportedLimits::maxComputeWorkgroupsPerDimension() const {
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  int seed;
  if (base_command_line->HasSwitch("fingerprints")) {
      std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> seed; 
  }else{
      auto now = std::chrono::system_clock::now();
      std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
      seed = static_cast<int>(now_time_t);
  }
  return seed % 128;
}
```

> 可以看到，这里的原理就是webGPU里的`maxComputeWorkgroupsPerDimension`属性设置成了返回随机数。其他属性按需照搬。

###### 4.编译

```
ninja  -C  out/Default chrome
```

*   找到`out/Default chrome`下新编译的执行文件`chrome.exe`执行
*   再次看看webGPU指纹，是不是每次访问都变成随机了。

五、在线指纹验证网站：
-----------

*   https://browserleaks.com/webgpu
*   https://abrahamjuliot.github.io/creepjs/

* * *
