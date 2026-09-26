# Chromium 无头检测绕过（一～二）

## 收录说明

本文由「Chromium 指纹浏览器编译系列」（CSDN：w1101662433 / fivcan）中同一主题的 2 篇合并而成（2026-09-26 整理）：原系列第 9 篇与第 25 篇「（二）」。各节标题为「篇次：原标题」，原文内容未删减；原文 3 处 setext 二级标题（文字下一行 `--`）改写为 `###` 以低于各篇的二级标题；原文链接与发布日期在原归档中未记录。合并前文件：`09-headless-detection-bypass.md`（保留路径）、`25-headless-detection-bypass-v2.md`（已删除）；系列目录保留原编号，第 25 篇位置改为指向本文。

## 第一篇：Chromium 无头检测绕过

来源：CSDN 博客系列（w1101662433 / fivcan）· 原系列第 9 篇 · 原文链接与发布日期未随归档记录

### 简介

*   无头浏览器就是没有界面的浏览器，但用作爬虫时会出现一些特征，会被网站识别为爬虫。
*   这里我们从修改chromium源码的级别，抹去这些特征。

### 一、修改webdriver

*   打开文件 third\_party\\blink\\renderer\\core\\frame\\navigator.cc

```c
//bool Navigator::webdriver() const {
//  if (RuntimeEnabledFeatures::AutomationControlledEnabled())
//    return true;
//
//  bool automation_enabled = false;
//  probe::ApplyAutomationOverride(GetExecutionContext(), automation_enabled);
//  return automation_enabled;
//}

bool Navigator::webdriver() const {
  return false;
}
```

### 二、修改rtt

*   打开文件 third\_party/blink/renderer/modules/netinfo/network\_information.cc

```c
//uint32_t NetworkInformation::rtt() {
//  MaybeShowWebHoldbackConsoleMsg();
//  std::optional<base::TimeDelta> override_rtt =
//      GetNetworkStateNotifier().GetWebHoldbackHttpRtt();
//  if (override_rtt) {
//    return GetNetworkStateNotifier().RoundRtt(Host(), override_rtt.value());
//  }
//
//  if (!IsObserving()) {
//    return GetNetworkStateNotifier().RoundRtt(
//        Host(), GetNetworkStateNotifier().HttpRtt());
//  }
//
//  return http_rtt_msec_;
//}

uint32_t NetworkInformation::rtt() {
  return 150;
}
```

### 三、修改Notification.permission

*   打开文件 third\_party/blink/renderer/modules/notifications/notification.cc

```c
String Notification::PermissionString(
    mojom::blink::PermissionStatus permission) {
  switch (permission) {
    case mojom::blink::PermissionStatus::GRANTED:
      return "granted";
    case mojom::blink::PermissionStatus::DENIED:
      //return "denied";
      return "default";
    case mojom::blink::PermissionStatus::ASK:
      return "default";
  }

  NOTREACHED();
  //return "denied";
  return "default";
}
```

### 四、修改user-agent

针对无头浏览器的HeadlessChrome：

*   打开文件C:\\src\\chromium\\src\\headless\\lib\\browser\\headless\_browser\_impl.cc  
    修改：

```c
//const char kHeadlessProductName[] = "HeadlessChrome";
const char kHeadlessProductName[] = "Chrome";

```

### 五、针对无头的plugin检测

*   修改third\_party\\blink\\renderer\\modules\\plugins\\navigator\_plugins.cc

```c
// static
//DOMPluginArray* NavigatorPlugins::plugins(Navigator& navigator) {
//  return NavigatorPlugins::From(navigator).plugins(navigator.DomWindow());
//}

// static
DOMPluginArray* NavigatorPlugins::plugins(Navigator& navigator) {
  DOMPluginArray* pluginsArray = NavigatorPlugins::From(navigator).plugins(navigator.DomWindow());
  pluginsArray->UpdatePluginData();
  return pluginsArray;
}
```

*   再修改 third\_party\\blink\\renderer\\modules\\plugins\\dom\_plugin\_array.cc

```c
void DOMPluginArray::UpdatePluginData() {
  if (should_return_fixed_plugin_data_) {
    dom_plugins_.clear();
    //if (IsPdfViewerAvailable()) {
      // See crbug.com/1164635 and https://github.com/whatwg/html/pull/6738.
      // To reduce fingerprinting and make plugins/mimetypes more
      // interoperable, this is the spec'd, hard-coded list of plugins:
      Vector<String> plugins{"PDF Viewer", "Chrome PDF Viewer",
                             "Chromium PDF Viewer", "Microsoft Edge PDF Viewer",
                             "WebKit built-in PDF"};
      for (auto name : plugins)
        dom_plugins_.push_back(MakeFakePlugin(name, DomWindow()));
    //}
    return;
  }
  
```

## 第二篇：Chromium 无头检测绕过（二）

来源：CSDN 博客系列（w1101662433 / fivcan）· 原系列第 25 篇 · 原文链接与发布日期未随归档记录

### 一、无头检测简介：

*   无头检测(`Headless Detection`)就是检测用户是否在无头浏览器。只要检测到，那百分百是爬虫。
*   无头检测我们多数使用这个站：https://bot.sannysoft.com/
*   之前写过一篇文章：[插眼传送](https://blog.csdn.net/w1101662433/article/details/139345179)，绕过了部分检测，但是不全，这里我们继续追加。

### 二、WebGL Render

*   无头模式下，不会使用gpu，所以检测webGL render是否有关键字"`SwiftShader`"，如果有那就是无头。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/46461877fe48488dbd59fa642aa96841.png)

*   打开文件 `\third_party\blink\renderer\modules\webgl\webgl_rendering_context_base.cc`

```c
case WebGLDebugRendererInfo::kUnmaskedRendererWebgl:
      if (ExtensionEnabled(kWebGLDebugRendererInfoName)) {
        if (IdentifiabilityStudySettings::Get()->ShouldSampleType(
                blink::IdentifiableSurface::Type::kWebGLParameter)) {
          RecordIdentifiableGLParameterDigest(
              pname, IdentifiabilityBenignStringToken(
                         String(ContextGL()->GetString(GL_RENDERER))));
        }
        //return WebGLAny(script_state,
        //                String(ContextGL()->GetString(GL_RENDERER)));

        // 追加 ==========================================
        base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
        int seed;
        if (base_command_line->HasSwitch("fingerprints")) {
          std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> seed;
        }else{
          auto now = std::chrono::system_clock::now();
          std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
          seed = static_cast<int>(now_time_t);
        }
			String tmp = " (NV/" + String(std::to_string(seed)) + ")";
			String render = (String(ContextGL()->GetString(GL_RENDERER)) + tmp);
			std::string renderer = render.Utf8();

			// 将全部SwiftShader替换成NVDIA
			std::string searchString = "SwiftShader";
	        std::string replaceString = "NVDIA";

			size_t start_pos = 0;
			while ((start_pos = renderer.find(searchString, start_pos)) != std::string::npos) {
				renderer.replace(start_pos, searchString.length(), replaceString);
				start_pos += replaceString.length();
			}
	        return WebGLAny(script_state, String(renderer));
	        // 结束追加 ==========================================

	        }
	      SynthesizeGLError(
	          GL_INVALID_ENUM, "getParameter",
	          "invalid parameter name, WEBGL_debug_renderer_info not enabled");
	      return ScriptValue::CreateNull(script_state->GetIsolate());
```

> 这里的逻辑是将`SwiftShader`关键字全部改成`NVDIA`了。

### 三、window.chrome

*   正常有头的chromium内核浏览器打开F12都是有`window.chrome`的，但无头浏览器会返回`undefined`。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/9b7c4a48a9e649c987659d0f6da798ba.png)

*   打开文件 `\content\renderer\render_frame_impl.cc`

```c
void RenderFrameImpl::DidClearWindowObject() {
  TRACE_EVENT_WITH_FLOW0("navigation", "RenderFrameImpl::DidClearWindowObject",
                         TRACE_ID_LOCAL(this),
                         TRACE_EVENT_FLAG_FLOW_IN | TRACE_EVENT_FLAG_FLOW_OUT);
  if (enabled_bindings_ & BINDINGS_POLICY_WEB_UI)
    WebUIExtension::Install(frame_);

```

*   替换为：

```c
void RenderFrameImpl::DidClearWindowObject() {
  TRACE_EVENT_WITH_FLOW0("navigation", "RenderFrameImpl::DidClearWindowObject",
                         TRACE_ID_LOCAL(this),
                         TRACE_EVENT_FLAG_FLOW_IN | TRACE_EVENT_FLAG_FLOW_OUT);
  //if (enabled_bindings_ & BINDINGS_POLICY_WEB_UI)
  //  WebUIExtension::Install(frame_);
    WebUIExtension::Install(frame_);
```

> 这里就是把if条件注释掉。

### 四、plugins插件

> 有头浏览器都会装5个默认插件，但无头会变成0个。\
> 这个上篇无头博客改了，但是改的有点乱，会被cloudflare检测到，所以上篇这里作废，我们重改。

*   打开：`\third_party\blink\renderer\modules\plugins\dom_plugin_array.cc`

```c
bool DOMPluginArray::IsPdfViewerAvailable() {
  auto* data = GetPluginData();
  if (!data)
    return false;
  for (const Member<MimeClassInfo>& mime_info : data->Mimes()) {
    if (mime_info->Type() == "application/pdf")
      return true;
  }
  return false;
}

```

*   替换为：

```c
bool DOMPluginArray::IsPdfViewerAvailable() {
  //auto* data = GetPluginData();
  //if (!data)
  //  return false;
  //for (const Member<MimeClassInfo>& mime_info : data->Mimes()) {
  //  if (mime_info->Type() == "application/pdf")
  //    return true;
  //}
  //return false;
  return true;
}

```

> 让这个函数一直返回`true`即可。

### 五、无头userAgent

*   上篇博客给userAgent去掉了`HeadlessChrome`特征，但是发现他一直不变，因为无头的UA和有头的UA是两套逻辑。这里我们给无头UA加些随机数。

*   打开：`\headless\lib\browser\headless_browser_impl.cc`


```c
std::string HeadlessBrowser::GetProductNameAndVersion() {
  return std::string(kHeadlessProductName) + "/" + PRODUCT_VERSION;
}
```

*   替换为:

```c
std::string HeadlessBrowser::GetProductNameAndVersion() {
  //return std::string(kHeadlessProductName) + "/" + PRODUCT_VERSION;

  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  int tmp = 0;
  if (base_command_line->HasSwitch("fingerprints")) {
    std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> tmp;
  }
  int fooversion = 124;
  return "Chrome/" + std::to_string(fooversion) + ".0.0.0 BigTom/" + std::to_string(tmp);
}
```

### 六、结语：

*   无头模式主要是为了后续做linux版本做准备，但博主太穷，没钱升级电脑。
*   所以短时间linux版的是搞不了了。
