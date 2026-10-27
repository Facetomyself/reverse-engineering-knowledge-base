---
schema_version: 2
id: jsvmp-analysis-triage-procedure
document_type: procedure
original_date: unknown
archived_date: 2026-10-23
scope:
  targets: [JSVMP, unknown web signer]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./jsvmp-from-toy-vm-to-devirt.md#三从请求定位-dispatcher
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告的分析顺序；不表示目标当前版本、运行时 parity 或服务端接受。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 验收项是来源提出的检查口径，本次未执行抓包回放或环境对照。
relations:
  - type: derived_from
    target: ./jsvmp-from-toy-vm-to-devirt.md#复用边界
tags: [procedure, JSVMP, dispatcher, opcode, devirtualization, source-report]
---

# JSVMP 分析分流流程

<a id="prerequisites"></a>
## 前提与输入

准备一条可重复触发的请求、浏览器开发者工具或等价执行观测手段，以及至少一份真实抓包输出。确认目标属于授权的 Web 逆向范围；本流程不把公开练习靶站经验外推到其他站点。

<a id="steps"></a>
## 步骤与分支

**S1：从请求定位签名入口。** 搜索接口路径/参数，或设置 XHR/fetch 断点，从调用栈回溯 token 拼装函数，并记录脚本内容锚。

**S2：确认 VM 形态。** 识别字节码、`pc`、栈和 dispatcher；区分 `switch`、handler table、threaded 或 wrapper 变体。若未发现这些边界，先停止 JSVMP 假设。

**S3：抓执行流。** 优先使用不暂停的日志断点或等价低扰动观测，记录 opcode、`pc`、栈变化和额外取数；多次触发以确认指令长度与路径稳定性。

**S4：判定算法所在层。** 若 handler 主要调用宿主密码原语，沿宿主边界做输入/输出对照；若转发到 WASM 或另一台 VM，记录转包接口并转向里层；只有算法骨架确实在当前 opcode 中时才进入逐 op。

**S5：处理观测干扰。** 检查 `debugger`、暂停耗时、反 hook、DevTools 探测和补环境缺口。常量从运算点取，不从静态字节码字面量猜；动态生成代码需先捕获 `eval`/`new Function` 产物。

**S6：处理动态/自修改字节码。** 监视 code 数组写入；先检查首遍 key 是否恒等。线性单次执行可在运行后 dump，分支/循环使用解密点执行序列 trace 重建。

**S7：选择收敛方式。** 能在宿主或里层闭合则停止拆 opcode；必须逐 op 时，将解释器改为表达式生成器并做常量折叠。分支/循环只宣称覆盖已观察路径。

<a id="outputs"></a>
## 输出

输出 dispatcher 定位证据、opcode/长度表或明确的未知项、观测环境记录、算法所在层判断、动态字节码 trace（如有）以及离线复现输入输出对照。所有结论标注来源报告、静态观察或运行时观察的边界。

<a id="acceptance"></a>
## 验收

至少完成一次请求触发与执行流对照；指令边界能解释 `pc` 推进；动态生成/自修改场景能说明捕获时点；离线输出与真实抓包按字节比较。通过本地对照不等于服务端接受，需单独记录。

<a id="failure-exits"></a>
## 失败出口

找不到稳定 dispatcher：保留请求入口和未决形态，停止猜测。输出受反调试影响：降低观测扰动并重新做环境对照。字节码仍为密文：确认是否真的改写、首遍 key 和覆盖路径。输出只在单一路径成立：标记路径限制，不升级为完整算法恢复。算法转入 WASM/里层：交接边界，不在外层继续逐 op。
