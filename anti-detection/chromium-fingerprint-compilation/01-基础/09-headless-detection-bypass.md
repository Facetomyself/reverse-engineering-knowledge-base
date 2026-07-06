简介
--

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

五、针对无头的plugin检测
---------------

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
