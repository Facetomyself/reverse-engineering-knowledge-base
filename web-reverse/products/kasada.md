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
5. 本地输出与浏览器样本的 /tl body 长度、类型、字节内容对照；若本地改发 `/r` 或长度差一个数量级，继续宿主面，不要拆 opcode
6. `x-kpsdk-r` 拒绝标记先做 D3，再判断是仪器化、绑定还是 IP/指纹

## 常见坑

- 把 Kasada 误判为 Akamai，去找 _abck/bmak/sensor_data
- 复用旧 ips.js、旧 /fp、旧 /tl body 或旧 x-kpsdk-ct
- 只看 /tl 返回 token，不验证业务接口是否放行
- 忽略 /tl body 与当前 Cookie、Header、脚本版本和 iframe 上下文的同轮关系
- 把二进制 body 当字符串处理，导致长度、编码或字节内容变化
- 本地发出 `POST /r` 短包（完整性失败）却把浏览器 `POST /tl` octet-stream 当成已对齐，转去拆 VM handler
- 本地长期保留大范围 VM tracer、全局 Proxy 或解释器插桩
- 过早暴露不完整的 canvas、webgl、audio、iframe 或 postMessage 能力，反而改变 /tl body
- 忽略 Header 大小写、顺序、Content-Type、Origin、Referer、UA 和 Cookie 合并细节

## 验证口径

- 当前 /fp、ips.js、KP_UIDz、x-kpsdk-* 与 /tl body 同轮对应；/tl body 字节长度和类型与浏览器一致
- /tl 响应返回当前可用的 x-kpsdk-ct 与通过状态；带 token 后业务接口返回正常业务数据，而非 403、429、空数据或二次 challenge
- 多轮重新获取动态脚本后仍能稳定生成和验证

## 2026-08-22 realtor.com 实测

公开首页 `https://www.realtor.com/`（课程线索，未复制历史 `ips.js`/`code.js`）：

- Flow 1 首页即 429：CloudFront HTML 先建 `window.KPSDK` / `KPSDK.now`，再加载 UUID 路径 `ips.js`
- `GET .../ips.js` 200，脚本约 320 KiB；`POST .../tl` 200，`Content-Type: application/octet-stream`，body 19802 字节
- 响应头出现 `x-kpsdk-ct`、`x-kpsdk-r=1-AA`（指纹或 IP 拒绝标记）、`x-kpsdk-cr=true`、`x-kpsdk-st`；请求头出现 `x-kpsdk-im` / `x-kpsdk-dt`
- 同轮未观察到首页从 429 恢复为业务 200。Node 加载本轮 `ips.js` 能跑到 `KPSDK.scriptStart`，随后拼出 `/tl` URL 却改发 `POST /r` 156B（完整性失败上报），浏览器走 `POST /tl` 19802B
- `/tl` vs `/r` 是请求边界宿主缺口，不是 opcode 内部题；禁止因此做 VM handler 提升
- `x-kpsdk-r=1-AA` 先做 D3（仪器化 vs 绑定 vs IP/指纹拒绝），不要默认当成「只能自动化」
- 残留 throw 仍可能是宿主面：`performance.memory.jsHeapSizeLimit`、timer `this`、`Function.prototype.toString` 的 this、`undefined.get`/`match`/`app`。miss 目录变空不是停止条件
- 该 case 未跑 RuyiDOM；主线应先最小 Gecko runner，再 Node 降级
- 证据 run `rt_20260822112906_c588a3b562` receipt integrity pass，rootSha256 `3d1849fff74a8b433c6be22e9ff3a0762657c8ace8586d6b0f0faf056b61de1a`

## 2026-08-23 RuyiDOM 主线对照

`workspace/kasada-ruyidom-demo` 同一站点、不复制历史 ips.js：

- Node/v8 路径（kasada-v1）走到 `POST /r` 156B；RuyiDOM 黑盒走到 `POST /tl`（本轮 bodyBytes 约 74KiB），`hasR=false`
- `/tl` 响应 200、`x-kpsdk-cr=true`；首页仍可能 429（`x-kpsdk-r` 拒绝标记）。请求边界对齐不等于 `serverAccepted`
- 禁止因此拆 VM handler。`/tl` 响应头里的 `x-kpsdk-ct` 必须带到下一跳业务 GET，不能只看 cookie jar
