---
schema_version: 2
id: cloud-real-device-fingerprint-collection-reference
document_type: reference
original_date: '2026-07-15'
archived_date: '2026-10-02'
scope:
  targets:
    - cloud-real-device
    - testin
    - utest
    - vmos-cloud
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260715-01.md#正文"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留自写采集 App、自有服务器和三个站点首页。没有字段、上报路径或鉴权。Testin 的广告点击参数未转写。未在这些平台安装采集端。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: “应采尽采”没有字段表。付费或认证后免费时长只是来源说法，没有额度、认证材料或失败后退路。
relations:
  - type: derived_from
    target: "./xfq-20260715-01.md#今天发现群里有人问怎么找设备指纹的一些信息焚诀来了"
tags:
  - cloud-real-device
  - device-fingerprint
  - source-report
---

# 云真机上自采设备指纹的来源边界

这张卡只回答：来源建议从哪里取得设备指纹样本，而不是自己填。不提供采集字段、上报接口或可运行的采集端。Android 设备画像的定性一致性仍以一致性参考卡为准；那张卡写明不提供采样器，这里不并入。

来源没有可公开定位的原文 URL。作者把“打开运行上传到服务器即可”写成完成，该说法保持 source-report。

<a id="interfaces"></a>
## 采集入口

来源把采集端写成自己开发的 App，把结果上报到自己的服务器，再把这个 App 装到云真机上运行。

> 自己写一个采集设备指纹的app,把设备指纹上报到自己的服务器

> 在云真机上安装自己的设备指纹采集app,打开运行上传到服务器即可

站点只出现了三个首页，不是采集 API：

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 采集端是自写 App，去向是自己的服务器。 | s1，`xfq-20260715-01.md:39`；quote：`自己写一个采集设备指纹的app,把设备指纹上报到自己的服务器` | source-report | 来源描述的采样通道 | 没有 URL、报文或鉴权 |
| C3 | 运行位置是云真机，安装后上传。作者把这一步写成即可完成。 | s1，`xfq-20260715-01.md:40`；quote：`在云真机上安装自己的设备指纹采集app,打开运行上传到服务器即可` | source-report | 同上 | 本次未安装，成功不升级 |
| C5 | 来源点名 Testin 云测首页。 | s1，`xfq-20260715-01.md:41`；quote：`https://www.testin.cn/website/` | source-report | Testin 首页这一入口 | 广告点击参数不转写；不是 API |
| C6 | 来源点名优测首页。 | s1，`xfq-20260715-01.md:42`；quote：`https://utest.21kunpeng.com/home` | source-report | 优测首页 | 只是首页 |
| C7 | 来源点名 VMOS Cloud 首页。 | s1，`xfq-20260715-01.md:43`；quote：`https://cloud.vmoscloud.com/` | source-report | VMOS Cloud 首页 | 只是首页 |

<a id="decision-flow"></a>
## 采集取舍

字段上，来源要求按自己的需要采集，并写成应采尽采，不要自己随便填充。它没有列出字段。

费用上，来源同时写了付费和白嫖，并把免费时长系在“有的云机平台”认证之后。没有认证材料、时长或失败后的另一条路。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 不要自己填充，按应采尽采处理。 | s1，`xfq-20260715-01.md:39`；quote：`应采尽采,不要自己随便填充` | source-report | 来源所说的采集策略 | 没有字段名单 |
| C4 | 可以付费，来源也写了可以不付费。 | s1，`xfq-20260715-01.md:40`；quote：`充点钱即可(也可以白嫖)` | source-report | 云真机平台的费用说法 | 没有价格或额度 |
| C8 | 有的平台认证后送免费时长，需求不大可以不付费。 | s1，`xfq-20260715-01.md:45`；quote：`有的云机平台你认证一下会送免费时长,如果需求不大白嫖即可` | source-report | 来源点到的部分平台 | 没有认证条件和失败出口 |

## 验证与限制

历史镜像在 Testin 首页问号处被截断，不另作一条入口。三个首页是否仍提供云真机、免费时长是否仍在，都不在本卡范围内。缺字段、缺上报样本、缺验收条件、缺失败出口，所以这不是流程。一致性参考卡的定性画像不能拿来给这条采样通道做验收。
