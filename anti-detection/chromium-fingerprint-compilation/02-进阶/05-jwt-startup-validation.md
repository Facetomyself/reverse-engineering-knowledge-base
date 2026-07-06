
### 一、目标：

*   1.启动浏览器时，追加`--validate=xxxx`参数，参数为标准jwt参数格式。如果验证通过，浏览器正常启动，不通过则不予启动
*   2.启动浏览器时，没有`--validate=xxxx`参数，不予启动

### 二、为什么添加启动校验：

*   1.如果你不希望你的浏览器被人拿到就可以直接使用，可以加上此校验参数
*   2.如果你希望用户只能在规定时间内使用，比如只能使用3个月，可以使用此参数
*   3.这是将你的软件迈向商业化的一小步

### 三、JWT格式说明：

###### 1.格式要求：

header:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

> header固定不变

playload:

```json
{
  "iat": 1732335753,
  "exp": 1732339851
}
```

> iat: 签发时间，exp: 超时时间，这2项为必填

secretKey:

```
"secret_key"
```

> secretKey暂定为"secret\_key"

###### 2.示例：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MzIzMzU3NTMsImV4cCI6MTczMjMzOTg1MX0.Rr4eeDguEVBssxF53gZTm1LF-sSvenH9EqN0A07bBHo
```

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/b007f1f5354f436dbd003ee7e7cbbac7.png)

> jwt加解码站点：[https://jwt.io/](https://jwt.io/)

### 四、安装jwt-cpp

###### 1.下载

```shell
git clone https://github.com/Thalhammer/jwt-cpp.git
```

> 下载好后放到src目录下

###### 2.创建文件`jwt-cpp\BUILD.gn`

*   写入：

```c
config("jwt_cpp_config") {
    cflags = [ 
        "-Wno-exit-time-destructors",
        "-Wno-extra-semi" ,
        "/EHsc",
        "-Wno-error",
    ]
    include_dirs = [ "include" ]  # 确保这是jwt-cpp头文件的正确路径
}
# 这个target不生成任何编译输出，只是一个配置的容器
group("jwt_cpp") {
  public_configs = [ ":jwt_cpp_config" ]
}
```

### 五、更改chromium 源码 ：

###### 1.打开：`\content\browser\BUILD.gn`

*   找到：

```c
 deps = [
 ...
 ]
```

*   后面追加：

```c
deps += [ "//jwt-cpp:jwt_cpp" ]
configs -= [
      "//build/config/clang:find_bad_constructs",
      "//build/config/clang:unsafe_buffers",
    ]
```

###### 2.打开：`\content\browser\browser_main_loop.cc`

*   引用：

```c
#include <iostream>
#include "jwt-cpp/jwt.h"
```

*   找到：

```c
void BrowserMainLoop::CreateStartupTasks() {
```

*   替换为：

```c
void BrowserMainLoop::CreateStartupTasks() {
  //追加=====================================
  if (parsed_command_line_->HasSwitch("validate")) {
    std::string jwt = parsed_command_line_->GetSwitchValueASCII("validate");
    try {
      // 替换以下的 secret_key 和验证方法为适合你的情况
      auto decoded = jwt::decode(jwt);
      auto verifier = jwt::verify()
          .allow_algorithm(jwt::algorithm::hs256{"secret_key"});  // HS256 算法和密钥  
      verifier.verify(decoded);
      // JWT 验证成功
      std::cerr << "JWT 验证成功"  << std::endl;
    } catch (const std::exception& e) {
      // JWT 验证失败
      std::cerr << "JWT 验证失败" << e.what()  << std::endl;
      return;
    }
  }else{
      return;
  }
  //结束追加=====================================
```

###### 3.编译

```
ninja  -C  out/Default chrome
```

