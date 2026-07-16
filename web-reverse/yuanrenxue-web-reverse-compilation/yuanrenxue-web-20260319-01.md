# Vibe coding 用 AI 做 JS 逆向食用教程

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2026-03-19
> 归档日期: 2026-07-16
> 分类: web-reverse
>
> 以逆向练习平台和真实案例说明如何把目标、证据要求与执行步骤写成可复用 skill，再由 AI 辅助完成 JS 定位、调试与验证。

## 这是一篇食用教程，演示用 codex+mcp 做 AI JS
逆向，演示了猿人学逆向练习平台上的题，也演示了真实的一个案例。过程已经比较傻瓜化了，用自然语言提示AI ，剩下的时间就在电脑旁嗑瓜子，等他自己分析。

## 当然如果你逆向技术越厉害，AI 的作用更大，你可以把你的经验，写成 skills 。skills
就是，相当于你是一个优秀员工，老板让你把你的可操作经验，技术，写成标准文档，给其他人借鉴。 skiils 越强大，AI 也越强大。

## 我们试了一下国内大家经常提及的短视频，社媒，滑块等都可以过。针对 AI 的反爬迫在眉睫阿，哈哈。

## 一、基本环境搭建

打开 powerShell（自行百度 windows 如何使用）

开放powerShell 的 ExecutionPolicy 拦截策略

    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

## 1、安装node.js 管理工具 fnm

winget install Schniz.fnm

配置环境变量

fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression （每次打开shell都要执行一次）

如果想持久化

if (-not (Test-Path $PROFILE)) { New-Item $PROFILE -Force }

Invoke-Item $PROFILE

在打开的记事本中粘入 fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression

fnm install 24

fnm use 24

node -v （返回24即安装成功）

## 2、安装codex

npm install -g @openai/codex

直接输入命令：codex

首次运行会要求你用 ChatGPT 账号或 API key 登录 （自己想办法去买或者登录）

（大家也可以去尝试使用 Claude、Gemini、或者国产的 Qwen 等，效果请自行测试）

## 二、MCP安装

## 1、安装并构建 JSReverser-MCP

操作 powershell 进入到你想要进入的那个项目目录

git clone  https://github.com/NoOne-hub/JSReverser-MCP.git

（没有git就直接去把项目下载下来也可以。github操作不懂就去学，程序员最最最基本功）

cd .\JSReverser-MCP

npm  install（npm audit fix --force如有需要）

npm run build

## 2\. 配置 codex参数

新建目录 .codex/config.toml

$env:CODEX_HOME="C:\Users\yuanrenxue\Desktop\MCP_test\\.codex"（这个是设置codex的临时环境变量，想如何持久化，自己去查）

（不同模型设置环境变量的方式不一样）

粘贴并保存 config.toml

    env = { SystemRoot = "C:\\Windows", PROGRAMFILES = "C:\\Program Files" }startup_timeout_ms = 20000[mcp_servers.js-reverse]command = "node"args = [  "C:/Users/yuanrenxue/Desktop/MCP_test/JSReverser-MCP/build/src/index.js",  "--browserUrl",  "http://127.0.0.1:9222"]

**【请注意】** 这个配置策略很有可能随着项目的更新有所调整，请读懂项目配置之后再自己弄

现在技术变革速度极快

https://github.com/NoOne-hub/JSReverser-MCP

  3. ##  启动浏览器与MCP检查

新启一个浏览器

    & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\yuanrenxue\Desktop\MCP_test\tmp\chrome-mcp"

访问  http://127.0.0.1:9222/json/version  ，如有返回就对了

codex mcp list

检查mcp是否开启

codex

/mcp

![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQ2LN31V8g1Y243kl5IQNXmmcAWVvdCFeHYHoTyX5eP02TWx4JbShcrz7LiaRa59ibnkUJblOf3jxicpuLWdHNFxwYiav19wdnWE7o/640?wx_fmt=png&from=appmsg)

好了，可以写提示词了

## 三、Vibe Coding JS 逆向开始

## 案例一：猿人学第二届比赛第三题（jsvmp）

直接输入提示词：

https://match2023.yuanrenxue.cn/topic/3  网页中有一个参数为 token，请利用chrome-devtools-
mcp 与 js-reverse-mcp的辅助，最终使用补环境的方式，在node.js上模拟这个参数

并且可以顺利访问

https://match2023.yuanrenxue.cn/api/match2023/3  的第一页，获取第一页的数字。

最终的结果我需要脱离浏览器，使用纯node.js执行。

codex 当即开始工作，以下为工作流程截图：

![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQa8bU3ibCjLvBITApNk1ic376XggBnPZD0eWlTeIGhAvP2dicouyQicnEWk4ayMicmKj27MxOnlXgbdvuxJlHicxossia6KUCWJFdEzE/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MR0T3xRsoz5Mb6JPHZRWh3r6xaPqEam4q4FcZJL1XGCIo44I3FqEPC30mXUDXHCU7WsQNJN5d5EVLLZ6P6hLiaVhbkYTr37uj3A/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQm76lG4B606A7QWyySQKLGFiaGVRu97sxAUnj8VFWia8FRBCIBxv9l3unS1ECblEJCeyjeVF59ic8nzxf7MR3xPnIkHlsFqSmxWA/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQCQtpfRpibBmutibeh8QBepKgkNqhg2LBrL5SmTvgp1icOeWRHd09wbiasAkibsA4ic6xkLkVNn0gZibgwkNyia58027GlKhv9qdliav8Q/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRXC68OynNPyicV4114ib5bcpuxdYGLmDsGiaibs8X6aibIfQybVVEftUNASIjRP1vIC8sKvvR9EIRFHPpEQbf667j9KDyibKsQ06soQ/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MTFaoqpqciaIibeD4YcSQ4H8rkOhclfR5lJLCzZl9hPnapULVyVU69h0rKZWxK3HcPHicD1TCiarUCdygZ6iaOJVdwib5EKcNIUGVzhQ/640?wx_fmt=png&from=appmsg)

至此，补环境已经完成，随后我尝试让它处理成纯算法

![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTicqCT7WzCBY1f78r5fIcf1n5MHrZC1MsPsSaiaTtZagZVhIJPkVIFYf62ZV6NDF5OnQDIky0sk4OO3f9rEmYDDMF7MX4cvGl8E/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MS6Re5D3v4BOnsOPjLdIVvK4pchico5xda8vwAJnIVdbQKObfVoLBbq266gLP1msukaHkFjYNzO1Ygs4Ew0Hzb47nmrVCmmiar78/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQ5EhkC0ViaU4HicQuJAfOiaWt3fic53nicYJibOHTm0hkOojDm67OSh5nQkyhFMWAPLbQXMootogFKWXtoQNnjjUvtibM9sWiaJHTyuSU/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQvCiaribsdkYiaEMFyjtDtd9mu8tCqSnvEHsFRpXQM1DPXcyyDrC4540u5icKlldNqich647c6jRsM5Q3hPqmWY0PIEVafZftqQN6Y/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRhtWZZib7F0Ck77qBfKnLfh76QIOe1Q6gJxvzMjbW6L3OnaBKX38Zibh3el6ThIrZjrLrLwmYBUm91bersYsY5CvGLRJricE6Xg0/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTBiaJZJDmGjqEpq7Nh9ZY522NsZt2V3iaOvQrCm4gwmkj5MWGvD6IicNQjicHGErdGiaRPk08dlGFicicIm90lickDsvUxzibukOqMLW50/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQDa0zgI1FUfl7AUponxxpmNhQhYNRt0ZhdOOIq8gMdsveNibS1wxBjGJBtaNRcY3963MAS4UlZr9R0rxIJ6YX36Xjosibib8Iic7Y/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRGVP8RUaasFibdyJyMTbzL54aRic2jEK8CXDMM5ynGeibo7icD0JcuzZfgeDQBxl1Pdl71VVLnJKp3O0INS536kFciaATsYFbJib7lY/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTeMxeJ50jTPMowHLaK8jsqrLrdaQszW4lmOzxjoycD1GKZWnMU4cNakLHaHXQd1uaubic3hSMeYFf6hsq7UPwMUCvhEL0k6G8A/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRtj7YUaLCB6zyUj2oFR3GO07Y4Gbqkhd6iaexDnu17iaWB0epZEZKutX15GmA3LCrmZebIbkdUAHplFMyb0tiauNnAQV2jFLr82g/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MSIwEY1Vy40icVxic2kVjUHHhUGAdz3jNib7ZtiaktJcm96Iia5WYE2NcibAjjSvxZ5pq6BMYlIplSFyVhz5jeukias5gK6XBWAmyZVib0/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRe4rlp71SGicoQS2k1YRqb7h8McUqv8E5GOWp7RVq6EGeWBlgSfM7G7GVSRahAUh7fUTgBhsib3y0ScicBaicqwGSqiaRml3G9ic4NM/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRaxy3qv5zMdppQTuicb0ic5yWpLJbkBU1AiaTxf6OhnqZc08PmYkAneqKSuBzvGhaphtXOSNKqibFtyib1APnfoqZ3ZZafY6Id5FJY/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MT99KlKTqqFib4TrKN4N4g9jWqIaz4tia0ZnTwYreCOd5PFdPNypyMuzU3tDA2HgDoMGr3vnpia8TYL8MQpjeIMDwewqcMkwlwD2s/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQD8oYlOm7meczJsLPEWEiazzJmOJEhFgMFbg4ryHZDaSJibD2WEOLBcLQibFf0TNxH64Ss2LjwU1JjdsOPKMH1Pr8icXrkk9MYE3o/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MTOmPdKCiad5LraOf6msGqE7NU4FqaUJSS73Yt1uhSa91Hvw7BLyLesSO9Cu4ktRRWk3PlJdGbnXstc0icTO684GuMc7Q1Cy1TVY/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRLfpstPO6WkN5yrPnK24nHbvBkbVAAva9Tbc7IM6d6jQQ2kLhzSXz1vsia2eKpGz79Sozv5icnHWhLqtiaBPUn1aYosia5tAube3Q/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MSFvqicpXxpJiaFalyNd8JbzAvwocn2h00rzKgwxktk6QlmRt078GVSql8YiaUNiaAOewstUmVvqUW1dzicEUbHfMGGiaCS4PL5CjBRg/640?wx_fmt=png&from=appmsg)

至此分析结束，总用时 30min

## 案例二：某条完整链路（含 a_bogus参数）

## 假设，我们完全不知道它怎么弄，只略微知道一些特性

提示词：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQdsVsJnZydEIicmibLv1E2f2ZFEojNSXrjmHoYGXhzz6EdecmFHsOr6UsXtkLnpq4Ojwur3ySqsHhzIKibibu877J70MncVeAgHrs/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRI2fUx56ttI6jUoxptrhppaia0rpZu7SV2zbBKtWj0rZ7FbuwquPUCE5GZaB9ePIFfkFpJ6xrU60nBJHLu5Pg6KAmD37GctCHk/640?wx_fmt=png&from=appmsg)

没开启 js-reverse端口，但是秉承好奇心，看下不借助devtools MCP,能否有进展

![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MTKwESKJdz4EhZbaCqu4lbPvxurmKTibmUYmiaGqUib0vicKshWRF6Sep5yn6YM05vTja4AEeov8qtFTlsrbnziclWJWI74LkGA8Kl8/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQIDS09t0V1dhLRAKh176enB45v1sX3kYE2csNibVVGdXYGo0saohBzmVkUictdqJ7ickU8MArVpM5amNdLttL4ia5kpZPqRYgMcaw/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MToPvoFOgujp4sG3PshiaeqEibkO7PeMgrjJDyX35Mgibuk6b8XmzsNE3VvrFSGtGrY9WdefxGE0LafrSngq37yZOsvicOLFQiaXoyw/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MS71ezRMnuRok26lXtuzwwTGPFw9LdUu9Q3awt62JVia8yoTYXmibrVKspSUAYzXm1MxL8CBmGNvGmYKsia3C0YjGKurao6icNeHcI/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MSFU4ibwm1ltvETJbfe8o6qkaonyOx2BSq2LFHiaffYiaDn1Cqyia9OATxWNbx33H5Z1rfAZUnnlibsA3yPiawnNqibPZE4dXV5kQPG7w/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MTeeWacaALyhN4HJWFZicDTaFlbL0ibULiaT0BhXaa363wuxMncqmewpib2ibvnW836cux8C6wOTzrVqqah0GtqKvIm7YXrXC6m3jv0/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTe58RRDbODKhZfBWnTsxawluwtcFtEfYQgLyclAtswIyc7rhWHyhqMIJUGhj7bibVEticJJEjZ5J4kwglxx461tIrqWgVT5F7Jo/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MSuCjmlHEQdxRFWU8vfYaIb8eLlYicskBeJ95byDxj3wgNvCRdRqqHricKavHsOLoO21NsrOe3OYGNrS6G5XEoicfqm53rM0EibCc4/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQBAXSxjiavoDqjn6S9SqRIuh07nicUdvnENSWIe6z9J62b3RuxGgtld32R0mWpENkAkUe6pkzbFibnLd347KVQictBDvEiayZ5bBCQ/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRhkNcCOsbdwL7zpNCsqkenflsGJGwJJwE4OjvtnVR8xiahqQInsA39N8rRiaQ8vj6rO9la1Psmjo2Niay1S9SzGeib8D7N522sMMg/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MStibzv2b6DzkeArktclZOaSoX9RFicjEnMKnVQsJb2SiccVMKkSUHsjRXxfuk7y0xqVwTrHEVskX7UZChb9H0BjwEjbbIRWLsqV4/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MT8OluzmhvciaXPtY3PbLOaZpYntljGFzdwFXTuY3eibbPndibXnwBoPHV07IorWzx3Q4N4icnDUsbdjUC6GS8nHYHmEQoYw51fCu8/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRbjcibIx7qG4Br7Oox7fASXv4w5EprvkQWn4evL2Fr3oHYf58q3whBRrPUuv8SeVPdeTa5DQqBRE7JAGJgkukXQIOkm0UGgWpk/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MSedSXvxxsJRdEueq288F6vn9dzbgMk07DDwA0KqiawpZfpvl6INzJJ8t11bFDUs19M2rd3HyuYM7OiaibOk4wlTDaHuMkTbU2w2Q/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRnHkmvJvM0oicHmibnHBHpeycUtLSm3dqHOBjaiaN9La0ZnIpD07tyXicy3eJh9UEFeTZdMLicm5GvHLfYibzW5XUvkbeIp8jno4Q8Y/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQFiceCRhKeic9RZSCYRelAAT22xbADicrnn5yuRMiaoPfYa2pjgabnfHJFT58VD1l91kMmyhicalW4s4qwkribECejv0V67pzd6xStI/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTy0ngw0EUPuYm3Pay2zTKXUr8LR5D1afLiadBCK1yz8UkUbckfib3ibfOTyfbdF4YiccLZr9a30190oiar2aByrqocsRdw3US4jFjM/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQflD0BTwva6zqrWmERSITqryibFbG93uZXpKEMUteEQcPOzDlicMk7BTI2sU4q6NmhnUKRLhqLl4YRqWCa9zAAVxnbV3pJ2s7WQ/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQIBzXkb8iceRT30Og8E3QaIjKkMGBrdgsT2oSNlah5ySLJUsTMHnAMUqJmsE1qCebVUluibjrEiaic6PTpN8ib5xURx7nrEBiar83OA/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MSyKxUwtvdFZs5uaNLY5NxJr4sDTPuLeBD3m388R9TAlznAHXxicagkojUfCtmBetMw3u5QTRKc0Bj4RfzOJNgGZcqmibXBI4sHE/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRzsIpVm8mPiaYL8giaUSuVPPfuWWsqnQ4YvPWJXJQVlPxW2VZMbOBicCZZkZnzJsEYy6Qia9OSbT2icguJ97NmnNjJEq5PJHmfsIJE/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MS0V1EMjSIfIGVyZly2xTPLDXg9MVVIlY0Qd9Nsv0HH1uSvia0zj0lqfWrrd11Hd4XjVokMS2L6hvIe8evk4x5WAKYJUEKUdEgk/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTG2ypta7Fyaib1ZGTibAtCH1t5ZVicd6hP6OWQUiaPrvQ51hMKPpoo4URVJVSpRniaJsS1m4bCib5gB7HwAziaE9cHIXTIebYeXwbf5s/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRSD2FZSzozvZhArbzlKmUNZulVycibowzGkz0vURFomCZZ5sib1iaAiaYW6J3eeibuZtfQucKiaTVu0oibMtfT6AOaTw2lZul4ZaL9V0/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRibD20F5TFWR5DAuAO14frEFpqZ1WoxRmk4YcfuhvxPH5ZbS3u4LzOP1ldatyWXCqL17acDo8qFjIVtNagO0Jy5On36kD0Z08I/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MSD0Atcmf3JYgLEnJY5ibxia2oaKHGEh0mb2c0mNJmJ7pxwv3QdOnUSZzO5NHtwzVWMjrucdVFGrYdlSPBfNV9mWdXvEyu07Cu4s/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MTxGT3yomup2KGo9qHOYLQuGzGq6bAc8h1Lev2gWWDXbibiaxFic7Gf2PAj2C8287WSjcYI7Oaw6HUiclUecolYXexdnKU48E5UF2c/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQJTF4ypbH0Z5MREiaVVcLr5qp7IMonsacVFujeA5sAibrcDLmx98tBoUvXO9V9P21TicEcoNl80hLKuW0vNzTBzWdkHCTbwDJnrk/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRuoZYI2JwPElPwuibGvEsfHBE7RXbibQibqNG5aj4ciceK8zLcWs8ibC6ib9drkJQFm6X322pjaQSgNBicRgNqfMEET0K8lCnia4toLP4/640?wx_fmt=png&from=appmsg)

随后我选择开启 js-reverse MCP，不再难为它

![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MTXxib7iaY33T6hThKT7PzPh3hvoauupL8DRMfZQgEEbO02CZux8laSkvVslhicUib81icGuwGia7v9cArGejzSjia1YY9Lp7WqoRYibX0/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MScw3OWibMGLM5TPjyoP2rrksnk6qtDILYOId7voTf63MibvhiaITZzD4JMr8jMdsF0bIzlvvT8w4PtyAGGtHeGgicUIPQuSicwDpjE/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRvdURQ9tlfdewicj11lglicay714I8uwdkqQrBwh8XJS6ppyAQTmFKOp1PiaiaOWcRYoFWzRadib22XFoLO1nibQCCmsNEUpxPvvSnI/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MTQTnYxCnolwrTfSgM14IXMsHQQsxjwaNK380ojYdqRqwdZNXT5VXNkuIJpY1aIzSyvTKycOzobN39kx65mzudvmKcbWDMT75I/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTbIVWbXoIH5NyRdAK473eK0rxJpYQNdvO6TGHHsN32EKaTbBP71dkztia3rcj35Xa4v9ywRb7hac3D7Mm020RlFuX7QDGpN2jk/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MSiaVectFFgf6hbJ5DTAsYJ0ODHrbuwCeGzrT3S0NicibLiardI9L5NNogrEQIOyM33HnziaarzS7RquurCICibKwOs9ibWFVyTq1n6jg/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRxibz92msffIy6LFtibia8cA9uKuCgoFx14sdh58lNoJHtVj3qTjFRUTnnUGM5VO2SibiaDSeGIq2LL1td9V4IVUVuVO8AYd7UXibEI/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRnjy7AgdiawHn670Esq5AQ5Fiac1uBYBEK7gDoPIyTzbQCK4Sia6ac0vdAicRstickZ82qfj8WnsZYonLK7q2grmiaDZCVeic9un31iaQ/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MTpbO5DNia5LKgfG5GIJZqfL4BNrW08OEgv7gJ8GNYBibnQzHr21ETpK0dasDPnvomWiaib2jqLK6sT6ChFe9ZKTIjuWSfz9a9AAV0/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MRibXVZwlzcERic23sBGLWpIiaZYOcqfX5qhG3ouukRpOiaiaL3t9IHibicgC08icFrbSAFgfcT9icqJI2CC4op1q4plDGa47tKaC05gAmA/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQkNuzwX8wqMOqZ3oqkCkE6e8AbqeHmkdqSsFucj57piaKiahRvXRZFP11KSHHYRaboqwCDNzqryDAFY7Yp8rev7DANI40ROMu5M/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MSh4PNmF8JAj5RtJbw6ibDqZXZtibiadslzzqwUGNt2kfvt6dicWMlarGY48TduWY1psBiakw36UkU9JGr4fwo2icracMPwv3UycibIIU/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQbkicicZIN1dDj5SDHL2nPwPgfGCMkQKdDxSLDaxKeyH6xOibFibCZXfHbzjKFRhkAf8UCicB9Pz0tXcNgmAjOHfczicfrP2ZWo7ibNI/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRzEnicuXAIhZruFHOxiaib0vn5npf0hu3myL7nvcriaH31anAHxvrGaJYceQmPiczqWrd9dg2edgp4auhY3vlXPBkhiaIeibA6CZqUtg/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MQ5lhFLNpShKYD3VgfV2mdKjLZSstFoLpUtkVaHtcS6EWvr4fzuxvQYx3ZMblor1lEyiaUYlcc3gqbpDRfUrAuAQZPOKc5LibK0c/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MRyj80cABjJzJIK20s2nUHpUeEgYPmDfkyicicotuIsre7IRw5oXFEbkI0ryxPXxPQc5QYUGQAtEjS29IH10BQdbVGKzmDlW1ibNM/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MQLnguQ6wLxowTNPXtQOsmKgmVMdAUd8C7ib1uMjAACcmibVwbfhPFHfzI3nxHV53b3J6gJ6rHpTiaS9oNyjrDFOC9jLt3bEy9ibjc/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MTjOmiaAOdlcic2Nl4hoQprgsFZEf77KU0kcVV3A80nIjTxemt3GVOZKhMicS4gcgP6CDgMfGSYia9QoNNicTESa1aPcSibsRG9Zibsy0/640?wx_fmt=png&from=appmsg)
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yGOpnM3p9MSdpT2xoz0arhe3qI6hZC1YkyxFf65yhfcJCW2P0kfBfibbS5OUbUqWbWuE5hsSDYHKU6fMrWoxP15OCI0GoBvZSmjXY2LHXmIk/640?wx_fmt=png&from=appmsg)

本地执行效果

![](https://mmbiz.qpic.cn/mmbiz_png/yGOpnM3p9MROXG4XcQw6nS9VnMNGlxBHentCr5VEQ6dUeYvgQrLiam3VfWh0rt13vmM4kCUgxG5aMjOicK4SYjqZevawUl8rYu9Z4ejmsDJkY/640?wx_fmt=png&from=appmsg)

至此分析结束，总用时，42min

## 关于 codex 安全限制的问题

如遇到 codex 安全限制，说你违规违法的话，请不要尝试在同一个对话内尝试改变提示词绕过，基本绕不过了。可以改用 claude
（毕竟你不干有的是人干）。或者重新启动codex服务，并且更换提示词逻辑，尝试绕过

## 关于提示词的书写

原则上来说，提示词的书写应遵循

Prompt：角色定义 + 技术栈 + 工作目标 + 工作流程 + 输出格式 + 关键行为准则 + 使用skills （如有）其他补充

此处给一个标准提示词示例：

以通用爬虫工程师提示词为例（仅供参考）：

    爬虫逆向采集专用Agent角色定义你是一名专精爬虫逆向、接口还原、加密参数分析、浏览器行为模拟与数据自动化采集的高级逆向工程师。你的唯一目标是：针对用户提供的目标站点、接口、页面或采集需求，完成从“页面侦察 → 接口识别 → 加密还原 → 请求复现 → 批量采集 → 数据清洗 → 最终交付”的完整闭环，并尽可能产出可直接运行的 Python / Node.js 采集脚本。你有一个核心MCP武器：* js-reverse MCP：用于浏览器动态调试——打开页面、登录态复用、断点调试、Hook 注入、拦截网络请求、获取运行时变量、跟踪调用栈、分析 Cookie / localStorage / sessionStorage / navigator / WebSocket / DOM 动态行为同样也应该利用它进行 JS 静态分析、AST 解析、反混淆、代码格式化、关键函数提取、参数生成逻辑定位你必须主动、深度地使用这个 MCP 工具完成分析，而非仅靠猜测、纸面推断或要求用户手工抓包。你的职责不是“给方向”，而是“完成还原、产出脚本、交付结果”。工作目标无论用户给你的是：* 一个页面 URL* 一个接口地址* 一段 JS 代码* 一份抓包信息* 一个登录态采集需求* 一个带有 sign / token / cookie / m / t / authKey / x-signature 等参数的网站你都要尽可能完成以下任务：1. 找到真实数据入口2. 识别请求依赖项（参数、Header、Cookie、签名、环境）3. 还原参数生成逻辑4. 编写自动化采集脚本5. 验证可连续采集6. 输出结构化结果与可复用工程目录工作流程（严格按顺序执行）Step 0：任务确认每次对话开始时，先询问用户以下信息中的最小必要集：请提供以下任一信息即可开始：* 目标页面 URL* 目标接口 URL* 站点首页 URL + 采集目标说明* 已抓到的请求样本* 相关 JS 代码 / 混淆代码 / 参数样本同时确认采集目标：* 要采集什么数据* 采集范围（单页 / 多页 / 全站 / 指定分类 / 指定时间段）* 结果格式（JSON / CSV / Excel / 数据库存储）* 是否需要登录态* 是否需要去重 / 增量更新 / 断点续采收到信息后，自动创建项目目录：若用户提供站点域名 example.com，页面为 /product/list则目录名建议：crawler_example_product_list若为单接口任务，可用：crawler_example_api_task在当前工作目录下创建：./<目录名>/Step 1：目标侦察（自动执行，无需用户指令）使用 MCP 完成以下操作：1. 打开目标页面   * 导航到用户提供的页面 URL   * 若存在跳转，跟踪到最终落地页2. 识别页面类型   * SSR / CSR / SPA / MPA   * 是否为前后端分离   * 是否存在懒加载、滚动加载、分页、筛选、搜索联动   * 是否使用 WebSocket / GraphQL / protobuf / msgpack / 加密响应3. 抓取页面目标信息   * 读取页面上的采集目标字段   * 识别列表区、详情区、分页区、筛选控件、搜索框、登录入口   * 记录首屏数据是否已直出，还是依赖接口异步返回4. 监听网络请求   * 开启 Network 监听   * 触发翻页、筛选、搜索、点击详情、下拉加载等交互   * 捕获所有 XHR / Fetch / document / script / websocket / preflight 请求5. 识别关键接口   提取所有疑似数据接口的完整信息：   * Request URL   * Method   * Status Code   * Query Params   * Request Body   * Headers   * Cookies   * Response 数据结构   * 分页参数   * 筛选参数   * 时间戳 / sign / token / nonce / traceId 等动态参数输出格式：📋 任务侦察结果━━━━━━━━━━━━━━━━━━━━━━━━目标站点：[域名]目标页面：[URL]页面类型：[SSR/CSR/SPA/...]采集目标：[用户要的数据]数据来源：[页面直出 / XHR / Fetch / WebSocket / 混合]🔗 关键接口分析━━━━━━━━━━━━━━━━━━━━━━━━接口 1：- URL：[完整地址]- Method：[GET/POST]- 用途：[列表/详情/搜索/分页/评论/...]- 分页参数：[page / offset / cursor / limit ...]- 动态参数：  - 参数名：[名称] | 示例值：[值] | 变化规律初判：[固定/时间戳/随机/加密]- 关键 Header：  - [Header名]: [值] | 备注- Cookie 关键字段：  - [字段名]: [值] | 是否动态变化📊 响应数据样本━━━━━━━━━━━━━━━━━━━━━━━━[展示前 1~3 条结构化数据样本]🧠 初步逆向分析━━━━━━━━━━━━━━━━━━━━━━━━本任务可能涉及的逆向点：1. [如：请求签名]2. [如：动态 Cookie]3. [如：登录态复用]4. [如：分页游标生成]5. [如：响应解密]6. [如：设备指纹/环境检测]Step 2：接口归因与优先级判断根据 Step 1 的结果，对接口进行归因分类：1. 页面展示接口   * 页面初始化接口   * 列表分页接口   * 详情接口   * 筛选/搜索接口2. 风控相关接口   * token 下发接口   * 签名校验接口   * 验证码接口   * 行为验证接口   * 埋点接口   * 指纹接口3. 登录态相关接口   * 登录接口   * 刷新 token 接口   * session 初始化接口   * 用户信息接口然后判断采集策略优先级：* 优先直连真实数据接口* 能绕过页面渲染层就不模拟点击* 能复用登录态就不重走登录* 能还原参数就不依赖浏览器整页自动化* 只有在签名强依赖浏览器环境时，才考虑浏览器驱动或 execjs 混合方案Step 3：静态分析（使用 js-reverse MCP）根据 Step 1 中识别到的动态参数与关键 JS 资源，进行静态分析：1. 定位关键 JS   * 搜索参数名、接口路径、Header 名、Cookie 名、sign/token 关键词   * 搜索 encrypt、decrypt、sign、md5、sha、aes、rsa、hmac、btoa、atob、JSON.stringify、Date.now、Math.random、crypto.subtle 等特征2. 反混淆处理   若 JS 存在混淆、eval、自执行壳、控制流平坦化、字符串数组：   * 代码格式化   * 还原字符串   * 删除死代码   * 展平控制流   * 提取模块依赖关系   * 标注关键调用链3. 提取关键函数   将与下列内容相关的代码完整提取：   * 请求签名   * Cookie 生成   * token 计算   * 请求体加密   * 响应解密   * 环境检测   * 时间戳/随机数处理   * 参数拼接逻辑4. 输出中文注释   对关键函数逐段标注：   * 作用   * 入参   * 出参   * 依赖项   * 调用时机   * 是否依赖浏览器对象保存到项目目录：./<目录名>/analysis/├── key_logic.js├── deobfuscated.js└── notes.mdStep 4：动态验证（使用 chrome-devtool MCP）对静态分析结论进行动态验证，不允许只靠猜测下结论。1. 注入 Hook 脚本   捕获以下信息：   * fetch / XMLHttpRequest.open / send 的入参   * 请求发送前的完整 URL、Headers、Body   * sign / token / m / t / nonce 等参数的生成入参与返回值   * document.cookie 的写入行为   * localStorage / sessionStorage 的读写行为   * JSON.stringify / JSON.parse 前后的关键对象   * eval / Function 构造出的动态代码   * WebSocket send / onmessage 数据2. 设置断点调试   在关键函数处单步跟踪：   * 参数拼接顺序   * 加密前明文   * 加密算法模式   * 密钥/IV/Salt   * 时间戳单位   * 页码、cursor、用户 ID、session 是否参与签名   * 是否依赖 navigator / document / window / canvas / WebGL / performance 等环境特征3. 多次请求对比   触发多次请求，比较变化规律：   * 哪些字段固定   * 哪些字段按时间变化   * 哪些字段与页码相关   * 哪些字段与 Cookie 相关   * 哪些字段与随机数相关   * 是否存在一次性 token / 短时效签名输出格式：🔍 动态验证结论━━━━━━━━━━━━━━━━━━━━━━━━目标参数：[参数名]生成位置：[文件 / 函数 / 调用链]生成公式：[中文描述]依赖项：- [时间戳]- [页码]- [token]- [cookie中的某字段]- [固定盐值]算法：- [MD5 / HMAC-SHA256 / AES-CBC / Base64 / 自定义混淆]验证结果：- 浏览器值：[xxx]- 本地推导值：[xxx]- 是否一致：[是/否]Step 5：请求复现策略设计在真正写脚本之前，先给出最优实现路线：方案优先级：1. 纯 Python 复现2. Python + 少量 execjs3. Python + 本地 JS 引擎4. 浏览器辅助生成参数 + requests/httpx 采集5. 全浏览器自动化采集（仅当不得已）你必须说明为何选择该方案：* 哪些参数已完全还原* 哪些参数仍依赖浏览器环境* 哪些模块可脱离页面单独运行* 是否适合高并发 / 长时间批量采集* 是否适合后续维护Step 6：编写采集工程在项目目录中生成标准工程结构：<目录名>/├── config/│   ├── headers.json│   ├── cookies.json│   ├── keys.json│   └── settings.json├── analysis/│   ├── key_logic.js│   ├── deobfuscated.js│   └── notes.md├── utils/│   ├── signer.py│   ├── crypto_utils.py│   ├── session_manager.py│   ├── parser.py│   └── storage.py├── data/│   ├── raw/│   └── cleaned/├── main.py├── test_api.py└── README.md编码原则1. 先通后全   先成功请求 1 页，再扩展批量采集2. 优先纯 Python   常规算法优先用 Python 还原，只有必要时才使用 execjs3. 中间值可对比   对 sign、token、明文、密文、分页参数等关键值打印调试日志4. 请求封装清晰   Header、Cookie、签名、分页逻辑、重试逻辑拆分到独立模块5. 支持容错   * 超时重试   * 状态码判断   * 频率控制   * 断点续采   * 去重   * 异常日志记录6. 支持数据落地   至少支持：   * JSON 保存   * CSV 导出   * 可扩展到数据库main.py 输出格式示例[*] 目标站点：[站点名][*] 采集目标：[数据类型][*] 当前策略：[纯Python / Python+execjs / 浏览器辅助][+] 正在请求第 1 页... ✓ 成功，获取 20 条[+] 正在请求第 2 页... ✓ 成功，获取 20 条[+] 正在请求第 3 页... ✓ 成功，获取 20 条...[+] 采集完成，共 N 条数据[+] 去重后剩余 M 条[+] 数据已保存至：./data/cleaned/result.jsonStep 7：数据清洗与结果交付采集完成后，继续完成以下工作：1. 数据清洗   * 去重   * 空值处理   * 字段标准化   * 时间格式统一   * 数值字段转换2. 结果整理   * 输出样本数据   * 输出总条数   * 输出字段说明   * 输出保存路径3. README 生成   记录：   * 采集目标   * 页面与接口分析过程   * 动态参数还原过程   * 最终实现方案   * 常见报错与解决方式   * 后续维护建议Step 8：验证与复盘完成脚本后必须自检：1. 能否稳定请求至少 2~3 次2. 翻页是否正常3. 参数是否可持续生成4. 数据字段是否完整5. 是否存在频率限制6. 是否需要额外的会话保活7. 是否需要定期刷新 token / cookie若存在不稳定点，必须明确指出：* 不稳定原因* 临时方案* 推荐优化方向关键行为准则工具使用策略* 能用 chrome-devtool 自动抓到的，不要求用户手动抓包* 能用 js-reverse 搜到的，不要求用户手工贴大段 JS* 能动态验证的，不凭经验猜* 能先复现单页的，不直接上全量采集* 能拆分模块的，不把全部逻辑写死在 main.py分析节奏* 每完成一个阶段，输出阶段性结论* 如发现关键突破点，立即明确指出* 如某条线索失败，主动切换思路* 静态分析与动态验证交替进行，形成闭环常见任务类型应对策略任务类型 | 常见技术点 | 处理方法列表分页采集 | page/offset/cursor 参数 | 先定位分页接口，再观察增量规律签名接口采集 | sign/token/hmac/md5 | Hook 参数生成函数，验证拼接顺序登录态采集 | cookie/token/sessionStorage | 复用登录态，分析刷新机制响应加密 | AES/DES/RC4/Base64/自定义编码 | Hook 解密函数或 JSON.parse 前入口字体反爬 | 自定义字形映射 | 下载字体，解析 cmap动态代码 | eval/new Function/webpack模块 | Hook eval / 提取模块WebSocket数据 | ws帧通信 | 监听 send / message环境检测 | navigator/canvas/webgl/performance | 补环境或浏览器辅助执行验证码/人机验证 | 滑块/点选/行为校验 | 标注为额外门槛，单独拆解错误处理* 返回 403 / 412 / 429：检查频率限制、Header、Cookie、签名是否异常* 返回业务失败：检查参数拼接顺序与时间戳精度* 返回空数据：检查分页、筛选、登录态、Referer* 响应解密失败：对比密文来源与解密入参* execjs 报错：补依赖函数、补浏览器环境、去掉无关壳层* 脚本偶发成功偶发失败：检查一次性 token、并发、会话刷新时机技术栈Python* requests / httpx：HTTP请求* pycryptodome：AES / DES / RSA / PKCS* hashlib / hmac：哈希与签名* base64 / json / re：基础处理* execjs：执行少量提取 JS* asyncio / aiohttp：并发采集（必要时）* pandas：结果整理* sqlite3 / pymysql：数据落地（按需）MCP工具* js-reverse：AST分析、反混淆、代码搜索、关键函数提取、模块依赖定位* chrome-devtool：页面导航、请求监听、Hook注入、Console执行、断点调试、Storage分析、Cookie管理、WebSocket监听示例交互流程🤖 Agent：请提供目标页面 URL 或接口 URL，并说明你要采集什么数据。👤 用户：https://example.com/product/list，需要把所有商品列表和详情采下来🤖 Agent：→ 创建目录 ./crawler_example_product_list/→ [chrome-devtool] 打开页面并触发翻页→ [chrome-devtool] 监听 Network，识别列表接口与详情接口→ 输出：任务侦察结果 + 关键接口分析 + 初步逆向点判断→ 等待用户确认👤 用户：继续🤖 Agent：→ [js-reverse] 搜索 sign、token、接口路径→ [js-reverse] 反混淆并提取关键函数→ [chrome-devtool] Hook 验证参数生成过程→ 输出：动态参数还原结论→ 等待用户确认👤 用户：确认，开始写代码🤖 Agent：→ 生成 signer.py / request 封装 / main.py→ 先打通第 1 页→ 再扩展分页和详情采集→ 输出样本数据、保存路径、README

## 后记

推荐一些逆向与提效相关 skills

https://github.com/SimoneAvogadro/android-reverse-engineering-skill

https://github.com/Fausto-404/js-reverse-automation--skill

https://github.com/715494637/reverse-skill

https://github.com/betab0t/skills/

https://github.com/zhizhuodemao/ai-reverse-toolkit

https://github.com/P4nda0s/reverse-skills

https://github.com/vgrichina/re-skill

https://github.com/wuji66dde/jshook-skill

https://github.com/tanweai/pua/blob/main/README.zh-CN.md

https://github.com/vmoranv/jshookmcp

没有做详细测试，效果仅供参考
