---
schema_version: 2
id: aosp-flag-secure-screen-capture-procedure
document_type: procedure
original_date: '2026-07-10'
archived_date: '2026-10-02'
scope:
  targets: [aosp-flag-secure-screen-capture]
  client: Android
  version: aosp_panther-user
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20260710-01.md#实机验收记录
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留来源点名的 WindowState、SurfaceControl 和 InputDispatcher 落点。补丁 diff 与刷机结果未在本轮打开。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: property 名和触摸字段范围都是来源文本。deviceId=4 与 source=0x5002 只对应来源所说的 Pixel 7，不是通用设备值。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 重启、dumpsys 分支和未实现的调用者分流都来自来源。本卡不补 uinput 或按调用者分流的实现。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 0 字节、isSecure 和触摸字段不固定都是来源写下的观察。本轮没有设备输出。
relations:
  - type: derived_from
    target: ./xfq-20260710-01.md#实机验收记录
tags: [aosp, flag-secure, surfaceflinger, inputdispatcher, source-report]
---

# AOSP 屏幕采集黑屏绕过：开关、验收与停止条件

这份流程回答：来源怎样在自编 ROM 里让外部截图、录屏和 scrcpy/qtscrcpy 不再因 secure layer 变黑，同时怎样判断该停。它不覆盖普通 App 发现投屏，也不覆盖 DRM。来源是 [屏幕采集绕过归档](./xfq-20260710-01.md#实机验收记录)。

同一棵 AOSP 笔记里的狐妖面具 shell、Java Crypto Hook 的 property，以及 jnilog 注入，都是别的 target。设备序列号、本机样本路径和 fastboot 所用序列号不写入本卡。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 系统 | 来源的验收构建是 `lunch aosp_panther-user`，刷完后 `ro.build.type=user`。设备产品名是 panther，也就是来源所说的 Pixel 7 | 不在这份带补丁的 user 构建上，不要把别的 ROM 的黑屏当成同一结论 |
| 补丁 | Window 级、Surface 子层、输入伪装分别对应来源点名的三组 patch。缺 Surface 那一组时，播放层仍会黑 | 只有窗口级改动就走 F2，不要把暂停态能看写成播放态已通过 |
| 开关 | `persist.rommgr.app.<package>.screen_secure_bypass=1` 与 `persist.rommgr.app.<package>.input_touch_spoof=1` | 属性不是 1 就走 F1 |
| 进程 | 勾选后要写入属性、`force-stop`，有启动入口再拉起。窗口和 Surface 多在创建时算完 | 只改属性不重启就走 F1 |

<a id="interfaces"></a>
## 框架落点

窗口级不改 App 的 flag。来源在 `WindowState.isSecureLocked()` 里写 `if (isXfScreenSecureBypassEnabled()) {`，命中后不再把该窗口当 secure layer。效果句是：App 仍可设置 `WindowManager.LayoutParams.FLAG_SECURE`，WindowManager 不再拿它做截图/录屏黑屏判断。

子层不要求 App 停止调用 setSecure(true)。覆盖点包括 SurfaceControl.Builder.build()、setFlags()、setSecure() 和 SurfaceControl.Transaction.setSecure()。来源原句是：命中后把 `SurfaceControl.SECURE` 从真正发给 SurfaceFlinger 的 flags 里清掉。

输入伪装在派发前改写 MotionEvent，落点是 `InputDispatcher`。它不是 uinput/KPM。

| claim_id | 结论 | 来源原句 | basis | 限制 |
|---|---|---|---|---|
| C1 | 窗口级开关让 `isSecureLocked` 走绕过分支 | `if (isXfScreenSecureBypassEnabled()) {` | source-report | 未对照补丁文件 |
| C2 | Surface 标志在进 SurfaceFlinger 前被清掉 | 命中后把 `SurfaceControl.SECURE` 从真正发给 SurfaceFlinger 的 flags 里清掉。 | source-report | 四个调用点只按来源列举 |
| C3 | App 自己的 FLAG_SECURE 调用仍保留 | 当前设计就是尽量不直接清 App 的业务 flag。 | source-report | 只说明设计，不是自测采集已分流 |

<a id="parameters"></a>
## 参数

两个属性按包名分开。屏幕采集用 `screen_secure_bypass`，触摸伪装用 `input_touch_spoof`。来源写 ROMManager 勾选后会立刻写属性并重启目标进程。

合成输入才会改：`deviceId < 0`，或 `source == TOUCHSCREEN(0x1002)`，或 source 命中 MOUSE。`ACTION_CANCEL 不改`。

来源给出的稳定字段是 `deviceId    = 4`、`source      = 0x5002`、工具类型 `FINGER`、`buttonState = 0`。抖动范围包括 `pressure      = 0.30~0.88；UP/POINTER_UP 为 0.22~0.48`，size、touch/tool 长短轴和 orientation 也在同一段里给出，不再逐项另作常数。seed 是 `targetPackageName + targetOwnerUid + downTime + eventTime + pointerId + action`。

`deviceId=4` / `source=0x5002` 是 Pixel 7 实测值。换机型时来源要求改从 InputReader 取真实触屏特征，而不是沿用这两个数。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 确认是带三组补丁的 user 构建，再把对应属性写成 1，force-stop 后按目标自己的启动方式拉起。需要指定 Activity 或 data uri 时不要用 monkey | 属性为 1，进程是新的 | 属性不是 1 或没重启，走 F1 |
| S2 | 看 SurfaceFlinger 里该包的 `isSecure` 和 `hasProtectedContent`，再做截图、短录屏或无窗口 scrcpy | 关闭绕过时来源记录 `protected_off.png size=0`；播放层案例里关闭时 screencap 为 0 bytes | `hasProtectedContent=true` 走 F3；`isSecure=true` 走 F2 |
| S3 | 只在要验收触摸伪装时，对同一目标做注入点击，并读 demo 看到的 MotionEvent | 关闭时来源记下 `source=TOUCHSCREEN(0x1002)` 且 `deviceId=-1`。开启后 `均被 demo 判定为真机触摸特征`，pressure/size 不固定 | 字段仍是固定的合成触摸，走 F1；要证明物理注入则走 F4 |
| S4 | 对照验收四条。不要把暂停态 UI 能看，写成播放用 SurfaceView 已通过 | 播放层来源记录 `isSecure=false` 且 `hasProtectedContent=false` | 任一验收条对不上就停在对应失败出口 |

<a id="outputs"></a>
## 输出

输出是三件能对上来源句子的记录：属性值、SurfaceFlinger 里该层的 secure 标志，以及截图或录屏是否仍是 0 字节。触摸伪装另加一组 MotionEvent 字段，用来看 pressure/size 是否不再固定。

不输出设备序列号、样本在开发机上的路径，也不把某一次文件字节数写成换机构建后仍然成立的常数。来源里的 393917、约 1.3M 和 central_mean 只说明那次 Pixel 7 记录，不是本卡的通过线。

<a id="acceptance"></a>
## 验收

1. 关闭 `screen_secure_bypass` 并重启后，来源对窗口 demo 的期望是 `protected_off.png size=0`。播放案例里 `screencap /sdcard/ev_off.png -> 0 bytes`，且该 SurfaceView `isSecure=true`。
2. 打开开关并重启后，播放层应变成 isSecure=false。来源把该案例写成：这不是 DRM：`hasProtectedContent=false`。它只是普通 secure layer 没被吃掉。
3. 开启触摸伪装后，连续注入点击应 `均被 demo 判定为真机触摸特征`，且 `pressure/size` 不固定。稳定字段仍要落在来源写的 deviceId、source、FINGER 和 buttonState 上。
4. App 仍能走设置 `FLAG_SECURE` / `setSecure(true)` 的路径。本卡不把“App 自查标志被清掉”当成通过。

<a id="failure-exits"></a>
## 失败出口

F1：属性不是 1，或目标进程没重启。来源写明：只改 property 不重启目标进程很容易看不到效果。旧窗口和旧 Surface 可能仍是 secure。停止把这次采集当成绕过失败或成功。

F2：`isSecure=true`：说明 Window 或 SurfaceControl 绕过没覆盖到这个 layer。先分开看是窗口 flag 还是 BLAST 子层。不要再加一条 App 层的“检测到投屏”。

F3：`hasProtectedContent=true`：不是本功能范围，可能是 DRM/protected buffer。来源写明不处理真实 DRM、Widevine、TEE protected path。停止把 secure-flag 补丁说成已覆盖受保护缓冲区。

F4：触摸字段在别的机型上仍写死 Pixel 7 的 `deviceId=4` / `source=0x5002`，或目标核对的是比 InputDispatcher 更底层的事件来源。来源把后者留到以后的 uinput/KPM，本卡停在这里，不补那条注入路径。

F5：目标 App 自己用 MediaProjection、captureLayers 或 captureDisplay 做自测。来源已经指出矛盾：`我明明打开了 FLAG_SECURE，但自测录屏/截图没有黑屏。` 按调用者分流只是留坑，`这个留坑先只记录，不在当前版本实现。` 停止把当前全局清 secure 说成已经对自测采集保持黑屏。

普通 App 实时发现 scrcpy/qtscrcpy 也不在本流程里。来源写 `它不是“普通三方 App 准确检测到投屏”的方案。` 用落盘、路由名或外接显示去猜，会误导验收。
