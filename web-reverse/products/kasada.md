# Kasada KPSDK

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> Kasada KPSDK 体系：动态脚本、/fp、ips.js、/tl 二进制指纹 payload 与 x-kpsdk-* token 链路。

## 命中特征

- 请求或响应头出现 `x-kpsdk-ct`、`x-kpsdk-v`、`x-kpsdk-h`、`x-kpsdk-im`、`x-kpsdk-dt`、`x-kpsdk-cr`
- Cookie 出现 `KP_UIDz` 或其它 KP_ 前缀状态
- 页面、脚本或请求路径出现 `KPSDK`、`p.js`、`ips.js`、`/fp`、`/tl`、`/mfc`
- `/fp` 返回 iframe/HTML 初始化片段，包含 `window.KPSDK`、`KPSDK.now`、postMessage("KPSDK:...")
- `ips.js` 执行后自行发起 `POST /tl`；`/tl` 请求常见 `Content-Type: application/octet-stream`，Body 是二进制指纹 payload
- 成功响应常见返回新的 `x-kpsdk-ct`，伴随 `x-kpsdk-cr: true` 或 Cookie 更新

目标没有 `_abck / bm_sz`，不要误判为 Akamai BMP。

## 常见链路

```text
请求受保护页面
→ 获取初始 Cookie / KPSDK 状态
→ 加载 p.js 或主 KPSDK 脚本
→ 请求 /mfc 获取或确认 x-kpsdk-h 等配置状态
→ 请求 /fp 获取 iframe HTML / KPSDK 初始化片段
→ 从 /fp 或页面中定位当前 ips.js
→ 执行当前 ips.js
→ ips.js 通过 XHR / fetch 发出 POST /tl（二进制 payload）
→ 服务端返回新的 x-kpsdk-ct / x-kpsdk-cr / KP_UIDz
→ 带当前 token、Cookie 和 Header 请求业务接口
```

核心是让当前 KPSDK 动态脚本在正确环境、当前 Cookie 和当前 Header 下自己走到 `/tl` 请求边界，而不是调用某个公开函数拿 token。同一轮对应关系：当前页面或 /fp HTML、当前 p.js/ips.js、当前 KP_UIDz、当前 x-kpsdk-v/h/im/dt、当前 /tl URL 与二进制 body、当前 x-kpsdk-ct、当前业务请求 Header/Cookie。

## 观察优先级

1. 确认 p.js、ips.js、/fp、/mfc、/tl 的实际顺序；ips.js 在主窗口、iframe 还是 worker 上下文执行
2. `/tl` 由 XHR、fetch 还是 sendBeacon 发出；body 是 ArrayBuffer、Uint8Array、Blob、form 还是字符串
3. 哪些 x-kpsdk-* Header 由脚本生成，哪些来自服务端响应；KP_UIDz 与 /tl body 是否绑定当前会话
4. 环境面：UA/plugins/mimeTypes/iframe/postMessage/performance/canvas/WebGL/audio/事件；二进制处理能力（ArrayBuffer、Uint8Array、Blob、TextEncoder）
5. 本地输出与浏览器样本的 /tl body 长度、类型、字节内容对照

## 常见坑

- 把 Kasada 误判为 Akamai，去找 _abck/bmak/sensor_data
- 复用旧 ips.js、旧 /fp、旧 /tl body 或旧 x-kpsdk-ct
- 只看 /tl 返回 token，不验证业务接口是否放行
- 忽略 /tl body 与当前 Cookie、Header、脚本版本和 iframe 上下文的同轮关系
- 把二进制 body 当字符串处理，导致长度、编码或字节内容变化
- 本地长期保留大范围 VM tracer、全局 Proxy 或解释器插桩
- 过早暴露不完整的 canvas、webgl、audio、iframe 或 postMessage 能力，反而改变 /tl body
- 忽略 Header 大小写、顺序、Content-Type、Origin、Referer、UA 和 Cookie 合并细节

## 验证口径

- 当前 /fp、ips.js、KP_UIDz、x-kpsdk-* 与 /tl body 同轮对应；/tl body 字节长度和类型与浏览器一致
- /tl 响应返回当前可用的 x-kpsdk-ct 与通过状态；带 token 后业务接口返回正常业务数据，而非 403、429、空数据或二次 challenge
- 多轮重新获取动态脚本后仍能稳定生成和验证
