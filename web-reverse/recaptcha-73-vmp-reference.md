---
schema_version: 2
id: web-reverse-recaptcha-73-vmp-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-13"
scope:
  targets: [recaptcha-73]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./recaptcha-73-vmp-source-archive.md#source-body
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅记录来源可读的 73 槽位输入和时间 / 盐依赖概述；函数体、关键中间量和截图缺失，无法复算完整算法。
relations:
  - type: derived_from
    target: ./recaptcha-73-vmp-source-archive.md#source-body
tags: [recaptcha-73, VMP, gpu-fingerprint, time-seed, source-report]
---

# reCAPTCHA “73” VMP 槽位算法参考

这张卡只整理 pending 文本里可读的算法轮廓。材料没有说明精确产品版本，也没有足够信息证明该 VMP 与知识库中的 Google reCAPTCHA v3 请求链属于同一分支，因此两者不合并。

<a id="parameters"></a>
## 来源报告中的输入与变换

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源称某个槽位会写入由 WebGL vendor、renderer 与支持扩展数量组成的数组；数组 JSON 序列化后逐字符写入字节数组。 | s1，`write_73` 相关段落 | source-report | 文中所称的“73”槽位 | 本卡不包含 GPU 原值、扩展列表或完整输入串。 |
| C2 | 来源把数组变换描述为逐项字节运算，状态与 anchor 中解析出的值、槽位 salt 及 `performance.now()` 读数有关；时间种子随后影响输出尾部。 | s1，变量还原段落 | source-report | 来源所述特定 VMP 代码 | 原文省略关键函数体和完整表达式，并指出一个反编译下标需要纠正；无法据此复算或声称算法已恢复。 |
| C3 | 来源称一个辅助解析函数用于从 anchor 响应提取变化值；该函数由作者借助 AI 生成。 | s1，末段说明 | source-report | 来源作者的分析过程 | 未提供输入 / 输出夹具、解析器实现或独立验证。 |

## 验证与限制

- 两个函数只以声明形式出现，没有可运行函数体；导出图片均为 1×1 占位资源，不能补全缺失算法。
- 原材料没有给出文章日期、reCAPTCHA 具体版本、站点范围或可复算的对照样本，因此 `scope.observed_at` 和 `version` 保持 `unknown`。
- 本轮未执行目标代码、请求服务或复核 VMP 输入输出。不要将来源对“算法简单”的评价视为算法完整性证据。
- 更广义的 Google reCAPTCHA v3 / invisible 请求链见 [产品参考](./products/google-recaptcha-v3.md)，两份资料的关系尚未确认。
