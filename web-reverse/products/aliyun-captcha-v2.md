# 阿里云验证码 v2（callback-proof 状态机）

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 现代 AliyunCaptcha.js 链路：initAliyunCaptcha → InitCaptcha 选轮 → 当轮 sg/FeiLin → callback proof 消费。

## 命中特征

- 页面加载 `AliyunCaptcha.js`，调用 `window.initAliyunCaptcha({...})`
- 初始化配置出现 `SceneId`、`prefix`、`mode`、`element`、`button`、`captchaVerifyCallback`、`getInstance`、`slideStyle`
- 初始化请求含 `Action=InitCaptcha`、`Version`、`SceneId`、`Mode`、`DeviceData`，响应同时出现 `Success`、`CaptchaType`、`StaticPath`、`CertifyId`、`DeviceConfig`
- 当前轮加载 `dynamicJS/sg.<3位>.<16hex>.js` 与 FeiLin 脚本
- 设备链出现 `Action=Log2` / `Action=Log3`，诊断链出现 `Action=UploadLog`
- DOM/运行时出现 `TRACELESS`、`SLIDING`、`startTracelessVerification`、滑块 DOM
- SDK callback proof 包含 `sceneId`、`certifyId`、`deviceToken`、`data`；站点业务请求把原始 proof 包装为 `captchaRequestParam` 类字段

强命中组合：`AliyunCaptcha.js + initAliyunCaptcha`，或 `Action=InitCaptcha + CaptchaType/StaticPath/CertifyId/DeviceConfig`，或 `sg + FeiLin + 四字段 proof`。仅凭单个 StaticPath、AWSC、acw_tc 或 Log3 只能算弱线索。

## 常见链路

```text
业务触发
→ initAliyunCaptcha 或页面 requestInfo
→ 发 InitCaptcha
→ 记录本轮 CertifyId / StaticPath / DeviceConfig / CaptchaType
→ 按 StaticPath 精确加载当轮 dynamicJS/sg，加载当轮 FeiLin
→ 同一执行 realm 运行 bootstrap / FeiLin / sg
→ 生成行为材料、DeviceToken、Data
→ Log2 / UploadLog / Log3
→ 进入校验出口：direct verify（Result 明确通过）或 callback proof（业务消费）
```

`StaticPath` 是服务端为本轮请求选择的精确动态脚本路径，不是版本号递增序列；`sg.042` 之后可以出现 `sg.001`。必须按本轮响应拼出精确 URL 并真实加载，禁止按编号选择"最新"或复用上一轮资源。FeiLin 与 sg 的网络下载可能并行，逻辑关系由同一个成功 InitCaptcha 响应选中，不要用毫秒先后硬编码依赖。

## 观察优先级

1. 每轮只从成功的 InitCaptcha 响应创建 round，记录 URL、bytes、hash 与会话材料（page/session/cookie/IP/UA/TLS/time）
2. 区分请求角色：InitCaptcha 只证明 init；FeiLin/sg 只证明资源取得；Log2/Log3/UploadLog 不能证明验证码通过；callback 只证明派发；业务接口才是最终判据
3. SLIDING 交互顺序：slider mousedown → document mousemove → document mouseup → 业务按钮 click → Log3/proof；mouseup 本身不一定提交 proof
4. proof 的 `sceneId/certifyId/deviceToken/data` 必须全部来自同一轮；成功后 refresh 的新 InitCaptcha 属于下一轮，禁止混入旧轮材料
5. 动态 sg 与 DeviceConfig 属验证码 runtime/配置，不是站点业务加密 JS；只有独立站点载荷加解密证据才登记第二层动态脚本
6. 外层对象存在 `startTracelessVerification` 不代表当前子实例支持无感入口，按本轮 CaptchaType、实例方法与 DOM 三者一致判断

## 常见坑

- 把 StaticPath 变化描述成升级或选最大编号；固定 trace 的 sg
- 混用不同轮的 CertifyId/StaticPath/DeviceConfig/sg/deviceToken/data/proof
- 独立运行 sg 后伪造缺失的共享全局能力（如 __ALIYUN_CRYPT.AES 类）；这是加载拓扑错误，不是要补的能力
- 用 opaque innerHTML 或验证码 ID 特判代替真实 DOM 树；动态脚本会立即按 ID/class/tag 查询并绑定事件
- 让未设置 CSS 属性返回 undefined（浏览器返回空字符串），动态分支会直接 slice 这类值
- 看到 `Network Error` 直接归因远端网络；loader 可能把脚本调度内部异常转写为网络失败
- 只发 mouseup 不执行 move 与业务按钮 click；复用失败轮 proof；对明确业务响应重发 guarded action

## 验证口径

最低验收同时满足：成功 InitCaptcha 被识别；当轮 StaticPath 的精确 dynamicJS 加载并记录 hash；FeiLin 与 sg 在同一共享执行环境完成；getInstance 或等价 runtime_ready 门禁通过；按当前 CaptchaType 进入真实交互；proof 四字段同轮；业务接口返回明确成功码和目标状态。callback 返回 `captchaResult:true` 与 SDK 成功 UI 均不能单独作为成功口径。至少执行多轮 fresh InitCaptcha，验证不同动态分支不依赖固定 sg。
