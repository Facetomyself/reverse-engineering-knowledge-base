---
schema_version: 2
id: aosp13-system-ca-bind-mount-procedure
document_type: procedure
original_date: '2026-06-14'
archived_date: '2026-10-02'
scope:
  targets:
    - AOSP 13 system CA bind-mount
  client: AOSP panther
  version: android13_r78 REL, sepolicy 33.0
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260614-02.md#为什么不能简单地写-systemetcsecuritycacerts"
    basis: source-report
  - id: s2
    ref: "./xfq-20260614-02.md#因此采用的设计唯一合规路径"
    basis: source-report
  - id: s3
    ref: "./xfq-20260614-02.md#sepolicy-冻结测试关键约束"
    basis: source-report
  - id: s4
    ref: "./xfq-20260614-02.md#-sepolicy-调通踩坑链真实编译逐轮定位非臆测"
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1, s2, s4]
    basis: source-report
    limits: 只整理来源对 android13_r78 REL 的 init bind-mount 设计。文件表仍写 public domain.te 与 coredomain appdomain，踩坑链结尾收窄到 system_server appdomain 且规则在 private。两处未在正文对齐。
  - name: parameters
    anchor: prerequisites
    sources: [s1, s3]
    basis: source-report
    limits: neverallow 行号、类型名和 33.0 冻结差量只对来源点名的 REL 树。不是通用 Android 证书安装参数。
  - name: validation
    anchor: acceptance
    sources: [s2, s4]
    basis: source-report
    limits: 编译退出码、同 inode 和 UI 分段是作者报告。本轮未编译、未刷机。同 inode 不等于目标 App 已经信任该 CA。
relations:
  - type: derived_from
    target: "./xfq-20260614-02.md#因此采用的设计唯一合规路径"
tags:
  - aosp
  - sepolicy
  - cacerts
  - source-report
---

# Android 13 REL 上把用户 CA 并入系统证书目录

这张流程只回答：在来源点名的 android13_r78 REL / panther 树上，为什么不能把目录 relabel 成系统 cacerts 再挂载，以及作者改成了哪条 init bind-mount 路径、用什么编译和挂载现象当验收。它不替代通用环境卡里的 remount 后 adb push。那条路径是另一个目标，而且正是本篇写明会被 neverallow 否决的做法。

<a id="prerequisites"></a>
## 前提与输入

- 构建树是来源写的 android13_r78，`PLATFORM_VERSION_CODENAME.TP1A := REL`，因此 `PLATFORM_SEPOLICY_VERSION = 33.0`，不等于 `10000.0` 的 TOT。`se_freeze_test` 对 `public/`、`private/` 与 `prebuilts/api/33.0/{public,private}/` 做 `diff -r -q`，任何差异即失败。
- `domain.te:560`：只有 init（以及来源原文里的 otapreopt_chroot 例外）能在 `system_file_type` 目录上 `mounton`。自定义域不能在 cacerts 上 bind-mount。
- `domain.te:510`：除 kernel 外不能把对象 relabel 成 `system_security_cacerts_file`。来源因此否定“准备目录、restorecon 成 cacerts 标签、再挂载”。
- 编译期证书要先变成 AOSP `.0`。文件名必须等于 `openssl x509 -subject_hash_old`。来源的 Reqable CA 示例是 `d8e119df.0`，主体与有效期只属于该示例，不外推。
- 运行期新增证书的暂存目录是 `/data/misc/xf_cacerts/added/<hash>.0`。合并目录是同树下的 `store/`。
- 本轮没有这棵构建树，也没有设备。序列号不进入本卡。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 先核对两条 neverallow 是否仍否决“自定义域 mounton”和“relabel 成 cacerts 标签”。 | `domain.te` 里对应 neverallow 的主体例外。 | 例外已经放宽则本流程不适用，走 F1；否则 S2。 |
| S2 | 用 `subject_hash_old` 把要内置的 PEM 收成 `.0`，经 `cacerts_xf` 打进 `/system/etc/security/cacerts/`。 | 文件名与 hash 一致的 `.0`，以及 `PRODUCT_PACKAGES` 里的 `cacerts_xf`。 | hash 与文件名不一致则停止，Android 按该 hash 查找；否则 S3。 |
| S3 | `post-fs-data` 里只让 init 建 `/data/misc/xf_cacerts/{added,store}`，`exec_start xf_cert_prep`，再由 init 把 `store` bind-mount 到 cacerts。prep 域复制系统证书并叠上 `added/*.0`。 | init.rc 片段、`xf_cert_prep` 服务和脚本。 | 挂载动作不在 init 上，走 F1；否则 S4。 |
| S4 | 新类型走 `core_data_file_type`，读权限不要写成 `allow domain`。来源踩坑链把主体收到 `{system_server appdomain}`，并把类型和 allow 放进 `private/`。 | policy 文件位置与 allow 主体。 | 文件表若仍写 `public/domain.te` 和 `{coredomain appdomain}`，以踩坑链结尾为准，并走 F1 核对是否又编过；否则 S5。 |
| S5 | 每一处 sepolicy 改动同步复制到 `prebuilts/api/33.0/` 对应文件。 | `diff -r -q` 无差异。 | 有差异走 F2；否则 S6。 |
| S6 | bind-mount 之后内置证书和原装证书在同一目录，运行时没有标记。用构建期 genrule 扫 `files/*.0` 生成 `xf_cacerts_manifest.txt`，再给证书打 `isBaked`。 | manifest 路径和 `listBakedCerts` / `listAospCerts`。 | 要在 UI 上区分两类证书却没有这份清单，走 F3；否则 S7。 |
| S7 | 编 `selinux_policy sepolicy_freeze_test xf_cert_prep`，再按来源的 system+product、不去 data 的刷法检查挂载。ROMManager 写入 `added/` 后，来源写明当前要到下次开机才重新 prep。 | 见验收。 | 挂载或冻结测试不闭合走 F2/F3。 |

正文是行为真源。S4 的最终主体来自踩坑链和“核心教训”，不是文件表的第一稿。

<a id="outputs"></a>
## 输出

- `cacerts_xf` 打进系统证书目录的 `.0`，文件名等于 `subject_hash_old`。
- `xf_cert_prep` 二进制，以及 init 在 `post-fs-data` 上的目录、oneshot 服务和 bind-mount。
- `xf_cacerts_data_file` 的类型、file_contexts，以及来源最终落在 `private/` 的 allow。
- 与 `prebuilts/api/33.0/` 同步后的 sepolicy 树。
- 可选的 `xf_cacerts_manifest.txt`：来源当时只有一行 `d8e119df`。
- 作者报告的挂载现象：系统路径与 `store/` 中同一 `.0` 同 inode，挂载点文件数等于 store。这不是本轮复测产物。

<a id="acceptance"></a>
## 验收

以下全部是来源自述，basis 保持 source-report。本轮未执行这些命令。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `m selinux_policy sepolicy_freeze_test xf_cert_prep` 被写成 `build completed successfully` / `XF_BUILD_EXIT=0`。 | s4，`xfq-20260614-02.md` 第 122 行 | source-report | 来源那次 sepolicy 构建 | 未保留完整日志。 |
| C2 | `/system/etc/security/cacerts/d8e119df.0` 与 `/data/misc/xf_cacerts/store/d8e119df.0` 同 inode，挂载点文件数 127 等于 store 127。 | s2 的后续真机节，第 154 行 | source-report | 来源报告的那一次启动 | 只说明 bind-mount 把 store 盖到了该路径。 |
| C3 | `xf_cert_prep` 的 exit status 0，且来源称无 xf 相关 avc denied。 | 第 155 行 | source-report | 同一份启动报告 | 没有 avc 原文。 |
| C4 | manifest 落地为 `d8e119df`；证书页把 ROM 内置默认展开、AOSP 预装默认折叠。 | 第 185-191 行 | source-report | 来源报告的 UI 重构刷机 | UI 分段不是 TLS 握手验收。 |

反例：浏览器或 Reqable 能抓到某个包，来源没有把它写成这次验收。待办里的“Reqable 抓包是否被系统信任”在后文没有对应结果。

<a id="failure-exits"></a>
## 失败出口

F1：主体用了 `domain`。来源第 1 轮是 294 个 neverallow，因为 vendor 域撞上 `domain.te:824` 对 `core_data_file_type` 的禁止。收成 `{coredomain appdomain}` 后仍有 11 个，包括只允许 zoneinfo 的 coredomain neverallow，以及 `xf_cert_prep` 使用了不在 `dac_override_allowed` 里的 capability。再收成 `{system_server appdomain}` 之后，public type 会缺 Treble `private/compat` 映射；把类型改成 private 后，`public/domain.te` 会报 `unknown type`。来源把 allow 挪到 `private/domain.te` 后才写成成功。文件表若与此不一致，停止用文件表当最终规则。

F2：`se_freeze_test` 的 `diff -r -q` 失败。REL 上每一处 public/private 改动都要同步到 `prebuilts/api/33.0/`。不同步就不要把“policy 已改”当成可编过。

F3：开机后系统证书路径与 `store/` 不同 inode、prep 非 0、或出现 xf 相关 avc。停止声称用户 CA 已进入系统信任。来源另写：写入 `added/` 后当前要重启才重新 prep。只被 system 侧引用的类型不应留在 public。仿 zoneinfo 做全域可读要维护约 14 处豁免，来源明确不采用。
