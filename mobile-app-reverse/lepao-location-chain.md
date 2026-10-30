---
schema_version: 2
id: lepao-location-chain
document_type: archive
original_date: unknown
archived_date: "2026-10-30"
scope:
  targets: [lepao]
  client: app
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: 如何定位系统定位的链路呢？（乐跑）
    reason: 原始 PDF 未提供可公开定位的链接
relations:
  - type: supplements
    target: ../anti-detection/risk-control-location.md#来源正文
source_completeness: partial
tags: [lepao, amap, location, art, source-report]
---

# 乐跑：从 LocationManager 到高德回调（来源报告）

来源 PDF 的标题是「如何定位系统定位的链路呢？」，页眉反复出现「乐跑」。包名写成 `com.lptiyu.tanke`，业务类落到 `school_run`。没有作者、没有日期、没有公开链接。定位风控的一般讨论见 [风控之关于定位](../anti-detection/risk-control-location.md)。本文只保留这份 PDF 文本层里的 App 链路，不把一般 GNSS 理论再写一遍。

作者的成功、拒绝码和「坐标不变」都是 source-report。本次没有安装应用，没有 hook，没有复核高德 SDK。

## 清洗与完整性说明

- 公开正文是文本层的清洗浓缩，不是逐页誊录。页眉「乐跑」和页码 `n / 21` 经核对是每页重复的版式，归档时去掉。正文里的「乐跑」和数字常量保留。未写入正文的抽取原文留在仓外证据，不进入本子仓。
- 回执：21 页都有文本层；图片 4 处、矢量 244 处未抽取；无内嵌文件；`complete=false`，`source_cleanup_allowed=false`。图和矢量里的调用图无法恢复。
- 多张表在文本层里被拆行。能按表头读出的已还原，并在对应节标明；对不齐的不猜。
- `f7995k` 一处写成 80，后一页标题又写成 30m，紧接着的代码注释仍是大于 80 米。冲突原样保留，不取其中一个当结论。
- 混淆字段号（如 `f8684p`）和行号来自作者当时的反编译，版本未知，缺图不能复核。
- 作者日志里的经纬度样值不入库。
- 代码按 PDF 换行重排，不补原文没有的语句。完整性为 partial。这不是 procedure。

## 来源正文

### 系统入口

作者当时不知道 App 的坐标从哪来，先把 `LocationManager` 的入口铺开。文本里的两条应用侧路线是：

- `FusedLocationProviderClient.getLastLocation()`，取最后一次缓存位置。
- `requestLocationUpdates(LocationRequest, LocationCallback)`，在 `onLocationResult` 里取最新坐标。作者示例把优先级写成 `PRIORITY_HIGH_ACCURACY`、间隔 2000 ms、最小距离 1 米，回调线程是主 looper，不用时 `removeLocationUpdates`。

系统原生则是 `LocationManager.getLastKnownLocation` 和 `requestLocationUpdates` + `LocationListener.onLocationChanged`。provider 名被写成 `gps`、`network`、`passive`、`fused`。

作者认为国内很多机器没有或不开 GMS，应用会用高德、百度或腾讯的定位 SDK，但这些 SDK 底下仍会调用系统 API。

### 高德怎样注册系统定位

作者 hook 了 `LocationManager.requestLocationUpdates` 的三个重载（4 参、带 `Looper` 的 5 参、带 `Executor` 的 5 参），打印参数个数和第一个参数，并打一次栈。作者记录到 5 参重载，provider 同时有 `gps` 和 `network`。栈被写成：

```text
LocationManager.requestLocationUpdates
  com.amap.api.col.3sl.u5.K (GpsLocation)
  com.amap.api.col.3sl.u5.p
  com.amap.api.col.3sl.b2$d.handleMessage (AmapLocationManager)
  Handler / Looper
  com.amap.api.col.3sl.b2$e.run
```

作者称高德自己建了定位线程。选 `Location.getLatitude` 做下一跳的理由是：不管上层怎么混淆，读坐标仍会走 getter；字段本身 hook 不到。作者称跳过前两次调用后再打印栈，看到：

```text
Location.getLatitude
  AMapLocation.<init>
  u5.g → u5.l → u5$c.onLocationChanged
  LocationListener.onLocationChanged
  LocationManager$LocationListenerTransport
```

系统投递被概括为 `u5$c.onLocationChanged` → `u5.g` → `AMapLocation.<init>`。

### App 入口与梆梆

静态候选有两条：`com.lptiyu.tanke.utils.u0` 实现 `AMapLocationListener`，且作者称是全 App 唯一实现；`RunHelper.s0(AMapLocation)` 的参数类型就是 `AMapLocation`。直接 hook 不到。作者把原因归到梆梆，并画了一张三层表。文本层能读出的是：

| 层 | 机制 | 作者看到的症状 | 这次是否命中 |
| --- | --- | --- | --- |
| A | Java2C，方法体抽到 native | hook 到了也只有一次 JNI 分发 | 命中，作者称可绕 |
| B | 方法处于 JIT/AOT | hook 装上且不报错，运行时零命中 | 作者称这是主要拦截 |
| C | 完整性 / 反调试 | hook 某些点会让 App 自毁 | 表在抽取里没有「这次是否命中」的独立单元格 |

层 A：作者称 Java2C 都经过 `cv`，末尾变参是方法表下标 JID；配合一份 18851 条 JID 到方法名的静态映射看执行流。调用形状被写成 `JniLib.cV(声明类, this, 实参..., JID)`，再进 `libdexjni.so` 的方法表。作者的日志钩子读取参数数组最后一个元素的 `intValue()` 当 JID。映射表本身不在 PDF 文本里。

层 B：作者用 ART 的 `ArtMethod.entry_point_from_quick_compiled_code_` 解释 hook 为何失效。解释执行时每次读这个字段再进解释器；JIT/AOT 之后调用点可以是硬编码 `bl` 或内联，不再读被 Frida 换掉的 entrypoint。Frida 侧被写成四步：找到 `ArtMethod`，备份原入口，换成自己的 trampoline，再进 JS。作者的结论是：梆梆 Java2C 的方法已经在机器码里，改 ART 字段也不被那条 `bl` 读取。

层 C 在抽取里没有单独展开，只留在上表。

### deopt

作者把 deoptimization 解释成从优化代码退回解释执行，并在退回时把寄存器和栈上的值搬进解释器帧。ART 里的触发包括显式 `Instrumentation::DeoptimizeMethod` / `DeoptimizeEverything`，以及类型检查失败、单实现假设破裂、JIT 重新编译、GC 挪对象后的代码修补、调试器 attach。

作者强调不能把 entrypoint 直接改成解释器入口，因为方法可能正在别的线程上跑。来源列出的顺序是：entrypoint 改成 deoptimization entry；给线程标上需要迁移的帧；线程在下一个 checkpoint 做 frame materialization；不在栈上的方法只作废代码。效果被收成两句：目标方法自己退回解释器；所有指向它的调用点作废。之后 Frida 换过的 entrypoint 才会被再次读取。

作者随后对 App 自己的监听器做了单方法降级，类和方法是 `com.lptiyu.tanke.utils.u0.onLocationChanged(AMapLocation)`。这是来源里的调用，本次未执行。

### 三条位置从哪来

作者区分的标记是：

| 标记 | 是谁 | 数据怎么来 |
| --- | --- | --- |
| `prov=gps` | 系统 gps provider | GNSS。作者称已用 test provider 替换 |
| `prov=network` | 系统 network provider | 基站 / Wi-Fi 粗定位 |
| `prov=lbs` | 高德自己的定位服务 | Wi-Fi 列表加基站，上传 `apilocate.amap.com`，服务器查指纹库返回坐标 |

`lbs` 被定义成 Location Based Service，和系统 network provider 不是同一条。作者称它的输入是周围 Wi-Fi 和基站，输出是服务器库里的参考点坐标。经纬度样值不入库。

作者把 App 侧链路写成：

```text
LocationManager.requestLocationUpdates("gps" / "network")
  → u5$c.onLocationChanged
  → AMapLocation.<init>（从 android.location.Location 复制）
  → u0.onLocationChanged
  → RunHelper.s0（作者标成距离/配速的消费点）
```

高精度模式 `Hight_Accuracy`（来源拼写）下，作者称 SDK 内部同时有 GPS、lbs、基站和 Wi-Fi。网络结果先返回；室内没有 GPS fix 时就采用网络结果。网络结果来自服务器上的 Wi-Fi/基站指纹，设备不动则指纹不变，作者用来解释距离一直为 0。

在 `u0.onLocationChanged` 里，作者 dump 的字段含义是：`err=0` 表示定位成功；`type=2` 被写成非 GPS（1=GPS，2=网络/基站）；`prov=lbs`；`acc` 被作者承认是 hook 改过的假值，真实值未知；`mock=false`；时间戳在变但坐标不变。作者由此认为回调是活的，内容不是缓存，而是高德读了 GPS 数据却没有采用，选了网络定位。

### 作者怎样理解 error 15

作者枚举 `AMapLocationClientOption.AMapLocationMode`，日志是 `0=Battery_Saving`、`1=Device_Sensors`、`2=Hight_Accuracy`。初始化路径被写成 `u0.b()` 里 `setLocationMode(Hight_Accuracy)`。运行期 `u0.g(int)` 会再切：作者称 1 是 `Device_Sensors`，其他是 `Hight_Accuracy`。作者把 `setLocationMode` 和 `u0.g` 都改成总是走 `Device_Sensors`，用来关掉网络通道、只留 GPS。之后的日志被写成 `err=15`、`type=0`、`prov=gps`，坐标为 0,0。作者把 15 解释成高德拒绝 test provider。

test provider 的限制按原文是：一旦注册，监听 gps 的应用收到的不是 GNSS，而是塞进去的坐标，并且每个 `Location` 会被盖上 mock 标记。作者称 `getLatitude` 能读到所设坐标，但 App 上的距离不动；`u0` 收到的是 `AMapLocation`，不是原始 `Location`。`errorCode` 是 `AMapLocation` 才有的字段，所以 15 是高德填的。

作者把 `Location.isFromMockProvider()`、Android 12+ 的 `isMock()`，以及 `AMapLocation.isMock` 换成恒返回 false，结论是高德的判定不读这三个 Java getter。`setMock` 的 hook 没有命中。作者据此认为系统给 test provider 打 mock 标记不走 public `Location.setMock()`，可能是内部直接改 `mIsMock`，或新版本换了 API。来源写「也可以试试 hook setMockEnable，我没试」，该尝试没有结果。

作者考虑过在 `AMapLocation` 交给 App 的瞬间改混淆字段，并给出当时的对照：`f8684p` 是 errorCode，`f8688t` 是 latitude，`f8687s` 是 locationType，`D` 是 mock。具体坐标不入库。这是作者的字段笔记，不是已复核的稳定偏移。

### SDK 内部分派

初始化顺序按原文是：`new AMapLocationClient`，`setLocationListener`，`setLocationOption`，`startLocation`。`b2.U()` 对应 `stopLocation`。模式表被写成：`Battery_Saving` → 1，只网络；`Device_Sensors` → 2，只 GPS；`Hight_Accuracy` → 3，双通道。作者用 `C0()` 里的判断说明：模式不是 `Device_Sensors` 时才 `g(1000, ...)` 启动网络定位。这被用来解释强制 `Device_Sensors` 之后 `prov=lbs` 不再出现。

GPS 注册是 5 参 `requestLocationUpdates("gps", interval, distance, listener, looper)`，外加 `registerGnssStatusCallback` 和旧的 `addGpsStatusListener`。

`u5.g` 的加工顺序，作者列了七步。第 5 步是 mock 判定：`k.a(loc, f8001q)` 为真则 `setMock(true)` 且 `setTrustedLevel(4)`；若 option 不允许 mock，前 4 次静默 return，之后 `err=15` 并把坐标清零。前面还有去超时消息、`new AMapLocation(location)`、`k.a(loc)` 拒绝空和 0,0、`setProvider("gps")`、`setLocationType(1)`。后面是卫星数、`D`/`E`/`J`（作者标成纠偏、其他校正、时间戳校正），再缓存并经 `z(loc)` 送出。规则的具体谓词在缺图的反编译里，这里不补。

出口 `b2.P` 被作者写成比较松：errorCode 非 0 时把 locationType 设为 0；errorCode 为 0 时做坐标范围检查，越界则 err=8；provider 为 `gps` 或 `network` 就直接分发给 `f6333j` 里的 listener。作者称这个出口不查 mock 标志和卫星数。

另一张通道表：

| 源 | provider | type | 作者写的特点 |
| --- | --- | --- | --- |
| GPS | gps | 1 | 精度高，室内无 fix |
| 系统网络 | network | — | 基站 / Wi-Fi 粗定位 |
| 高德服务器 | lbs | 2 | Wi-Fi 指纹查库，坐标恒定 |

作者对「谁的分高」的更正是：没有一个全局融合器；GPS 和 LBS 各自过滤，谁先完成谁先交给同一个出口 `b2.P`。前面采用 LBS，是因为 LBS 能通过自己的弱过滤，而 GPS 在 mock 判定里被丢掉。

GPS 结果的消息路径被写成：`u5.g` 成功则 `z(loc)`，消息 what=10，进 `b2.L`，再 `w`，再 `b2.P`。APS / 内部请求是 what=13：对象非空就直接 `P`，否则交付 err=33 的失败对象。

### 80 与 240，以及文中的 30

`f7994j` 初始 240，`f7995k` 初始 80。作者称这两个常量会被 Bundle 覆盖，也写了服务器可以改默认值。

- `u5.o`：不需要地址，或者与上一点距离大于等于 `f7994j`（240 米）时直接返回；否则沿用上一次逆地理地址。作者把 240 米叫做逆地理刷新门限。
- `u5.t`：间隔和「现在减去上次是否超过 interval−8000」构成时间门；距离上一次上报点大于 `f7995k` 才 `sendMessage`（what=5）。代码注释写的是大于 80 米。
- 紧挨着的小标题却写「阈值2: f7995k=30m」和「GPS 上报门限」。30 与 80 同时出现，抽取不能判定哪一个是笔误。两者都保留，不合并。

作者还提到 `u5` 的 `f(i10)` 和 `filters/a.java` 会做平滑或去噪，没有贴出滤波器实现。

卫星：遍历 `gnssStatus`，用 `usedInFix` 计数，结果放进 `f8001q`。作者称这个数既参与 mock 判定，也会写进结果。

`b2.w` 在交付前组装质量报告：定位模式、`setGPSSatellites`、`setGpsStatus`、Wi-Fi 是否可用、网络类型；locationType 为 1 或 provider 为 gps 时 `setNetUseTime(0)`。`setInstallHighDangerMockApp` 表示本机是否安装了作者所说的已知虚拟定位应用，结果放进质量报告交给 App。应用名只有「如 Fake Location 之类」，没有清单。

### AMapLocation 的自有字段

作者写 `AMapLocation` 继承 `android.location.Location`，但重写 getter/setter，经纬度存在自己的 `f8688t` / `f8689u`，不走 `super`。构造函数先 `super(location)`，再把 `getLatitude` / `getLongitude` 抄进这两个字段。errorCode、locationType、mock 分别对应前面的 `f8684p`、`f8687s`、`D`。作者用这一点解释：test provider 之后，高德仍可能读到「正常坐标」，因为读的是它自己复制出来的字段，而不是父类字段。字段号未在本次复核。

PDF 在这一构造函数处结束，没有单独的结论节。

## 复用边界

类名、消息号、error 8/15/33、模式枚举和 240 米门限都是这份 PDF 的 source-report。30 米与 80 米的冲突没有被消掉。4 张图和 244 处矢量没有看。混淆字段号不能当成当前高德 SDK 的布局。作者日志中的坐标不入库。不能把「距离不动」或 err=15 当成本次观察，也不能把单方法 deopt 或改字段写成已验收的做法。
