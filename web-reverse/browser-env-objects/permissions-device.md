# 权限 / 设备 / 环境探测参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

权限和设备对象是浏览器能力状态。它们通常影响 navigator 子对象、media/geolocation/clipboard 成功失败、事件回调和指纹内容。

## 检测面

- PermissionStatus：`name/state/onchange` 与 listener 表；`state` 通常为 `granted/denied/prompt`；权限变化触发 change 事件，target/currentTarget 指向 PermissionStatus；同一 permission name 的状态与相关设备 API 行为一致。
- BatteryManager：`charging/chargingTime/dischargingTime/level` 与 listener 表；`level` 是 0 到 1 数值；charging 与两个 time 互相解释；change 事件先更新状态再回调。
- NetworkInformation：`effectiveType/rtt/downlink/saveData` 与 listener 表；网络字段属于同一网络状态，不随机组合；change 后再读得到新状态。
- MediaQueryList：原始 query 字符串、当前 `matches`、listener 表；`matchMedia(query)` 返回 MediaQueryList；`matches` 基于 window/screen/viewport/display 状态派生；`addEventListener('change')` 与旧式 `addListener` 操作同一 listener 状态。
- Clipboard：方法返回 Promise，读写受权限与安全上下文影响。
- Notification：`permission` 与 `requestPermission()` 结果一致。
- Orientation：`screen.orientation.type/angle` 与 screen/window 尺寸方向一致；`orientation.lock()` 返回 Promise 或抛异常，不是空函数。
- 一致性：`navigator.permissions.query` 返回的 PermissionStatus 影响对应 API 行为；`navigator.connection` 与 NetworkInformation 是同一状态来源；matchMedia 结果与 screen/visualViewport/layout 状态同源；device motion/orientation 事件字段与权限和设备状态一致。

## 常见坑

- `matchMedia` 直接返回 true/false，目标读 matches/addEventListener 断裂。
- permission 状态与 geolocation/media/clipboard 行为矛盾，query granted 但调用拒绝。
- Battery 字段组合不可能（charging 且 dischargingTime 同时有效）。
- `orientation.lock` 空函数同步返回 undefined。
- change 事件先回调后更新状态，回调内读到旧值。
- media query 结果与 viewport/resize 状态不同源。

## 观察优先级

- 先看浏览器证据里权限/设备入口：permissions.query 的 name 清单、matchMedia query、battery 读取还是 orientation。
- 记录各 permission name 的实际 state 与对应 API 行为配对。
- 核对 matchMedia 的 query 字符串与 viewport/screen 状态。
- 记录设备字段组合（battery、network、orientation）的互相解释关系。
- 未触达的权限/设备面不预补；触达面先对齐状态再定值。

## 补环境要点

- permission 状态表集中维护，query 结果与设备 API 行为配对。
- matchMedia 返回 MediaQueryList 语义对象，matches 与 viewport 同源。
- battery / network 字段组合互相解释，change 事件先更新状态再回调。
- orientation.type / angle 与 screen 尺寸方向配套。
- addEventListener 与 addListener 共用同一 listener 状态。
- 未触达的权限/设备面不预补。
