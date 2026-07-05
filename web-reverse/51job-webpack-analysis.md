# 51job Webpack 模块自吐分析

## 基本信息

| 项目 | 值 |
|------|-----|
| 目标 | `we.51job.com/pc/search` |
| 框架 | Vue 2.7.14 + Webpack 4 (webpackJsonp 模式) |
| 模块总数 | **1634** 个 factory |
| 已加载模块 | **1310** 个 |
| 有 exports 模块 | **429** 个 |
| 分析时间 | 2026-07-03 |

## Webpack 架构

```
入口: webpackJsonp = []  (pre-v5 array chunk loading)
    │
    ├── we-vue-bundle.js  → Webpack bootstrap (module 1017) + Vue runtime
    ├── 12 个 app-*.js chunk (同步加载的入口 chunk)
    │   ├── app-06837ae4 (5+ modules)
    │   ├── app-253ae210 (5+ modules)
    │   ├── app-e2e93592 (含 module 0/1/2 — 入口模块)
    │   └── ...
    └── chunk-72c3a0aa (异步 chunk, 含搜索组件)
```

## 关键模块识别

### 加密 / 签名

| 模块 ID | 库 | 关键 exports | 用途推测 |
|---------|-----|-------------|---------|
| `8429` | **CryptoJS** | MD5, HmacMD5, SHA1, HmacSHA1, SHA256, HmacSHA256, SHA224, SHA384, SHA512, HmacSHA384, HmacSHA512, enc, algo, x64 | API 签名 / token 生成 |
| `d233` | query-string | encode, decode, arrayToObject, combine, isBuffer, compact | URL 参数编解码 |

### 网络请求

| 模块 ID | 库 | 关键 exports | 用途推测 |
|---------|-----|-------------|---------|
| `cebe` | **Axios** | request, get, post, put, delete, patch, interceptors, Axios, CancelToken, create | 所有 HTTP 请求 |

### 监控 / 埋点

| 模块 ID | 库 | 关键 exports | 用途推测 |
|---------|-----|-------------|---------|
| `0580` / `7bea` | **ARMS RUM** | ArmsRum, ApiCollector, ClickCollector, ExceptionCollector, PerfCollector, PvCollector, WebVitalsCollector, WhiteScreenCollector, hackFunction, restoreHackFunction | 阿里云前端监控 |
| `17e5` | **神策 SDK** | init, JSBridge, vtrackcollect, vapph5collect, detectMode, registerFeature, registerInterceptor, store | 用户行为埋点 |
| `6f69` | RUM Utils | ConfigManager, EventType, interceptFunction, restoreFunction, generateGUID, generateTraceId | 监控工具函数 |

### UI 框架

| 模块 ID | 库 | 关键 exports |
|---------|-----|-------------|
| `8bbf` | **Vue 2.7.14** | version, use, mixin, component, directive, extend, nextTick, set, delete, observable |
| `b2ff` | Element-UI utils | getValueByPath, generateId, valueEquals, escapeRegexpString, kebabCase, capitalize, isIE, isEdge, isFirefox |
| `c4d2` | Element-UI DatePicker | formatDate, parseDate, toDate, isDate, getI18nSettings, getDayCountOfMonth |
| `bd0c` | Vue-Baidu-Map | BaiduMap, BmView, BmMarker, BmPolyline, BmGeolocation |
| `2ef0` | **Lodash** (全量) | 307 exports |
| `c1df` | **Moment.js** | 40 exports |

### 业务组件 (module `5615`)

15 个候选人搜索筛选组件：
- CandidateActiveTimePicker, CandidateAgePicker
- CandidateCompanyTypePicker, CandidateEducationInfoPicker
- CandidateEngageFunctionPicker, CandidateEngageIndustryPicker
- CandidateExpectSalaryPicker, CandidateExpectSalaryRangePicker
- CandidateExpectedFunctionPicker, CandidateExpectedIndustryPicker
- CandidateGenderPicker, CandidateGraduationDatePicker
- CandidateJobExpectationPicker, CandidateLanguageRequirementPicker
- CandidateLivingAreaPicker

### 其他

| 模块 ID | 库 | 关键 exports |
|---------|-----|-------------|
| `18a0` | 微信 JSSDK | config, ready, checkJsApi, onMenuShareTimeline, onMenuShareAppMessage |
| `PCApplyJob` | 投递组件 | PCApplyJob |
| `html2canvas` | 截图 | html2canvas |
| (dict 相关) | 字典数据 | getCityDictData, getDictData, getDictTranslate, getSearchJobAreaDictData |
| (cookie 相关) | Cookie 工具 | getCookie, setCookie |
| `785a` | DOMTokenList polyfill | item, contains, add, remove, replace, toggle |

## API 签名路径推断

基于模块分析，搜索 API 调用链路推测：

```
Vue Component (搜索按钮点击)
    ↓
Axios (cebe) → HTTP request
    ↓
[可能经过] CryptoJS (8429) → 生成签名参数
    ↓
we.51job.com/api/job/search-pc
```

待定位: 签名生成函数（`CryptoJS` + 自定义参数拼接逻辑）

## 自吐方法

已注入 spy 模块 `__WP_SPY_MODULE__`，通过 `webpackJsonp.push` 获取 `__webpack_require__` 引用：

```javascript
// 模块缓存在 require.c (installedModules)
// 模块 factory 在 require.m (modules)
// 公有路径在 require.p

window.__WP_REQUIRE__ = require;
window.__WP_CACHE__ = require.c;  // 1310 个 loaded modules
```
