---
schema_version: 2
id: anti-detection-chromium-noimage-loading-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-noimage]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./19-disable-image-loading.md#一目标
    basis: unknown
  - id: s2
    ref: ./19-disable-image-loading.md#二给chromium子进程传参
    basis: unknown
  - id: s3
    ref: ./19-disable-image-loading.md#三禁用图片格式后缀的请求
    basis: unknown
  - id: s4
    ref: ./19-disable-image-loading.md#四禁用content-type为图片格式的请求
    basis: unknown
  - id: s5
    ref: ./19-disable-image-loading.md#4编译
    basis: unknown
  - id: s6
    ref: ./19-disable-image-loading.md#20250521-追加更新
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s6]
    basis: unknown
    limits: 只记录开关名和作者后来给出的 blink-settings 替代。没有 Chromium 版本，也没有本地启动记录。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3, s4]
    basis: unknown
    limits: 只按来源贴出的三个编译单元和符号整理。没有源码树对照，不能确认这些签名仍在当前分支。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s3, s4]
    basis: unknown
    limits: 分支只描述贴出的谓词。网络进程是否看得到 noimage、未列出的图片类型，以及 data URL 是否可显示，都未验证。
  - name: validation
    anchor: validation
    sources: [s5]
    basis: unknown
    limits: “没有图片请求”是作者对截图的自述。本轮未编译、未启动、未看图，不能写成运行观察。
relations:
  - type: derived_from
    target: ./19-disable-image-loading.md#一目标
tags: [chromium, noimage, imagesEnabled, unknown]
---

# Chromium 禁图开关与两层拦截

这张卡只回答：来源要把图片请求停在哪一层，自定义 `--noimage` 和后来的 `--blink-settings=imagesEnabled=false` 各是什么入口。它不是可照抄的编译流程。来源没有失败出口，作者的“无图”结论保持 `source-report`。

<a id="parameters"></a>
## 开关

作者的目标是启动时带上 `--noimage`，并声称这样可以从底层抹掉图片访问。同一处 renderer 命令行追加还转发已有的 `--fingerprints`；来源明确这两个开关不是同一个用途。

20250521 的追加把更优做法写成启动参数 `--blink-settings=imagesEnabled=false`，并说不必再走前面的补丁。来源没有写这个 blink setting 的版本范围，也没有把它和 `--noimage` 的组合行为说清楚。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 自定义入口是启动参数 `--noimage` | s1，`19-disable-image-loading.md:27` | unknown | 作者描述的自编译 Chrome | 未本地启动 |
| C2 | renderer 命令行同时转发 `fingerprints` 与 `noimage` | s2，`19-disable-image-loading.md:66` | unknown | 贴出的 `AppendRendererCommandLine` | 只看到 renderer 追加 |
| C3 | 追加更新给出 `--blink-settings=imagesEnabled=false` | s6，`19-disable-image-loading.md:206` | unknown | 作者称为更优的启动参数 | 版本与组合行为未知 |

<a id="interfaces"></a>
## 三个编译单元

贴出的落点是三个符号，不是一条已经核对过的调用链：

1. `\content\browser\renderer_host\render_process_host_impl.cc` 的 `RenderProcessHostImpl::AppendRendererCommandLine`。
2. `\net\url_request\url_request_context.cc` 的 `URLRequestContext::CreateRequest`，前面加了按路径后缀改写的函数。
3. `\third_party\blink\renderer\platform\loader\fetch\resource_fetcher.cc` 的 `ResourceFetcher::RequestResource`。

第四节标题写的是按 Content-Type 禁用。贴出的条件不是响应头，而是 `factory.GetType() == ResourceType::kImage`，并且 URL 字符串前四位是 `http`，然后 `ResourceForBlockedRequest(..., kOther, ...)`。

<a id="decision-flow"></a>
## 贴出的分支

```text
browser command line has noimage
  -> AppendRendererCommandLine copies noimage onto the renderer command line
  -> CreateRequest: path suffix in the listed set
       -> replace URL with a data:image URL
     else keep original URL
  -> RequestResource: type is kImage and URL begins with http and noimage
       -> ResourceForBlockedRequest kOther
```

后缀集合在贴出的代码里是 `.jpg`、`.jpeg`、`.png`、`.gif`、`.bmp`、`.tiff`、`.webp`、`.ico`，用路径最后一个点之后的子串做区分大小写的相等比较。没有扩展名就原样返回。SVG、AVIF，以及只出现在查询串里的图片，都不在这个数组里。

改写目标是一条 `data:image/png;base64` URL。本卡不转写那段载荷。fetcher 分支只处理前缀为 `http` 的 `kImage` 请求，因此它不会按标题去读响应 Content-Type，也不会拦住非 http(s) 图片 URL。

`AppendRendererCommandLine` 只显示把开关追加到 renderer。`URLRequestContext::CreateRequest` 所在进程是否本来就有浏览器启动参数，来源没有写。不能从这段贴码推出网络服务进程一定看得到 `--noimage`。

<a id="validation"></a>
## 作者验收与缺口

作者给出的构建命令是 `ninja  -C  out/Default chrome`，然后在命令行执行 `./chrome.exe --noimage`，并称一张图片请求链接都没有。页面上的结果图本轮没有做视觉审查。

来源没有写：开关拼错、网络进程未继承开关、扩展名不在列表、非 http 图片、以及 blink-settings 与自定义补丁互相覆盖时怎么退。这些都保持未知。感想段关于爬虫是否够用，不构成验收。
