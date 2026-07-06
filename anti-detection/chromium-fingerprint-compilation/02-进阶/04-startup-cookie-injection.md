
### 一、目标：

*   实现传入参数`--set-cookies='[{"domain":"https://baidu.com","name":"AAAA","value":"111"},{"domain":"https://baidu.com","name":"BBB","value":"222"}]'`，实现浏览器启动时，默认带上这2个cookie

> 阅读此篇博客前，请确保已具备chromium编译基础。

### 二、为何要传参传入cookies

*   已知自动化工具selenium，puppeteer等都有启动时携带初始cookie功能，所以这部分用户可以忽略。
*   已知chromium的cookie存储位置是`user-data-dir/Default/Network/Cookies`。这个文件没有后缀，但实际是个sqlite库文件，可以使用sqlite打开。
*   但是在源码里写sql还是有点麻烦，不如直接用调用源码中已有的函数，拿来调用即可。

### 三、修改chromium源码

*   打开 `/content/browser/storage_partition_impl.cc`

###### 1.引用：

```c
#include <iostream>
#include "base/json/json_reader.h"   
#include "net/cookies/canonical_cookie.h"
```

###### 2.找到：

```c
network::mojom::CookieManager*
StoragePartitionImpl::GetCookieManagerForBrowserProcess() {
  DCHECK(initialized_);
  // Create the CookieManager as needed.
  if (!cookie_manager_for_browser_process_ ||
      !cookie_manager_for_browser_process_.is_connected()) {
    // Reset `cookie_manager_for_browser_process_` before binding it again.
    cookie_manager_for_browser_process_.reset();
    GetNetworkContext()->GetCookieManager(
        cookie_manager_for_browser_process_.BindNewPipeAndPassReceiver());
  }
  return cookie_manager_for_browser_process_.get();
}
```

###### 3.替换为：

```c
network::mojom::CookieManager*
StoragePartitionImpl::GetCookieManagerForBrowserProcess() {
  DCHECK(initialized_);
  // Create the CookieManager as needed.
  if (!cookie_manager_for_browser_process_ ||
      !cookie_manager_for_browser_process_.is_connected()) {
    // Reset `cookie_manager_for_browser_process_` before binding it again.
    cookie_manager_for_browser_process_.reset();
    GetNetworkContext()->GetCookieManager(
        cookie_manager_for_browser_process_.BindNewPipeAndPassReceiver());
  }
  // 开始追加 ===========================================
  // 传参：--set-cookies='[{"domain":"https://baidu.com","name":"AAAA","value":"111"},{"domain":"https://baidu.com","name":"BBB","value":"222"}]'
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string json_str = base_command_line->GetSwitchValueASCII("set-cookies"); 
  auto parsed_json = base::JSONReader::Read(json_str);
  if (parsed_json && parsed_json->is_list()){
    for (const auto& item : parsed_json->GetList()) {
      if (!item.is_dict()) 
          continue;
      network::mojom::CookieManager* cookie_manager = cookie_manager_for_browser_process_.get();
      const auto& dict = item.GetDict();
      const std::string* domain = dict.FindString("domain");
      const std::string* name = dict.FindString("name");
      const std::string* value = dict.FindString("value");
      
      //GURL url("https://baidu.com/");
      GURL url(*domain);
      std::string cookie_line = *name + "=" + *value + ";domain=" + url.host();
      std::cerr <<  "set-cookie: " << cookie_line << std::endl;
      //std::string cookie_line = std::string("BBBBB=222222222;domain=") + url.host();
      auto cookie = net::CanonicalCookie::Create(
      url, cookie_line, base::Time::Now(), absl::nullopt /* server_time */,
      std::nullopt, 
      net::CookieSourceType::kOther,
      /*status=*/nullptr
      );
      
      cookie_manager->SetCanonicalCookie(
          *cookie, url, net::CookieOptions::MakeAllInclusive(),
           base::BindOnce([](net::CookieAccessResult result) {
              // 可在此添加日志或错误处理
           })
      );
    }
  }
  // 结束追加 ===========================================
  
  return cookie_manager_for_browser_process_.get();
}

```

> 注意：此处为chromium137版本，其他版本略有不同，需要自行理解。

### 四、检测：

*   cmd执行：

```sh
./chrome.exe https://www.baidu.com/ --user-data-dir=e:/1111/223111 --set-cookies='[{"domain":"https://baidu.com","name":"AAAA","value":"111"},{"domain":"https://baidu.com","name":"BBB","value":"222"}]'
```

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/3e37c5d1541b49dda06e8713e5d3af86.png)

> 可以看到，cookie写入成功了。

