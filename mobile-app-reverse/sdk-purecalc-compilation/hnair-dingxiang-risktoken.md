# 顶象 DXRisk：riskToken 是签发请求不是本地拼串

> 来源: workspace/hnair-dingxiang-risktoken
> 原始发布时间: 2026-08-14 源码
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> 海南航空 Android 接入顶象 DXRisk。客户端构造 `/udid/m1` 签发请求，token 在响应里。不收录 appKey、XXTEA key 和 189 项真实画像。

## 结论

`riskToken` 由顶象服务端签发。不存在「本地拼 8 位时间十六进制 + 32 位随机串」的真实算法。

```text
RiskSdk.getToken()
  -> JNI
  -> metadata + N 项 profile
  -> protobuf
  -> sign = MD5(appKey || protobuf || appKey)
  -> ZIP(entry=data, raw DEFLATE)
  -> XXTEA(include_length=true)
  -> POST /udid/m1
  -> 响应 XXTEA -> ZIP -> protobuf -> riskToken
```

HTTP 是 `application/octet-stream`。query 带 `sign` / `appKey` / 包名 / SDK 版本。

## ZIP 约束

Native 固定向量要求手工拼 ZIP 头：DOS 时间、extra、注释均为 0。用 `zipfile` 默认时间戳会对不齐逐字节对照。

## 画像

profile 必须成组，来自同一台设备的一次 Native 捕获。Windows 主机不能实时读 Android API。只刷新已证明有时间关系的少数键，禁止逐项随机或 SoC/GPU hybrid。

## 边界

- protobuf 逐字节对齐 ≠ `serverAccepted`
- 接入常量和 XXTEA 材料按 App/SDK 版本绑定，不能跨包混用
- 完整字段字典和实现留 `workspace/hnair-dingxiang-risktoken/source/`
