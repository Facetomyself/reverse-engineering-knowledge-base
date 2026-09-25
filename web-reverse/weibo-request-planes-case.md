# 微博案例：PC、移动、创作者上传三条面

> 来源: `workspace/cv-cat`（WeiboApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 这份对照仓没有一个全站签名函数。PC 接口把 Cookie 里的 `XSRF-TOKEN` 双写到头，移动接口换一套 m.weibo 头，创作者上传另算文件 MD5 和自定义 CRC。`static/weibo.js` 不在 Python 运行时里。

## 三条面

| 面 | 入口 | 鉴权材料 |
|----|------|----------|
| PC | `apis/weibo_apis.py` + `utils/weibo_utils.py` | Cookie；`x-xsrf-token` 等于 `cookies["XSRF-TOKEN"]` |
| 移动 | `weibo_mobile_apis.py` | 移动端头和 Cookie，搜索/详情不走 PC 的 XSRF 双写 |
| 创作者上传 | `weibo_creator_utils.py` | 文件 MD5、自定义 CRC、`session_id`、视频上传的 `X-Up-Auth` |

PC 发帖头在 `weibo_utils.py` 直接读 `XSRF-TOKEN`。这是 Cookie 双写，不是本地哈希。缺这个 Cookie 键会在组头时失败，应看成登录态材料缺失。

## 案例：图片/视频上传参数

`weibo_creator_utils.py`：

- `get_file_md5` 是文件字节的标准 MD5。
- `get_file_cs` 是一张自定义 CRC 表上的校验，初值 `0xFFFFFFFF`，结果再异或 `0xFFFFFFFF`。表体不入库。它不是 zlib CRC32 的默认多项式可以直接替换，除非对拍过同一文件。
- `generate_session_id(file_size, file_name)` 对拼接串做 MD5。
- 图片上传参数带 `raw_md5`。视频检查头带 `X-Up-Auth`，参数里的 `check` 也是文件 MD5。
- 发微博的 `x-xsrf-token` 仍来自登录 token，和文件校验并列，不是同一个算法。

```text
pc_post:
    headers["x-xsrf-token"] = cookies["XSRF-TOKEN"]
    POST weibo API

upload_image:
    md5 = md5(file_bytes)
    cs = custom_crc(file_bytes)          # table stays in source
    session_id = md5(size_and_name)
    POST media init with raw_md5, cs, session_id

upload_video:
    headers["X-Up-Auth"] = upload_auth   # server-issued
    check = md5(file_bytes)
```

## 落地判断

仓内存在 `static/weibo.js`，但 API 路径没有 `execjs.compile` 它。看到 JS 文件不能推断 PC 请求在跑这包。移动 HTML 解析和 PC JSON API 的成功口径也不同，不能用一边的空 body 解释另一边。

## 证据边界

自定义 CRC 表和上传域名留在源码。本库没有重放发帖。Cookie 与 `X-Up-Auth` 都是服务端材料，不能本地随机。
