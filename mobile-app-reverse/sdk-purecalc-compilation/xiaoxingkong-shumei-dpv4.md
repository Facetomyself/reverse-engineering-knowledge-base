# 数美 deviceprofile/v4：AES key 是 hexdigest 不是 raw MD5

> 来源: workspace/xiaoxingkong-shumei-dpv4
> 原始发布时间: 2026-08-13 源码
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> 小星空启动时的数美 `POST /deviceprofile/v4`。四层模型：App 接入、Java `a*` 画像、Native 封装、HTTP。不收录 organization/appId、证书 PEM 和 Pixel 6 原值。

## 四层

```text
App SmAntiFraud.create(SmOption)
  -> 数美 Java：采集 a* （Build/网络/存储/电池/签名路径）
  -> libsmsdk.so：补 a16/b*、a21/a82/a81，压缩加密
  -> POST data/tn/ep
```

接入固定值不能跨 App 混用。

## 外层字段

`organization` / `os` / `appId` / `encode` / `compress` / `data` / `tn` / `ep`

```text
ep_plain  = 16 字母数字
tn_plain  = MD5(UTF8(ep_plain)).hexdigest()     # 32 ASCII，不是 16 字节 raw
ep / tn   = Base64(RSA-OAEP-SHA256(cert, plain))
a16.b23   = ep_plain || random_alnum(16)
a82_key   = MD5(UTF8(b23)).hexdigest()          # 同样是 32 ASCII 当 AES-256 key
data      = Base64(AES-256-CBC(ASCII(tn_plain), iv, raw_deflate(profile)))
iv        = ASCII("0102030405060708")
```

RSA 模长 2048，每次输出 256 字节再 Base64。证书属于该 App 内置数美 SDK。

## 生命周期

| 类 | 规则 |
|----|------|
| 接入固定 | organization/appId/证书/包信息 |
| 安装稳定 | 安装目录、SDK 设备数据成组 |
| 设备稳定 | 型号/Build/分辨率/CPU 成组 |
| 开机稳定 | boot_id 派生 |
| 运行状态 | IP/SSID/电池/输入法 |
| 每请求 | a9/a80/a21/b23/a82/data/tn/ep |

## 边界

离线生成 `data/tn/ep` 长度与依赖 ≠ 数美返回 `deviceId`。实现留 `workspace/xiaoxingkong-shumei-dpv4/source/`。
