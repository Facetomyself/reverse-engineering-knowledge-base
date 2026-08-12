# 浏览器采集器稳定性：ruyipage Firefox 断言崩溃与 OOM 连锁

> 来源: `workspace/radwell`
> 原始发布时间: 2026-08-12
> 归档日期: 2026-08-12
> 分类: collection-engineering
>
> 从一次 44326 页 ruyipage Firefox 批量采集（采 39% 后因崩溃与 OOM 终止）中提炼：
> 真实浏览器采集器的稳定性边界 —— 定制 Firefox 的断言崩溃触发条件、单出口 IP 的
> CF 风控有效窗口、多实例并发的崩溃放大效应，以及"崩溃残留进程 → 内存耗尽"的
> OOM 连锁机制。重点不是某个站点的数字，而是为什么"多开窗口"在真实风控目标上
> 行不通，以及崩溃如何从单点故障演变成整机 OOM。

## 结论先行

1. **定制 Firefox 的崩溃是确定性断言失败，不是随机问题**：实测 12 小时内 118 次
   崩溃中 96%（113 次）异常码 `0x80000003`（断点异常 = MOZ_ASSERT），模块集中在
   `mozglue.dll` / `xul.dll`。单实例、页面正常时零崩溃；多实例并发 + 页面加载失败时
   密集崩溃 —— 触发条件是**可复现的代码路径**，不是内存问题。
2. **单出口 IP 有风控有效窗口**：目标 CF 对每个出口 IP 的有效窗口约 30-60 分钟
   （约 400-600 页）。窗口耗尽后页面返回 200 + 3KB 空壳（软挑战，`title` 恒定、
   DOM 永不就绪），采集器 poll 超时。这是整条崩溃链的起点。
3. **OOM 是连锁反应，不是泄漏**：Firefox 崩溃后 ruyipage 无法回收残留进程
   （"孤儿 session"重连失败），进程数从实例数累积到 91 个，按单实例 ~350MB 估算
   约 32GB，吃满整机内存后拖垮同机其他应用（实测 VSCode OOM）。
4. **并发实例数要等于健康出口数，且 ≤ 4**：4 worker 健康期崩溃最少；8-12 worker
   并发时崩溃按小时计达 28-37 次。

## 崩溃证据链

| 现象 | 频次/统计 | 含义 |
|------|----------|------|
| `WebSocket 接收错误: WinError 10054` | 高频 | Firefox 进程退出，BiDi WebSocket 被对端关闭 |
| `无法回收孤儿 session`（重连 6 次失败） | 高频 | ruyipage 检测旧 session 残留但无法接管 |
| `导航错误: Error: Address rejected` | 中频 | 代理连接被拒绝 |
| `导航超时: browsingContext.navigate (20s)` | 高频 | 页面加载超时（CF 软挑战壳永不就绪） |
| Application Error `0x80000003` | **113 次/12h** | Firefox MOZ_ASSERT 断言失败 |
| Application Error `0xc00000fd` | 1 次 | 栈溢出 |
| Application Error `0xc0000005` | 3 次 | 访问违规 |

崩溃时间分布与运行阶段完全对应：并发越高、页面失败率越高，崩溃越密。

## 根因链

```
CF 对单出口 IP 风控（有效窗口 30-60 分钟）
  → 页面返回 200 + 3KB 空壳（title 恒定、DOM 永不就绪）
  → 采集器 poll 超时 → FAILED
  → Firefox 在"页面加载失败 + BiDi 高频轮询"下触发 MOZ_ASSERT（0x80000003）
  → Firefox 崩溃退出
  → ruyipage 检测孤儿 session，重连 6 次失败
  → worker 卡死（poll 继续空转）或退出
  → 崩溃残留 Firefox 进程未被回收，进程数累积（8 → 91）
  → 91 × ~350MB ≈ 32GB 内存耗尽 → 同机应用 OOM
```

## 已排除的假设（实测）

| 假设 | 排除依据 |
|------|---------|
| 指纹注入（smart_fingerprint）导致崩溃 | 去掉后仍崩溃 |
| headless 模式导致崩溃 | 非 headless 同样崩溃 |
| 内存泄漏导致崩溃 | 崩溃是断言（0x80000003）非 OOM 异常；单实例长跑不崩 |
| 出口 IP 质量导致崩溃 | 单实例任意 IP 全通过；多实例同 IP 崩溃 |
| 轮换（quit+relaunch）导致崩溃 | 不轮换时也崩溃 |

## 稳定性改进清单（下次采集的执行规范）

1. **并发上限**：目标实例数 = 可用健康 IP 数（1 实例/IP），且 ≤ 4。
2. **IP 生命周期**：每 IP 采 ~300 页（低于风控窗口）主动换 IP，不要等失败；
   sidecar/节点重启换出口验证有效（5 分钟内全池恢复）。
3. **崩溃自愈**：worker 检测到 Firefox 崩溃（10054/孤儿 session）时 quit+relaunch，
   不要重连 6 次空转；连续 3 次崩溃则 worker 退出并停用该端口。
4. **内存护栏**：主进程监控 Firefox 进程总数，超过实例数 × 阈值时强制清理僵尸进程。
5. **失败快速识别**：CF 空壳页（title 恒定 + html < 10KB）立即标记 FAILED_CF_SHELL，
   不要 poll 25s 空转。
6. **不做 smart_fingerprint**：其 numpy/OpenBLAS 路径长跑报内存分配失败，且在线
   geo 探测慢；默认随机指纹 + 显式调试端口即可。
7. **进程清理**：停止时按 `multiprocessing.spawn` 特征杀 worker 子进程 —— 只杀
   主进程会漏掉 spawn 子进程（命令行不含业务名），残留 Firefox 继续空转。
8. **多进程并发注意**：ruyipage 的端口探测存在跨进程竞态（类级锁只在进程内），
   必须显式指定每实例唯一调试端口。

## 关联阅读

- [高并发 HTTP 采集控制面](./high-concurrency-http-collector-control-plane.md)：
  代理租约 / Sticky SID / AIMD / 故障恢复的控制面设计（curl_cffi 场景）
- 本文是"真实浏览器（BiDi）采集器"一侧的稳定性边界；两者组合 = 采集器全谱系
