---
schema_version: 2
id: chromium-taskbar-badge-icon-reference
document_type: reference
archived_date: '2026-10-02'
scope:
  targets: [chromium-taskbar-badge]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./06-taskbar-badge-icon.md#一目标"
    basis: unknown
  - id: s2
    ref: "./06-taskbar-badge-icon.md#三修改chromium源码"
    basis: unknown
  - id: s3
    ref: "./06-taskbar-badge-icon.md#四备注"
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: unknown
    limits: 只记录开关名、作者示例和粘贴里的尺寸与钳位。不把示例数字当成唯一合法值，也没有 Windows 版本或 DPI 合同。
  - name: interfaces
    anchor: interfaces
    sources: [s2]
    basis: unknown
    limits: 只整理 `chrome/browser/win/app_icon.cc` 粘贴中的三个辅助函数和 `GetAppIcon` 调用顺序。未编译，未核对符号是否仍在。绘制函数正文不转写。
  - name: validation
    anchor: validation
    sources: [s2, s3]
    basis: unknown
    limits: 来源没有编译后的检查步骤。图片未审。备注里的另一篇只给了链接，不能当成这条路径的失败出口。
relations:
  - type: derived_from
    target: "./06-taskbar-badge-icon.md#三修改chromium源码"
tags: [Chromium, Windows, taskbar, HICON, unknown]
---

# Chromium Windows 任务栏数字徽章的图标接缝

这张卡定位 `--notice-number` 在来源粘贴里如何进入 `GetAppIcon`。它不是画图标的实现副本，也不是 procedure：来源没有编译后的验收步骤，也没有失败出口。Firefox 任务栏编号笔记是另一产品，不覆盖这条 Chromium 路径。

<a id="parameters"></a>
## 开关与粘贴中的常数

作者的目标是启动参数 `--notice-number`，示例值写在目标句里，用来在任务栏图标上叠数字，以便多开时区分进程。粘贴里的 `CreateNumberIcon` 把大于 999 的数钳成 999。徽章位置被写成常数 16 和 48，注释掉的右上角计算没有启用。数字图标宽度传入 64，底图先缩到 96。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 开关名是 `notice-number`，作者用它在任务栏图标上叠数字 | *   目标一：传入参数`--notice-number=899`，可以在chromium的任务栏图标上，覆盖一个对应数字的提示。 | s1 06-taskbar-badge-icon.md:25 | unknown | 作者描述的 Windows 任务栏图标 | 示例数字不是取值合同 |
| C2 | 大于 999 的数字在生成函数里被钳位 |     if (number > 999) number = 999; | s2 06-taskbar-badge-icon.md:61 | unknown | `CreateNumberIcon` 粘贴 | 未运行 |
| C3 | 徽章横坐标在粘贴里是常数 16 |   const int badgeX = 16; | s2 06-taskbar-badge-icon.md:156 | unknown | `CombineIconWithBadge` 粘贴 | 注释中的右上角计算没有启用 |
| C4 | 数字图标与底图使用 64 和 96 |       HICON num = CreateNumberIcon(notice_number, 64); | s2 06-taskbar-badge-icon.md:290 | unknown | `GetAppIcon` 追加片段 | 未测不同 DPI |

<a id="interfaces"></a>
## GetAppIcon 调用顺序

文件是 `/chrome/browser/win/app_icon.cc`。作者在 `GetAppIcon` 里读取 `notice-number`，用 `std::istringstream` 解析整数，然后 `LoadIcon`、`CreateNumberIcon`、`ResizeIconTo`、`CombineIconWithBadge`，最后返回合成图标。未命中开关时仍走原来的 `LoadIcon`。构建命令是 `ninja -C out/Default chrome`。

三个辅助函数的 GDI 正文不转写。静态上能看到的边界是：`ResizeIconTo` 在 `GetIconInfo` 失败时返回空指针；同函数在缩放前用白色画刷铺满目标矩形。所示头部引用有 `command_line.h`，粘贴的引用块里没有看到 `<sstream>`，但后面使用了 `std::istringstream`。这只说明粘贴不完整或未自洽，不是本轮编译失败记录。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C5 | 修改点是 Windows 的 app icon 实现文件 | *   打开：`/chrome/browser/win/app_icon.cc` | s2 06-taskbar-badge-icon.md:42 | unknown | 所示路径 | 未核对当前树 |
| C6 | 命中开关后才走合成分支 |   if (base_command_line->HasSwitch("notice-number")) { | s2 06-taskbar-badge-icon.md:285 | unknown | `GetAppIcon` 粘贴 | 未看到开关注册 |
| C7 | 整数值用 istringstream 从 ASCII 开关读出 |       std::istringstream(base_command_line->GetSwitchValueASCII("notice-number")) >> notice_number; | s2 06-taskbar-badge-icon.md:287 | unknown | 该行 | 引用块是否包含 sstream 以粘贴为准，未编译 |
| C8 | 合成顺序是数字图标、缩放、再叠加 |       resp = CombineIconWithBadge(resp, num); | s2 06-taskbar-badge-icon.md:292 | unknown | 紧挨着的三行调用 | 资源释放是否成对未知 |
| C9 | `GetIconInfo` 失败时缩放函数返回空指针 |    if (!GetIconInfo(hOriginalIcon, &original_info)) { | s2 06-taskbar-badge-icon.md:210 | unknown | `ResizeIconTo` 开头 | 调用方没有对应的空指针分支 |

<a id="validation"></a>
## 未闭合的验收

目标段只有示意图链接，没有编译后的检查步骤。图片未审。备注把“找窗口句柄加徽章”指到另一篇日志，没有把步骤写进本文，因此不能当作失败出口，也不能把这篇升成 procedure。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C10 | 构建命令只写到 ninja chrome | ninja -C out/Default chrome | s2 06-taskbar-badge-icon.md:306 | unknown | 作者给出的命令 | 本轮未执行 |
| C11 | 另一条窗口句柄路线只留了外链 | *   之前记录了一种方法：任务栏图标右上角加提示徽章，是通过找到当前窗口句柄来做的，感兴趣的可以传送： | s3 06-taskbar-badge-icon.md:312 | unknown | 备注的一行 | 外链正文不在本篇，未展开 |

未知：Chromium 版本、任务栏是否仍走 `GetAppIcon`、高 DPI 下 16/48 是否仍落在图标内，以及白色底刷对透明通道的实际效果。
