---
schema_version: 2
id: anti-detection-chromium-jwt-startup-validation-reference
document_type: reference
archived_date: '2026-10-02'
scope:
  targets: [chromium-startup-validation]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./chromium-fingerprint-compilation/02-进阶/05-jwt-startup-validation.md#reference-extraction-118
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理 `BrowserMainLoop::CreateStartupTasks`、parsed command line、jwt-cpp decode/verify 与 GN dependency 位置；没有源码 checkout、构建或运行时进程生命周期证据。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录 `validate` switch、JWT header/payload 的角色和算法配置边界，不复制 token、secret、iat/exp 数值或账号材料；版本与密钥管理未知。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 来源仅描述 decode/verify 成功或抛异常后的日志与 return 分支；没有 exit code、进程退出、时钟、过期策略或服务端授权证据。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留启动分支的静态形状，不把函数内 `return` 解释成已验证的浏览器拒启动合同，也不覆盖刷新、续期或撤销。
relations:
  - type: derived_from
    target: ./chromium-fingerprint-compilation/02-进阶/05-jwt-startup-validation.md#reference-extraction-118
tags: [Chromium, startup, JWT, jwt-cpp, authorization, decision-flow, source-report]
---

# Chromium 启动 JWT 校验参考

这是一张窄范围 `source-report` reference，用于检索“启动参数进入本地授权检查”的代码边界。它不提供 JWT signer、密钥管理、可运行构建步骤或服务端授权结论；原文示例 token、secret 和时间值均不进入本卡。

<a id="interfaces"></a>
## 接口与依赖边界

来源把校验入口放在 `content/browser/browser_main_loop.cc` 的 `BrowserMainLoop::CreateStartupTasks()`，通过 `parsed_command_line_` 检查 `validate` switch 并读取其字符串值。随后使用 jwt-cpp 的 `jwt::decode` 解析 token，以 `jwt::verify` 和指定的 HS256 algorithm verifier 执行校验；构建侧在 `content/browser/BUILD.gn` 增加 jwt-cpp 的 include/config 依赖。

这些名称描述来源报告的调用面，不表示当前 Chromium 分支仍拥有相同函数签名，也不表示 `return` 会在所有调用上下文中终止浏览器进程。

<a id="parameters"></a>
## 参数角色

| 输入/配置 | 来源中的角色 | 本卡边界 |
|---|---|---|
| `validate` startup switch | 启动时携带待校验的 JWT 字符串 | 不记录 token 样值、命令行样例或账号绑定 |
| JWT header | 来源要求固定的 algorithm/type 角色 | 不把来源格式要求当作通用 JWT 合同 |
| JWT payload | `iat` / `exp` 被来源标为时间字段 | 不复制具体时间值，且未验证库的 required/clock semantics |
| HS256 verifier configuration | 本地校验所需的密钥配置角色 | 不记录 secret，不讨论生产密钥分发或轮换 |

来源没有固定 jwt-cpp commit、Chromium branch、时钟来源、允许偏差、续期/撤销和密钥生命周期；这些变量必须在独立 case 中重新取证。

<a id="validation"></a>
## 校验结果边界

来源报告了两类静态分支：有 `validate` 时 decode/verify，异常进入失败日志与 `return`；没有该 switch 时直接进入另一条 `return` 分支。来源还给出成功/失败日志位置，但没有提供进程退出状态、启动后窗口状态、调用者对返回的处理、有效/过期 fixture 或服务端授权读回。

因此，本卡最多支持“启动授权检查点”的定位，不支持以下结论：JWT 已成功授权当前浏览器、`iat`/`exp` 语义已闭合、失败必然阻止整个进程、或本地校验等同服务端授权。

<a id="decision-flow"></a>
## 决策流形状

```text
S1 read parsed_command_line_
  -> D1 validate switch present?
     -> no: source return branch
     -> yes: decode JWT
              -> verify configured algorithm
                 -> success: source success-log branch
                 -> exception: source failure-log + return branch
```

`S1` / `D1` 只用于标识来源代码中的静态分支；它们不是已验收的流程步骤，也没有覆盖进程退出、刷新、续期、撤销或服务端决策。

## 证据限制

全部模块均为 `source-report`。本轮未下载或审查来源图片，未构建 Chromium、未执行 jwt-cpp、未固定库/内核版本、未做 clock/expiry fixture、runtime parity 或 server acceptance；不应由本卡生成 procedure 或生产授权策略。
