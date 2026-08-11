# 瑞数 RS6

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 瑞数 RS6 / RuiShu 类动态防护链路：页面 challenge、长 cookie、行为/环境采集与业务请求动态后缀组成的混合链。

## 命中特征

- 页面首屏或业务页返回 challenge HTML，包含动态 meta content、内联 script 和外链自动化 JS
- 页面或脚本出现 `$_ts`、`$_ts.nsd`、`$_ts.cd`、`$_ts.lcd`
- 脚本通过 document.cookie 写入长 cookie，cookie 名和值每站点或每轮可能变化
- 业务接口需要额外动态 query 参数，且参数由 JS 请求边界或 XHR/fetch 包装生成
- 脚本注册或采集 mousemove、scroll、mousedown、mouseup、mouseenter、mouseleave、click 等行为事件
- 同一流程出现两阶段或多阶段 challenge：入口页先下发 cookie，业务页再下发 cookie 或业务请求动态参数
- API 请求前需要刷新 challenge cookie，否则同样的业务 URL 会失败、返回空数据、重定向或重新进入 challenge

## 目标类型判定

```text
只恢复业务动态 query / 请求后缀 = signature，但必须保留前置 cookie challenge
恢复 cookie challenge + 业务动态 query = hybrid
从入口页、业务页、cookie 刷新一路跑到最终业务 API = full_flow
只处理入口页能否放行 = challenge 类前置防护，不要误判为最终业务成功
```

RS6 很容易被误判为"只有一个签名参数"。业务 API 前仍需刷新 cookie，或动态 query 与 cookie 必须同轮生成时，按 hybrid 或 full_flow 推进。

## 常见链路

```text
入口页 → 解析 meta content → 解析内联 ts_js → 拉取外链 auto_js
→ 执行首阶段 challenge → 生成并写入 RS cookie

业务页 → 同样的解析与执行流程 → 写入第二阶段 RS cookie

每次业务 API 请求前
→ 重新生成 challenge cookie
→ 在 XHR.open / fetch 边界生成动态 query 参数（输入含 method + 完整 URL + 原始 query）
→ 用同一 session / cookie jar 请求真实业务 API
```

动态参数只在 XHR/fetch 边界出现时，不要强行寻找单独返回参数的内部函数；保留最小请求边界包装，让目标 JS 自己走到边界，再返回完整动态 query 或请求片段。

## 观察优先级

1. meta content 定位不固定 XPath，按当前 HTML 和 trace 定位；meta content 可能经 window 全局别名读取，需要同步映射
2. `document.currentScript.src` 必须跟随当前轮外链脚本，不硬编码历史路径
3. 挑战阶段只生成并回填 cookie，不要提前触发业务 XHR 后缀（会污染同轮状态）
4. 真实会话中站点首页类请求可能负责建立后续页面需要的服务端会话 cookie，不能省略；只拿到挑战 cookie 直接重试原 URL 常见 400 空体
5. 动态 query 输入必须含 method + 完整 URL（含 path 与原始 query），多个业务 API 各自生成
6. 行为事件是否参与校验按当前 trace 判断；cookie/参数长度与浏览器样本差异大时，把事件轨迹差异列为重点排查项
7. 服务端 cookie 与 JS 生成 cookie 合并，注意 Domain/Path；登录态/业务会话 cookie 与 RS cookie 区分

## 常见坑

- 把 RS6 当普通签名，只恢复动态 query，漏掉 challenge cookie
- 只跑入口页 challenge，漏掉业务页第二阶段 challenge
- 固定旧 meta content、旧 auto_js、旧 cookie 名或旧 cookie 值
- API 前不刷新 cookie，导致动态参数和 cookie 不同轮
- 动态参数只传 path，不传完整 URL 和原始 query
- 多个业务 API 共用一个旧后缀
- 用浏览器现场先消费的 cookie/参数再本地重放
- 忽略业务登录态 cookie，把会话失败误判成 RS6 失败

## 验证口径

- 入口页与业务页各阶段 cookie 生成；API 前刷新同轮 cookie；动态 query 与 cookie 同一轮
- 业务请求使用同一个 session/cookie jar；业务响应是正常业务 JSON/页面内容，不是 challenge HTML、空数据、重定向或风控错误
- 多轮重新拉页面、重新拉动态脚本后仍能稳定复现；只复现样本固定 cookie 或固定后缀不能视为完成
