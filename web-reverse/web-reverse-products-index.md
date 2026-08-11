# Web 安全产品强制命中索引

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 面向 Web 逆向与风控请求链复现的安全产品特征索引。命中特征 → 映射产品 → 只读对应文档，是定位签名、验证码、状态型业务链时的第一道分类门。

## 用途

当目标名称、参数名、脚本名、Cookie、Header、URL、响应体或日志出现安全产品同类特征时，先用本索引判定可能的产品面，再只读命中产品对应的子文档。索引只负责识别常见产品、优先观察点和常见坑，不替代当前目标实测——补入本地运行环境的任何值、API 行为、事件顺序、异常栈、descriptor、prototype 或 `toString` 外观，都必须来自当前目标的浏览器证据与请求面证据。

## 强制命中纪律

- 出现同类安全产品特征时**必须**命中本索引中的产品，命中后在进展账本写明：安全产品同类特征、命中的产品、读取的产品文档。
- 一个任务可以同时命中验证码产品和签名产品；例如京东登录可同时读取 `jd_jcap`（验证码）与 `jd`（签名）。
- 判定为 `captcha` / `hybrid` 类型，或完整链路明确包含验证码 / challenge 子链时，先命中验证码 / challenge 文档，再按后续业务请求命中签名 / 加密文档。
- 出现同类特征但无法映射到现有文档时，必须记录为「未知安全产品特征」，按当前目标实测继续定位，不得假装没有产品特征。
- 产品文档只提供观察顺序和常见坑，不允许直接套旧值、旧环境或旧请求链。

## 产品一览

| 产品 | 命中特征摘要 | 子文档 |
|------|--------------|--------|
| Cloudflare 5s challenge | `cf_clearance` Cookie、`challenge-platform`、5 秒盾 interstitial、`cf_chl_` 字段 | [cloudflare_5s.md](web-reverse-products-index/cloudflare_5s.md) |
| DataDome | `datadome` Cookie、`x-datadome*` 头、`ct.captcha-delivery.com` 域、`var dd={...}` | [datadome.md](web-reverse-products-index/datadome.md) |
| Akamai | `_abck` Cookie、`bm-verify` 头、`ak_bmsc` / `bm_sz`、`__utmvc` | [akamai.md](web-reverse-products-index/akamai.md) |
| Kasada | `kpsdk_ct` / `x-kpsdk-ct`、`kasada` 域、`kpxd`、bot 检测后 interstitial | [kasada.md](web-reverse-products-index/kasada.md) |
| PerimeterX | `_px3` / `_pxhd` Cookie、`px-captcha` 域、`_pxff` / `_pxhd` 头 | [perimeterx_px.md](web-reverse-products-index/perimeterx_px.md) |
| F5 Shape | `shape` / `__shape_` Cookie、`shape.com` 域、`f5_ca` 头、`si` 字段 | [f5_shape.md](web-reverse-products-index/f5_shape.md) |
| reese84（网页端） | `reese84` Cookie、`r8` 参数、`.cdnreese84.com` 域、`r84` challenge 链 | [reese84.md](web-reverse-products-index/reese84.md) |
| 瑞数 rs6（动态网页） | `FSSBBIl1UgzbN7N80S` 动态 Cookie、`__wd` 段、动态 JS 重新加载自身 | [rs6.md](web-reverse-products-index/rs6.md) |
| 瑞数 ruishu_rs6 | 同上，侧重验证码滑块 `c` 参数、`R` 请求与行为 proof | [ruishu_rs6.md](web-reverse-products-index/ruishu_rs6.md) |
| 同盾 tongdun | `token` / `black_box`、`fingerprint.js`、`collect` 上报、`umid` | [tongdun.md](web-reverse-products-index/tongdun.md) |
| 腾讯验证码 tx_captcha | `ticket` / `randstr`、`ssl.captcha.qq.com`、`captcha-type`、滑块/点选 | [tx_captcha.md](web-reverse-products-index/tx_captcha.md) |
| Google reCAPTCHA v3 | `grecaptcha.execute`、`api2/anchor`、`api2/reload`、`rresp`、`g-recaptcha-response` | [google_recaptcha_v3.md](web-reverse-products-index/google_recaptcha_v3.md) |
| 阿里云验证码（v1/v2/v3） | `aliyunCaptcha`、`nc_` 字段、`ic.getNcCode`、`appkey`、`scene` | [aliyun_captcha.md](web-reverse-products-index/aliyun_captcha.md)、[aliyun_captcha_v2.md](web-reverse-products-index/aliyun_captcha_v2.md)、[aliyun_captcha_v3.md](web-reverse-products-index/aliyun_captcha_v3.md) |
| 阿里 H5Sec/ACW/火眼 | `acw_sc__v2`、`h5sec`、`aliyun.com` 验证头、`__ac_signature` | [alibaba_h5sec_awsc_fireye.md](web-reverse-products-index/alibaba_h5sec_awsc_fireye.md) |
| 阿里 BxUA | `bx-ua` 头、`bXuaParams`、`bx.com.cn` 域 | [ali_bxua.md](web-reverse-products-index/ali_bxua.md) |
| 饿了么 ACCS/LWP | `accs` / `lwp` 参数、`security` 字段、`x-egw-*` 头 | [ele_accs_lwp.md](web-reverse-products-index/ele_accs_lwp.md) |
| 美团外卖 WS | `mt_waimai_ws` 域、WebSocket 心跳/ack、`sensor_data`、`wmspider` | [mt_waimai_ws.md](web-reverse-products-index/mt_waimai_ws.md) |
| 京东 jd | `h5st`、`_stk`、`request_algo`、`tk03`、`x-rp-client` | [jd.md](web-reverse-products-index/jd.md) |
| 京东到家 WS | `wss://ws1-dd.jd.com/`、`dsm.o2o.order` 接口、`waiterPin` | [jd_daojia_ws.md](web-reverse-products-index/jd_daojia_ws.md) |
| 京东 JCAP（验证码） | `jcap` / `c-4` 字段、`captcha.jd.com`、`validate`、`vt` 凭证 | [jd_jcap.md](web-reverse-products-index/jd_jcap.md) |
| 京东 JCAP 滑块 | `jcap` 滑块、`acToken`、`fp`、`gid`、行为 proof 上报 | [jd_jcap_slider.md](web-reverse-products-index/jd_jcap_slider.md) |
| 抖音 a_bogus | `a_bogus`、`msToken`、`verifyFp`、`webmssdk`、`sdk-glue`、`SecureSDK` | [dy_abgous.md](web-reverse-products-index/dy_abgous.md) |
| 抖音创作 IM | `imapi.douyin.com`、`bd-ticket-guard-client-data`、`identity_security_token` | [dy_creator_im.md](web-reverse-products-index/dy_creator_im.md) |
| 抖音 TicketGuard | `bd-ticket-guard-*` 头族、`ticket` 动态 token、`re-verify` 链 | [dy_ticket_guard.md](web-reverse-products-index/dy_ticket_guard.md) |
| 抖音验证中心滑块 | `verifycenter` 域、`verifyFp`、滑块 proof、`verify_token` | [dy_verifycenter_slide.md](web-reverse-products-index/dy_verifycenter_slide.md) |

## 使用边界

- 一份 trace 通过只代表当前版本可用，不代表跨版本稳定；安全产品、验证码 SDK、动态签名 runtime 的 payload 都按版本材料记录 hash 与适用目标集合。
- 无法确认是否为 VMP 字节流 / 动态载荷时，按多版本风险候选处理，不因「日志量少」误判成证据不足。
- 本索引与子文档只用于识别与观察优先级；验证码 token、动态签名与业务放行口径始终以当前目标的实时请求与业务读回为准。

## 与主线工作流的衔接

- 命中判定写入 `web-case.json` 的 challenge phase 与 `analysis-progress.md` 进展账本。
- 验证码 / challenge 子链属于 `web-challenge` 的路由面；签名 / 加密参数属于 `web-reverse` → `web-env-patcher` / `protocol-recovery` 路由面。
- 产品文档描述的补环境对象（iframe、Worker、MessagePort、canvas 等）参考 [env-objects-reference](./web-reverse-env-objects-reference.md)。
