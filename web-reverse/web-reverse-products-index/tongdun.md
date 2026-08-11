# 同盾 / TrustDecision

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 同盾 / TrustDecision / TrustDeviceJs 指纹链路：fm.js、/web/v2 上报与 black_box 业务落点。

## 命中特征

- 页面加载 TrustDecision 的 fm.js（static.trustdecision.com 或 static.tongdun.net 路径）
- JS 头部、注释或脚本内容出现 `TrustDeviceJs`、`TrustDecision`、`Tongdun`、`tdfp`
- 请求链出现 apitd.net 的 `/web/v2` 上报端点
- 目标字段名出现 `black_box`、`blackBox`、`BlackBox`、`blackbox`、`currentBlackBox`、`tddf`
- 业务 Header、Body 或请求配置中出现 `Anti-Headers.black_box`、`BlackBox`、`blackbox`、`blackBox`
- 初始化配置出现 `window._fmOpt`、`partner`、`appName`、`success`、`error`
- SDK 构造 `Blob`、`URL.createObjectURL`、`Worker`，Worker 分支参与指纹生成
- 上报请求 body 常见表单格式 `data=<payload>`

同页可能同时出现验证码、客服或统计 SDK；先以业务字段和请求链确认目标产品，不要被同页噪声带偏。

## 常见链路

```text
请求页面或业务入口
→ 页面加载 fm.js
→ SDK 读取 BOM/DOM、storage、Worker、canvas 等环境
→ SDK POST data 到 /web/v2
→ 响应 result / requestId，回调或 storage 获得 black_box
→ 业务请求从 sessionStorage / 内存状态取 black_box
→ 写入 Anti-Headers 或业务参数
→ 服务端按 black_box 放行业务接口
```

时序坑：业务首个请求可能早于 SDK 回调或 storage 写入完成，导致 blackBox 为空并返回快速验证失败类错误。验证时要等回调完成再组装业务请求，不要用首个失败包的空值判断算法失败。

## 观察优先级

1. `black_box` 落点按当前 trace 确认：自定义 Header JSON 字段（Anti-Headers.black_box）、独立 Header、JSON body 字段；字段大小写与双落点按业务要求保留
2. 短回调值只能当候选或诊断值；部分业务需要长 `tddf<metadata>.<payload>` 值，payload 来自 SDK 对 /web/v2 发出的真实 data 请求边界，元信息来自当前 trace 的版本、partner 等状态
3. 如果业务从 sessionStorage.currentBlackBox 读取，确认 storage 写入时机、业务注入时机与最终请求上的 Anti-Headers JSON
4. Worker 分支：若 trace 证明 SDK 构造了 Blob 和 object URL，按浏览器外观补 Blob、URL.createObjectURL/revokeObjectURL、Worker 实例、onmessage/postMessage/terminate 与事件派发
5. 同页其它 SDK 流量未流入业务请求的，不成为补环境主线

## 常见坑

- 把同页其它安全 SDK 流量误认为目标产品
- 只拿回调短 black_box，忽略业务实际需要的长值
- 忽略 sessionStorage 写入与业务读取时机；复用首个空 blackBox 失败请求
- 只复现 SDK 入口，不捕获 /web/v2 的 data 请求边界
- 业务请求重建时覆盖航线、日期、channel、Referer、Cookie、原有 Anti-Headers 结构或字段大小写
- 只把值放入 Header 或只放入 Body，漏掉当前业务要求的双落点
- Worker 分支缺失导致 payload 长度、字段或分支不稳定
- 在 SDK 混淆逻辑或 VM/opcode 层插装；只看本地能输出值，不验证业务数据

## 验证口径

- SDK 来自当前页面、当前版本；/web/v2 的 URL、Method、Header、Content-Type、Body 编码与浏览器一致；data payload 来自当前本地运行链而非旧样本
- black_box 写到业务实际读取的位置；业务请求只替换目标字段并保留原业务上下文
- 业务响应返回正常业务数据（status/msg/data），而不是只返回 HTTP 200 或空数据
- 多轮更换会话、业务参数或 SDK 版本后，能定位是业务参数变化还是环境差异
