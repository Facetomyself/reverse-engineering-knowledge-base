# 网易易盾行为式验证码（Web jigsaw / NECaptcha）

> 来源: netease-yidun-jigsaw-v2285（trial 页 live compact-replay）
> 原始发布时间: 2026-08-27
> 归档日期: 2026-08-27
> 分类: web-reverse
>
> 网易易盾 Web 行为式验证码（NECaptcha / dun.163.com）：getconf → get → 题面 → check → validate。
> 以 SDK 2.28.5 滑块 `type=2` 为实证主链，整理风控分层、纯算方法论、缺口与 token 生命周期。
> 不要和 App 侧 NES 加固（`libnesec` / `libpoison`）混成同一个产品面。

## 命中特征

- 脚本、页面或网络出现 `c.dun.163.com`、`dun.163.com`、`necaptcha.nosdn.127.net`、`necaptcha-nosdn.126.net`
- 请求 `GET /api/v2/getconf`、`GET /api/v3/get`、`GET /api/v3/check`，响应是 JSONP（`__JSONP_<rand>_0({...})`）
- 查询参数出现 `captchaId` / `id`、`fp`、`cb`、`dt`、`irToken`、`version`、`loadVersion`、`runEnv`、`iv`、`type`、`width`
- 窗口或 SDK 出现 `window.gdxidpyhxde`（fp 产物）、`core-optimi`、`watchman`、`NECaptcha`
- get 响应含 `token`、`bg[]`、`front[]`、`type`、`waitTime`、`zoneId`
- check 的 `data` 是 JSON 字符串，字段为 `d`、`m`、`p`、`f`、`ext`
- 成功响应 `data.result === true` 且 `validate` 非空；失败常见 `result === false` 且 `validate=""`；形态错误常见 `error=100` / `param check error`
- 滑块题：`type=2`，背景 JPG + 带 alpha 的拼图 PNG，widget 宽度常见 320
- 业务回传字段名常见 `validate` / `NECaptchaValidate`；站点还有二次校验（服务端拿 validate 再问易盾）

同时出现 `libnesec.so`、`libpoison.so`、`com.netease.nis.wrapper.MyApplication` 时，那是 **App 加固/反调试面**，不是本 Web captcha 链。App 面见泡泡以安网易云音乐易盾实战，不要把 Web `validate` 方法论套到 native 壳。

## 产品分层（不要混面）

| 面 | 典型标记 | 本文件职责 |
|----|----------|------------|
| Web 行为式验证码 | `c.dun.163.com/api/v3/*`、`validate` | 主文：题面、轨迹 proof、check 放行 |
| Web 设备/反作弊辅助 | `getconf.ac`、`ir`、`watchman`、`acToken` | 只记录同轮绑定；未实证前不要写成 check 必填 |
| App NES 加固 | `libnesec`、`libpoison`、wrapper Application | **不是**本文；走 native-reverse / packing-bypass |

一个站点可以同时接 Web 验证码和 App 加固。命中后在账本写清当前任务是哪一面，禁止用 App 反调试结论指导 Web 滑块，也禁止用滑块 `validate` 宣称 App 已绕过。

## 核心边界

目标凭证是 check 成功下发的 **`validate` 字符串**，不是 get 的 `token`，不是缺口像素 `x`，也不是本地拼出来的 `data`。

`validate` 绑定：

- 同轮 `token`（get 下发，check 一次性消费）
- 同轮题面（`bg` / `front`）与提交的位移 `p`、轨迹 `d`/`f`
- 同轮 `dt`（getconf）以及当前 UA / Referer / Cookie jar
- 短时效；浏览器或业务后端消费后本地重放常失败

`dumped` ≠ `unpacked` 的 App 纪律在这里对应：

```text
get 200 + 非空 token     ≠ 已通过
check HTTP 200           ≠ 已通过
data.result === false    = 协议形态过了、风控/答案未过
data.result === true
  且 validate 非空       = 验证码口径通过
业务接口真正放行         = serverAccepted（站点二次校验之后）
```

trial 页（`dun.163.com/trial/jigsaw`）只能证明验证码口径。接进登录/下单时，必须看业务 readback，不能把 trial 的 `validate` 当业务成功。

## 风控分层

易盾滑块不是「识别缺口就过」。服务端至少叠了下面几层，失败时先定性是哪一层，再改那一层。

| 层 | 看什么 | 典型失败 | 不要做什么 |
|----|--------|----------|------------|
| 0 协议形态 | JSONP 能解析、`error=0`、字段齐 | `error=100` param check error | 不要当轨迹问题去调缺口 |
| 1 题面答案 | 位移 `x`、百分比 `p` 与洞对齐 | 洞偏了仍 `result=false` | 不要在同一 token 上扫 ±1..±4 |
| 2 行为 proof | 轨迹点、47 维特征 `f`、`ext` 的按下次数/点数 | 坐标对仍被拒 | 不要用一条折线或恒定速度硬顶 |
| 3 会话/指纹 | `fp`、`dt`、UA、Cookie、Referer | get 过、check 系统性假 | 不要 get 用一套 UA、check 换一套 |
| 4 提交节奏 | 从 get 到 check 的墙钟 vs 轨迹时长；token 只 check 一次 | 报 2.9s 拖拽却 200ms 就提交 | 不要把偏移扫描当「提高精度」 |
| 5 业务二次校验 | 站点后端拿 `validate` 再问易盾 | 验证码 true、业务仍拒 | 不要只停在 check |

经验规则：无感通过是环境 + IP + 行为的联合得分，**不能把「IP 好/坏」当成单一归因**。trial 页 IP 干净也仍有概率 `result=false`。可复用策略是 **换新 token 再来一轮**，不是在死 token 上打补丁。

2026-08-27 trial `type=2` / SDK `2.28.5` 单变量事实：

- get **必须**带 `fp`；check **不要**带 `fp`。把 get 的 fp 原样塞进 check query，会得到 `result=false`。
- dummy fp（环境项全 0、`ec=1`）可以被 get 接受，不证明设备指纹已还原。
- `dt` 来自 getconf，check 带着走。
- 同一 token 失败后再用 ±1..±4 重放，既像机器，也浪费唯一提交机会。

## 常见链路

SDK 2.28.5 滑块（`type=2`，widget 宽 320）：

```text
打开业务页或 trial 页（建议先 GET 页面拿 Cookie）
→ GET /api/v2/getconf?id=<captchaId>&referer=...
   → dt、zoneId、ac、ir、imageServer
→ 本地生成 fp、cb
→ GET /api/v3/get  (fp, cb, dt, id, type=2, version, width=320, runEnv, iv, callback)
   → JSONP { token, bg[], front[], type, waitTime, zoneId }
→ 下载 bg[0]（JPG 背景，洞已挖空）和 front[0]（PNG 拼图块，含 alpha）
→ 视觉得到洞的 left 像素 x（显示宽度 320；图已是 320 则 scale=1）
→ 生成拖拽轨迹 [(x,y,t,flag)]，末点落在目标 x
→ xor_encode(token, ...) 后再走自定义 AES，拼 data = {d,m,p,f,ext}
→ 等到 max(waitTime, 轨迹时长) 再提交
→ GET /api/v3/check (token, data, dt, cb, width, type, version；不要 fp)
   → JSONP data.result + validate
→ 把 validate 交给业务回调 / 业务接口；站点后端做二次校验
```

`bg` / `front` 常给两个 CDN 主机、同一对象。内容相同，不要当成 2x 图。2026-08-27 trial 实测背景 `(160, 320)`、拼图块 alpha 裁切后约 `55x55`。

`type` 由 captcha 配置决定，不要写死滑块。未采到的智能无感、点选、短信题型标 `runtime-pending`，不得套用 jigsaw 的 `data` 五字段。

## 方法论

### 1. 先命中产品，再取证

出现上一节特征时，必须命中本文，不要当「未知安全产品」继续猜。命中后在 `analysis-progress.md` 写：同类特征、本文路径、当前 SDK `version` / `loadVersion`。

常量、字母表、SBOX、seed、`cb` 插位都跟 SDK 版本绑定。一份 2.28.5 通过，不代表 2.25.x 或未来小版本还能用。换版本先对 `fp`/`cb`/`data` 做 fixture，再 live。

### 2. 能纯算就不要补整页

满足下面条件才走纯算（`purecalc-loop`）：

- 请求边界已对齐：URL / method / JSONP / 字段名与浏览器一致
- 变换可读：fp 编码、xor、自定义 AES、47 维特征都能写成无 DOM 的函数
- 不读现场 canvas 像素、不读 `crypto.subtle`、不依赖活 Worker
- 缺口 `x` 来自题面图，不是来自浏览器鼠标事件

看见「轨迹 / isTrusted / 行为特征」不要立刻判无法纯算。它们是外部宿主面的**产物**；能按同轮 token 本地再生 proof，就继续纯算。只有 M4 穷尽证明还要 C++ 内部状态时，才升补环境或自动化。

### 3. 单变量实验，不要堆参数

一次只改一项，用新 token 对照：

| 实验 | 用来区分 |
|------|----------|
| 只改缺口 x，轨迹模板不动 | 层 1 题面 |
| x 固定，只改轨迹时长/点数 | 层 2 行为 |
| 协议字段增删（check 是否带 fp） | 层 0/3 |
| 同一 token 二次 check vs 新 get | 层 4 token 生命周期 |
| trial 通过后的业务接口 | 层 5 二次校验 |

禁止把「多扫几个偏移 + 换 UA + 加 sleep」一次打出去。那种日志无法归因。

### 4. 同轮绑定

下面这些必须来自同一轮 get，禁止混轮：

- `token`、`bg`、`front`、`waitTime`
- 由该 `token` xor 出来的 `d/p/f/ext`
- 该轮算出来的 `x` 与 `p`（`int(x)/width*100`）
- 该轮 `dt`

`fp` 在 get 上是设备身份，可以在短会话内复用；**不要**把它写进 check query（2.28.5 trial 实证）。

## 观察优先级

1. 先看 check 的 `error` 与 `result`，把层 0 和层 1+ 分开。
2. 锁 SDK：`version`、`loadVersion`、`iv`、`runEnv`、`type`、`width` 以当前 get 为准。
3. 图：用 `bg[0]`/`front[0]` 的真实宽高算 scale；`x_submit = x_pixel * (widget_width / bg_width)`。trial 2.28.5 常见 320×160，scale=1。
4. 缺口算法：拼图 PNG 是**原图像素 + alpha**，背景 JPG 的洞是**挖空轮廓**。用 Canny/轮廓去对洞，不要用灰度纹理去对原图内容。灰度高峰经常贴在滑块起点左侧。
5. `data` 五字段：`d` 采样轨迹，`p` 位移百分比，`f` 47 维特征，`ext` 为 `mouseDown次数,轨迹点数`，`m` 在 2.28.5 trial 可为空。先 xor(token, 明文) 再自定义 AES。
6. 轨迹末点必须落在目标 `x`；时间戳严格递增，避免除零把特征打成 `NaN`/`Infinity` 过多。
7. 墙钟等待 ≥ `max(waitTime, 轨迹最后 t)`，再发 check。
8. 失败后 **get 新题**。不要对死 token 做偏移扫描。
9. 业务链：`validate` 注入后看业务 readback，而不是只看 check。

## 技巧与细节

### 缺口：对洞，不对纹理

背景已经把洞挖掉。拼图块带的是洞里原来的像素。因此：

- `matchTemplate` 灰度 + mask 会在图左、纹理相似处给出 0.85+ 的假高峰
- Canny 对的是拼图外形和洞外形，分数可以低到 0.2~0.4，但位置才是洞
- 搜索区至少跳过一块宽度（洞不会出现在滑轨起点）
- Canny 与灰度 loc 相差 ≤4px 时，才用灰度做亚像素
- 拼图 PNG 含大片半透明阴影，先按 alpha 裁切再匹配

widget 宽与图片宽不一致时必须缩放。不要把 480 宽原图像素直接当 320 宽位移。

### `data` 字段

| 字段 | 明文大意 | 编码 |
|------|----------|------|
| `d` | 采样后的轨迹点 `x,y,t,flag`，用 `:` 拼接 | xor(token) → 自定义 AES |
| `m` | 拖拽前鼠标移动；2.28.5 trial 可空 | 同上 |
| `p` | `int(x)/width*100` 的字符串 | 同上 |
| `f` | 47 维：位移/速度/加速度的 min/max/mean/std/unique/p25/p75 | 同上 |
| `ext` | `mouse_down_counts,trace_len` | 同上 |

自定义 AES **不是**标准 AES-CBC。字母表、pad、round、sbox 都是 SDK 私有表，跟版本走。fixture 要冻 Python/JS 对齐，不要拿标准库 AES 去碰。

`cb` 是另一条同样的 AES：32 位随机串，在固定下标插入短码（2.28.5 为 `vfnv46`）。get 和 check 各生成一次，不要复用。

### fp

fp 是自定义 base64 链，载荷含 `v/fp/u/h/ec` 等。环境向量可以降级成全 0，get 仍接受。这只说明 **get 的协议门不严**，不说明指纹层已关闭。不要把 dummy fp 写成「已还原设备指纹」。

`u` 里带时间戳；整串末尾 `:<ts>`。跨太久的 fp 不要当长期身份。

### token 生命周期

- get 一次，check 一次。`result=false` 之后这个 token 按作废处理
- 可复用入口是 `solve(max_attempts=N)`：每次独立 getconf/get/算洞/check
- 首枪不是 100%。2026-08-27 trial 上，独立新题重试在第 2 轮拿到 `result=true`；首枪抽样会明显更低
- 不要用「扫偏移提高识别精度」掩盖行为层拒绝

### JSONP 与 HTTP

- 响应永远按 JSONP 剥最外层 `{...}`，不要 `response.json()`，不要截断 500 字符
- `requests` 会把 query 里的 `+` `/` 百分号编码，服务端按 query 解码即可
- 全程同一 `Session`、同一 UA、同一 Referer。get 用 Edge UA、check 用裸 Chrome UA 是额外指纹裂缝
- 先 GET 业务页或 trial 页再打 getconf，有助于带上站点 Cookie

### 轨迹形态

真人拖拽常见：加速、过冲、回撤、y 轴有弯曲、末段变慢。模板可以来自一次真实采集，但：

- 末点 x 必须等于提交的 x
- t 严格递增
- 点数随位移变，不要固定 50 个物理点再硬采样；`d` 侧再采样到约 50
- 墙钟耗时不要远短于轨迹自报时长

## 常见坑

- 把 get 的 `token` 或非空 HTTP 200 当通过
- 灰度模板匹配当缺口，洞在右侧却提交 x≈40
- 图片 2x / widget 320 不缩放
- 标准 AES 替换自定义 AES；字母表、pad 抄错
- check 带 `fp`、漏 `dt`、UA/Referer 来回切
- 同一 token 扫 ±1..±4
- 轨迹有重复时间戳，47 维出现大量 NaN
- 把 trial 的 `validate` 当任意站点的业务放行
- 把 Web captcha 结论套到 App `libnesec` 反调试
- 跨 SDK 版本复用 seed、字母表、`cb` 插位
- 把 `watchman` / `acToken` 写成 check 必填，但当前目标 getconf 虽下发 `ac.enable=1`、live 仍能在无 acToken 时通过——以当前目标实测为准，不要把「有字段」升级成「无则必挂」

## 验证口径

验证码口径（单独 captcha 目标，例如 trial 页）：

1. getconf 能取出 `dt`
2. get JSONP `error=0` 且 `token`、`bg[0]`、`front[0]` 非空
3. 缺口 loc 与题面洞一致（Canny 与洞外形对齐，或与灰度在 4px 内同意）
4. check JSONP `error=0` **且** `data.result === true` **且** `validate` 长度明显非空（trial 实证约 170+ 字符）
5. 失败轮不得复用该 token

业务口径（登录/下单/采集）：

- 同会话立刻把 `validate` 注入业务回调或表单
- 业务接口越过验证码参数错误，返回业务层结果（账号错误、数据体、下一步挑战）
- 只有这一步才能写 `serverAccepted`

## 版本材料

| 项 | 2026-08-27 trial 实证 |
|----|------------------------|
| 产品 | 网易易盾 NECaptcha / 行为式验证码 |
| SDK | `version=2.28.5`，`loadVersion=2.5.4`，`iv=4`，`runEnv=10` |
| 题型 | `type=2` jigsaw，`width=320`，背景 320×160 |
| 烟囱目标 | 官方试用页 `https://dun.163.com/trial/jigsaw`（只做验证码口径，captchaId 以页面为准，不跨站复用） |
| 落地 | 纯算 compact-replay；workspace `netease-yidun-jigsaw-v2285` |
| 未覆盖 | 智能无感、点选、短信、acToken/watchman 强制路径、站点二次校验差异 |

换站点时只替换 `id`（captchaId）和 `referer`。算法表仍按该站实际 SDK 版本重新对 fixture，不要把 trial 的 captchaId 写进其它站。
