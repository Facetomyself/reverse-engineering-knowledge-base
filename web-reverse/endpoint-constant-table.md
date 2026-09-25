# 技巧：端别常量表，按抓包填，不为统一抹平

> 来源: `workspace/cv-cat`（DouYin_Spider `HOST_APP_IDS` / `with_platform`、MTOP appKey、头条与西瓜 aid）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 同一算法常嵌入 aid、page_id、appKey、version_code。这些数按 host 和接口变化。为了「公共参数统一」抹平差异，会在强校验接口上被判成人机，或签到错误的网关。常量表来自抓包，会过期，但「签名函数必须吃端别」这条不过期。

## 怎么建表

每一行是一次抓包，不是一个站点一个数。列至少包括：host、path、query 里的 aid/appKey、签名函数内嵌的另一组 id、version_code、谁在用这组数。

抖音对照里已经分开的行：

| 用途 | 值 | 不能拿去填 |
|------|----|------------|
| `a_bogus` 内嵌 www | aid 6383，page_id 11881 | 直播 page_id 7571、登录 6241、创作者 2906/33638 |
| 创作者 query `aid` | 1128 | 换证书和 `read_aid` 用的 2906 |
| 主站公共 `version_code` | 170400 / 17.4.0 | detail 实录 190500，post 290100，search 190600 |
| 直播电商公共组 | version 320100，`support_dash=0`，rtt 50 | 主站 `support_dash=1`，rtt 0 |
| 头条 feed | aid 24，execjs `get_ab` | 抖音纯算和 6383 |
| 西瓜列表 | aid 1768，三个签名位为空 | 头条的 `_signature` |
| 淘宝 H5 | appKey 12574478，host `h5api.m.taobao.com` | 闲鱼 Web 34839810，闲鱼 App 21407387 |

`with_live_platform` 的注释写明：四处差异不要为了统一抹掉。`get_work_info` 的注释写明：换成公共 `with_platform()` 时把 detail 的 version 一起降成 170400，是自己引入的回退。

## 真实流程

```text
capture one XHR
row = {
  host, path, method,
  query_aid, query_version,
  signer_host_arg,          # a_bogus 的 host，不是 query 里那个 aid
  signer_embedded_ids,
  app_key, gateway
}
table.append(row)

sign(request):
    row = table.match(request.host, request.path)
    if row is None:
        fail closed                  # 未知端别不要退回主站再当成功
    return signer(request, host=row.host, ids=row.signer_embedded_ids)
```

未知 host 退回主站，只适合本地调试默认值。强校验接口上，退回本身就是错误端别。抖音 `app_ids_for` 对未知 host 回 www，调用方仍应传对 host，不能依赖这个退回。

## 同名常量的三层

创作者发布同时存在：

1. query `aid=1128`，来自 `with_creator_platform`。
2. `read_aid` 和换证书用 `2906`。
3. `a_bogus(..., host=creator.douyin.com)` 内嵌 `(2906, 33638)`。

表上写成三行。合并成一个 `CREATOR_AID` 会让证书、query、签名各错一层。

MTOP 同样三行：H5 appKey、body 里的 IM app-key、App 的 `21407387`。淘宝仓里残留的 goofish URL 不进淘宝那一行。脏常量留在表外，并注明「未被调用」。

## 过期

`version_code`、page_id、appId（京东搜索 `f06cc`）都是抓包窗口的数。复用的是建表动作：新抓一条就加一行，旧行标日期。不要把表抄进另一个 Cookie 会话当设备指纹。
