# AI 逆向实战：Flutter + Swift 混合型 App 的 Jailbreak 检测分析与绕过

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2026-05-29
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 本文记录一次 iOS 逆向实践：目标 App 启动后被第三方安全 SDK 拦截，直接出现 Jailbroken Device Detected 阻断弹窗。

0\. 引言：一次真实 iOS 混合 App 的 AI 逆向实践

本文记录一次 iOS 逆向实践：目标 App 启动后被第三方安全 SDK 拦截，直接出现  Jailbroken Device Detected
阻断弹窗。

这个 App 不是简单 Demo，而是  Native Swift/ObjC 主体 + Flutter 模块 + 第三方安全 SDK + 混淆字符串 +
动态 selector  的混合型 App。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MST6zTBbpBVLNOBHVPNzpb2dtHEqlRU7ANnfrkjgUsT7BTQLZ0Nl0XicU121boJ4e0RBbUxSgibhhzzffaJoh9sZmv8UBADgHfo4/640?wx_fmt=png&from=appmsg)

正常人工分析难点在于：

  * 检测链路长

  * 关键字符串不完全明文

  * Swift/ObjC/Flutter/ZDefend 多栈交织

  * 全量 hook 还可能触发额外 tamper 风险

这次尝试把分析过程尽量交给 AI：人工只给初始提示词和方向，AI 负责读上下文、写 Frida probe、跑 UI
自动化、整理日志、定位调用链、生成证据矩阵，最终把链路收敛为：

ZDefend rule -> 系统检测函数 -> threat/status -> TargetApp 消费点 -> UIKit alert
builder

本文重点记录这个过程：先用截图确认 App 确实存在 jailbreak 检测，再展示 AI 如何一步步还原链路，最后说明本地绕过为什么选择“结果消费层
sanitize”，而不是盲目 hook 所有底层检测函数。

0.1 实战结果：绕过前 vs 绕过后

绕过前：  目标 App 启动后直接被 jailbreak 检测拦截，只能看到阻断弹窗：

![绕过前：启动即触发 Jailbreak 检测]

![](https://mmbiz.qpic.cn/mmbiz_jpg/yGOpnM3p9MQzslEgEqNnxOarIzCjLU7HSUkMfiaryj6wwRpuFOvbTQGVX5OJoicSSicAt2IbfzlSfFA6baGEYJw6oBX5AsCDfB54jn5iadt2Oiao/640?wx_fmt=jpeg&from=appmsg)

完成分析并在结果消费层做 sanitize patch 后，App 可以正常进入主界面，不再被启动期 jailbreak 弹窗阻断：

![绕过后：App 正常进入主界面]

![](https://mmbiz.qpic.cn/mmbiz_jpg/yGOpnM3p9MT7MicIDTYJibyCgNKFFCWh77KxAfkdiaict82eZpPULSPnLEAe8su7t5N0SNYjvHyribdmwtlWPsWZnd4xva7wEaZDExb7EoEa8ibibE/640?wx_fmt=jpeg&from=appmsg)

这两个截图对应本文的核心目标：

不是简单隐藏一个弹窗，而是先还原  ZDefend rule -> threat/status -> App UI 消费点
的完整链路，再选择副作用更小的本地绕过位置。

0.2 开始分析前：真实提示词片段

这次不是先人工完整分析完再让 AI 总结，而是先给 AI 一个总体方向，再不断让它沿着证据继续深挖。

下面是本次推动 Jailbreak 检测链路分析的真实提示词片段；为了不偏离本文主题，只保留和安全检测链路相关的部分：

    # 最终通用 iOS 登录/验证码接口逆向提示词你扮演一名资深 iOS 逆向工程师。当前任务只在本地授权 CTF/测试环境中进行。目标是通过 **已有上下文读取 + 静态分析 + 运行时验证 + Python replay 复现**，还原目标 iOS App 的登录、验证码、注册、重置密码、token/bootstrap/refresh 等认证相关接口，并输出可脱离原 App 独立运行的纯 Python 复现脚本。最终结果必须能够清楚区分：- 网络不可达 / timeout- HTTP 空响应- 参数错误- 签名 / requestId / 加密错误- 账号、密码、验证码等业务错误- 服务端异常- 成功请求重要原则：**不要预设目标一定有自研签名。** 如果实际使用 Supabase、Firebase、Auth0、Cognito、Clerk、OAuth、GraphQL、WebView/H5 或其它第三方认证体系，应以静态和运行时证据为准，按真实 wire protocol 复现。---## 0. 工作目录与产物约定当前工程目录可能包含：```text.ipa / .app / Payload/主二进制 / Frameworks/Info.plist / ProjectConfig.plist / buildInfo.confstrings / nm / otool / class-dump / IDA 输出Frida 脚本与日志iOS MCP 调用脚本、UI 截图、元素树历史 Python replay 脚本、state、请求响应 capture```所有新产物继续写入：```textanalysis/analysis/frida_scripts/analysis/captures/docs/output/```不要把长期有效 access token、refresh token、session、Keychain secret 明文写入最终文档或最终回复。文档中使用：```text<server_issued_access_token><server_issued_refresh_token><device_id><session_id>```state 文件可以用于本地验证，但文档和总结必须脱敏。---## 1. 先读取已有上下文，避免重复从零开始如果存在以下文件，必须先读取并延续已有结论：```textdocs/login_reverse_summary.mddocs/next_prompt.mdanalysis/header_bootstrap_logic.mdanalysis/captures/runtime_key_excerpts.mdanalysis/captures/python_*_*.jsonanalysis/captures/frida_*_login*.logoutput/*_login_replay.pyoutput/*_runtime_state.json```先判断每条已有结论的证据类型：```text运行时事实 > Python replay 验证 > 静态反编译推断 > strings/grep 猜测```如果已有结论和运行时证据冲突，以运行时最终请求为准。---## 2. 先做基础状态与网络确认确认 App、设备、Frida、iOS MCP、网络是否可用：```bashfrida-ps -Uai | grep -i '<app_or_bundle_keyword>'python3 ios_mcp_call.py call get_frontmost_app '{}'python3 ios_mcp_call.py call get_screen_info '{}'python3 ios_mcp_call.py call get_ui_elements '{"max_depth":25,"max_elements":3000}'```如果存在本地 CTF 服务地址，例如 `http://<private-ip>`，先测：```bashcurl -i -sS --max-time 5 http://<local-ip>/```如果 timeout / connection refused / no route to host，要记录为：```textMac 到本地服务不可达```不要误判为 Python 脚本、参数或签名失败。---## 3. 先判断认证体系类型静态和运行时都要判断目标属于哪类认证体系：```text1. Supabase / Firebase / Auth0 / Cognito / Clerk 等 BaaS/Auth SDK2. OAuth / Apple / Google / Facebook 等第三方 token exchange3. 自研 REST API4. GraphQL5. WebView / H5 登录6. React Native / Flutter / Hybrid 自定义桥接网络层```识别依据包括：```textbase URL / hostSDK 字符串anon key / api key / client id / project idAuthorization 格式token 缓存 key接口 path运行时最终 JSON body/query请求 headers响应 body```如果是 BaaS/Auth SDK：- 不要强行假设存在自研 `sign` / `requestId`。- 公开 client key / anon key 可以作为客户端配置使用。- 服务端签发 token 不要伪造，应通过 login / otp / refresh / bootstrap 正常获得。- Python replay 应按 SDK 的真实 HTTP 协议复现。如果是自研 API：- 再重点追踪 `sign`、`signature`、`requestId`、`nonce`、`timestamp`、HMAC、AES、RSA、URL encoding 等逻辑。---## 4. 静态分析任务### 4.1 App 基础信息提取并记录：```textBundle IDApp 名称版本号 / build主二进制名称Frameworks最低系统版本URL Scheme / Associated DomainsATS 配置```### 4.2 环境与 base URL定位：```text生产 / 测试 / staging / debug 环境切换逻辑API base URLCDN / gateway / auth hostGraphQL endpointWebView/H5 URL本地 CTF 域名重定向关系```### 4.3 网络层定位重点查找：```textAPI Manager / Service / Router / TargetType / Endpoint / RequestBuilderMoya / Alamofire / AFNetworking / NSURLSessionSupabase / Firebase / Auth0 / Cognito / GraphQL ClientReact Native RCTNetworkingFlutter MethodChannel / Dio / http clientWebView bridge```要还原：```textmethodpathquerybodyheaderstimeoutcontent-type公共 interceptor / middleware```### 4.4 登录相关接口范围至少覆盖：```text密码登录获取验证码 / 重发验证码验证码登录注册 / 注册验证码忘记密码 / 重置密码验证码token refreshbootstrap / init / anonymous session第三方登录 token exchange，如果存在登出，如果会影响 session/token```### 4.5 签名 / 加密 / 编码定位只在有证据时深入，不要先入为主。搜索关键词：```textsign / signature / requestId / nonce / timestamp / tshmac / sha1 / sha256 / md5AES / RSA / CCCrypt / CCHmac / CC_SHA / CC_MD5encrypt / decrypt / encode / urlEncode / base64buildHeaders / buildRequest / appendPublicParams```如果存在自研签名，必须还原：```textcanonical string 组成参与签名的 query/body/header 字段参数排序规则空值/null/数组/嵌套对象处理方式URL encode 在签名前还是签名后timestamp 来源、单位、精度nonce/requestId 生成方式secret/key 来源：硬编码、配置、服务端下发、本地派生hash/HMAC/RSA/AES 算法细节输出大小写、hex/base64 格式GET query 与 POST body 是否统一参与签名```如果没有自研签名，要明确写：```textN/A: runtime evidence indicates no custom sign/requestId```---## 5. Runtime token / device / session 来源追踪不要硬编码 Frida 抓到的 token、session、ST、UT、device id、install id、push token。必须追踪来源：```text本地生成：UUID / install id / device id / random nonce本地缓存：NSUserDefaults / Keychain / SQLite / plist / AsyncStorage服务端下发：bootstrap / anonymous session / login response / refresh response第三方下发：Apple / Google / Firebase / APNS / FCM```如果某个 header 是服务端签发 token/JWT：- 不要伪造服务端签名。- 应在 Python 中复现 App 的 bootstrap / login / refresh 请求来获取。- 如果无法获取，必须说明阻塞点和证据。建议文档化 state schema：```json{  "app": "<app_name>",  "bundle_id": "<bundle_id>",  "base_url": "https://<host>",  "device_id": "<device_id>",  "install_id": "<install_id>",  "access_token": "<server_issued_access_token>",  "refresh_token": "<server_issued_refresh_token>",  "session_id": "<session_id>",  "expires_at": 0,  "updated_at": 0}```---## 6. Frida hook 策略Frida hook 至少覆盖 request-side：```textNSURLSession dataTask/uploadTaskNSURLSessionTask resumeNSMutableURLRequest setURL:NSMutableURLRequest setHTTPMethod:NSMutableURLRequest setHTTPBody:NSMutableURLRequest setValue:forHTTPHeaderField:NSMutableURLRequest addValue:forHTTPHeaderField:NSMutableURLRequest setAllHTTPHeaderFields:```同时根据 App 类型覆盖：```text业务入口：login / auth / otp / verify / register / reset / refresh公共参数：appendHttpPublic / buildRequest / buildHeaders / interceptor存储：NSUserDefaults / Keychain / SQLite / AsyncStorage / plistCrypto：CC_MD5 / CC_SHA* / CCHmac / CCCrypt / SecKey / RSAReact Native：RCTNetworking / fetch / XMLHttpRequest bridgeWebView：WKWebView loadRequest / evaluateJavaScript / messageHandlerFlutter：MethodChannel / URLSession / Dart 层网络桥接，如能定位```启动示例：```bashfrida -U -f <bundle_id> \  -l analysis/frida_scripts/<app>_login_hooks.js \  -o analysis/captures/frida_<app>_login.log```如果当前 Frida 版本不支持 `--no-pause`，不要加该参数。如果 wrapping completion block 导致 App 或 FridaAgent 崩溃，则降级为稳定 request-side hook；响应由 Python replay 捕获。---## 7. 用 iOS MCP 真实触发 UI 流程你可以通过 iOS MCP 服务操作一台 iPhone 设备。MCP 地址: http://<private-ip>:8090/mcp支持的操作:- 触控：点击、滑动、长按、双击、拖拽- 文字输入：快速粘贴输入、逐字键盘模拟、特殊键（回车、删除等）- 硬件按键：Home、电源、音量、静音- 截图（screenshot 返回 MCP image content，不是 text；图片 base64 在 result.content[0].data，mimeType 通常是 image/jpeg）- App 管理：启动、关闭、列表、安装 IPA（无需签名）、卸载- UI 无障碍：获取当前页面节点树、坐标查询元素- 剪贴板：读写剪贴板内容- 设备控制：锁屏/解锁、亮度、音量- 打开 URL 或 URL Scheme- Shell 命令执行- 设备信息：型号、iOS 版本、电池、存储操作规则:1. 开始前先获取当前前台 App、UI 节点和必要截图。2. 交互时优先根据 UI 节点执行点击和输入，不要盲点。3. 页面变化后重新读取 UI 节点，再继续下一步。4. 如果目标元素不明显，先截图再判断。5. 处理 screenshot 结果时，按 image content 解析，不要读取 result.content[0].text。必须尽量通过 UI 真实触发，而不是只看静态代码。触发范围：```text密码登录获取验证码 / 重发验证码验证码登录忘记密码 / 重置密码验证码注册 / 注册验证码第三方登录 token exchange，如果有入口```使用 UI tree / 截图定位，不要盲点：```bashpython3 ios_mcp_call.py call get_ui_elements '{"max_depth":25,"max_elements":3000}'python3 ios_mcp_call.py call tap_screen '{"x":<x>,"y":<y>}'python3 ios_mcp_call.py call input_text '{"text":"<test@example.com>"}'python3 ios_mcp_call.py save_image screenshot analysis/captures/ios_screenshot_<step>.jpg '{}'```保存关键 UI 状态：```textanalysis/captures/ios_ui_<step>.jsonanalysis/captures/ios_screenshot_<step>.jpg```如果 MCP UI tree 失败，要保存错误、截图和替代证据；不要因此停止静态分析或 Python replay。---## 8. 从 Frida 日志提取接口证据使用类似命令提取关键线索：```bashgrep -nE 'REQ_SET_URL|REQ_SET_METHOD|REQ_SET_BODY|REQUEST|RCT_NETWORKING|CRYPTO_IN|CRYPTO_OUT|Authorization|token|refresh|otp|verify|login|password|register|reset|apikey|client-info|device|install|push|sign|requestId|signature' \  analysis/captures/frida_<app>_login.log | tail -300```每个接口必须记录：```text场景：密码登录 / 验证码发送 / 验证码登录 / 重置密码 / 注册 / refresh / bootstrap认证体系类型：自研 / Supabase / Firebase / Auth0 / GraphQL / WebView / 其它method:path:base_url:headers:运行时最终 body/query:公共参数:token/session/device/push 来源:requestId/sign preimage/value（如存在）:是否 AES/HMAC/RSA/编码:服务端响应:错误分类:证据来源：Frida 日志行号 / IDA 函数 / Python capture 文件```关键原则：**运行时最终 key 优先**。不要只相信 Swift/ObjC/JS 方法入参标签。例如静态看到：```textaccount / userPsd / isEmail```运行时可能实际发送：```textemail / password / loginType / msgToken```最终 replay 以运行时请求为准。---## 9. Python replay 脚本要求输出：```textoutput/<app>_login_replay.pyoutput/<app>_runtime_state.json```脚本必须可脱离原 App 独立运行。### 9.1 CLI 参数至少支持：```text--dry-run--send--api <name>--base-url--sign-base-url--timestamp--request-id-preimage--expect-sign--param key=value--header key=value--state-file output/<app>_runtime_state.json--refresh-auth--no-auto-auth--no-runtime-headers--timeout```建议支持：```text--method--path--body-json--proxy--insecure--verbose--save-capture```### 9.2 参数和 header 处理要求：1. CLI 可接受静态字段别名，但最终发送运行时真实 key。2. 显式 `--header` 优先级最高。3. `--base-url` 与 `--sign-base-url` 分离，便于本地 IP 直连但按生产 host 构造 canonical/sign。4. 公共参数结构必须和运行时一致。5. Content-Type、User-Agent、locale、timezone、app version 等 headers 要按运行时证据复现。### 9.3 dry-run 输出`--dry-run` 必须输出：```textapi namemethodfinal URLfinal headersfinal body/querysorted params/bodycanonical stringrequestId/sign preimagerequestId/sign value 或 N/A: no custom signingexpect-sign check 结果```如果有 `--expect-sign`：```text-- expect-sign check --OK:<sign/requestId>```或：```textFAIL:expected=<value>actual=<value>```### 9.4 send 输出`--send` 必须输出：```textstatusresponse headersresponse body，JSON 自动格式化error/timeout 摘要classificationcapture 文件路径```请求和响应保存到：```textanalysis/captures/python_<app>_<api>_<timestamp>.json```capture 建议包含：```json{  "request": {    "method": "POST",    "url": "https://<host>/<path>",    "headers": {},    "body": {}  },  "response": {    "status": 200,    "headers": {},    "body": {}  },  "classification": "ok",  "error": null}```### 9.5 自动 runtime bootstrap如果缺少 token、session、ST、UT、device id、install id、anon key 等运行时字段：1. 先查 `--header` / `--param` 显式输入。2. 再查 state 文件。3. 如允许 auto auth，则调用 bootstrap / anonymous / login / refresh 获取。4. 获取后写回 state。5. 如果 `--no-auto-auth`，不得自动联网 bootstrap。6. 如果 `--refresh-auth`，强制重新获取并覆盖 state。7. 如果 `--no-runtime-headers`，完全关闭自动运行时 headers。---## 10. 错误分类规则必须按以下优先级分类：```textnetwork_timeout: timeout / 连接超时network_unreachable: connection refused / DNS / no route / unreachableserver_empty_body: HTTP 有响应但 body 空ok: HTTP 2xx 且请求语义正常，尤其先于文本关键字扫描business_auth_failed: invalid credentials / user not found / password error / session_not_found / refresh_token_not_foundbusiness_otp_failed: invalid OTP / expired OTP / invalid verification tokenparameter_error: missing parameter / invalid parameter / validation errorsignature_or_requestid_error: 明确 invalid sign / invalid signature / invalid requestId / timestamp invalidserver_error: HTTP 5xxunknown_error: 无法归类```重要修正：- HTTP 2xx 要优先考虑 `ok`，不要仅因 body 包含 `sign` 字段就误判签名错误。- 不要因为响应字段包含 `last_sign_in_at`、`sign_in_provider` 等词就误判为 sign 错误。- 账号不存在、密码错误、验证码错误通常说明请求已到业务层，不等于签名失败。- timeout/connection refused 是网络问题，不是签名问题。---## 11. 验证命令模板### 11.1 dry-run 复现 Frida 抓到的 sign/requestId仅在存在自研签名时使用：```bashpython3 output/<app>_login_replay.py \  --dry-run \  --api<login_password|login_code|send_code|reset_code> \  --request-id-preimage '<Frida_CRYPTO_IN_preimage>' \  --expect-sign '<Frida_body_requestId_or_sign>' \  --param account='<test@example.com>' \  --param pwd='<password>' \  --param isEmail=true```预期：```text-- expect-sign check --OK: <sign/requestId>```如果无自研签名，应输出：```textN/A: runtime evidence indicates no custom sign/requestId```### 11.2 send 到生产/测试环境```bashpython3 output/<app>_login_replay.py \  --send \  --api login_password \  --param account='<test@example.com>' \  --param pwd='<password>' \  --param isEmail=true \  --timeout 15```### 11.3 send 到本地 CTF IP```bashpython3 output/<app>_login_replay.py \  --send \  --api login_password \  --base-url http://<local-ip> \  --sign-base-url https://<production-host> \  --param account='<test@example.com>' \  --param pwd='<password>' \  --param isEmail=true \  --timeout 15```如果 timeout，要明确打印：```textclassification=network_timeoutstatus=Nonebody=<empty>```如果 HTTP 有响应但 body 为空，要明确打印：```textclassification=server_empty_bodystatus=<status_code>body=<empty>```---## 12. 证据矩阵要求最终文档中每个关键结论都要尽量包含证据来源。建议表格：```text结论 | 类型 | 证据来源 | 文件/函数/日志行 | 可信度 | 备注```类型包括：```textruntime_requestruntime_cryptopython_replaystatic_decompilestrings_guess```可信度建议：```texthigh: 运行时最终请求或 replay 验证通过medium: 静态反编译和日志部分吻合low: 仅 strings/grep 推测```---## 13. 文档输出要求每轮结束必须更新：```textdocs/login_reverse_summary.mddocs/next_prompt.mdanalysis/header_bootstrap_logic.mdanalysis/captures/runtime_key_excerpts.md````docs/login_reverse_summary.md` 至少包含：```text1. App 基础信息2. 认证体系类型与判断依据3. base URL / env 选择逻辑4. 登录/验证码/重置/注册/refresh/bootstrap 接口列表5. 每个接口的 method/path/headers/body/query6. 运行时最终参数字段，不只写静态方法标签7. 公共 headers/params8. token/device/install/session/push 来源9. sign/requestId/encryption 结论：存在则写算法，不存在则明确 N/A10. Python replay 使用方法11. dry-run 验证结果12. send 验证结果与错误分类13. 本地 CTF IP 是否可达14. 未解决问题与下一步建议15. 敏感 token 脱敏说明````analysis/header_bootstrap_logic.md` 如存在复杂 runtime header/token，必须写：```text字段名来源生成/获取步骤是否缓存过期/刷新逻辑Python replay 中如何处理````docs/next_prompt.md` 必须面向下一轮工作，包含：```text当前已确认结论当前阻塞点下一步最小验证路径建议优先执行的命令不要重复做的事情```---## 14. 最小闭环优先级不要一开始就试图还原所有接口。优先完成一个最小闭环：```text1. 选一个最关键接口，例如 send_code 或 login_password2. 通过 Frida 获取运行时最终请求3. 用 Python dry-run 复现最终请求/sign4. 用 Python send 得到服务端响应5. 正确分类响应6. 保存 capture7. 再扩展其它接口```如果项目很复杂，优先顺序：```text认证体系判断 > runtime 最终请求 > token/bootstrap 来源 > Python replay > 其它接口补全 > 文档整理```---## 15. 验收标准本轮任务完成时必须满足：```text1. Python replay 可独立运行2. --dry-run 能展示最终请求和 canonical/sign 信息3. 如果存在自研 sign/requestId，--dry-run --expect-sign 能复现 Frida 抓到的值4. 如果不存在自研签名，明确输出 N/A: no custom signing5. --send 能打印完整响应或明确 timeout/empty body6. 不依赖硬编码 Frida 抓到的服务端 token7. state/bootstrap/refresh 逻辑清楚8. 登录失败能区分业务失败、参数失败、签名失败、网络不可达9. 每个关键结论有证据来源10. 文档和最终回复中的敏感 token 已脱敏```最终回复必须使用中文，列出：```text关键文件路径已验证命令验证结果错误分类仍未解决的问题下一步建议```

后续 AI 的行为基本都围绕这几句话展开：先找原始检测，再下钻到 rule，再追系统调用，最后把 threat/status 到 App
弹窗的链路闭环验证。

0.3 本次 AI 辅助逆向使用到的工具与技术清单

本次分析不是单靠某一个工具完成，而是由 AI 编排多类静态、动态和自动化验证手段，持续把“猜测”收敛成“可复现证据”。

下表是本次实际用到的主要工具/技术：

类别  |  工具 / 技术  |  本次用途
---|---|---
静态反汇编 / 反编译  |  IDA Pro / Hex-Rays  |  分析  `
` ` TargetAppProd  ` 与  ` ZDefend.framework/ZDefend  ` ，  定位  ` ZDeviceStatus
` 、  ` ZDefendThreat  ` 、0x100902864  alert builder、native primitive
IDA 自动化  |  IDA Python / MCP 查询  |  批量导出函数、xrefs、字符串解密点、stub/import map、Swift field metadata，减少人工翻函数时间
Mach-O 分析  |  ` otool  ` / Mach-O segment/stub/indirect symbol 解析  |  确认  ` _objc_msgSend  ` 、  ` _sel_registerName  ` 、  ` _objc_getClass  ` 、Swift bridge 等 stub 归属
字符串与配置搜索  |  ` strings  ` / grep / JSON 汇总  |  搜索 Framework、SDK、ZDefend asset 和策略相关字符串；确认很多关键 rule/path 并非明文硬编码
Swift metadata 分析  |  ` __swift5_fieldmd  ` / ObjC ivar metadata  |  确认  `
` ` AppDelegate.jailBreakAlert: UIAlertController?  ` 、  `
TargetAppTabBarController.deviceStatusRegistration  ` 等字段
运行时插桩  |  Frida  ` Interceptor.attach  ` |  只读观察  ` lstat/sysctlbyname/fcntl  ` 、  ` activeThreats  ` 、UIKit alert/present
运行时方法替换  |  Frida  ` method_setImplementation  ` / ObjC method implementation assignment  |  在本地 sanitize build 中做  参数级验证：固定  `
` ` internalThreatID=39/severity=3/isMitigated=0  ` 并触发真实 UI
C API 调用链追踪  |  Frida backtrace + system call hook  |  串联  ` JB  ` ` Dopamine-Roothide -> sub_25297C/sub_252848 -> lstat/lstat64(paths)  `
ObjC/Swift selector 追踪  |  ` objc_msgSend  ` callsite hook / selector decode  |  确认  `
` ` activeThreats  ` 、  `
` ` internalThreatID  ` 、  ` UIAlertController  ` 、  `
presentViewController:animated:completion:  ` 等动态 selector
iOS UI 自动化  |  iOS MCP  |  启动 App、读取 UI tree、截图、点击弹窗、验证 App UI 状态和 jailbreak alert 文案
Runtime 状态解析  |  base64 JSON decode / threat/status 结构化  |  解析  `
` ` device_status_base64  ` ，脱敏保存
threats、ruleName、legacyThreatId、severity、forensic 摘要
Python 自动化  |  Python 脚本 / JSON evidence generator  |  生成结构化证据文件、整理 runtime 参数、维护 capture/state、辅助整理 runtime 证据
本地 patch  |  Mach-O 指令级 patch / IPA 重打包安装  |  对 ZDefend 结果 getter 做 sanitize patch，绕过启动期阻断 UI，进入正常 App 流程
证据管理  |  Markdown 报告 + evidence matrix  |  按 runtime 事实、静态反编译、strings 猜测分级记录结论
AI 协作方式  |  上下文读取、计划拆解、日志归并、代码生成、文档同步  |  自动串联静态/动态证据，生成 Frida probe、Python parser、最终文章和下一步提示词

其中最关键的协作点是：AI 不直接把某个字符串命中当结论，而是持续要求每条判断都有证据来源。

例如  internalThreatID=39 -> Jailbroken Device Detected  这条链路，先由静态字符串解密得到映射，再由
Frida runtime 参数级验证，最后用 iOS MCP UI tree 复核弹窗文本，才写入 high-confidence 结论。

0.4 这是一份由 AI 主导完成的逆向分析结果

本次分析比较特别的一点是：我主要在开始阶段给出总体提示词，明确目标、证据优先级和输出要求；后续的大部分分析流程，基本由 AI 自行推进。

AI 自动完成了上下文读取、Frida probe 编写、运行时日志整理、IDA/Swift metadata 交叉定位、UI tree
复核、调用链归纳和文档更新。我更多是在过程中确认方向，并不断要求它继续下钻到 rule、系统调用和 runtime 参数验证。

所以这篇文章记录的不只是一次 jailbreak 检测绕过，也是一种 AI 辅助逆向的实践方式：给出清晰目标后，让 AI
持续生成实验、验证证据，并把零散结果整理成完整链路。

0.5 本文范围

本文只聚焦  Jailbreak 检测链路分析与本地绕过实践  ：包括 ZDefend rule、系统检测函数、threat/status 结构、App
侧消费点、UIKit 阻断弹窗和 sanitize patch
设计。其它业务流程、账号体系、服务端交互等内容不在本文展开，以保证文章主线集中在本地安全检测与 UI 阻断链路。

1\. 现象截图：目标应用确实存在 Jailbreak 检测

先看最直观的现象：在测试设备上启动目标 App，主界面没有正常进入，而是直接弹出  Jailbroken Device Detected  阻断框。

![目标 App 启动后触发Jailbreak 检测]

![](https://mmbiz.qpic.cn/mmbiz_jpg/yGOpnM3p9MQzslEgEqNnxOarIzCjLU7HSUkMfiaryj6wwRpuFOvbTQGVX5OJoicSSicAt2IbfzlSfFA6baGEYJw6oBX5AsCDfB54jn5iadt2Oiao/640?wx_fmt=jpeg&from=appmsg)

对应 UI tree 中能读到完整文案：

    title   = Jailbroken Device Detectedmessage = Your device appears to be jailbroken. For your security, TargetApp cannot be used. Contact your device service centre to fix your device.button  = 了解

这一步很重要：它先证明问题不是“猜测 App 有越狱检测”，而是运行时 UI 已经高可信确认存在 jailbreak blocking alert。

如果按传统方式硬翻，第一反应可能是搜索

Jailbroken Device Detected  、  isJailbroken  、  jailBreakAlert  等字符串。

但这次实际情况并不简单：弹窗文案不是普通明文路径；App 侧也不是一个简单 if 判断；

真正的触发链路跨过

ZDefend SDK、Swift/ObjC 状态机、

动态 selector 和 UIKit alert builder。

后续静态与运行时证据显示，真实链路更复杂：

    ZDefend native rule / classifier  -> device_status_base64  -> ZDeviceStatus / ZDefendThreat  -> TargetAppProd activeThreats 消费点  -> TargetAppProd alert builder  -> UIKit blocking alert

换句话说，阻断 UI 不是单个路径检查直接弹窗，

而是 ZDefend SDK 先生成 threat/status，

再由目标 App 主工程消费  activeThreats  并展示安全弹窗。

2\. 运行时威胁事实

在未 sanitize 的原始状态下，ZDefend 运行时生成了多个 active threat。脱敏后的核心结果如下：

threat  |  ruleName  |  internalThreatID  |  severity  |  说明
---|---|---|---|---
` DEVICE_ROOTED  ` |  ` JB Dopamine-Roothide  ` |  39  |  3  |  RootHide/Dopamine/Sileo 相关越狱痕迹命中
` DEVICE_ROOTED  ` |  ` ios_combined_classifier  ` |  39  |  3  |  iOS 综合越狱/环境分类器命中
` APP_TAMPERING  ` |  ` ios_combined_classifier  ` |  75  |  3  |  App tamper / 注入 /  完整性类风险

一个关键经验是：不要只依赖  strings  查找。

DEVICE_ROOTED  、

JB Dopamine-Roothide  、

ios_combined_classifier

等并不是主二进制明文硬编码出来的普通字符串，

而是运行时 status/policy 产物。

3\. ZDeviceStatus：

从 status JSON 到 activeThreats

ZDefend 的关键入口是：

    +[ZDeviceStatus sendDeviceStatusToListeners:] @ 0x102c0

它接收 JSON 字符串，解析外层 status，再把  device_status_base64  解成内层 status JSON，最终构造
ZDeviceStatus  。

关键初始化函数：

    -[ZDeviceStatus initWithStatusDict:priorStatus:] @ 0xe548

其中  threats  数组会

逐个被包装成  ZDefendThreat  ：

    for each item in status["threats"]:    threat = [[ZDefendThreat alloc] initWithThreat:item]    [self.allThreats addObject:threat]    if threat.isMitigated:        [self.mitigatedThreats addObject:threat]    else:        [self.activeThreats addObject:threat]

相关 getter 的 ivar offset 如下：

Getter  |  地址  |  原始 ivar offset  |  含义
---|---|---|---
` -[ZDeviceStatus allThreats]  ` |  0x10d90  |  0x70  |  所有  threat
` -[ZDeviceStatus activeThreats]  ` |  0x10dd4  |  0x78  |  未  mitigated 的  active threat
` -[ZDeviceStatus mitigatedThreats]  ` |  0x10e18  |  0x80  |  已  mitigated threat
` -[ZDeviceStatus activeNewThreats]  ` |  0x10e5c  |  0x88  |  与  priorStatus  比较后的新增  active threat

这为后续“结果消费层绕过”提供了很好的切入点。

4\. ZDefendThreat：威胁对象字段映射

-[ZDefendThreat initWithThreat:] @ 0xc23c

会把 threat dict 中的字段保存到 ObjC 对象。关键字段映射：

getter / 含义  |  来源字段  |  说明
---|---|---
` internalThreatID  ` |  ` legacyThreatId  ` |  39 表示  DEVICE_ROOTED；  75 表示 APP_TAMPERING
` severity  ` /  ` threatSeverity  ` |  ` severity  ` |  ` CRITICAL  ` 映射为数值 3
` mitigated  ` /  ` isMitigated  ` |  ` mitigated  ` |  决定是否进入  `
` ` activeThreats  `
` internalName  ` |  ` lang_description.internalLocalizationName  ` |  运行时为  `
` ` DEVICE_ROOTED  ` /  ` APP_TAMPERING  `
` ruleName  ` |  顶层  ` internalName  ` |  运行时为  ` JB Dopamine-Roothide  ` /  `
` ` ios_combined_classifier  `

因此，App 层真正关心的不是底层检测函数本身，而是最终可见的 threat getter 返回值。

5\. rule 级分析：最原始检测方式

为了确认最原始的检测方式，使用只读 Frida probe 调用：

    +[ZDDHelper runRuleBlocking:Details:]

重点验证两个 rule：

    JB Dopamine-Roothideios_combined_classifier

5.1 JB Dopamine-Roothide

该 rule 的完整链路为：

    ZDDHelper.runRuleBlocking("JB Dopamine-Roothide")  -> com.zimperium.dd.runRule  -> ZDefend rule VM / evaluator  -> sub_25297C / sub_252848  -> lstat / lstat64(path)  -> ZDDRuleResult(triggered=true)  -> ZDefendThreat(ruleName="JB Dopamine-Roothide", legacyThreatId=39)

运行时  lstat/lstat64  命中的典型路径包括：

    /var/mobile/Library/Caches/com.opa334.Dopamine/var/mobile/Library/Caches/org.coolstar.SileoStore/var/mobile/Library/HTTPStorages/com.opa334.Dopamine/var/mobile/Library/HTTPStorages/org.coolstar.SileoStore/var/mobile/Library/SplashBoard/Snapshots/org.coolstar.SileoStore

对应 rule result：

    triggered    = truetriggerValue = 02 00 00 0e 01forensic     = Reasons=Dopamine detected

其中事件 ID  0x0e  在 ZDefend taxonomy 中对应  com.zimperium.fs.mounted_all  类文件系统信号。

5.2 ios_combined_classifier

ios_combined_classifier  是综合分类器，观测到的底层特征包括：

    sub_F14A4 -> sysctlbyname(security.mac.*_enforce)sub_F9A94 -> sub_D84F0 -> sub_D8568 -> open + fcntl(fd, 61)injected library forensic

运行时 forensic 摘要：

    Reasons = ML: App tampering detectedfeatures_vector_len = 27injected_libs = /usr/lib/systemhook-...dylib

这解释了为什么同一个综合 classifier 既可能映射到  DEVICE_ROOTED  ，

也可能映射到  APP_TAMPERING  ：底层输出是风险特征，策略层再映射为业务threat。

5.3 应用/SDK 中用到的系统检测函数列表

下表只列本轮已通过 imports、静态反编译或 runtime call-chain probe 确认的函数。

它们主要位于

ZDefend.framework/ZDefend  ，宿主 App

通过  ZDeviceStatus  /  ZDefendThreat  消费最终结果。

类别  |  系统函数 / runtime API  |  本轮证据  |  作用判断
---|---|---|---
文件存在性 / 越狱痕迹  |  ` access  ` |  imports /  ` sub_F68B8  ` / primitive registry  |  检查策略中配置的路径是否存在
文件状态  |  ` stat  ` |  imports /  ` sub_25297C  ` 静态反编译  |  读取文件 metadata；iOS 上 runtime 观测与  ` lstat/lstat64  ` 包装有关
符号链接 / 路径状态  |  ` lstat  ` ,  ` lstat64  ` |  live call-chain probe  |  ` JB Dopamine-Roothide  ` 直接命中 Dopamine/Sileo/SplashBoard 路径
文件系统 / 挂载状态  |  ` statfs  ` |  ` sub_F022C  ` |  读取  ` f_flags/f_fstypename/f_mntfromname/f_mntonname  ` 等，用于挂载/文件系统异常判断
文件打开  |  ` open  ` |  ` sub_D8568  ` /  ` ios_combined_classifier  ` |  为后续完整性或签名校验打开目标文件
文件关闭  |  ` close  ` |  ` sub_D8568  ` 调用链  |  与  ` open/fcntl  ` 配套
目录枚举  |  ` opendir  ` ,  ` readdir  ` |  imports / runtime probe 范围  |  枚举目录项，辅助发现越狱或注入相关文件
路径解析  |  ` readlink  ` |  imports / runtime probe 范围  |  检查 symlink / 重定向路径
标准 IO  |  ` fopen  ` |  imports  |  读取策略或本地文件内容的辅助路径
内核/系统状态  |  ` sysctl  ` |  imports /  ` sub_F19CC  ` |  按 MIB 读取内核/系统状态
命名  sysctl  |  ` sysctlbyname  ` |  ` sub_F16F4  ` ,  ` sub_F11A4  ` , live probe  |  ` ios_combined_classifier  ` 读取  ` security.mac.*_enforce  ` 特征
文件控制 / 完整性  |  ` fcntl(fd, 61, ...)  ` |  ` sub_D8568  ` |  代码签名/文件完整性相关信号，和 APP_TAMPERING 语义吻合
环境变量  |  ` getenv  ` |  ` sub_247F58  ` |  检查注入/调试/运行时环境变量
ObjC 方法检查  |  ` class_getInstanceMethod  ` |  ` sub_EBB70  ` |  ZDefend 自己的 touch events hook 管理；不是本轮 jailbreak 主因
ObjC IMP 读取  |  ` method_getImplementation  ` |  ` sub_EBB70  ` |  同上，也可作为 hook/tamper 检查基础
ObjC IMP 替换  |  ` method_setImplementation  ` |  ` sub_EBB70  ` |  ZDefend 内部 instrumentation；full hook 场景可能引入 tamper 信号
symlink 辅助  |  ` +[OsFunctions fileIsSymlink:]  ` |  0xed028  |  对路径是否为符号链接做封装判断

补充说明：

  * live  JB Dopamine-Roothide

规则的关键系统调用是

lstat/lstat64(path)  ；

这一路已经精确到具体

Dopamine/Sileo/SplashBoard artifact。

  * live  ios_combined_classifier  的关键系统

调用包括

sysctlbyname(security.mac.*_enforce)

与  open + fcntl(fd,61) + close  。

  * 本轮未在原始 imports 中确认直接导入  ptrace  、  fork  、

dladdr  、  csops  等传统反调试/签名 API；

ZDefend 的 taxonomy 中存在

com.zimperium.proc.*  事件名，

但具体 iOS 实现可能被内联或由其它策略模块触发，本文不把它们列为“已确认调用”。

6\. App 侧消费链路：

activeThreats 到弹窗

ZDefend 生成 status 后，会通过 listener 回调宿主 App。最终定位到 目标 App 主工程中的链路：

    TargetAppTabBarController.deviceStatusRegistration  -> 0x10090f14c  -> 0x1008f344c register ZDeviceStatus callback  -> block invoke 0x1003d9abc  -> Swift closure 0x1008f4864  -> active handler 0x100904c98  -> objc_msgSend(selector=activeThreats) @ 0x100905c28

activeThreats  非空后，  0x100904c98  会选择 threat 并调用真正的 alert builder：

    0x100904c98  -> 0x1009055cc: bl 0x1009028640x100902864  -> objc_msgSend(selector=internalThreatID)  -> switch internalThreatID  -> 解密 title/message 与 UIKit selector  -> UIAlertController.alertControllerWithTitle:message:preferredStyle:  -> UIAlertAction.actionWithTitle:style:handler:  -> addAction:  -> presentViewController:animated:completion:

静态解密后得到的部分 threat ID 映射：

internalThreatID  |  title  |  说明
---|---|---
14  |  ` SSL Strip Warning  ` |  通信被拦截风险
37  |  ` System Tampering Detected  ` |  系统篡改
38  |  ` Rogue Access Point  ` |  Rogue AP
39  |  ` Jailbroken Device Detected  ` |  越狱设备
75  |  ` App Tampering Detected  ` |  App 篡改
125  |  ` Compromised Network Detected  ` |  网络被攻陷
130  |  ` Pegasus Spyware Detected  ` |  间谍软件风险
default  |  ` Device is compromised  ` |  默认风险提示

7\. runtime 参数级验证

为了确认  internalThreatID=39  是否确实对应原始 jailbreak 弹窗，

使用本地 sanitize build 做参数级闭环：构造真实  ZDefendThreat  对象，

临时固定关键 getter 返回值，

再调用  TargetAppProd +0x902864  。

验证脚本：

    analysis/frida_scripts/targetapp_zdefend_alert_builder_runtime_verify_methodset.js

关键 runtime 参数：

    ZDefendThreat.internalThreatID = 39ZDefendThreat.severity         = 3ZDefendThreat.isMitigated      = 0

调用后 UI tree 显示：

    title   = Jailbroken Device Detectedmessage = Your device appears to be jailbroken. For your security, TargetApp cannot be used. Contact your device service centre to fix your device.button  = 了解

这证明

0x100902864  的  internalThreatID=39

分支就是原始阻断弹窗的App 侧构造路径。

下图是验证结果截图，可以看到弹窗内容和绕过前一致：

![runtime 参数级验证后的Jailbreak 弹窗]

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/yGOpnM3p9MSYBf1USzgUf3cTkVVoZ5wgia93lQqSNHHrOKKnbbic35XKIKsvfDicSANmPqH6aobhAU94cIEwLV1YLzBsUT0hQswdb1p1aGiayrk/640?wx_fmt=jpeg&from=appmsg)

一个有价值的反例是：使用自定义 fake ObjC class 虽然实现了

internalThreatID  selector，但进入 builder 后会因对象布局不兼容触发  access violation
accessing 0x1c  。

这说明 builder 不只是“鸭子类型”发消息，还期望真实  ZDefendThreat  / Swift-ObjC 兼容对象布局。

8\. 绕过策略：选择结果消费层而不是底层 detector

![绕过后：App 正常进入主界面]

![](https://mmbiz.qpic.cn/mmbiz_jpg/yGOpnM3p9MRe2y4RpwlEOc3Plrat628jBX6zY1MPVNIauy3ZCaPgFBvQSYADf9AtKUqNbTs8VSdNTXiaRQM0RHqwEEeM0e3GnysXtTlMJZqk/640?wx_fmt=jpeg&from=appmsg)

    这次绕过没有删除底层检测函数，也没有试图把所有 `lstat/sysctl/fcntl` 都 hook 成良性值。

原因有三点：

1、 ZDefend rule VM 和 policy 复杂，底层检测点很多；

2、 全量 Frida hook 容易引入额外

APP_TAMPERING /

apptampering_hooked  ；

3、 宿主 App 最终依赖的是

activeThreats/allThreats/internalThreatID/severity/mitigated  这些结果字段。

因此采用“结果消费层 sanitize”策略：让 SDK 底层检测继续运行，但让宿主 App 看到的 threat 结果变成良性或不可阻断。

当前 patch 产物：

    analysis/patched/targetapp_zdefend_sanitize.ipa

核心修改点：

函数  |  原始逻辑  |  patch 后  |  目的
---|---|---|---
` -[ZDeviceStatus allThreats] @ 0x10d90  ` |  读取 offset  ` 0x70  ` |  改读 offset  ` 0x88  ` |  让 allThreats  指向通常为  空的  activeNewThreats
` -[ZDeviceStatus activeThreats] @ 0x10dd4  ` |  读取 offset  ` 0x78  ` |  改读 offset  ` 0x88  ` |  避免  App 看到  active threat
` -[ZDefendThreat internalThreatID] @ 0xd75c  ` |  返回真实 threat ID  |  ` mov w0,  #0  ; ret  ` |  避免命中 39/75  等阻断分支
` -[ZDefendThreat isMitigated] @ 0xd7a0  ` |  读取真实 mitigated  |  ` mov w0,  #1  ; ret  ` |  将 threat  视为已缓解
` -[ZDefendThreat mitigated] @ 0xdf54  ` |  读取真实 mitigated  |  ` mov w0,  #1  ; ret  ` |  同上
` -[ZDefendThreat severity] @ 0xdbe0  ` |  返回真实 severity  |  ` mov w0,  #0  ; ret  ` |  降低风险等级
` -[ZDefendThreat threatSeverity] @ 0xe020  ` |  返回真实 severity  |  ` mov w0,  #0  ; ret  ` |  同上

绕过后，App 可以进入正常主界面；后续分析只保留只读或窄口 hook，

避免继续触发

ZDefend 的 tamper classifier。

9\. 为什么不建议 full hook

在早期尝试中，替换大量 ZDefend 方法虽然能短暂绕过某些 getter，但也会引入新的风险信号：

    APP_TAMPERING / apptampering_hooked

这类信号会污染样本，导致后续很难区分：

  * 原始设备越狱风险；

  * 重签/注入/Frida 引入的 tamper 风险；

  * App 自身对 ZDefend 结果的消费逻辑。

因此后续采集运行时证据时，应优先使用只读/窄口 hook，只观察必要对象、selector 和系统调用，不再替换 ZDefend 检测函数。

10\. 最终调用链总结

最终可以把链路串成：

    [1] rule 执行层    ZDDHelper.runRuleBlocking / com.zimperium.dd.runRule[2] primitive / 系统调用层    JB Dopamine-Roothide:      sub_25297C/sub_252848 -> lstat/lstat64(paths)    ios_combined_classifier:      sub_F14A4 -> sysctlbyname(security.mac.*)      sub_F9A94/sub_D84F0/sub_D8568 -> fcntl(fd,61)      injected library forensic

[3] 结果归一化层

        ZDDRuleResult.setFromJson      -> triggered / triggerValue / forensicJson

[4] ZDefend status 层

        ZDeviceStatus.sendDeviceStatusToListeners      -> ZDeviceStatus.initWithStatusDict      -> ZDefendThreat.initWithThreat      -> activeThreats / allThreats

[5] TargetApp UI 层

    TargetAppTabBarController.deviceStatusRegistration      -> callback 0x1003d9abc / closure 0x1008f4864      -> active handler 0x100904c98      -> alert builder 0x100902864      -> internalThreatID=39      -> Jailbroken Device Detected

11\. 原理小结：它到底是怎么做检测和阻断的

从原理上看，这套 jailbreak 检测不是

App 自己直接调用一个 `isJailbroken()` 函数后弹窗，而是分成三段：

    1. **检测层**：ZDefend rule VM 调用系统 primitive，例如 `lstat/lstat64` 检查 Dopamine/Sileo 痕迹，`sysctlbyname` 读取系统安全特征，`fcntl(fd,61)` 做完整性/签名相关检查。2. **归一化层**：检测结果被整理成 `ZDDRuleResult`、`device_status_base64`、`ZDeviceStatus` 和 `ZDefendThreat`，核心字段包括 `internalThreatID`、`severity`、`mitigated`。3. **App 消费层**：TargetApp 读取 `activeThreats`，发现 `internalThreatID=39` 且风险未缓解后，进入 `0x100902864` alert builder，动态解密文案和 selector，最终展示 UIKit 阻断弹窗。因此本地绕过的关键不是“让所有系统调用都返回正常”，而是让 App 在消费结果时看不到 active threat，或者看到的是低风险/已缓解 threat。这就是为什么本文选择sanitize `activeThreats/allThreats/internalThreatID/severity/mitigated` 这些结果字段，而不是粗暴 patch 所有 detector。

12\. 经验总结

这次分析中最重要的经验有三点：

1\. **先拆清安全门禁的触发层级，再做最小化绕过。** 目标不是“隐藏检测”，而是在测试环境中确认 detector、status 和 App UI
消费层分别在哪里。

2\. **不要把底层 detector 和 App 消费层混为一谈。** ZDefend 仍然能检测到 Dopamine/Sileo 痕迹；绕过只是让
App 不再消费这些 active threat 去阻断 UI。

3\. **runtime 证据优先。** 静态能解出 `internalThreatID=39` 的文案映射，但最终仍通过真实
`ZDefendThreat` 入参与 UI tree 完成了闭环验证。
