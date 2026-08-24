# 京东 JCAP 空间推理（tp=22）

> 来源: reverse_ENV 实测（`jd-slider-v1`）
> 原始发布时间: 2026-08-22
> 归档日期: 2026-08-22
> 分类: web-reverse
>
> 京东 PC 登录 JCAP 的空间推理题型。服务端用 `tp=22` 下发题面，与滑块 `tp=30` / 旋转 `tp=26` 不是同一条交互链。

## 命中特征

- 登录页仍加载 `requireCaptchaPc.js`、`jcap_*.js`，甚至 `jdSlide*.js`
- `POST /cgi-bin/api/fp` 返回 `code=0` 且 `tp=9`（指纹阶段，不是题面）
- `POST /cgi-bin/api/check` 与 `/cgi-bin/api/refresh` 返回 `code=0` 且 `tp=22`
- 同轮没有 `vt`；滑块成功口径（第二次 check `code=0` 且 `vt` 非空）不成立
- 操作者看到的是空间推理题，而不是可拖动滑块
- **有 Slide 脚本 ≠ 本题是滑块**；题型只看当前 `tp`

2026-08-22 `passport.jd.com/uc/login` 一轮：fp ×3 为 `tp=9`；check ×3、refresh ×1 为 `tp=22`；全程无 `vt`。证据 run `rt_20260822110405_3d8001ac4e`（receipt pass）。题面语义依人机观察，网络边界依 `tp`。

## 常见链路

```text
登录页加载 JCAP 脚本栈
→ POST /api/fp → st/fp，tp=9
→ 题面阶段 /api/check 或 /api/refresh → tp=22（空间推理）
→ 人机完成空间推理
→ 答题阶段 /api/check → 成功才有 vt
→ vt 注入登录提交（同时仍要 h5st）
```

`code=0` 在题面阶段只表示服务端下发了题，不等于验证通过。

## 观察优先级

1. 先记 `tp`，再决定走滑块专项还是本题型；不要用脚本文件名分流
2. `st`、sessionId、jwtToken、Cookie 仍同轮绑定；空间推理的答案/proof 字段以当前 check 请求体为准，不得套 `tp=30` 的 A/touchList 或 `ht/wt/bw/sw` 轨迹模板
3. 无 `vt` 时不要做 Node 滑块补环境，也不要把课程历史 `code.js` 当运行输入
4. 题面图、选项坐标、交互 DOM 文案若要复现，另开 case 取 DOM/img 证据；本篇只锁定题型分流

## 常见坑

- 把 `jdSlide` / `requireCaptchaPc` 当成滑块已出
- 把 fp 的 `tp=9` 或题面 check 的 `code=0` 当成验证通过
- 对 `tp=22` 套用滑块 offset、touchList、轨迹 proof
- 登录滑块不稳定时仍卡在滑块 demo，不改走业务签名（h5st）等不依赖登录验证码的页面

## 验证口径

- 网络：当前轮 check/refresh 的 `tp` 与是否出现 `vt`
- 人机：题面是空间推理还是滑块/旋转，必须写清，且不得与 `tp` 矛盾
- 成功：答题 check `code=0` 且 `vt` 非空，再注入登录；未拿到 `vt` 只能标 triage
- 滑块专项见 [jd-jcap-slider.md](jd-jcap-slider.md)；JCAP 总览见 [jd-jcap-captcha.md](jd-jcap-captcha.md)
