---
schema_version: 2
id: anti-detection-ruyi-20251025-devtools-font-tokens-reference
document_type: reference
original_date: '2025-10-25'
archived_date: '2026-10-02'
scope:
  targets: [devtools-frontend]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20251025-01.md#chromium内核教程--devtools面板字体和大小源码层定制
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录作者给出的 front_end 目录，以及 application_tokens 与 design_system_tokens 两个文件名主干。扩展名和该目录下的相对路径未知。未打开源码树。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录平台块名、三个自定义属性的作者释义，以及 Windows 示例里的家族名和 12px。不抄 linux/mac 的上游字体栈。编译后变字体是作者自述。
relations:
  - type: derived_from
    target: ./ruyi-20251025-01.md#chromium内核教程--devtools面板字体和大小源码层定制
tags: [chromium, devtools, fonts, source-report]
---

# Chromium DevTools 面板字体令牌位置

这份参考只回答：如意私塾 2025-10-25 这篇把 DevTools 面板字体放在哪一层、哪个平台块、哪三个自定义属性上。它不覆盖 Blink 侧的字体枚举，也不提供编译流程。近邻查询 `devtools-frontend` 的 parameters 与 interfaces，以及 `devtools` 的 interfaces，都是 0 条。

来源没有编译失败时怎么退回，所以这里不是流程卡。作者写的“字体已经发生了改变”保持 source-report。

<a id="interfaces"></a>
## 接口与文件

DevTools 面板在作者文本里不是 C++ 界面。原句是面板“其实是一个前端页面，并非C++构成”，并由 HTML、CSS、TypeScript/JavaScript 组成，再打包进 Chromium。

作者给的目录是 `chromium\src\third_party\devtools-frontend\src\front_end`。同段说 application_tokens 文件定制面板图标，design_system_tokens 文件里才有字体相关代码。扩展名、以及 front_end 之下的子路径，正文没有写全。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 面板被写成前端页面，不是 C++ | s1；“并非C++构成” | source-report | 这篇对 DevTools 面板的组成说明 | 未对照源码文件类型 |
| C2 | 字体编辑面被放在 front_end 下的 design_system_tokens，图标才是 application_tokens | s1；目录与两个文件名主干 | source-report | 作者点名的这棵 devtools-frontend 树 | 没有完整相对路径 |

<a id="parameters"></a>
## 平台块与字体属性

作者说源码按 mac、linux、win 分块，自己改的是 platform-windows。三个属性的作者释义是：

| 属性 | 作者释义 |
|---|---|
| default-font-family | UI 文本（非代码） |
| monospace-font-family | 等宽文本（命令行、代码） |
| source-code-font-family | 代码编辑器区域（特化） |

Windows 示例把这三套 family 都写成 `"Microsoft YaHei", "SimHei", sans-serif`，并把等宽与代码字号写成 12px。linux、mac、screenshot-test 的上游家族串不录入。正文前面还说要改 css 里的 default-font；块内出现的名字是 `--default-font-family`。作者没有展示一个叫 default-font 的独立符号。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | Windows 修改点是 platform-windows，不是 mac/linux 块 | s1；“因此修改的是platform-windows” | source-report | 作者声明的 win 讲解 | 其他平台块只被点名 |
| C4 | 三个 family 属性分别对应 UI、等宽文本、代码编辑器 | s1；三行释义 | source-report | design_system_tokens 里作者标出的这三项 | 未核对选择器是否只作用于 DevTools |
| C5 | 作者示例使用 Microsoft YaHei、SimHei 和 12px | s1；platform-windows 替换块 | source-report | 这一处示例 | 不是设备采集到的字体指纹 |

## 验证与限制

作者最后写“编译之后，可以发现，字体已经发生了改变”。没有编译命令、没有对照图、也没有字体没变时的退回。这句话只作 source-report。缺扩展名或子路径时，不能自行补全文件位置。
