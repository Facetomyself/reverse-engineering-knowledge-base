---
schema_version: 2
id: ruyi-20260622-xiaojianbang-tool-gate-reference
document_type: reference
original_date: '2026-06-22'
archived_date: '2026-10-02'
scope:
  targets: [xiaojianbang-auto-reverse]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260622-01.md#小肩膀逆向skillxiaojianbang-auto-reverse他来了
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留来源写明的工具门禁和误判边界。不收录路径伪装返回值、机型清单、签名校验破解、注入目录或密钥变量。没有驳回后的验收。
relations:
  - type: derived_from
    target: ./ruyi-20260622-01.md#小肩膀逆向skillxiaojianbang-auto-reverse他来了
tags: [xiaojianbang-auto-reverse, source-report]
---

# xiaojianbang-auto-reverse 的工具门禁

这张卡只回答：分析 Android native 检测时，来源要求先确认什么、什么不能互相替代、什么不能写成 App 自己的绕过。不提供伪装或注入步骤。

<a id="decision-flow"></a>
## 工具门禁

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 先分开入口：分析时要求区分 helper 函数和真实检测入口，避免把工具函数、字符串初始化函数、日志函数误判为检测点。 | s1，源文件第 104 行 | source-report | 该 Skill 的 native 检测链阅读 | 没有某个 so 的入口地址 |
| C2 | 闪退不能改用动态试错：在闪退、崩溃、退出场景下是硬门禁，不允许用 Frida | s1，源文件第 179 行 | source-report | syscall-filter 已具备的退出定位 | 下一行才写完后半句；不展开采集命令 |
| C3 | 混淆还原前先定界：先确认函数范围，再尝试还原，不能直接基于错误函数范围给出 patch 结论。 | s1，源文件第 259 行 | source-report | 明显 OLLVM/CFF/dispatcher | 没有还原步骤 |
| C4 | 隐藏注入不是 HWBP 的主流程：Skill 禁止把 HWBP/stealth-hook | s1，源文件第 304 行 | source-report | 来源写成让 Frida 注入后仍不被发现 | 只有禁令，没有替代步骤 |
| C5 | 此时只能辅助：此时 HWBP 只能作为辅助验证手段，用来确认参数、返回值、窄 patch 或 syscall 证据。 | s1，源文件第 305 行 | source-report | 与 C4 同一句的后半 | 不记录如何改返回值 |
| C6 | 复杂逻辑超出 HWBP 时，来源只写回到另一条路线：若 HWBP 功能不支持所需复杂逻辑，再回到 Frida 过检测路线。 | s1，源文件第 306 行 | source-report | 来源所称强 Frida 检测下的算法任务 | 没有过检测步骤 |
| C7 | 定制系统能力要先确认设备：必须先确认当前连接设备是否为“小肩膀定制系统” | s1，源文件第 345 行 | source-report | 脱壳、注册监听、任意 so 注入、内置 root、dex 合并 | 确认方法本身没有写 |
| C8 | 未确认则停：确认前不能启用这些能力。 | s1，源文件第 359 行 | source-report | 上列定制系统能力 | 不是通用 Frida 的禁令 |
| C9 | 两个内核工具不在这道门里：不属于定制系统能力。它们只依赖通用前置条件：root/su、APatch/KernelPatch、KPM、arm64/GKI 等。 | s1，源文件第 378 行 | source-report | syscall-filter 与 stealth-hook，工具名在上一行 | 不记录加载命令 |
| C10 | 系统伪装不是样本成果：不能误写成目标 App 的检测绕过成果。 | s1，源文件第 382 行 | source-report | 小肩膀定制系统已有的环境适配 | 清单不转入本卡 |
| C11 | App 自己的检测仍要单独看：App 自身检测链仍然要按常规流程分析。 | s1，源文件第 410 行 | source-report | 与 C10 同一节 | 没有常规流程的逐步说明 |

## 验证与限制

近邻没有同一目标的 decision-flow。路径存在性伪装、2.8 的无痕特征、3.2 的伪装清单、3.3.2 的签名校验和 3.4.2 的 so 注入都缺验收，不进入本卡。第 6 节只有要写记录一句。作者的成功叙述保持 source-report。
