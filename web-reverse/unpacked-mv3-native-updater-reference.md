---
schema_version: 2
id: web-reverse-unpacked-mv3-native-updater-reference
document_type: reference
original_date: '2026-08-24'
archived_date: '2026-10-03'
scope:
  targets: [unknown]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./unpacked-mv3-native-updater.md#reference-extraction-217
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理渠道清单 → zip → 本机覆盖 → 协议唤醒 → 本机进度口的来源链；未跑更新器、未请求清单接口。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 记录五层职责与 zip/协议/进度合同；不收录清单 URL、协议名、端口、zip 哈希或账号 token。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: Load unpacked 与覆盖后重启浏览器均为来源打包纪律；本轮无 runtime 或商店验收。
relations:
  - type: derived_from
    target: ./unpacked-mv3-native-updater.md#reference-extraction-217
tags: [MV3, sideload, unpacked, custom-protocol, updater, source-report]
---

# 未上架 MV3 sideload 更新器五层合同参考

这张窄卡只整理来源 archive 对 **渠道 zip、本机绿色更新器、自定义 URL 协议唤醒、可 Load unpacked 的扩展目录，以及账号面与安装面分离** 的打包合同。样本是谋臣界更新器，合同不绑定该产品。不收录渠道 URL、协议名、本机端口、zip 哈希或 `userToken`。

<a id="request-chain"></a>
## 分发链

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 报告称五层是：渠道清单+对象存储 zip → 本机更新器覆盖目录 → 可 Load unpacked 的扩展目录 → 开发者模式加载 → 网站账号/配额。 | s1，「五层模型」 | source-report | 来源 sideload 样本 | 不是 CWS `update_url`。 |
| C2 | 报告称更新器先 GET 工具清单，按稳定渠道 id 选记录再下 zip；zip 根只有扩展目录。渠道版本字段与 `manifest.json` version 分开。 | s1，「渠道面」 | source-report | 来源清单规则 | 不收录接口路径或版本样值。 |
| C3 | 报告称扩展/网页用自定义协议把控制交给本机进程；更新器在本机回进度，扩展用同一 taskId 轮询；成功后重启浏览器。 | s1，「协议唤醒与本机进度」 | source-report | 来源 Win 更新器 | 协议名、端口不收录。 |

<a id="parameters"></a>
## 层职责

分开 encoding、token、配置：

| 层 | 来源描述的角色 | 类别 | 边界 |
|---|---|---|---|
| 渠道 | 当前 zip 与不可变对象地址 | 配置 | 不承担浏览器加载或会员判定。 |
| 本机更新 | zip → 磁盘目录；HKCU 协议；多位置登记；本机进度 | encoding | 覆盖须排除 exe/说明/config/log。 |
| 扩展目录 | 能直接看到 `manifest.json` 的 MV3 目录 | 配置 | 不要打进 `_metadata/`。 |
| 浏览器加载 | 一次人工 Load unpacked；之后覆盖+重启 | 配置 | 无企业策略时不能静默写入 Profile。 |
| 账号 | 登录态与配额在网站 | token | 安装包不含卡密或离线授权。 |

最小自有实现可以只做扩展目录+人工加载；标准实现再加清单与更新器。改协议名或 exe 行为必须发新更新器，只更 zip 不够。

<a id="validation"></a>
## 验证与限制

- 覆盖目录后要重启浏览器，不要假设 service worker 吃到全部新文件。这是来源打包纪律。
- 更新失败与未登录是两类错误。
- 本轮未运行更新器、未请求清单、未加载扩展。
- 不收录 Cookie、账号 token、清单 URL、协议名、本机端口、zip 哈希或工作区路径。
- Native Messaging 与自定义协议的取舍见来源对照表，不是已验证实现。
