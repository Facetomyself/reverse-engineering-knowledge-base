# 京东 h5st

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 京东 PC/Web 链路中 h5st、request_algo、tk03/tk06、fp 与业务风控参数链路的通用参考。

## 命中特征

- 业务接口出现 `functionId=pc_detailpage_wareBusiness`、`pc_search_searchWare` 等；appid 形如 `pc-item-soa`、`search-pc-java`；client 为 pc
- 请求参数出现 `h5st`、`t`、`uuid`、`loginType`、`appid`、`clientVersion`、`client`
- Header 出现 `x-api-eid-token`、`x-skuid-param`、`x-referer-page`、`x-rp-client`
- Cookie 出现 `3AB9D23F7A4B3CSS`、`3AB9D23F7A4B3C9B`、`sdtoken`、`thor`、`flash`、`TrackID`、`pin`、`token` 等状态
- `h5st` 字段中出现 `tk03...`，request_algo 阶段出现 `tk06...`
- 固定抓包重放出现 HTTP 403 空 body、服务端下发新的 `X-Rp-Sdtoken`，或业务响应出现签名/风控类错误码

登录验证码联动场景同时出现 JCAP 类特征（jcap 域、requireCaptchaPc、graphicCaptchaVerifyToken、vt）时，按京东 JCAP 产品处理；本文负责登录提交与业务请求的 h5st 签名链。

## 常见链路

```text
页面入口 / 业务上下文
→ 读取 cookie、storage、eid、fp、地区、sku/search 参数、Referer
→ request_algo 或同类前置算法链路生成/刷新 tk03（自身可能需要 tk06）
→ h5st 逻辑使用 tk03、fp、t、body、functionId、appid 等字段生成业务 h5st
→ 携带 h5st、t、x-api-eid-token、x-skuid-param/pcdk、cookie 请求业务接口
→ 按响应状态判断签名、cookie、TLS/HTTP、账号态或风控层级问题
```

`tk03` 与 `tk06` 必须区分：业务请求 h5st 中最终使用的通常是 `tk03`，来自 request_algo 响应；`tk06` 用于 request_algo 自身签名链路，不能直接当业务 token。`tk03` 可按证据证明的缓存周期复用，过期或环境变化后必须重新请求。

## 观察优先级

1. h5st 字段含义与数量按当前证据确认，不靠固定位置命名：时间格式字段、fp、appid/algo 标识、tk03、业务摘要/hash、版本、毫秒时间戳、环境指纹密文、二次摘要、末尾配置段
2. `t` 必须动态生成，与 h5st 内部毫秒时间戳同轮对齐；fp 不默认写死，按缓存逻辑或生成算法维护
3. canonical string、stk、字段排序、URL 编码、body 序列化按当前证据确认；详情、列表、店铺、活动页可能不同 appid/client/x-rp-client/stk/body
4. 详情与列表分别记录 appid、x-rp-client、body、stk；`x-api-eid-token` 与设备 Cookie 同轮一致；area/ipLoc/areaId 一致
5. fp 分析顺序：查生成入口 → 查 storage 缓存 → 查环境读取面 → 可还原则动态生成，服务端/页面缓存则记录来源与刷新条件
6. request_algo 的 tk03 缓存 key 与 appid、fp、cookie、eid、UA、账号态绑定；判断何时复用、何时刷新

## 常见坑

- 把 request_algo 阶段的 tk06 当成业务 h5st 的 tk03
- 固定抓包 h5st、t、fp、x-skuid-param 长期重放
- 只换 cookie，不同步 x-api-eid-token、设备 Cookie、sdtoken、area、pvid 等绑定字段
- 详情和列表混用 appid、x-rp-client、body 或 stk
- body 在 h5st 摘要中一种序列化、实际请求另一种；忽略列表请求的重复参数
- HTTP 403 只怀疑 cookie，忽略算法错误、fp/tk03 失效或客户端指纹差异
- HTTP 200 但业务错误继续补环境，未先查 h5st 摘要、字段顺序、时间戳和 token 新鲜度

## 验证口径

- 详情/列表接口返回正常业务数据；记录 functionId、appid、x-rp-client、tk03 来源与刷新条件、eid-token 与 Cookie 同轮一致性
- 分层判断：403 空 body + 下发 X-Rp-Sdtoken 优先查算法链、h5st、fp、cookie/eid 绑定、TLS/HTTP 指纹；200 但业务码错误优先查摘要、字段顺序、body 编码、t/fp/token 新鲜度
- 不同请求客户端（标准客户端与浏览器指纹客户端）表现不同时，先区分 JS 算法错误、会话/eid/sdtoken 失效、TLS/HTTP2/JA3/Header 顺序、参数序列化四类
