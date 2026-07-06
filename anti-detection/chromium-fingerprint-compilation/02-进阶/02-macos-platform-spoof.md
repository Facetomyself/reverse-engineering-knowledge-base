
一、目标：
-----

*   实现传入参数`--platform=mac`，将浏览器获取到的操作系统变为macOS
*   并且可以通过creepjs和browserscan的检测。

二、js如何判断操作系统是否为Mac
------------------

> 方法比较多，这里我将他们挨个列出来

*   1 . 通过`navigator.platform`

```js
console.log(navigator.platform)
```

输出：

```
MacIntel
```

*   2 . 通过`navigator.userAgent`

> 正常mac的UA类似长这样：`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36`

```js
function detectOS() {
   const userAgent = navigator.userAgent.toLowerCase();
  
  if (userAgent.includes('win')) {
    return 'Windows';
   } else if (userAgent.includes('mac')) {
    return 'Mac';
   }
   return '其他系统';   
}

console.log(detectOS())
```

输出：

```
Mac
```

*   3 . 通过`navigator.userAgentData`

```js
let tmp = await navigator.userAgentData.getHighEntropyValues(["platform", "platformVersion"])
console.log("操作系统：", tmp.platform)
console.log("版本号：", tmp.platformVersion)
```

输出：

```
操作系统： macOS
版本号： 10.11.2
```

*   4 . 通过字体

```js
function detectOSByFont() {
   // 定义系统特征字体（按检测优先级排序）
   const osFonts = {
    mac: ["Geneva", "Helvetica Neue", "Luminari"],
    win: ["Segoe UI", "Ink Free", "Segoe UI Emoji"]
   };
   // 字体检测方法
   const isFontAvailable = fontName => {
    try {
      await (new FontFace("Helvetica Neue", `local("${fontName} Neue"`)).load()
      return true;
    } catch (e) {
      return false;
    }
   };
   // 优先检测Mac字体
   for (const font of osFonts.mac) {
    if (isFontAvailable(font)) return "Mac";
   }
   // 其次检测Windows字体
   for (const font of osFonts.win) {
    if (isFontAvailable(font)) return "Windows";
   }
   // 最终回退到UserAgent检测
   const ua = navigator.userAgent;
   if (/Mac/i.test(ua)) return "操作系统：Mac";
   if (/Win/i.test(ua)) return "操作系统：Windows";
   return "其他操作系统";   
}

console.log(detectOSByFont())
```

输出：

```
Mac
```

*   5.通过特性

```js
if('BarcodeDetector' in window){
    console.log('是Mac')
}else{
    console.log('不是Mac')
}

```

输出：

```
是Mac
```

三、修改`navigator.platform`
------------------------

> 在开始修改源码之前，请确保已具备chromium编译基础。

*   打开文件 `\third_party\blink\renderer\core\execution_context\navigator_base.cc`
    
*   找到函数：
    

```c
String GetReducedNavigatorPlatform() {
```

*   追加几行：

```c
String GetReducedNavigatorPlatform() {
  // 开始追加 =====================================
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string platform = base_command_line->GetSwitchValueASCII("platform"); 
  if (platform == "mac"){
      return "MacIntel";
  }
  // 结束追加 ==================================

```

四、修改`navigator.userAgent`
-------------------------

*   打开文件：`\components\embedder_support\user_agent_utils.cc`
    
*   找到：
    

```c
std::string GetUserAgent(
    UserAgentReductionEnterprisePolicyState user_agent_reduction) {
  std::optional<std::string> custom_ua = GetUserAgentFromCommandLine();
  if (custom_ua.has_value()) {
    return custom_ua.value();
  }
  return GetUserAgentInternal(user_agent_reduction);
}
```

*   替换为：

```c
std::string GetUserAgent(
    ForceMajorVersionToMinorPosition force_major_to_minor,
    UserAgentReductionEnterprisePolicyState user_agent_reduction) {
  absl::optional<std::string> custom_ua = GetUserAgentFromCommandLine();
  if (custom_ua.has_value()) {
    return custom_ua.value();
  }

  // 开始修改========================
  //return GetUserAgentInternal(user_agent_reduction); // 133版

  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string ignores = base_command_line->GetSwitchValueASCII("ignores"); 


  if(!base_command_line->HasSwitch("user-agent") && ignores.find("useragent") == std::string::npos){
      std::string ua;
      std::string target;
      std::string replacemen; 
      std::string result = ua;
      size_t pos;
      
      std::string platform = base_command_line->GetSwitchValueASCII("platform");
        
      if (platform == "mac"){
        target = "Windows NT 10.0; Win64; x64";
        replacement = "Macintosh; Intel Mac OS X 10_11_2"; 
        pos = 0;
        while ((pos = result.find(target, pos))!= std::string::npos) {
            result.replace(pos, target.length(), replacement);
            pos += replacement.length();
        }
      }
      return result;   
  }else{
      return GetUserAgentInternal(user_agent_reduction); 
  }
  // 结束修改=======================================
}

```

> 注意：不同大版本的源代码会略有不同，不要直接覆盖，注意理解。

五、修改`navigator.userAgentData`
-----------------------------

*   还是打开：`\components\embedder_support\user_agent_utils.cc`
    
*   找到函数：
    

```c
std::string GetPlatformForUAMetadata() {
```

*   追加几行：

```c

std::string GetPlatformForUAMetadata() {
    // 开始追加 =================================
    base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
    std::string platform = base_command_line->GetSwitchValueASCII("platform");
    if (platform == "mac"){
        return "macOS";
    }else if (platform == "win"){
        return "Windows";
    }else if (platform == "linux"){
        return "Linux";
    }
    // 结束追加===========================================
```

六、修改font
--------

*   打开：`\third_party\blink\renderer\core\css\css_font_family_value.cc`
    
*   找到函数：
    

```c
CSSFontFamilyValue* CSSFontFamilyValue::Create(
```

*   追加几行：

```c
CSSFontFamilyValue* CSSFontFamilyValue::Create(
     const AtomicString& family_name) {
         
  // 开始追加=======================================
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string ignores = base_command_line->GetSwitchValueASCII("ignores"); 
  std::string now_font_str = family_name.GetString().Utf8();
  if (base_command_line->HasSwitch("finger-log")) {
    std::cerr << "调用canvas字体: " << now_font_str << std::endl;
  }
  if(ignores.find("fonts") == std::string::npos){
      int seed;
      auto now = std::chrono::system_clock::now();
      std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
      int int_now = static_cast<int>(now_time_t);
      if (base_command_line->HasSwitch("fingerprints")) {
          std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> seed; 
      }else{
          seed = int_now;
      }
      std::vector<std::string> stringsAarry = {"Goudy Old Style", "Bell MT", "Browallia New", "Rod", "Zurich Ex BT", "BinnerD", "Gill Sans Ultra Bold Condensed", "INTERSTATE", "Arabic Typesetting", "Fransiscan", "AvantGarde Md BT", "Segoe Fluent Icons", "Broadway", "Bodoni MT Poster Compressed", "Miriam Fixed", "PetitaBold", "DFKai-SB", "Poster", "MS Outlook", "DIN", "Charlesworth", "Cuckoo", "VisualUI", "Geometr231 Lt BT", "Denmark", "Adobe Garamond", "Eras Bold ITC", "Meiryo", "MS PMincho", "Herald", "Didot", "Bodoni MT", "Bazooka", "Kristen ITC", "MS Mincho", "Khmer UI", "Lydian BT", "ShelleyVolante BT", "Kailasa", "Pickwick", "GOTHAM", "ZapfEllipt BT", "Geometr231 BT", "MT Extra", "Papyrus", "Mrs Eaves", "Letter Gothic", "Albertus Extra Bold", "Vladimir Script", "Chalkboard SE", "SCRIPTINA", "Storybook", "OzHandicraft BT", "Wingdings 2", "Tunga", "PosterBodoni BT", "Baskerville Old Face"};
      auto selectedArray = selectRandomFonts2(stringsAarry, 199, seed);
      if (std::find(selectedArray.begin(), selectedArray.end(), now_font_str) != selectedArray.end()) { //如果在selectedArray中
        return MakeGarbageCollected<CSSFontFamilyValue>(AtomicString("sans-serif"));
      }
      std::vector<std::string> winFontsAarry = {"Segoe Fluent Icons", "Ink Free", "Bahnschrift", "Segoe MDL2 Assets", "HoloLens MDL2 Assets", "Segoe UI Emoji", "Javanese Text", "Leelawadee UI", "Nirmala UI", "Myanmar Text", "Gadugi", "Aldhabi", "Lucida Console", "Cambria Math"};
      if (base_command_line->GetSwitchValueASCII("platform") == "mac"){
          std::vector<std::string> macFontsAarry = {"Helvetica Neue", "Geneva", "Kohinoor Devanagari Medium", "Luminari", "PingFang HK Light", "InaiMathi Bold", "PGalvji", "Chakra Petch" };
          if(std::find(winFontsAarry.begin(), winFontsAarry.end(), now_font_str) != winFontsAarry.end()){
              //std::cerr << "now_font_str:"<< now_font_str << std::endl;
              return MakeGarbageCollected<CSSFontFamilyValue>(AtomicString("sans-serif"));
          }else if(std::find(macFontsAarry.begin(), macFontsAarry.end(), now_font_str) != macFontsAarry.end()){
              return MakeGarbageCollected<CSSFontFamilyValue>(AtomicString("Arial"));
          }
      } 
  }
  // 结束追加=======================================  
```

*   我还定义了一个函数：

```c
std::vector<std::string> selectRandomFonts2(const std::vector<std::string>& fontArray, size_t count, unsigned int seed) {
    // 随机选多个
    std::mt19937 rng(seed);
    std::uniform_int_distribution<size_t> dist(0, fontArray.size() - 1);
    std::vector<std::string> selectedFonts;
    selectedFonts.reserve(count);
    std::vector<bool> selected(fontArray.size(), false);
    while (selectedFonts.size() < count) {
        size_t index = dist(rng);
        if (!selected[index]) {
            selectedFonts.push_back(fontArray[index]);
            selected[index] = true;
        }
    }
    return selectedFonts;
}
```

> 上述代码将mac的字体列表 `{"Helvetica Neue", "Geneva", "Kohinoor Devanagari Medium", "Luminari", "PingFang HK Light", "InaiMathi Bold", "PGalvji", "Chakra Petch" }` 全部有效返回。

七、追加`window.BarcodeDetector`
----------------------------

*   打开 `\third_party\blink\renderer\platform\runtime_enabled_features.json5`
    
*   找到：
    

```json
   {
      name: "BarcodeDetector",
      status: {
        // Built-in barcode detection APIs are only available from some
        // platforms. See //services/shape_detection.
        "Android": "stable",
        "ChromeOS_Ash": "stable",
        "ChromeOS_Lacros": "stable",
        "Mac": "stable",
        "default": "test",
      },
      base_feature: "none",
    }
```

*   替换成：

```json
   {
      name: "BarcodeDetector",
      status: {
        // Built-in barcode detection APIs are only available from some
        // platforms. See //services/shape_detection.
        "Android": "stable",
        "ChromeOS_Ash": "stable",
        "ChromeOS_Lacros": "stable",
        "Mac": "stable",
        // 追加一行 ============================
        "Win": "stable",
        "default": "test",
      },
      base_feature: "none",
    }
```

八、编译：
-----

```
ninja -C out/Default chrome
```

九、测试效果：
-------

*   测试站点1：https://www.browserscan.net/zh/
*   测试站点2：https://abrahamjuliot.github.io/creepjs/

```
./chrome.exe --paltform=mac
```

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/caa73a49684f42588f9ba7f4dff1e843.png)

