---
schema_version: 2
id: koohai-20260105-jsdom-proxy-lookup-reference
document_type: reference
original_date: '2026-01-05'
archived_date: '2026-10-02'
scope:
  targets:
    - khbox
    - jsdom
    - node
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20260105-01.md#二js-侧jsdom-与-khbox-的准备工作"
    basis: source-report
  - id: s2
    ref: "./koohai-20260105-01.md#三node_contextifyccvm-全局属性拦截与三级查找"
    basis: source-report
  - id: s3
    ref: "./koohai-20260105-01.md#1-getter-proxypropertygetter"
    basis: source-report
  - id: s4
    ref: "./koohai-20260105-01.md#2-setter-proxypropertysetter"
    basis: source-report
  - id: s5
    ref: "./koohai-20260105-01.md#2-getfromkhbox从-khboxenvfuncs-取补丁函数"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2]
    basis: source-report
    limits: 只保留来源对 setJsdomWindow、PropertyGetterCallback 和 CreateProxyObject 的描述。未对照 Node 源码，粘连 demo 不能当补丁。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s5]
    basis: source-report
    limits: envFuncs 优先是来源的下一步。GetFromKhBox 在本篇写明还未生效。未运行 demo。
  - name: parameters
    anchor: parameters
    sources: [s3, s4]
    basis: source-report
    limits: lookup_key 只来自本篇伪代码。setter 以外的 has 和属性定义来源写明尚未完成。
relations:
  - type: derived_from
    target: "./koohai-20260105-01.md#三node_contextifyccvm-全局属性拦截与三级查找"
tags:
  - khbox
  - jsdom
  - source-report
---

# KhBox 接入 jsdom 时的查找顺序与 envFuncs 键

这张卡只回答：来源如何描述自定义 Node 的 VM 沙箱在第一次访问 `document`、`navigator` 等名字时先查哪里，以及 `KhBox.envFuncs` 的键怎样由基名和属性名拼出来。不提供可编译补丁。作者日志里的 UA 和 cookie 原值不进入本卡。

作者把 demo 写成「成功了一点」。那是来源自述。同一篇把 `GetFromKhBox` 写成还未生效。2026-01-12 的原型链和 Illegal invocation、2026-01-25 的 addon `jsDispatch` 都不是这条 contextify 查找。

<a id="interfaces"></a>
## 接入点

来源称 jsdom 的底层已经自动使用，jsdom 缺少的函数可以自己定义，例子是 `navigator_userActivation_get`。demo 调用 `KhBox.setJsdomWindow(dom.window)`，把 jsdom 的 window 交到 C++。自定义函数挂在 `KhBox.envFuncs`。

C++ 侧，首次访问由 `node_contextify.cc` 的 `PropertyGetterCallback` 接管。拿到 jsdom 对象后不直接返回，而是 `CreateProxyObject` 包一层带拦截器的 ProxyObject。JS 侧准备的函数，来源说后面要由 `GetFromKhBox` 和 `CallKhBoxFunction` 找到；这条查找在本篇还没生效。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 来源称 jsdom 底层已经自动接入，jsdom 没有的函数可以自己定义，并点名 navigator_userActivation_get。 | 完成了jsdom 的底层自动使用。遇到自定义函数比如navigator_userActivation_get 等jsdom缺少的，可以自己定义。 | ./koohai-20260105-01.md:37 | source-report | 完成与否是作者自述，本轮未运行。 |
| C2 | demo 通过 KhBox.setJsdomWindow 把 jsdom 的 window 交到 C++ 层。 | KhBox.setJsdomWindow(dom.window) | ./koohai-20260105-01.md:47 | source-report | 只见于粘连后的 demo 文本，不是可编译补丁。 |
| C3 | 从 jsdom 拿到 document 这类对象时，来源用 CreateProxyObject 包一层带拦截器的 ProxyObject。 | CreateProxyObject | ./koohai-20260105-01.md:105 | source-report | 未对照 node_koohai_proxy.cc。 |

<a id="decision-flow"></a>
## 查找顺序

来源写的全局属性三级查找是：沙箱本地对象，Node 原有的 global_proxy，然后才是 koohai 扩展。扩展内部先 `GetFromJsdom(env, context, name, &result)`，再 `GetFromKhBox(env, context, name, &result)`。`document`、`navigator`、`location` 按名字从已登记的 jsdom window 上取。

下一步清单要求自己的 `KhBox.envFuncs` 优先于 jsdom；不写就用 jsdom，或者在方法不存在时抛异常。这和正文现状不一致：`GetFromKhBox` 一节只有「还未生效」。来源还写明目前只在 `PropertyGetterCallback` 里做了一点修改，直接 set 未处理的 proxy 对象时还要改 `PropertySetterCallback`。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C4 | 来源把 KhBox.envFuncs 写成应优先于 jsdom；不写则走 jsdom，或在方法不存在时抛异常。 | 自己实现的方法KhBox.envFuncs 应该优先于jsdom。如果不写 就是默认jsdom，或者抛异常方法不存在。 | ./koohai-20260105-01.md:89 | source-report | 这是 next 清单，不是本篇已经生效的行为。 |
| C5 | 本篇只声明改了 PropertyGetterCallback，set 等路径还要改 PropertySetterCallback。 | 目前只在PropertyGetterCallback内部进行了一点修改 | ./koohai-20260105-01.md:93 | source-report | 未看到对应 C++ diff。 |
| C6 | koohai 扩展的查找先调用 GetFromJsdom。 | GetFromJsdom(env, context, name, &result) | ./koohai-20260105-01.md:142 | source-report | 调用顺序来自来源对 node_contextify.cc 的转述。 |
| C7 | GetFromJsdom 之后再调用 GetFromKhBox。 | GetFromKhBox(env, context, name, &result) | ./koohai-20260105-01.md:143 | source-report | 同篇写明这条补丁查找还未生效。 |
| C8 | GetFromKhBox 一节的正文只有「还未生效」。 | 还未生效 | ./koohai-20260105-01.md:173 | source-report | 不能把 envFuncs 优先写成已经落地。 |

<a id="parameters"></a>
## 键名

Proxy getter 从 internal field 取出基名和属性名，拼成 `lookup_key = base_name + "_" + property + "_get"`。来源举的键是 `navigator_userActivation_get`、`document_cookie_get`、`location_href_get`。`CallKhBoxFunction` 找到并返回值就用补丁，否则回退到 jsdom 原始对象的 `Get`。

setter 把后缀换成 `_set`，来源的例子是 `document_cookie_set` 和 `location_href_set`。`has`、`deleteProperty` 和属性定义被写成后续再完善，本篇没有给出键名。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C9 | getter 的 envFuncs 键是基名、属性名和 _get 用下划线拼接。 | lookup_key = base_name + "_" + property + "_get" | ./koohai-20260105-01.md:203 | source-report | 只是本篇伪代码，未对实际字符串求值。 |
| C10 | 来源举的 getter 键包括 navigator_userActivation_get，以及 document_cookie_get、location_href_get。 | navigator_userActivation_get | ./koohai-20260105-01.md:204 | source-report | 键名可以记录；日志里的 UA 和 cookie 原值不记录。 |
| C11 | envFuncs 没有返回值时，getter 回退到 jsdom 原始对象的 Get。 | 否则回退到 jsdom 原始对象 | ./koohai-20260105-01.md:209 | source-report | 回退条件写在伪代码里，未单步验证。 |
| C12 | setter 使用同一拼法，后缀改为 _set。 | lookup_key = base_name + "_" + property + "_set" | ./koohai-20260105-01.md:221 | source-report | 来源写明 has 和属性定义仍待完善。 |

## 验证与限制

未运行 demo，也没有把 `node_contextify.cc`、`node_koohai_interceptor.cc`、`node_koohai_proxy.cc` 和正文对过。公众号导出的代码围栏是粘连的，不能当补丁。日志中的 UA 和 cookie 赋值原值故意不摘录。

本篇没有验收条件，也没有失败出口。`GetFromKhBox` 未生效、setter 未改完，所以不能建成流程。缺的键是否抛异常，来源只在下一步里提到，没有给出观察点。
