随机指纹chromium编译-传参固定指纹(二)
------------------------

#### 目标：

*   目标1：启动chrome时，传入参数`--fingerprints=123123123`(正整数)，则指纹固定不变。当正整数更换，则获得一个新指纹。
*   目标2：启动chrome时，不传参数`--fingerprints`，则每个访问请求的指纹全部随机生成。

###### 注意的点

*   之前的随机生成指纹的代码都需要删掉，全部替换新代码。
*   由于我接受的是int类型，所以`--fingerprints`只能传整数，且最大值为2,147,483,647
*   这里我默认大家都看过我之前的博客，对修改源码的流程已经非常熟悉。

#### 一、固定字体指纹

> 之前发现字体指纹的检测方式特别多，这里搞了个偷懒方式，一招全部解决。。  
> 这个偷懒的方式就是：随机将字体偷换成别的字体。。不过这样做可能会出现页面上的字体发生改变。各位按需更改。

打开：`\third_party\blink\renderer\core\css\css_font_family_value.cc`

```c
#include "base/command_line.h"
```

###### 1\. 定义一个抽数函数：

```c
std::vector<std::string> randomlyRemoveElements(std::vector<std::string> arr, unsigned int seed) {
    srand(seed);  // 设置随机数生成器的种子
    std::vector<std::string> result;  // 存储最终结果的向量
    
    for (const auto& item : arr) {
        if (rand() % 2 == 0) {  // 随机选择是否保留每个元素
            result.push_back(item);
        }
    }
    return result;
}

```

###### 2.找到 `CSSFontFamilyValue::Create` 函数

```c
CSSFontFamilyValue* CSSFontFamilyValue::Create(
     const AtomicString& family_name) {
 if (family_name.IsNull()) {
    return MakeGarbageCollected<CSSFontFamilyValue>(family_name);
  }
  CSSValuePool::FontFamilyValueCache::AddResult entry =
      CssValuePool().GetFontFamilyCacheEntry(family_name);
  if (!entry.stored_value->value) {
    entry.stored_value->value =
        MakeGarbageCollected<CSSFontFamilyValue>(family_name);
  }
  return entry.stored_value->value.Get();
}
```

###### 3.替换成下面的代码

```c
CSSFontFamilyValue* CSSFontFamilyValue::Create(
     const AtomicString& family_name) {
         
  // 开始追加=======================================
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string ignores = base_command_line->GetSwitchValueASCII("ignores"); 
  if(ignores.find("fonts") == std::string::npos){
	  std::vector<std::string> stringsAarry = {"Lucida Sans", "Lucida Sans Typewriter", "Lucida Sans Unicode", "Microsoft Sans Serif", "Monaco", "Monotype Corsiva", "MS Gothic", "MS Outlook", "MS PGothic", "MS Reference Sans Serif", "MS Sans Serif", "MS Serif", "MYRIAD", "MYRIAD PRO", "Palatino", "Palatino Linotype", "Segoe Print", "Segoe Script", "Segoe UI", "Segoe UI Light", "Segoe UI Semibold", "Segoe UI Symbol", "Tahoma", "Times", "Times New Roman", "Times New Roman PS", "Trebuchet MS", "Verdana", "Wingdings", "Wingdings 2", "Wingdings 3", "Bahnschrift", "Cambria Math", "Gadugi", "HoloLens MDL2 Assets", "Ink Free", "Javanese Text", "Leelawadee UI", "Lucida Console", "MS Outlook", "Myanmar Text", "Nirmala UI", "Segoe Fluent Icons", "Segoe MDL2 Assets", "Segoe UI Emoji","Abadi MT Condensed Light", "Academy Engraved LET", "ADOBE CASLON PRO", "Adobe Garamond", "ADOBE GARAMOND PRO", "Agency FB", "Aharoni", "Albertus Extra Bold", "Albertus Medium", "Algerian", "Amazone BT", "American Typewriter", "American Typewriter Condensed", "AmerType Md BT", "Andalus", "Angsana New", "AngsanaUPC", "Antique Olive", "Aparajita", "Apple Chancery", "Apple Color Emoji", "Apple SD Gothic Neo", "Arabic Typesetting", "ARCHER", "ARNO PRO", "Arrus BT", "Aurora Cn BT", "AvantGarde Bk BT", "AvantGarde Md BT", "AVENIR", "Ayuthaya", "Bandy", "Bangla Sangam MN", "Bank Gothic", "BankGothic Md BT", "Baskerville", "Baskerville Old Face", "Batang", "BatangChe", "Bauer Bodoni", "Bauhaus 93", "Bazooka", "Bell MT", "Bembo", "Benguiat Bk BT", "Berlin Sans FB", "Berlin Sans FB Demi", "Bernard MT Condensed", "BernhardFashion BT", "BernhardMod BT", "Big Caslon", "BinnerD", "Blackadder ITC", "BlairMdITC TT", "Bodoni 72", "Bodoni 72 Oldstyle", "Bodoni 72 Smallcaps", "Bodoni MT", "Bodoni MT Black", "Bodoni MT Condensed", "Bodoni MT Poster Compressed", "Bookshelf Symbol 7", "Boulder", "Bradley Hand", "Bradley Hand ITC", "Bremen Bd BT", "Britannic Bold", "Broadway", "Browallia New", "BrowalliaUPC", "Brush Script MT", "Californian FB", "Calisto MT", "Calligrapher", "Candara", "CaslonOpnface BT", "Castellar", "Centaur", "Cezanne", "CG Omega", "CG Times", "Chalkboard", "Chalkboard SE", "Chalkduster", "Charlesworth", "Charter Bd BT", "Charter BT", "Chaucer", "ChelthmITC Bk BT", "Chiller", "Clarendon", "Clarendon Condensed", "CloisterBlack BT", "Cochin", "Colonna MT", "Constantia", "Cooper Black", "Copperplate", "Copperplate Gothic", "Copperplate Gothic Bold", "Copperplate Gothic Light", "CopperplGoth Bd BT", "Corbel", "Cordia New", "CordiaUPC", "Cornerstone", "Coronet", "Cuckoo", "Curlz MT", "DaunPenh", "Dauphin", "David", "DB LCD Temp", "DELICIOUS", "Denmark", "DFKai-SB", "Didot", "DilleniaUPC", "DIN", "DokChampa", "Dotum", "DotumChe", "Ebrima", "Edwardian Script ITC", "Elephant", "English 111 Vivace BT", "Engravers MT", "EngraversGothic BT", "Eras Bold ITC", "Eras Demi ITC", "Eras Light ITC", "Eras Medium ITC", "EucrosiaUPC", "Euphemia", "Euphemia UCAS", "EUROSTILE", "Exotc350 Bd BT", "FangSong", "Felix Titling", "Fixedsys", "FONTIN", "Footlight MT Light", "Forte", "FrankRuehl", "Fransiscan", "Freefrm721 Blk BT", "FreesiaUPC", "Freestyle Script", "French Script MT", "FrnkGothITC Bk BT", "Fruitger", "FRUTIGER", "Futura", "Futura Bk BT", "Futura Lt BT", "Futura Md BT", "Futura ZBlk BT", "FuturaBlack BT", "Gabriola", "Galliard BT", "Gautami", "Geeza Pro", "Geometr231 BT", "Geometr231 Hv BT", "Geometr231 Lt BT", "GeoSlab 703 Lt BT", "GeoSlab 703 XBd BT", "Gigi", "Gill Sans", "Gill Sans MT", "Gill Sans MT Condensed", "Gill Sans MT Ext Condensed Bold", "Gill Sans Ultra Bold", "Gill Sans Ultra Bold Condensed", "Gisha", "Gloucester MT Extra Condensed", "GOTHAM", "GOTHAM BOLD", "Goudy Old Style", "Goudy Stout", "GoudyHandtooled BT", "GoudyOLSt BT", "Gujarati Sangam MN", "Gulim", "GulimChe", "Gungsuh", "GungsuhChe", "Gurmukhi MN", "Haettenschweiler", "Harlow Solid Italic", "Harrington", "Heather", "Heiti SC", "Heiti TC", "HELV", "Herald", "High Tower Text", "Hiragino Kaku Gothic ProN", "Hiragino Mincho ProN", "Hoefler Text", "Humanst 521 Cn BT", "Humanst521 BT", "Humanst521 Lt BT", "Imprint MT Shadow", "Incised901 Bd BT", "Incised901 BT", "Incised901 Lt BT", "INCONSOLATA", "Informal Roman", "Informal011 BT", "INTERSTATE", "IrisUPC", "Iskoola Pota", "JasmineUPC", "Jazz LET", "Jenson", "Jester", "Jokerman", "Juice ITC", "Kabel Bk BT", "Kabel Ult BT", "Kailasa", "KaiTi", "Kalinga", "Kannada Sangam MN", "Kartika", "Kaufmann Bd BT", "Kaufmann BT", "Khmer UI", "KodchiangUPC", "Kokila", "Korinna BT", "Kristen ITC", "Krungthep", "Kunstler Script", "Lao UI", "Latha", "Leelawadee", "Letter Gothic", "Levenim MT", "LilyUPC", "Lithograph", "Lithograph Light", "Long Island", "Lydian BT", "Magneto", "Maiandra GD", "Malayalam Sangam MN", "Malgun Gothic", "Mangal", "Marigold", "Marion", "Marker Felt", "Market", "Marlett", "Matisse ITC", "Matura MT Script Capitals", "Meiryo", "Meiryo UI", "Microsoft Himalaya", "Microsoft JhengHei", "Microsoft New Tai Lue", "Microsoft PhagsPa", "Microsoft Tai Le", "Microsoft Uighur", "Microsoft YaHei", "Microsoft Yi Baiti", "MingLiU", "MingLiU_HKSCS", "MingLiU_HKSCS-ExtB", "MingLiU-ExtB", "Minion", "Minion Pro", "Miriam", "Miriam Fixed", "Mistral", "Modern", "Modern No. 20", "Mona Lisa Solid ITC TT", "Mongolian Baiti", "MONO", "MoolBoran", "Mrs Eaves", "MS LineDraw", "MS Mincho", "MS PMincho", "MS Reference Specialty", "MS UI Gothic", "MT Extra", "MUSEO", "MV Boli", "Nadeem", "Narkisim", "NEVIS", "News Gothic", "News GothicMT", "NewsGoth BT", "Niagara Engraved", "Niagara Solid", "Noteworthy", "NSimSun", "Nyala", "OCR A Extended", "Old Century", "Old English Text MT", "Onyx", "Onyx BT", "OPTIMA", "Oriya Sangam MN", "OSAKA", "OzHandicraft BT", "Palace Script MT", "Papyrus", "Parchment", "Party LET", "Pegasus", "Perpetua", "Perpetua Titling MT", "PetitaBold", "Pickwick", "Plantagenet Cherokee", "Playbill", "PMingLiU", "PMingLiU-ExtB", "Poor Richard", "Poster", "PosterBodoni BT", "PRINCETOWN LET", "Pristina", "PTBarnum BT", "Pythagoras", "Raavi", "Rage Italic", "Ravie", "Ribbon131 Bd BT", "Rockwell", "Rockwell Condensed", "Rockwell Extra Bold", "Rod", "Roman", "Sakkal Majalla", "Santa Fe LET", "Savoye LET", "Sceptre", "Script", "Script MT Bold", "SCRIPTINA", "Serifa", "Serifa BT", "Serifa Th BT", "ShelleyVolante BT", "Sherwood", "Shonar Bangla", "Showcard Gothic", "Shruti", "Signboard", "SILKSCREEN", "SimHei", "Simplified Arabic", "Simplified Arabic Fixed", "SimSun", "SimSun-ExtB", "Sinhala Sangam MN", "Sketch Rockwell", "Skia", "Small Fonts", "Snap ITC", "Snell Roundhand", "Socket", "Souvenir Lt BT", "Staccato222 BT", "Steamer", "Stencil", "Storybook", "Styllo", "Subway", "Swis721 BlkEx BT", "Swiss911 XCm BT", "Sylfaen", "Synchro LET", "System", "Tamil Sangam MN", "Technical", "Teletype", "Telugu Sangam MN", "Tempus Sans ITC", "Terminal", "Thonburi", "Traditional Arabic", "Trajan", "TRAJAN PRO", "Tristan", "Tubular", "Tunga", "Tw Cen MT", "Tw Cen MT Condensed", "Tw Cen MT Condensed Extra Bold", "TypoUpright BT", "Unicorn", "Univers", "Univers CE 55 Medium", "Univers Condensed", "Utsaah", "Vagabond", "Vani", "Vijaya", "Viner Hand ITC", "VisualUI", "Vivaldi", "Vladimir Script", "Vrinda", "Westminster", "WHITNEY", "Wide Latin", "ZapfEllipt BT", "ZapfHumnst BT", "ZapfHumnst Dm BT", "Zapfino", "Zurich BlkEx BT", "Zurich Ex BT", "ZWAdobeF"};
	  int seed;
	  if (base_command_line->HasSwitch("fingerprints")) {
		  std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> seed; 
	  }else{
		  auto now = std::chrono::system_clock::now();
		  std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
		  seed = static_cast<int>(now_time_t);
	  }
	  
	  std::string now_font_str = "";
	  AtomicString tmp_family_name("");
	  for (const std::string& font : stringsAarry) {
		  tmp_family_name = AtomicString (String(font)); 
		  if (tmp_family_name==family_name){
			 now_font_str = font;
			 break;
		  }
	  }
	  AtomicString res_family("monospace"); 
	  auto modifiedArray = randomlyRemoveElements(stringsAarry, seed);
	  if (std::find(modifiedArray.begin(), modifiedArray.end(), now_font_str) != modifiedArray.end()) {
		return MakeGarbageCollected<CSSFontFamilyValue>(res_family);
	  }
  }
  // 结束追加=======================================	
  
  // 以下是原函数内容
  if (family_name.IsNull()) {
    return MakeGarbageCollected<CSSFontFamilyValue>(family_name);
  }
  CSSValuePool::FontFamilyValueCache::AddResult entry =
      CssValuePool().GetFontFamilyCacheEntry(family_name);
  if (!entry.stored_value->value) {
    entry.stored_value->value =
        MakeGarbageCollected<CSSFontFamilyValue>(family_name);
  }
  return entry.stored_value->value.Get();
}
```

#### 二、固定audio指纹：

*   找到 `/third_party/blink/renderer/modules/webaudio/offline_audio_context.cc`

```c
#include <random>
#include "base/command_line.h"

int getRandomIntForFoo6Modern() {
    static std::mt19937 generator(static_cast<unsigned long>(time(NULL))); // 静态以确保只初始化一次
    std::uniform_int_distribution<int> distribution(0, 99);
    return distribution(generator);
}
```

```c
OfflineAudioContext::OfflineAudioContext(LocalDOMWindow* window,
                                         unsigned number_of_channels,
                                         uint32_t number_of_frames,
                                         float sample_rate,
                                         ExceptionState& exception_state)
    : BaseAudioContext(window, kOfflineContext),
      total_render_frames_(number_of_frames) {
		  
	base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
	int tmp;
	if (base_command_line->HasSwitch("fingerprints")) {
	  std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> tmp;
	}else{
	  tmp=getRandomIntForFoo6Modern();
	}
    tmp = tmp%99;
    destination_node_ = OfflineAudioDestinationNode::Create(
      this, number_of_channels, number_of_frames , sample_rate+tmp);
  Initialize();
}

```

#### 三、webGL指纹

*   找到 `\third_party\blink\renderer\core\html\canvas\html_canvas_element.cc`

```c
#include "base/command_line.h"
```

```c
String HTMLCanvasElement::toDataURL(const String& mime_type,
                                    const ScriptValue& quality_argument,
                                    ExceptionState& exception_state) const {
  if (ContextHasOpenLayers(context_)) {
    exception_state.ThrowDOMException(
        DOMExceptionCode::kInvalidStateError,
        "`toDataURL()` cannot be called with open layers.");
    return String();
  }

  if (!OriginClean()) {
    exception_state.ThrowSecurityError("Tainted canvases may not be exported.");
    return String();
  }

  double quality = kUndefinedQualityValue;
  if (!quality_argument.IsEmpty()) {
    v8::Local<v8::Value> v8_value = quality_argument.V8Value();
    if (v8_value->IsNumber())
      quality = v8_value.As<v8::Number>()->Value();
  }
  
  String data = ToDataURLInternal(mime_type, quality, kBackBuffer);

  TRACE_EVENT_INSTANT(
      TRACE_DISABLED_BY_DEFAULT("identifiability.high_entropy_api"),
      "CanvasReadback", "data_url", data.Utf8());
      
 
  //这里追加几行
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  int tmp;
  std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> tmp;
  int randomNum;
  if (base_command_line->HasSwitch("fingerprints")) {
    randomNum = tmp%999;
  }else{
    srand((int)time(NULL));
    randomNum = rand()%999;
  }
  std::string spaces(randomNum, ' ');
  data = data + String(spaces);
  //LOG(ERROR) << "data:('" << data << "') data";
  
  return data;
}
```

> 原理是修改`toDataURL()`函数，给结尾处随机加上多个空格。  
> 这个函数许多网站生成canvas指纹最后步骤也会使用，我们就顺便把修改canvas指纹也加强了。

#### 四、固定canvas指纹

*   打开`\third_party\blink\renderer\modules\canvas\canvas2d\base_rendering_context_2d.cc`

```c
void BaseRenderingContext2D::setFillStyle(v8::Isolate* isolate,
                                          v8::Local<v8::Value> value,
                                          ExceptionState& exception_state) {
  V8CanvasStyle v8_style;
  if (!ExtractV8CanvasStyle(isolate, value, v8_style, exception_state))
    return;

  ValidateStateStack();

  UpdateIdentifiabilityStudyBeforeSettingStrokeOrFill(v8_style,
                                                      CanvasOps::kSetFillStyle);
  CanvasRenderingContext2DState& state = GetState();
  
  // 追加
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  int tmp;
  if (base_command_line->HasSwitch("fingerprints")) {
    std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> tmp;
  }else{
      auto now = std::chrono::system_clock::now();
      std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
      tmp = static_cast<int>(now_time_t);
  }
  state.SetStrokeColor(Color::FromRGBALegacy(tmp % 5, tmp % 6,tmp % 7, tmp % 255));
  
  
  switch (v8_style.type) {
    case V8CanvasStyleType::kCSSColorValue:
      state.SetFillColor(v8_style.css_color_value);
      break;
    case V8CanvasStyleType::kGradient:
      state.SetFillGradient(v8_style.gradient);
      break;
    case V8CanvasStyleType::kPattern:
      if (!origin_tainted_by_content_ && !v8_style.pattern->OriginClean())
        SetOriginTaintedByContent();
      state.SetFillPattern(v8_style.pattern);
      break;
    case V8CanvasStyleType::kString: {
      if (v8_style.string == state.UnparsedFillColor()) {
        return;
      }
      Color parsed_color = Color::kTransparent;
      if (!ExtractColorFromV8ValueAndUpdateCache(v8_style, parsed_color)) {
        return;
      }
      if (state.FillStyle().IsEquivalentColor(parsed_color)) {
        state.SetUnparsedFillColor(v8_style.string);
        return;
      }
      
      //这里追加1行
      parsed_color = Color::FromRGBALegacy(parsed_color.Param1() + tmp % 5, parsed_color.Param1()+ tmp % 6, parsed_color.Param2() + tmp % 7, parsed_color.Alpha()*255);
  
      state.SetFillColor(parsed_color);
      break;
    }
  }

  state.SetUnparsedFillColor(v8_style.string);
  state.ClearResolvedFilter();
}
```

> 原理是随机微调canvas的RGB颜色。

```c
ImageData* BaseRenderingContext2D::getImageDataInternal(
    int sx,
    int sy,
    int sw,
    int sh,
    ImageDataSettings* image_data_settings,
    ExceptionState& exception_state) {
        
  // 这里追加一行
  if (sh==1){return nullptr;}
```

> 这里追加一行是为了应对creepjs的反指纹检测。

#### 五、固定ja4指纹

###### 1.给utility进程追加参数

*   打开 `\content\browser\utility_process_host.cc`

```c
cmd_line->AppendSwitchASCII(switches::kProcessType,
                                switches::kUtilityProcess);
```

替换为

```c
cmd_line->AppendSwitchASCII(switches::kProcessType,
                                switches::kUtilityProcess);
                                
const base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
if (base_command_line->HasSwitch("fingerprints")) {
  const std::string tmp = base_command_line->GetSwitchValueASCII("fingerprints");
  cmd_line->AppendSwitchASCII("fingerprints", tmp);
}
```

###### 2\. 改ja4指纹

*   打开 `\net\socket\ssl_client_socket_impl.cc`

定义：

```c
std::vector<std::string> randomlyRemoveElements(std::vector<std::string> arr, unsigned int seed) {
    srand(seed);  // 设置随机数生成器的种子
    std::vector<std::string> result;  // 存储最终结果的向量
    
    for (const auto& item : arr) {
        if (rand() % 2 == 0) {  // 随机选择是否保留每个元素
            result.push_back(item);
        }
    }
    return result;
}
```

找到：

```c
std::string command("ALL:!aPSK:!ECDSA+SHA1:!3DES");
```

替换成：

```c
  // std::string command("ALL:!aPSK:!ECDSA+SHA1:!3DES");
  
  std::string command("ALL");
  std::vector<std::string> stringsAarry = {":!aPSK", ":!kRSA",":!ECDSA",":!ECDSA+SHA1",":!3DES"};
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  int seed;
  if (base_command_line->HasSwitch("fingerprints")) {
      std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> seed; 
  }else{
      auto now = std::chrono::system_clock::now();
      std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
      seed = static_cast<int>(now_time_t);
  }
  auto modifiedArray = randomlyRemoveElements(stringsAarry, seed);
  for (const std::string& key : modifiedArray) {
	  command.append(key);
  }
```

> 原理是随机抽取部分加密函数给去掉。

#### 六、固定plugins指纹

*   修改 `/third_party/blink/renderer/modules/plugins/dom_plugin.cc`

> 方法在上一篇博客里有：[插眼传送](https://blog.csdn.net/w1101662433/article/details/139772516)

#### 七、关于更新

感谢读者的反馈和支持
