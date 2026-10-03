---
schema_version: 2
id: chromium-macos-platform-surfaces-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-platform-spoof]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./02-macos-platform-spoof.md#二js如何判断操作系统是否为mac"
    basis: unknown
  - id: s2
    ref: "./02-macos-platform-spoof.md#三修改navigatorplatform"
    basis: unknown
  - id: s3
    ref: "./02-macos-platform-spoof.md#四修改navigatoruseragent"
    basis: unknown
  - id: s4
    ref: "./02-macos-platform-spoof.md#五修改navigatoruseragentdata"
    basis: unknown
  - id: s5
    ref: "./02-macos-platform-spoof.md#六修改font"
    basis: unknown
  - id: s6
    ref: "./02-macos-platform-spoof.md#七追加windowbarcodedetector"
    basis: unknown
  - id: s7
    ref: "./02-macos-platform-spoof.md#九测试效果"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3, s4, s5, s6]
    basis: unknown
    limits: 五个读取面都只对作者粘贴的片段有效。多处片段在原函数返回前截断。不记录 UA 全文或字体名单。
  - name: parameters
    anchor: parameters
    sources: [s2, s3, s5]
    basis: unknown
    limits: 开关名来自原文。空串查找、标识符不一致和选择计数是对粘贴文本的 static-review。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s5, s6]
    basis: unknown
    limits: 五个 JS 判断是作者列举的读取面，不是 creepjs 或 BrowserScan 的现行规则。字体样例按文本不能直接运行。
  - name: validation
    anchor: validation
    sources: [s7]
    basis: unknown
    limits: 作者写可以通过两个站点。启动命令的开关拼写与代码不一致。截图未审，本轮未运行。
relations:
  - type: derived_from
    target: "./02-macos-platform-spoof.md#四修改navigatoruseragent"
tags: [chromium, navigator, platform, unknown]
---

# Chromium `--platform` 的五个读取面

这张卡检索作者为了让页面把系统看成 macOS 而点名的五个面：`navigator.platform`、`navigator.userAgent`、`navigator.userAgentData`、字体和 `BarcodeDetector`。不收录 UA 全文、版本样值或字体名单，也不把粘贴片段当成可编译补丁。

<a id="interfaces"></a>
## 接口边界

`navigator.platform` 落在 `\third_party\blink\renderer\core\execution_context\navigator_base.cc` 的 `GetReducedNavigatorPlatform`。开关值为 `mac` 时片段返回 `MacIntel`。片段停在插入块结束，没有写出原函数的后续返回。

`navigator.userAgent` 和 `navigator.userAgentData` 都落在 `\components\embedder_support\user_agent_utils.cc`。前者是 `GetUserAgent`，后者是 `GetPlatformForUAMetadata`。元数据片段对 `mac`、`win`、`linux` 分别早返回 `macOS`、`Windows`、`Linux`，同样没有展示其余路径的原返回。作者找到的 `GetUserAgent` 签名和替换片段的签名不是同一个，注释里标了 133 版，并写明不同大版本不要直接覆盖。

字体落在 `\third_party\blink\renderer\core\css\css_font_family_value.cc` 的 `CSSFontFamilyValue::Create`。`BarcodeDetector` 不走这个开关：作者改的是 `\third_party\blink\renderer\platform\runtime_enabled_features.json5`，把 `Win` 的 status 写成 `stable`。那是编译期特性，片段里没有 `platform` 判断。

<a id="parameters"></a>
## 开关与文本形态

目标开关是 `--platform=mac`。UA 分支另外要求没有 `user-agent` 开关，且 `ignores` 里找不到 `useragent`。字体分支在 `ignores` 不含 `fonts` 时才进入；里面还读 `fingerprints` 和 `finger-log`。

UA 替换片段先声明空的 `ua`，再把 `result` 设成它，然后才在 `mac` 分支里对 `result` 做查找。空串上的查找不会发生替换，函数仍 `return result`。同一片段声明了 `replacemen`，后面赋值用的是另一个标识符。

字体选择调用是 `selectRandomFonts2(stringsAarry, 199, seed)`。同一行数组有 57 个引号项，而循环要凑满 199 个未选下标，按这段文本不会返回。作者后文写 mac 字体列表全部有效返回；那句话对应的是更后面的改写，但选择循环写在它前面。

<a id="risk-control"></a>
## 作者列出的判断

作者依次列出 `navigator.platform`、`navigator.userAgent`、`navigator.userAgentData`、字体和 `BarcodeDetector`。字体样例在非 async 箭头函数里使用 `await`，`FontFace` 的参数文本也没有闭合，不能当成可运行探针。`BarcodeDetector` 的页面判断是 `'BarcodeDetector' in window`。把 Win 特性标成 stable 会影响这个 Windows 构建上的所有页面，不随 `--platform` 切换。

<a id="validation"></a>
## 验证边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 作者称结果可以通过 creepjs 和 browserscan | s7 的目标节，来源第 26 行 | unknown | 作者自述 | 没有本轮运行 |
| C34 | 测试站点 1 是 BrowserScan | s7，来源第 399 行 | unknown | 作者列出的 URL | 本轮未访问；配图未审 |
| C35 | 测试站点 2 是 creepjs 的公开页 | s7，来源第 400 行 | unknown | 作者列出的 URL | 本轮未访问 |
| C36 | 文末启动命令把开关写成 `paltform` | s7，来源第 403 行 | static-review | 该命令文本 | 代码读取的开关名是 `platform`，二者对不上 |
| C19 | UA 片段从空字符串开始查找 | s3，来源第 213 行 | static-review | 粘贴的 GetUserAgent 替换 | 不是作者声称的失败；只说明片段不能按字面完成替换 |

没有闭合的失败出口。签名差异、空串查找、字体循环和命令拼写都还开着，因此不建 procedure。
