# 腾讯 TCaptcha 滑块验证码

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 腾讯验证码 TCaptcha / TDC 滑块链路：prehandle 初始化、tdc.js 产出 collect/eks、滑块答案 ans、PoW 与 ticket/randstr 凭证。

## 命中特征

- 页面加载 TCaptcha.js；脚本出现 `new TencentCaptcha(appid, callback, options)`、`captcha.show()`
- 请求链出现 `cap_union_prehandle`、`cap_union_new_verify`
- 初始化响应或脚本中出现 `tdc.js`、`tdc_path`、`window.TDC`、`TDC.setData`、`TDC.getData`、`TDC.getInfo`
- 验证码 iframe 或模板来自 captcha 静态资源域的 drag 模板
- Cookie、storage 或脚本中出现 `TDC_itoken`、`__tdc_st_`
- 题型或脚本出现 `move_slide`、`watermarkMoveSlide`、`DynAnswerType_POS`
- prehandle 响应出现 `comm_captcha_cfg`、`dyn_show_info`、`bg_elem_cfg`、`sprite_url`、`fg_elem_list`、`pow_cfg`、`sess`
- 校验请求体出现 `collect`、`tlg`、`eks`、`sess`、`ans`、`pow_answer`、`pow_calc_time`
- 校验成功响应或页面回调出现 `ticket`、`randstr`

## 核心边界

目标是当前会话可用的验证码通过凭证 `ticket + randstr`，来源是 `cap_union_new_verify` 校验成功后的服务端响应或回调，不是 tdc.js 本地直接生成。它绑定同轮 prehandle 的 `sess`、同轮 live `tdc.js`、同轮 `pow_cfg`、同一浏览器环境/UA/Cookie/storage/TDC token 与题面答案；短时效，拿到后应立即注入原业务回调或业务请求。

## 常见链路

```text
目标页入口
→ 加载 TCaptcha.js → new TencentCaptcha(appid, callback, options) → captcha.show()
→ GET cap_union_prehandle → sess、tdc_path、pow_cfg、dyn_show_info、背景图和滑块小图路径
→ GET 当前轮 tdc.js → 加载拖拽模板或 iframe
→ 下载背景图、sprite 图，解析 fg/bg 配置
→ 识别滑块答案 x/y
→ 执行当前轮 live tdc.js
→ TDC.setData(...) 注入当前轮环境和轨迹上下文
→ TDC.getData(true) 产出 collect → TDC.getInfo().info 产出 eks
→ 按 pow_cfg 计算 pow_answer 和 pow_calc_time
→ POST cap_union_new_verify
→ 返回 errorCode=0、ticket、randstr
→ 回到页面 callback 或原业务接口验证放行
```

## 观察优先级

1. prehandle 字段按轮次整体使用：sess、tdc_path、pow_cfg、dyn_show_info、图片路径；上一轮的 sess/图片/tdc_path/pow_cfg 不混入当前轮
2. collect/tlg/eks：`collect = decodeURIComponent(TDC.getData(true))`，`tlg = collect.length`，`eks = TDC.getInfo().info`
3. UA 一致性：prehandle 的 ua 与 TDC 执行时 UA 一致，否则 collect 无效
4. `ans = [{"elem_id":1,"type":"DynAnswerType_POS","data":"x,y"}]` 形态；x 按背景图与滑块小图匹配，y 按题面小块初始位置/控件坐标；坐标参考系与当前题面配置和模板一致
5. PoW：按当前轮 pow_cfg 枚举 nonce 满足哈希条件，`pow_answer` 来自当前轮配置，记录 `pow_calc_time`，不固定旧值或固定耗时
6. 校验失败优先排查 collect/eks、sess、pow_answer、UA、Cookie/storage、坐标参考系与同轮绑定，不要只反复调识别模型

## 常见坑

- 只解图片不跑 TDC，通常只能得到坐标，不能通过服务端校验
- 固定旧 tdc.js、旧 collect、旧 sess、旧 pow_answer，破坏同轮绑定
- `tlg` 与实际 `collect.length` 不一致
- prehandle 的 UA 与 TDC 执行时 UA 不一致，collect 无效
- ans 坐标参考系错误：sprite 裁剪坐标、背景图缩放和控件偏移混用
- ticket/randstr 短时效，浏览器现场先消费后本地重放可能失败
- 把脚本加载失败时构造的 terror_* 票据当作通过凭证
- 脚本版本、js 路径、tdc_path、模板路径都可能变，必须从当前请求链取 fresh 值

## 验证口径

- 单独验证码目标：`cap_union_new_verify` 返回 `errorCode == "0"` 且带 `ticket/randstr` 作为验证码口径成功
- 业务链目标（登录、下单、活动等）：必须继续验证原业务接口真正放行，不能只看验证码通过
