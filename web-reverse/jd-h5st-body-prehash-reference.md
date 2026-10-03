---
schema_version: 2
id: web-reverse-jd-h5st-body-prehash-reference
document_type: reference
scope:
  targets: [jd]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./jd-h5st-runtime-case.md#案例搜索-searchware
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅整理来源案例中的 body 摘要、服务端材料阶段、时间字段和序列化边界；不复制 Cookie、token、appId 或请求样值，也未重验当前京东协议。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只抽取来源报告描述的装配顺序；没有公开源码、抓包 fixture、当前接口响应或可执行客户端。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 失败分流和新鲜度检查是来源方法，不是本轮 runtime、parity 或 server acceptance 结果。
relations:
  - type: derived_from
    target: ./jd-h5st-runtime-case.md#案例搜索-searchware
tags: [jd, h5st, body-prehash, request-chain, source-report]
---

# 京东 h5st body 预哈希与运行时分链参考

这是一张窄范围 `source-report` reference，解决“业务 body 如何进入 h5st、服务端材料与本地兜底如何分层、重试时哪些字段必须重新装配”的检索问题。它不替代 [京东案例归档](./jd-h5st-runtime-case.md) 或 [京东 h5st 产品参考](./products/jd-h5st.md)，也不证明当前服务端仍接受该链路。

<a id="parameters"></a>
## 参数机制

- 来源将**参与签名的 body 表示**与**实际发送的业务 body**分开：前者先对紧凑 JSON 做摘要，后者仍发送原业务 JSON。摘要输入的空格、字段顺序和序列化方式必须保持同一份合同，不能边签名边换格式。
- 来源把服务端取得的业务阶段材料与库的本地兜底材料分开。业务请求不得把“本地能生成”的中间结果直接当作服务端阶段材料；材料来源、缓存绑定和刷新条件应单独记录。
- 时间字段属于同一轮装配：重试时重新取时间并重新生成 h5st，不能长期复用抓包中的 h5st 或把另一段内部时间覆盖到业务 query。
- 同名 query 参数不能用会丢失重复键的普通映射表示；需要保留键值对顺序和重复项，再按实际请求合同发送。

<a id="request-chain"></a>
## 请求链

来源案例给出的最小装配关系是：

```text
会话上下文（cookie / origin / referer）
  -> 紧凑业务 JSON
  -> body 摘要
  -> 运行时 signer 获取 h5st
  -> 检查服务端阶段材料是否满足业务门
  -> 保留重复 query 键并装配业务参数
  -> 发送原业务 body
```

这条链强调 signer 的运行时、前置材料获取和业务请求是连续但不同的阶段。登录验证码或其他 challenge 链不能因为同一请求同时携带 h5st 就与 h5st 失败互相替代解释；应按响应中的题型/阶段字段单独分流。

<a id="validation"></a>
## 验证与限制

复用这张卡时至少分别记录：

1. 摘要输入与实际 body 的字节表示是否一致，尤其是紧凑 JSON、字段顺序和重复 query。
2. 服务端阶段材料的来源、缓存绑定和刷新条件；本地兜底只记录为 fallback，不当作业务完成材料。
3. 每次重试是否重新生成时间、签名和 query；不能用旧 h5st 解释新一轮请求。
4. 业务响应、前置材料响应和验证码响应分别归因；HTTP 状态或单个业务错误不能单独证明算法、会话或风控原因。

来源只支持 `source-report`：本轮没有执行目标页面、signer、HTTP 请求、对拍或服务端业务读回。具体字段名、版本、appId、Cookie/token 值和响应样值必须回到当前目标的脱敏证据重新核验。
