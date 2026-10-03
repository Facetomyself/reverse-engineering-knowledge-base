---
schema_version: 2
id: sequential-port-contention-rho-reference
document_type: reference
original_date: '2026-03-27'
archived_date: '2026-10-02'
scope:
  targets: [sequential-port-contention]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260327-01.md#顺序端口竞争单线程也能做
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 ρ 的定义、同端口/不同端口判读，以及来源列出的代际合并。没有指令序列，不能拿来测量。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源声称的浏览器覆盖和“稳定但非唯一”这个边界。不记录采集步骤。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 准确率、耗时、噪声和虚拟化/仿真差异都是论文转述。KVM 与 TCG 只说明信号是否还在，不是环境选择说明。
relations:
  - type: derived_from
    target: ./ruyi-20260327-01.md#顺序端口竞争单线程也能做
tags: [sequential-port-contention, source-report]
---

# 顺序端口竞争的代际信号边界

这篇卡检索的是：来源如何定义单线程端口竞争的 ρ，代际被合并到哪一层，以及哪些来源报告的条件会让这个信号不能再当 CPU 代际证据。不收录测量实现。

<a id="parameters"></a>
## 比值与分组

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>ρ = time(分组) / time(交替)</td><td>s1，源文件第 89 行</td><td>source-report</td><td>该文对顺序端口竞争的定义</td><td>没有测量代码</td></tr>
<tr><td>C2</td><td>如果ρ ≈ 1：两条指令走相同端口，没有并行空间</td><td>s1，源文件第 91 行</td><td>source-report</td><td>同一对指令的判读</td><td>未本地测量</td></tr>
<tr><td>C3</td><td>如果ρ > 1：两条指令走不同端口，交替排列能并行化</td><td>s1，源文件第 92 行</td><td>source-report</td><td>同一对指令的判读</td><td>未本地测量</td></tr>
<tr><td>C4</td><td>crc32（P1）+ aesdec（P0）</td><td>s1，源文件第 101 行</td><td>source-report</td><td>来源举的 Whiskey Lake 原生例子</td><td>同行 ρ = 1.8 不能外推到别的 CPU</td></tr>
<tr><td>C5</td><td>Coffee Lake  |  Coffee Lake, Whiskey Lake, Comet Lake</td><td>s1，源文件第 178 行</td><td>source-report</td><td>来源的六组分类目标</td><td>不能拆到具体 SKU</td></tr>
</table>

<a id="risk-control"></a>
## 信号能说明什么

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C6</td><td>所有主流浏览器都存在这个侧信道，包括专门做隐私保护的Tor和Brave。</td><td>s1，源文件第 143 行</td><td>source-report</td><td>来源点名的浏览器实验</td><td>WebAssembly 的 ρ 已被稀释，且没有当前版本复测</td></tr>
<tr><td>C7</td><td>CPU代际指纹的价值不在于唯一性，而在于</td><td>s1，源文件第 303 行</td><td>source-report</td><td>来源对代际指纹用途的限定</td><td>不能单独当设备标识</td></tr>
</table>

<a id="validation"></a>
## 来源报告的边界

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C8</td><td>（50个CPU，来自真实网页采集的不受控环境）：  ** 95%  **</td><td>s1，源文件第 192 行</td><td>source-report</td><td>该评估集转述</td><td>不是本地结果</td></tr>
<tr><td>C9</td><td>10  |  ** 95%  ** |  ** 12秒  **</td><td>s1，源文件第 222 行</td><td>source-report</td><td>多数投票表的这一行</td><td>单条 trace 在同表只有 70%</td></tr>
<tr><td>C10</td><td>5-8个stress线程（超过核数）：75%准确率</td><td>s1，源文件第 231 行</td><td>source-report</td><td>四核 i5-8365U 的满载转述</td><td>核数未满时来源另写 93%</td></tr>
<tr><td>C11</td><td>所有版本都正确分类。</td><td>s1，源文件第 238 行</td><td>source-report</td><td>该 CPU 上 Chrome 91–101 与 Firefox 89–100</td><td>更早且无 SIMD 的版本不在这句里</td></tr>
<tr><td>C12</td><td>在QEMU/KVM虚拟化环境中，顺序端口竞争完全有效。</td><td>s1，源文件第 250 行</td><td>source-report</td><td>来源的硬件虚拟化观察</td><td>只说明信号还在</td></tr>
<tr><td>C13</td><td>在QEMU TCG（全系统仿真）模式下，顺序端口竞争  ** 完全失效  **</td><td>s1，源文件第 254 行</td><td>source-report</td><td>来源的全系统仿真观察</td><td>此时 ρ 不能再解释成端口分配</td></tr>
</table>

## 验证与限制

`browser-fingerprint` 的 risk-control 是宿主对象总纲，`cpu-fingerprint` 与 `webassembly` 没有同模块卡片。降计时精度、插入屏障、打乱指令和性能计数器都没有可复用参数。反仿真用法和自动化环境建议没有写入本卡。所有数字保持 source-report。
