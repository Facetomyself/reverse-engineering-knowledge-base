# 京东 JCAP 滑块专项（tp=30 滑块 / tp=26 旋转）

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 京东 PC 登录 JCAP 滑块的专项补充：tp=30 滑块与 tp=26 旋转题型的视觉答案、轨迹 proof、同轮状态与在线成功判定。

## 命中特征

- 与 JCAP 基础特征相同：`/cgi-bin/api/fp` 与 `/cgi-bin/api/check`；`window.jdCAP`、`jdCAP.captcha`、`requireCaptchaPc.js`
- `/api/check` 题面响应含 `tp=30`、`img.b1`（背景大图）、`img.b2`（滑块小图）
- 题面或源码中出现 `tp=26`、`rotate_img`、`drag_box`、`slider`、`slide_path`
- proof 对象中出现 `ht/wt/bw/sw/mw/list/ii` 或 `bw/sw/track/list/ii`
- 提交失败返回 `code=16807`、`s_code=16130`、`msg=验证失败，请重新验证`
- 任务是判断动态生成是否成立，而不是只重放成功样本
- 2026-08-22 `passport.jd.com/uc/login` 交互轮未稳定下发 `tp=30`：同轮 JCAP 为 `tp=22`（空间推理）与 `fp tp=9`。本专项只覆盖滑块/旋转；空间推理不得套用 tp=30 轨迹模板，见 [jd-jcap-spatial.md](jd-jcap-spatial.md)

## 成功判定

真实成功只看当前在线第二次 `/api/check`：`response.code == 0` 且 `vt` 非空。以下现象均不能单独当成功：本地执行能跑完、本地 fixture 能生成请求、/api/fp 返回 code=0、题面阶段 check 返回 code=0、证明长度接近样本、响应字段或 body 长度与样本相似。历史样本的 code=0/vt 只证明当时浏览器链路成功。

## 常见链路

```text
window.jdCAP.captcha(info)
→ captchaFactory(option)
→ instance.create(createOption)
→ DOM 渲染题面与滑块/旋转组件
→ 派发 mousedown / mousemove / mouseup
→ 内部生成 proof
→ XHR/fetch 边界收集 /api/check
```

同轮状态强绑定：sessionId、jwtToken、cookie jar、fp 响应、challenge st、challenge img、answer proof、vt。常见失败原因：sessionId/jwtToken 旧、st 来自上一轮题面、题面图片与 answer proof 不是同一轮、vt 已被消费、执行环境拆分导致 instance 内部 records/fpt 状态断裂。

## 观察优先级

1. tp=30：保存 b1/b2 → 人眼或 PIL/视觉确认 offset → 生成轨迹并触发真实 drag → 抓 proof（ht/wt/bw/sw/mw/list/ii）→ 第二次 /api/check
2. tp=26：视觉 API 返回的角度必须确认是"顺时针校正角"而非"当前偏转角"；换算 `angle = offset / max_offset * 360`，offset 需 clamp 到轨道范围；线性或平滑旋转轨迹更符合组件
3. 轨道参数按题型区分：tp=30 与 tp=26 的 trackWidth 不同，轨迹模板不互相套用
4. DOM layout 影响 proof：slider.clientWidth、drag_box.clientWidth、getBoundingClientRect、event.clientX/Y 须给目标链路触达的元素合理 layout
5. 视觉 API 只负责图片层答案，不负责 token、cookie、session、ct/tk/cs、proof 结构、事件轨迹与业务放行
6. 失败 16807 先核对 offset/angle、轨迹形态、证明输入与同轮状态，再考虑环境问题

## 常见坑

- 用样本的 code=0/vt 当本地成功，而不是重新在线提交
- 只做到 check_challenge code=0 就停止
- 固定旧题面与旧 st，却宣称动态通过
- tp=30 的轨道宽度、轨迹模板套到 tp=26
- 视觉返回角度后未区分当前角与校正角；tp=30 已稳定时强行改视觉造成偏移误差
- split runtime 导致 instance 内部状态断裂
- 看到 16807 先补环境，而不是先核对 offset、proof、同轮状态

## 验证口径

- 在线第二次 /api/check code=0 且 vt 非空；成功判定来自当前在线响应而非样本
- 未采到 fresh 题面（如 tp=26 未自然下发）时，明确记录"未采到 fresh 题面"或具体失败响应，不宣称在线通过；只能验证轨迹产参路径
- 调试抓取只在外围序列化层（JSON.stringify 包装）确认 proof 形状，不进入 VMP/opcode
