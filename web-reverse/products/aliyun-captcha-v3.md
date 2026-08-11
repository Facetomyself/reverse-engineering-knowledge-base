# 阿里云验证码 V3（direct-verify / CHECK_BOX）

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 现代 Aliyun Captcha V3 的 direct-verify 分支：Log1/DeviceConfig → FeiLin → Log2 → InitCaptchaV3 → dynamicJS/cx → VerifyCaptchaV3 → captchaVerifyParam。

## 命中特征

- 页面加载 `AliyunCaptcha.js`，调用 `initAliyunCaptcha`
- 设备接口出现 `Action=Log1`，响应含 `ResultObject.DeviceConfig`
- 当前轮加载 FeiLin 脚本，随后出现 `Action=Log2`
- 初始化请求出现 `Action=InitCaptchaV3`，成功响应含 `CaptchaType=CHECK_BOX`、`StaticPath`、`CertifyId`
- 当前轮加载 `dynamicJS/cx.<digits>.<hash>.js`
- 诊断/设备链出现 `Action=UploadLog`、`Action=Log3`；校验请求 `Action=VerifyCaptchaV3`
- 校验响应含 `Success`、`VerifyResult`、`VerifyCode`；SDK 成功边界产生非空 `captchaVerifyParam`

强匹配建议满足 `Log1 + DeviceConfig + InitCaptchaV3 + dynamicJS/cx + VerifyCaptchaV3`。只看到 AliyunCaptcha.js、DeviceConfig、FeiLin 或 StaticPath 不能区分 v2/v3，必须继续看 Action 名、动态脚本文件族和最终校验形态。

## 常见链路

```text
页面/业务触发
→ 静态 AliyunCaptcha.js bootstrap → Log1
→ 从本轮成功 Log1.ResultObject.DeviceConfig 派生 FeiLin URL → GET fresh FeiLin → Log2
→ InitCaptchaV3 → 从本轮成功响应 StaticPath 派生 dynamicJS/cx URL → GET fresh cx
→ getInstance / runtime_ready → CHECK_BOX 行为事件 → UploadLog / Log3
→ VerifyCaptchaV3 → 服务端 VerifyResult/VerifyCode
→ SDK 生成 captchaVerifyParam → 站点业务消费
```

三类脚本角色必须区分：静态 loader（AliyunCaptcha.js）、fresh FeiLin（URL 由当前 attempt 的 Log1 派生）、fresh business-stage dynamicJS/cx（URL 由当前 attempt 的 InitCaptchaV3.StaticPath 派生）。DeviceConfig 是配置材料不是源码；dynamicJS/cx 是验证码业务阶段 runtime，不等于站点自己的业务加密 JS。

## 观察优先级

1. 每个 attempt 重新读取 fresh 响应并派生 exact URL；URL 重复不等于跨轮复用，URL 不同也不等于 SDK 升级（编号可前后跳变）
2. 同一 attempt 内保持同一规范 HTTP 会话、Cookie、UA/TLS/IP 与同一执行 realm；不要分进程拆开 FeiLin 与 cx
3. 请求角色分层记录：Log1 只证明设备配置选择，FeiLin/cx GET 只证明资源，Log2/UploadLog/Log3 不证明挑战通过，Verify 才进入校验层
4. CHECK_BOX 行为契约：pointermove+mousemove → pointerdown → mousedown → focusout → pointerup → mouseup → click；瞬时 down/up/click 不足，行为材料会进入 Verify
5. 传输与重试分层：fresh URL 已产生但 GET timeout 属资源 transport；脚本已加载、交互已派发、Verify 返回 false 才进入行为 proof 归因；Verify/业务不能按资源重试逻辑盲发
6. 顶层重试必须创建 fresh challenge；失败轮的 proof、CertifyId、StaticPath、captchaVerifyParam 不得重放

## 常见坑

- 把 dynamicJS/cx 编号变化称为升级或选择最大编号；把静态 loader 算进"两份动态 JS"
- 固定上一轮 FeiLin/cx 作为 live 正式资源；动态 GET 不应把上一轮源码当正式运行输入
- 分进程独立运行 FeiLin 与 cx，伪造缺失共享全局
- 串行代理所有 XHR，制造浏览器不存在的假 timeout
- 用主 realm 别名伪造 iframe child realm；用 opaque innerHTML 或 ID 特判代替 DOM 树
- 看到 loader `Network Error` 继续补 DOM/BOM；应先展开原始 script runtime error 与 transport error
- 把 fixture 成功、fallback callback 或 Verify 请求已发出当通过；对未经证实的成功码写官方语义
- N/N 验收把失败轮移出分母或用补跑替换

## 验证口径

分层状态：`chain_replayed`（fixture 路由可执行）→ `runtime_ready`（两份 fresh 动态脚本 loaded）→ `interaction_dispatched`（本轮独立事件 profile 已执行）→ `challenge_verified`（2xx Verify、Success=true、VerifyResult=true、当前目标接受的成功码、非空 captchaVerifyParam）→ `business_released`（业务接口明确成功码与目标状态）。具体成功码以当前目标证据为准，不写成通用常量。连续多轮验收：每轮独立进程与 fresh 材料，失败计分母，interaction profile 不跨轮完全相同，全部满足 `challenge_verified` 才通过。
