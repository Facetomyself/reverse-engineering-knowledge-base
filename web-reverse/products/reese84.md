# Reese84（Imperva / Incapsula）

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> Reese84 / Imperva / Incapsula 体系：动态 challenge、p 生成与 84/reese84 放行链路。

## 命中特征

- Cookie、响应体、脚本或日志中出现 `reese84`、`84`、`visid_incap_*`、`incap_ses_*`、`nlbi_*`
- 页面返回 403、短 HTML、iframe block 或 `_Incapsula_Resource` 资源
- 页面动态写入 challenge script src，且 src 每轮可能变化
- challenge POST 通常发往当前动态脚本对应路径，常见带 `?d=<hostname>` 形态
- POST body 中出现 `solution`、`interrogation`、`p`、`st`、`sr`、`cr`、`og`、`performance`、`version`
- 页面中存在 `reese84-resubmit-data` 或类似 resubmit 字段
- challenge POST 返回 200 和 token，但业务页或业务接口仍可能继续被拦截

拿到 `84 / reese84` 不等于业务请求成功，必须继续验证业务页或业务接口是否真正放行。

## 常见链路

```text
请求受保护页面
→ 从页面 HTML 提取本轮动态 challenge src
→ 请求当前 src 对应的 challenge js
→ 在浏览器环境或本地执行层执行当前 challenge js
→ challenge js 通过 fetch / XHR 发出 challenge POST
→ 截获 solution.interrogation.p 等字段
→ 提交本轮 challenge POST
→ 服务端返回 84 / reese84 / 相关 Incapsula Cookie
→ 带当前 Cookie 请求业务页或业务接口
→ 仍进入过渡页时，再分析后续 _Incapsula_Resource、reload 或 resubmit 链
```

同一轮对应关系：当前页面 HTML、当前动态 src、当前 challenge js、当前 challenge POST URL、当前 POST body.p、当前 84/reese84、当前业务请求 Cookie。

## 观察优先级

1. 动态 src 从哪里写入或拼接；challenge js 是否每轮变化，是否存在动态参数
2. challenge POST URL 是否由动态脚本路径推导；POST body 是 JSON、form、文本还是其它格式
3. `p` 是否由 fetch / XHR 边界产出；服务端返回的 token 写入 Cookie、localStorage 还是仅由会话保存
4. token 后是否还有 `_Incapsula_Resource`、reload、resubmit 或二次 POST
5. 环境面：navigator/permissions/plugins/opener/visualViewport、performance、canvas/WebGL/audio、媒体能力；若 p 只在请求边界出现，复现最小 challenge 执行链并在包装入口返回完整 POST body
6. direct 业务请求失败时再考虑 resubmit 或后续过渡资源回放，不要默认先走 resubmit

## 常见坑

- 复用旧 src、旧 challenge js、旧 p 或旧 token
- 把 challenge POST 200 当成最终成功
- 业务页返回 200 但内容仍是 iframe block，却误判为放行
- 手工拼 p，没有让当前动态 JS 自己产出
- POST URL、p、Cookie 不是同一轮运行产物
- challenge 后丢掉服务端新下发的 `visid_incap_* / incap_ses_* / nlbi_*`
- 把一次成功的 Cookie、宽高、语言、canvas、webgl、audio 固定套到新目标
- 过早暴露不完整的 audio/WebGL/canvas 能力，反而改变 p 或降低 token 质量
- 用过死的随机数、时间戳、performance 值推进验证

## 验证口径

- 当前轮动态 src、challenge js、POST URL、POST body 和 token 对应；challenge POST 返回 200 且响应含当前可用的 84/reese84
- Cookie 合并后包含当前服务端新下发的反爬 Cookie
- 业务页不再是 iframe block、短 HTML、验证码页或重定向页；业务接口返回正常业务 JSON，而不是空数据、风控结构或拦截 HTML
- 多轮重新获取动态 src 后仍能稳定生成和验证
