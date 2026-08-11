# Akamai（Bot Manager / BMP / CSC）

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> Akamai Bot Manager、BMP、CSC 与 TLS 指纹层的通用识别、链路观察与验收参考。

## 命中特征

- Cookie 出现 `_abck`、`bm_sz`、`ak_bmsc`、`bm_sv`、`bm_mi` 等字段；`_abck` 初始值常见以 `~-1~-1~-1~-1~-1` 结尾，通过后更新为带状态段的值
- 页面加载无扩展名随机路径混淆脚本；运行链出现 `bmak`、`get_telemetry`、`sensor_data`
- 浏览器侧可观察到 `sensor_data` 提交到 Akamai 脚本同路径或相邻路径
- 响应状态为 403，HTML 中出现 `sec-if-cpt-container`、challenge 容器或保护页标记
- 标准 HTTP 客户端出现 HTTP/2 stream reset、连接超时、TLS 指纹不匹配，但浏览器正常

Akamai 不是单一形态，至少先区分三类：

```text
BMP / Bot Manager = 常见 _abck + bm_sz + sensor_data 链路
CSC / Client-Side Challenge = 更强 challenge 页面，iframe / challenge 容器 / 保护页
TLS/HTTP2 指纹层 = JS 还没执行，请求在传输层已被 reset、timeout 或策略拦截
```

## 常见链路

BMP 典型链路：

```text
请求首页或受保护页面
→ 服务端下发 _abck / bm_sz
→ 页面加载混淆脚本，收集浏览器环境、指纹和行为状态
→ 生成 sensor_data，POST 到校验端点
→ 服务端更新 _abck / 相关 Cookie
→ 带更新后的 Cookie 请求目标页面或接口
```

CSC 典型链路：

```text
请求受保护入口
→ 返回 403 或短 HTML challenge 页面
→ 页面加载二次 challenge 脚本，验证环境、事件、iframe、storage 或行为
→ 成功后触发 reload、跳转、cookie 更新或继续请求
→ 再访问业务页面或业务接口
```

TLS 指纹层不属于本地执行层的 JS 补环境问题。请求在未进入 JS 链路前就被 reset、timeout 或 HTTP/2 策略拦截时，优先排查请求客户端的 TLS、HTTP/2、Header 顺序和 UA。

## 观察优先级

1. 定位 `sensor_data` 的 POST 边界（URL、Header、Body、调用栈），并记录 `_abck` 更新前后状态
2. 确认失败发生在 TLS/HTTP2 层、challenge 页面层、sensor_data 层还是业务请求层
3. `window.bmak.get_telemetry()` 存在只说明是候选入口，必须确认当前目标是否真实调用它产出 `sensor_data`
4. CSC 场景同一轮可能发起多条同路径 XHR（先短 body，再一至多条长 body），按浏览器产生顺序全部收集并去重
5. 关注 POST 后 `_abck` 是否真实更新、CSC 后 `sec-if-cpt-container=False` 是否出现
6. 环境值（UA、screen、canvas、WebGL、audio、事件序列、descriptor）以当前目标浏览器证据为准，不得套旧项目固定值

## 常见坑

- 把 TLS reset 当作 JS 补环境问题
- 只看 POST 状态码，不看 `_abck` 是否真实更新
- 复用旧 `_abck / bm_sz / sensor_data`；旧值常与当前脚本、时间、Cookie、IP/TLS 状态绑定，会污染 fresh 会话
- CSC 多段 XHR 只提交最长 body；正确做法是按请求顺序提交每个去重后的 body
- 把 `bmak.get_telemetry()` 当作所有 Akamai 站的固定入口
- 忽略 Header 顺序、Content-Type、Referer、Origin、HTTP/2 和 Cookie 合并细节
- 只生成参数，不验证业务接口是否真正返回正常数据

## 验证口径

- 初始 `_abck / bm_sz` 来自当前会话；脚本来自当前页面、当前版本
- `sensor_data` POST 的 URL、Method、Header、Body 编码与浏览器一致
- challenge POST 覆盖浏览器真实全部 XHR body、顺序、Header 和每次响应后的 Cookie 更新
- 带更新 Cookie 请求业务页面或接口返回正常业务内容；仍返回 challenge、短 HTML、403 或重定向视为未通过
