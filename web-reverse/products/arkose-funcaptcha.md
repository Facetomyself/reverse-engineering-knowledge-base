# Arkose Labs / FunCaptcha

> 来源: spider-skill-tzpnode 2026-08-19 增量（clean-room 重写）
> 原始发布时间: 未知
> 归档日期: 2026-08-19
> 分类: web-reverse
>
> Arkose Labs / FunCaptcha 的产品识别、状态请求链、动态输入和业务读回验收边界。

## 命中特征

- 页面、iframe 或脚本域名出现 `arkoselabs.com`、`funcaptcha`、`FunCaptcha` 或 Arkose `api.js`。
- 请求路径出现 `/fc/gt2/public_key/`、`/fc/gfct/`、`/fc/ca/`。
- 请求或响应出现 `public_key`、`session_token`、`challengeID`、`game_token`、`guess`、`bio`、`render_type`。
- 题面或配置出现 `audio_challenge_urls`、音频选择题、图像旋转或其它 Arkose game 类型。

只有 `audio`、`challenge` 或通用 `token` 字段不足以确认产品，必须结合域名、`/fc/*`
路径和字段形状交叉判断。

## 状态链

典型链路按当前集成版本重新取证，不得把以下阶段写死成固定 URL 或字段集合：

```text
业务入口下发 Arkose 配置或 blob
-> public_key 初始化，生成当前轮 client fingerprint payload
-> 获取 session token 与 challenge 配置
-> 拉取题面或 game 资源
-> 生成当前轮 answer / proof / behavior payload
-> 提交 challenge
-> 将通过凭证注入原业务请求
-> 原业务接口 readback
```

每个阶段都要记录 source、consumer、状态写入和下一阶段依赖。`public_key`、SDK 版本、动态
脚本、blob、session token、题面、答案和 proof 必须属于同一 `roundScope`。

## 动态输入

- client fingerprint 字段的名称和编码随 SDK 版本变化；历史资料中的 `c`、`bda`、AES/RSA
  组合只能作为定位线索，必须回到当前脚本和 request boundary 确认。
- `guess` 的明文可能是选项索引、单词或题型专用编码；其加密字段、IV、salt 和 key derivation
  以当前 runtime 为准。
- `bio` 常承载鼠标、触摸或键盘事件序列。只在 browser/V8 paired facts 证明它进入目标请求时
  建模，不复用历史轨迹，不用同步假回调制造完成状态。
- 音频或图像识别属于 answer 生成面，应与环境 patch、请求构造和 transport 分层，低置信度时
  停止当前轮提交并保留失败证据。

## 观察优先级

1. 固定当前 SDK、public key、业务入口、iframe/script 资源 hash 和 challenge 类型。
2. 从当前请求链确认初始化、题面、answer/proof 提交、token 注入和业务 readback 的真实顺序。
3. 定位 fingerprint、answer 与 behavior payload 的 writer、输入和 request boundary。
4. 对 iframe、Worker、Canvas/WebGL/Audio、事件与 timing 只建模目标链路实际触达的最小语义。
5. 使用同一 session、代理、headers、浏览器族和 TLS 基线验证原业务接口。

## 常见坑

- 把 `/fc/gt2/public_key/` 或 `/fc/gfct/` 的 HTTP 200 当作 challenge 通过。
- 把 `/fc/ca/` 的单轮 `solved=true` 当作原业务完成。
- 混用旧 SDK、旧 blob、旧 session token、旧题面或历史答案。
- 仅按字段名猜测 fingerprint / answer 加密算法，未核对当前脚本与 wire body。
- 把音频识别失败直接归因于加密或环境，未先核对下载、解码、分段、题型和答案映射。
- 为跑通 challenge 批量补全浏览器或复刻历史行为轨迹，未证明这些输入进入当前 proof。

## 验证口径

- 本地每轮实时生成 fingerprint、answer 和 proof；关键输出 hash 或 token 应体现新鲜度，不能是回放。
- challenge 的 initialize、prompt、answer、proof、submit 阶段均有同轮 evidence pointer。
- challenge endpoint 的通过状态只记为 `submit=pass`，不能直接标记 `challenge accepted`。
- 通过凭证注入原业务请求后，只有目标业务响应达到预期成功状态，才能写
  `business-readback=pass` 和 `challenge accepted`。
