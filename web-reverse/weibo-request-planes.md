---
schema_version: 2
id: web-reverse-weibo-request-planes
document_type: reference
scope:
  targets:
  - weibo
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: ./weibo-request-planes-case.md
  basis: source-report
tags: [request-planes, xsrf, upload-integrity]
archived_date: '2026-10-01'
modules:
- name: interfaces
  anchor: interfaces
  sources:
  - s1
  basis: source-report
  limits: PC、移动与创作者上传的划分来自不可公开定位的本地来源报告；未核验对应仓库或当前站点，不能据此推断完整 endpoint 顺序。
- name: parameters
  anchor: parameters
  sources:
  - s1
  basis: source-report
  limits: 字段来源及校验描述仅为来源报告；自定义 CRC 表未公开且无对拍样本，不提供算法实现或 parity 结论。
relations:
- type: derived_from
  target: ./weibo-request-planes-case.md#三条面
---

# 微博请求面与上传参数边界

这张 reference 将来源文章里容易混为一谈的请求身份、文件校验和服务端授权拆开。所有内容均为 `source-report`，详见 [来源案例](./weibo-request-planes-case.md)。

<a id="interfaces"></a>
## Interfaces

| 来源报告中的请求面 | 归档描述 | 不应合并的边界 |
|---|---|---|
| PC | `x-xsrf-token` 从 Cookie 的 `XSRF-TOKEN` 直接双写 | 这是登录/CSRF 材料映射，不是本地计算出的文件摘要或签名 |
| 移动 | 使用另一套移动端头与 Cookie | 不把 PC 的 XSRF 双写或 HTML/JSON 响应口径直接套过来 |
| 创作者上传 | 图片/视频上传使用文件检查字段，视频检查还涉及 `X-Up-Auth` | 上传完整性参数与发帖登录材料分开；该头被来源描述为服务端材料 |

来源文章称，邻近存在的 `static/weibo.js` 没有由所述 Python API 路径通过 `execjs.compile` 接入；仅凭文件存在不能认定 PC API 在执行它。

<a id="parameters"></a>
## Parameters

| 字段/材料 | 来源报告中的关系 | 复用时的边界 |
|---|---|---|
| `x-xsrf-token` | 直接取 Cookie `XSRF-TOKEN`；缺键会在组头时失败 | 将其记为 Cookie 派生材料，不误标为本地哈希 |
| 上传 `raw_md5` / `check` | 对文件字节计算标准 MD5 | 图片与视频字段位置不同；不等于请求签名 |
| 上传 `cs` | 来源描述为自定义 CRC 表计算，表体未收录 | 不能直接以通用 `zlib.crc32` 替代；需同一文件对拍后再判断 |
| `session_id` | 来源描述为对文件大小和文件名拼接串计算 MD5 | 拼接细节与测试向量未提供，不据此重建实现 |
| 视频 `X-Up-Auth` | 来源将其描述为服务端签发材料 | 不随机生成，也不把它与文件 MD5 混为一类 |

来源文章明确未重放发帖；本条目不提供运行时、parity 或 server-accepted 结论。移动 HTML 解析与 PC JSON API 的成功口径也应分别核对。
