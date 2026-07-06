
(附加)指纹浏览器开发-禁止访问图片
------------------

*   使用浏览器自动化进行爬虫工作都有一个痛点，就是速度太慢。其中图片流量占据很多比重。
*   如果从底层禁掉图片的网络访问，一可以省流量，二可以省时间。

#### 一、目标

*   目标：启动chrome时，传入参数`--noimage`的话，从底层彻底抹除图片的访问请求。
*   体验无图浏览器的真正急速模式。

#### 二、给chromium子进程传参

*   打开 `\content\browser\renderer_host\render_process_host_impl.cc`

###### 找到源码:

```c
void RenderProcessHostImpl::AppendRendererCommandLine(
    base::CommandLine* command_line) {
  // Pass the process type first, so it shows first in process listings.
  command_line->AppendSwitchASCII(switches::kProcessType,
                                  switches::kRendererProcess);
```

###### 变更为：

```c
void RenderProcessHostImpl::AppendRendererCommandLine(
    base::CommandLine* command_line) {
  // Pass the process type first, so it shows first in process listings.
  command_line->AppendSwitchASCII(switches::kProcessType,
                                  switches::kRendererProcess);
						
  //追加
  const base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string key;
  if (base_command_line->HasSwitch("fingerprints")) {
	  key = base_command_line->GetSwitchValueASCII("fingerprints");
	  command_line->AppendSwitchASCII("fingerprints", key);
  }	
  if (base_command_line->HasSwitch("noimage")) {
	  key = base_command_line->GetSwitchValueASCII("noimage");
	  command_line->AppendSwitchASCII("noimage", key);
  }
```

> 这里有2个参数，`--fingerprints`是以前用的，`--noimage`是这里要用的。

#### 三、禁用图片格式后缀的请求

*   打开 `\net\url_request\url_request_context.cc`

###### 1.导入

```c
#include "base/command_line.h"
```

###### 2.找到源码：

```c
std::unique_ptr<URLRequest> URLRequestContext::CreateRequest(
    const GURL& url,
    RequestPriority priority,
    URLRequest::Delegate* delegate,
    NetworkTrafficAnnotationTag traffic_annotation,
    bool is_for_websockets,
    const std::optional<net::NetLogSource> net_log_source) const {

  return std::make_unique<URLRequest>(
      base::PassKey<URLRequestContext>(), url, priority, delegate, this,
      traffic_annotation, is_for_websockets, net_log_source);
}
```

###### 3.替换为：

```c
GURL disableImageUrl(const GURL& gurl) {
    const std::string imageExtensions[] = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".ico"};
    std::string url = gurl.path();
    size_t dotPosition = url.find_last_of(".");
    if(dotPosition == std::string::npos) {
        return gurl;
    }
    std::string extension = url.substr(dotPosition);
    for (const auto& ext : imageExtensions) {
        if (extension == ext) {
            //LOG(ERROR) << "old_url "<< gurl;
            return GURL("data:image/png;base64,iVBORw0KGgo");
        }
    }
    return gurl;
}


std::unique_ptr<URLRequest> URLRequestContext::CreateRequest(
    const GURL& url,
    RequestPriority priority,
    URLRequest::Delegate* delegate,
    NetworkTrafficAnnotationTag traffic_annotation,
    bool is_for_websockets,
    const std::optional<net::NetLogSource> net_log_source) const {

  //追加
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  GURL tmp_url;
  if (base_command_line->HasSwitch("noimage")) {
	  tmp_url = disableImageUrl(url);
  }else{
	  tmp_url = url;
  }
  
  return std::make_unique<URLRequest>(
      base::PassKey<URLRequestContext>(), tmp_url, priority, delegate, this,
      traffic_annotation, is_for_websockets, net_log_source);
}
```

#### 四、禁用Content-Type为图片格式的请求

*   打开`\third_party\blink\renderer\platform\loader\fetch\resource_fetcher.cc`

###### 1.导入

```c
#include "base/command_line.h"
```

###### 2.找到源码

```c
Resource* ResourceFetcher::RequestResource(FetchParameters& params,
                                           const ResourceFactory& factory,
                                           ResourceClient* client) {
  base::AutoReset<bool> r(&is_in_request_resource_, true);
  
```

###### 3.替换为

```c
Resource* ResourceFetcher::RequestResource(FetchParameters& params,
                                           const ResourceFactory& factory,
                                           ResourceClient* client) {
  base::AutoReset<bool> r(&is_in_request_resource_, true);
  
  // 追加
  if (factory.GetType() == ResourceType::kImage) {
    std::string url = params.Url().GetString().GetString().Utf8();
    if (url.substr(0, 4) == "http"){
      //LOG(ERROR) << url;
      base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
      if (base_command_line->HasSwitch("noimage")){
        return ResourceForBlockedRequest(params, factory, ResourceRequestBlockedReason::kOther, client);
      } 
    }
  }
```

###### 4.编译

```
ninja  -C  out/Default chrome
```

*   找到`out/Default chrome`下会出现新编译的执行文件`chrome.exe`，打开cmd里执行`./chrome.exe --noimage`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/62cd8af00ec44c56838652b38a614aa2.png)

> 可以看到；一张图片请求链接都没有！

#### 五、感想

*   随机指纹浏览器开发到这里，已经可以胜任绝大多数的爬虫任务了。
*   网上的指纹浏览器基本全是收费的，我将随机指纹浏览器的开发全过程，全部记录在这里，自觉也是一种开源精神。
*   小伙伴照着我的开发流程慢慢跑，2天应该能把全过程跑一遍，编译一个自己的指纹浏览器。
*   感谢读者的反馈。

* * *

### 20250521 追加更新

*   群友提供了更优秀的解决方法，只需要启动是带上参数：

```c
--blink-settings=imagesEnabled=false
```
