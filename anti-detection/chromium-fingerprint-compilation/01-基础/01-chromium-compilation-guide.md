> chromium编译是个非常耗时的过程，网上教程一搜一大把，我也懒得详细写。  
> 且chromium一直都在更新，编译教程还是要以官网为准。

*   官方编译文档：[https://github.com/chromium/chromium/blob/main/docs/windows\_build\_instructions.md](https://github.com/chromium/chromium/blob/main/docs/windows_build_instructions.md)

### 一、系统要求

*   一台64位的英特尔机器，至少有8GB的内存。推荐超过16GB
*   在ntfs格式的硬盘上至少有100GB的可用磁盘空间。否则 将无法工作，因为一些Git数据包文件大于4GB。
*   VisualStudio的一个适当版本，如下所述。
*   Windows 10 或更新。

### 二、安装 `Visual Studio`

*   您必须安装的组件: "Desktop development with C++"、"MFC/ATL support"
*   或者用命令行安装：

```shell
$ PATH_TO_INSTALLER.EXE ^
--add Microsoft.VisualStudio.Workload.NativeDesktop ^
--add Microsoft.VisualStudio.Component.VC.ATLMFC ^
--includeRecommended
```

### 三、安装SDK

*   Windows 11 SDK version 10.0.22621.2428.
*   (Windows 11) SDK Debugging Tools 10.0.22621.755或更高
*   打开"控制面板\\程序\\程序和功能"，选择"Windows Software Development Kit \[version\] -> Change -> Debugging Tools for Windows"，确定保存。

### 四、安装 `depot_tools`

下载 [depot\_tools bundle](https://storage.googleapis.com/chrome-infra/depot_tools.zip) 解压到 (eg: C:\\src\\depot\_tools).

### 五、设置环境变量

*   将depot\_tools路径添加到path的第一位
*   设置环境变量`DEPOT_TOOLS_WIN_TOOLCHAIN`=0
*   设置环境变量`vs2022_install`=你的vs2022安装路径

### 六、科技梯子

*   设置代理为http://127.0.0.1:10809

### 七、下载源码

```shell
netsh winhttp set proxy http://127.0.0.1:10809 "<local>"
set http_proxy=http://127.0.0.1:10809
set https_proxy=http://127.0.0.1:10809
git config --global user.name "fivcan"
git config --global user.email "fivcan@163.com"
 
mkdir chromium && cd chromium
fetch  --no-history chromium
gclient sync
```

### 八、构建与编译

##### 1\. 构建

```shell
gn gen out\Default --args="is_component_build = false is_debug = false enable_nacl = false  blink_symbol_level = 0 v8_symbol_level = 0 symbol_level = 0"
```

> 以上是最小构建方式  
> 注意：不要打开is\_debug，否则编译出的chromium会非常卡  
> 注意：不要乱去空格，否则构建不了

*   **可选：追加html播放器支持**

```shell
# 追加html播放器支持
proprietary_codecs = true
ffmpeg_branding = "Chrome"
is_component_ffmpeg = false
```

*   **可选：编译release版本**

```shell
# 编译release版本
is_official_build = true
use_official_google_api_keys = false
chrome_pgo_phase = 0
```

> release版本体积更小，但是没有调试信息，仅在正式发布时追加此参数。

##### 2\. 编译

```shell
ninja  -C  out/Default chrome
```

*   out/Default目录下许多会生成文件，chrome.exe是启动文件

##### 3.生成安装包

```shell
ninja  -C  out/Default  mini_installer
```

*   out/Default目录下会生成一个安装包mini\_installer.exe
*   mini\_installer.exe采用静默安装，安装路径默认为：C:\\Users%USERNAME%\\AppData\\Local\\Chromium
*   out/Default目录下生成的chrome.package.7z是绿色免安装包，可以解压即用

> 注意：编译非常慢
