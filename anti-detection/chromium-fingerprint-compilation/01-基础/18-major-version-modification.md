关于更改chromium源码\-修改大版本
---------------------

*   上篇博客实现了更改chromium小版本：[插眼传送](https://blog.csdn.net/w1101662433/article/details/140542646)
*   但已经好几个同学都在尝试模拟手机端和微信端，需要模拟较低版本的chromium内核。
*   我之前尝试过更改大版本，但发现有坑，就一直拖着，今天就将研究过程记录下。

### 一、源码位置

###### 1.聪明的你肯定已经找到了内核版本所在文件：

*   `\components\version_info\version_info_with_user_agent.cc`
*   `\third_party\blink\renderer\core\frame\navigator_ua.cc`

###### 2.换掉内核版本

```c
return base::StrCat(
      //{"Chrome/", GetMajorVersionNumber(), ".0.", build_version, ".0"});
      {"Chrome/", "106.0.5249.62"});
```

```c
//ua_data->SetBrandVersionList(metadata.brand_version_list);
  UserAgentBrandList uabl;
  uabl.emplace_back("chromium", "106");
  uabl.emplace_back("Chrome", "106");
  ua_data->SetBrandVersionList(uabl);
  
  //ua_data->SetUAFullVersion("106." + String(std::to_string(randomNum % 99)) +".6572.0");
  ua_data->SetUAFullVersion("106." + String("0") +".5249.62");
```

> 编译后可以看到，浏览器的大版本已成功变更。

###### 3.反指纹检测验证

*   browserscan检测:

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/b1ad741c0ae4496dbac5412bd4211119.png)

*   creepjs检测:

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4c7ba3aa7781494aa03466500ed627d7.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/97db9eff83924d1b82073623822fd745.png)

> 注意：内核更改是成功了，但发现creepjs和browserscan都无法通过反指纹检测。

### 二、新旧版本差异

*   这里creepjs已经把不能通过的原因写的很明显了，v106的版本特性和当前浏览器的版本特性有差异
    
*   这里拿`JSON.rawJSON`函数举例，106版本内核没有这个函数，因为它是115版本的新特性。当在106版本浏览器里发现这个函数，很明显就是篡改
    

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/8781213664f8422581b522377127404a.png)

### 三、看creepjs源码

*   我们找到creepjs源码：[https://github.com/abrahamjuliot/creepjs](https://github.com/abrahamjuliot/creepjs)
    
*   找到creepjs源码里的文件`\creepjs\src\features\index.ts`
    

###### 1.各个版本内核的js新特性：

```js
const blinkJS = {
		'76': ['Document.onsecuritypolicyviolation', 'Promise.allSettled'],
		'77': ['Document.onformdata', 'Document.onpointerrawupdate'],
		'78': ['Element.elementTiming'],
		'79': ['Document.onanimationend', 'Document.onanimationiteration', 'Document.onanimationstart', 'Document.ontransitionend'],
		'80': ['!Document.registerElement', '!Element.createShadowRoot', '!Element.getDestinationInsertionPoints'],
		'81': ['Document.onwebkitanimationend', 'Document.onwebkitanimationiteration', 'Document.onwebkitanimationstart', 'Document.onwebkittransitionend', 'Element.ariaAtomic', 'Element.ariaAutoComplete', 'Element.ariaBusy', 'Element.ariaChecked', 'Element.ariaColCount', 'Element.ariaColIndex', 'Element.ariaColSpan', 'Element.ariaCurrent', 'Element.ariaDisabled', 'Element.ariaExpanded', 'Element.ariaHasPopup', 'Element.ariaHidden', 'Element.ariaKeyShortcuts', 'Element.ariaLabel', 'Element.ariaLevel', 'Element.ariaLive', 'Element.ariaModal', 'Element.ariaMultiLine', 'Element.ariaMultiSelectable', 'Element.ariaOrientation', 'Element.ariaPlaceholder', 'Element.ariaPosInSet', 'Element.ariaPressed', 'Element.ariaReadOnly', 'Element.ariaRelevant', 'Element.ariaRequired', 'Element.ariaRoleDescription', 'Element.ariaRowCount', 'Element.ariaRowIndex', 'Element.ariaRowSpan', 'Element.ariaSelected', 'Element.ariaSort', 'Element.ariaValueMax', 'Element.ariaValueMin', 'Element.ariaValueNow', 'Element.ariaValueText', 'Intl.DisplayNames'],
		'83': ['Element.ariaDescription', 'Element.onbeforexrselect'],
		'84': ['Document.getAnimations', 'Document.timeline', 'Element.ariaSetSize', 'Element.getAnimations'],
		'85': ['Promise.any', 'String.replaceAll'],
		'86': ['Document.fragmentDirective', 'Document.replaceChildren', 'Element.replaceChildren', '!Atomics.wake'],
		'87-89': ['Atomics.waitAsync', 'Document.ontransitioncancel', 'Document.ontransitionrun', 'Document.ontransitionstart', 'Intl.Segmenter'],
		'90': ['Document.onbeforexrselect', 'RegExp.hasIndices', '!Element.onbeforexrselect'],
		'91': ['Element.getInnerHTML'],
		'92': ['Array.at', 'String.at'],
		'93': ['Error.cause', 'Object.hasOwn'],
		'94': ['!Error.cause', 'Object.hasOwn'],
		'95-96': ['WebAssembly.Exception', 'WebAssembly.Tag'],
		'97-98': ['Array.findLast', 'Array.findLastIndex', 'Document.onslotchange'],
		'99-101': ['Intl.supportedValuesOf', 'Document.oncontextlost', 'Document.oncontextrestored'],
		'102': ['Element.ariaInvalid', 'Document.onbeforematch'],
		'103-106': ['Element.role'],
		'107-109': ['Element.ariaBrailleLabel', 'Element.ariaBrailleRoleDescription'],
		'110': ['Array.toReversed', 'Array.toSorted', 'Array.toSpliced', 'Array.with'],
		'111': ['String.isWellFormed', 'String.toWellFormed', 'Document.startViewTransition'],
		'112-113': ['RegExp.unicodeSets'],
		'114-115': ['JSON.rawJSON', 'JSON.isRawJSON'],
	}
```

###### 2.各个版本内核的CSS新特性：

```js
const blinkCSS = {
		'76': ['backdrop-filter'],
		'77-80': ['overscroll-behavior-block', 'overscroll-behavior-inline'],
		'81': ['color-scheme', 'image-orientation'],
		'83': ['contain-intrinsic-size'],
		'84': ['appearance', 'ruby-position'],
		'85-86': ['content-visibility', 'counter-set', 'inherits', 'initial-value', 'page-orientation', 'syntax'],
		'87': ['ascent-override', 'border-block', 'border-block-color', 'border-block-style', 'border-block-width', 'border-inline', 'border-inline-color', 'border-inline-style', 'border-inline-width', 'descent-override', 'inset', 'inset-block', 'inset-block-end', 'inset-block-start', 'inset-inline', 'inset-inline-end', 'inset-inline-start', 'line-gap-override', 'margin-block', 'margin-inline', 'padding-block', 'padding-inline', 'text-decoration-thickness', 'text-underline-offset'],
		'88': ['aspect-ratio'],
		'89': ['border-end-end-radius', 'border-end-start-radius', 'border-start-end-radius', 'border-start-start-radius', 'forced-color-adjust'],
		'90': ['overflow-clip-margin'],
		'91': ['additive-symbols', 'fallback', 'negative', 'pad', 'prefix', 'range', 'speak-as', 'suffix', 'symbols', 'system'],
		'92': ['size-adjust'],
		'93': ['accent-color'],
		'94': ['scrollbar-gutter'],
		'95-96': ['app-region', 'contain-intrinsic-block-size', 'contain-intrinsic-height', 'contain-intrinsic-inline-size', 'contain-intrinsic-width'],
		'97-98': ['font-synthesis-small-caps', 'font-synthesis-style', 'font-synthesis-weight', 'font-synthesis'],
		'99-100': ['text-emphasis-color', 'text-emphasis-position', 'text-emphasis-style', 'text-emphasis'],
		'101-103': ['font-palette', 'base-palette', 'override-colors'],
		'104': ['object-view-box'],
		'105': ['container-name', 'container-type', 'container'],
		'106-107': ['hyphenate-character'],
		'108': ['hyphenate-character', '!orientation', '!max-zoom', '!min-zoom', '!user-zoom'],
		'109': ['hyphenate-limit-chars', 'math-depth', 'math-shift', 'math-style'],
		'110': ['initial-letter'],
		'111-113': ['baseline-source', 'font-variant-alternates', 'view-transition-name'],
		'114-115': ['text-wrap', 'white-space-collapse'],
	}
```

###### 3.各个版本内核的window新特性：

```js
const blinkWindow = {
		'80': ['CompressionStream', 'DecompressionStream', 'FeaturePolicy', 'FragmentDirective', 'PeriodicSyncManager', 'VideoPlaybackQuality'],
		'81': ['SubmitEvent', 'XRHitTestResult', 'XRHitTestSource', 'XRRay', 'XRTransientInputHitTestResult', 'XRTransientInputHitTestSource'],
		'83': ['BarcodeDetector', 'XRDOMOverlayState', 'XRSystem'],
		'84': ['AnimationPlaybackEvent', 'AnimationTimeline', 'CSSAnimation', 'CSSTransition', 'DocumentTimeline', 'FinalizationRegistry', 'LayoutShiftAttribution', 'ResizeObserverSize', 'WakeLock', 'WakeLockSentinel', 'WeakRef', 'XRLayer'],
		'85': ['AggregateError', 'CSSPropertyRule', 'EventCounts', 'XRAnchor', 'XRAnchorSet'],
		'86': ['RTCEncodedAudioFrame', 'RTCEncodedVideoFrame'],
		'87': ['CookieChangeEvent', 'CookieStore', 'CookieStoreManager', 'Scheduling'],
		'88': ['Scheduling', '!BarcodeDetector'],
		'89': ['ReadableByteStreamController', 'ReadableStreamBYOBReader', 'ReadableStreamBYOBRequest', 'ReadableStreamDefaultController', 'XRWebGLBinding'],
		'90': ['AbstractRange', 'CustomStateSet', 'NavigatorUAData', 'XRCPUDepthInformation', 'XRDepthInformation', 'XRLightEstimate', 'XRLightProbe', 'XRWebGLDepthInformation'],
		'91': ['CSSCounterStyleRule', 'GravitySensor', 'NavigatorManagedData'],
		'92': ['CSSCounterStyleRule', '!SharedArrayBuffer'],
		'93': ['WritableStreamDefaultController'],
		'94': ['AudioData', 'AudioDecoder', 'AudioEncoder', 'EncodedAudioChunk', 'EncodedVideoChunk', 'IdleDetector', 'ImageDecoder', 'ImageTrack', 'ImageTrackList', 'VideoColorSpace', 'VideoDecoder', 'VideoEncoder', 'VideoFrame', 'MediaStreamTrackGenerator', 'MediaStreamTrackProcessor', 'Profiler', 'VirtualKeyboard', 'DelegatedInkTrailPresenter', 'Ink', 'Scheduler', 'TaskController', 'TaskPriorityChangeEvent', 'TaskSignal', 'VirtualKeyboardGeometryChangeEvent'],
		'95-96': ['URLPattern'],
		'97-98': ['WebTransport', 'WebTransportBidirectionalStream', 'WebTransportDatagramDuplexStream', 'WebTransportError'],
		'99': ['CanvasFilter', 'CSSLayerBlockRule', 'CSSLayerStatementRule'],
		'100': ['CSSMathClamp'],
		'101-104': ['CSSFontPaletteValuesRule'],
		'105-106': ['CSSContainerRule'],
		'107-108': ['XRCamera'],
		'109': ['MathMLElement'],
		'110': ['AudioSinkInfo'],
		'111-112': ['ViewTransition'],
		'113-115': ['ViewTransition', '!CanvasFilter'],
	}
```

> 注意：以上新特性也只是部分例举，不代表是全部。

### 四、总结：

1.  想要将大版本从高改到低，需要将这些高版本的特性进行酌情抹除才行。反之亦然，小伙伴可以按需自行研究。
2.  但大版本是可以微调的，比如123-125版本几乎没啥变化，我就选择在这之间反复横跳啦。
3.  要跨多个版本，我个人推荐的最终解决方案是：下载旧版本chromium源码，重新编译。
