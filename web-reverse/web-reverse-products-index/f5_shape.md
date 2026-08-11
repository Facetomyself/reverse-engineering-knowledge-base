# F5 Shape / Shape Defense

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> F5 Shape 体系的 API 级或页面级防护、动态混淆 JS/WASM、Shape Cookie、fetch/XHR 包装与请求边界 header 注入。

## 命中特征

- 请求 Header 出现一组六个同前缀字段，后缀常见 `-a`、`-b`、`-c`、`-d`、`-f`、`-z`
- Cookie 出现站点随机命名的 Shape 状态；Cookie 名不是通用固定值，必须按当前目标确认
- 页面或脚本链出现 Shape、F5、bm-verify、`/_sec/cp_challenge/verify`、ponos 类回传端点、伪装第一方路径的动态资源或大体积混淆 JS
- 业务请求本身看似普通，但浏览器侧通过 fetch / XMLHttpRequest 包装自动注入 Shape headers，业务代码不显式传这些字段
- 脚本资源伪装成站点普通 JS 或 `/resources/<hash>`、`/resources/<hash>/e_<id>_<version>.js` 形态
- trace 中可见 `Request.get headers` 后紧跟多次 `Headers.set("prefix-*", ...)`；最终 fetch 入参可能从 string/init 变成 Request 对象
- 去掉任意一个 Shape header 后业务接口返回风控错误

不要只因为出现 `_abck`、`bm_sz`、`ak_bmsc` 就把目标误判成 Akamai BMP；主线应以目标业务请求真正必要的 headers、cookie、challenge 和响应错误码为准。

## 常见链路

两类形态：

```text
页面级挑战: 访问受保护页 → 反代 302/短 HTML → 跳 /_sec/cp_challenge/verify 或 bm-verify 挑战页
→ Set-Cookie 下发初始 Shape Cookie → 加载混淆 JS/WASM → 后续请求带 Cookie + headers 放行

API 级暗哨: 页面正常加载 → 伪装第一方 JS 的响应头 Set-Cookie 下发 Shape Cookie
→ 包装 window.fetch / XMLHttpRequest / Request / Headers
→ 业务请求进入 wrapper → 请求边界写入 prefix-a/b/c/d/f/z → 业务接口校验
```

```text
页面入口 → 加载 Shape 主脚本或伪装脚本 → 动态脚本/WASM
→ 读取 currentScript、nonce、document magic key、location、storage、navigator、screen、performance
→ 安装 fetch/XHR/Request/Headers wrapper → 可选前置请求（JWKS/config/telemetry）
→ 业务请求进入 wrapper → 规则匹配 URL/method/headers/body
→ Request.get headers → 连续 Headers.set 写入六个字段 → 业务接口
```

## 观察优先级

1. Shape Cookie 多数来自服务端 HTTP Set-Cookie，不一定由 JS 写入；`document.cookie` setter 无断点触发是阴性证据，Cookie 维护放在请求会话层
2. Shape headers 在请求边界由 wrapper 写入，不一定存在公开函数直接返回；先做字段必要性实验（逐个去掉看错误码与响应体）
3. telemetry/ponos 类回传可能是指纹/校验回传，不等于最终业务接口
4. Idempotency-Key、X-API-Key、X-Channel-ID、Referer、Origin 等可能是业务接口要求，不一定属于 Shape
5. 关键宿主面：`Function.prototype.toString` 覆盖实例调用与 `Function.prototype.toString.call(fn)`；`Request`/`Headers` 的构造、getter、clone、set/append/get/forEach；`HTMLAnchorElement` URL 解析（设置 href 后读 pathname/host/protocol/search/hash）；currentScript/src/nonce/动态 script append；Blob/URL.createObjectURL/Worker/postMessage
6. 动态生成验收：基础请求头不含 trace 固定 Shape headers，由原始 Shape 外围链在本地最终 Request 上重新写入

## 常见坑

- 拿到业务数据不等于动态生成成功（trace 固定头重放也能返回 200，只是 replay 不是动态生成）
- 把 Shape Cookie 当客户端算法硬逆
- Cookie 必要性随请求窗口变化，单次样本不是永久结论
- 误判为 Akamai 主线
- 进入 VMP/opcode 内部找入口；成功路线通常在外层 DOM/BOM、Worker、Request、Headers、URL 与 fetch/XHR 边界
- 把 trace 时间字段当真实等待；冷启动性能与服务化性能是两回事；标准 HTTP 客户端抖动不应误判为参数错误

## 验证口径

- 基础请求头中不包含 trace 固定 Shape headers；本地执行原始外围链后最终 Request 含完整 prefix-a/b/c/d/f/z
- 去掉任一 Shape header 触发风控，保留完整动态 headers 返回业务数据
- 最终验收是业务接口返回正常业务 JSON（而非 telemetry 或 challenge 接口成功）
- 连续多次验证，记录状态码、Cookie 是否存在、动态 headers 是否启用、业务数量与耗时；有性能要求时区分冷启动、预热、动态生成与业务 POST 耗时
