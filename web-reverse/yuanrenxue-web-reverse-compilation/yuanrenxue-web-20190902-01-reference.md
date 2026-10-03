---
schema_version: 2
id: yuanrenxue-web-20190902-miniprogram-wxapkg
document_type: reference
original_date: '2019-09-02'
archived_date: '2026-10-02'
scope:
  targets:
    - wechat
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-web-20190902-01.md#谈下微信小程序的抓取技巧"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留 2019-09-02 正文里的版本分支。未换机，未打开 Fiddler 或 Charles，也没有补 root 步骤。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 路径、仓库和开发者工具地址是来源原文。未拷贝 wxapkg，未运行 node 命令，未导入项目。
relations:
  - type: derived_from
    target: "./yuanrenxue-web-20190902-01.md#谈下微信小程序的抓取技巧"
tags:
  - wechat
  - wxapkg
  - source-report
---

# 2019 笔记里的小程序包路径和抓包分支

这张卡只回答：这篇 2019-09-02 的笔记把小程序抓包分成哪两条，以及它把包体文件、解包仓库和开发者工具写在哪里。它不提供 root 方法，不提供域名或证书开关的点击路径，也不把「绝大部分能抓」当成当前结果。

公众号 HTTP 的 getmsg 卡是另一个目标，不覆盖这里的包路径。

<a id="decision-flow"></a>
## 抓包分支

来源把抓不到包主要写成安卓和微信版本过高，并给出它当时使用的低版本组合。高版本则改走开发者工具里的 Network。加密参数只被点名，没有算法。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 低版本抓包被写成安卓 4.4 配微信 6.7 左右，工具是 Fiddler 或 Charles。quote: 换用安卓系统是4.4的手机和微信APP版本在6.7左右的版本。使用Fiddler或Charles抓包妥妥的。 | s1，抓包问题 | source-report | 来源写的那组旧版本 | 作者自述。更高版本是否仍失败，本卡没有新证据 |
| C2 | 高版本的替代入口是小程序开发者工具的 Network，不是再写一套代理步骤。quote: 一种小技巧就是借助小程序开发者工具来抓包 | s1，调试小节后半 | source-report | 已能在开发者工具里打开的包 | 面板位置写的是「上图红框」，正文没有控件名 |
| C3 | 拷贝包目录被写成需要 root，或者使用作者称为默认已 root 的安卓模拟器。quote: 拷贝该目录需要你拥有root权限 | s1，拷贝句 | source-report | 来源点名的手机目录 | 没有 root 步骤。模拟器品牌未写 |

IP、登录账号、参数加密都只被说成还要另做。域名和 ssl 证书的关法只有「如下」和一张图，不进入本表。

<a id="interfaces"></a>
## 包路径和解包入口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 包目录被写成这个路径，其中微信号文件夹没有给具体 id。quote: /data/data/com.tencent.mm/MicroMsg/微信号id文件夹/appbrand/pkg/ | s1，路径句 | source-report | 来源描述的微信数据目录 | 未在设备上列出该目录 |
| C5 | 该目录里以 .wxapkg 结尾的文件被当成编译后的前端。quote: 以.wxapkg结尾的文件就是小程序前端代码被编译之后的形式。 | s1，路径下一句 | source-report | 同一次打开后留下的文件 | 未核对文件头 |
| C6 | 解包程序被指到这个仓库。quote: https://github.com/qwerty472123/wxappUnpacker | s1，解包小节 | source-report | 来源给出的仓库 | 未克隆，也没有提交号 |
| C7 | 还原命令被写成 node 加上 wxapkg 文件名。quote: node xxxxxx.wxapkg | s1，命令行 | source-report | 已装好 node 和该解包程序时 | 占位文件名。作者写明报错和分包没有展开 |
| C8 | 开发者工具下载地址是这一条。quote: https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html | s1，调试小节 | source-report | 来源给出的下载页 | 未下载，版本号不在正文 |

来源还写导入解包目录后，sources 里打断点、console 里跑代码，看起来像 Chrome。断点教程被推回公众号，不在本篇。

## 验证与限制

作者写解包报错和分包没有展开。quote: 还有解分包的问题。
本篇因此没有失败出口，不能当成流程卡。

「就能抓取绝大部分小程序」是作者收束句，保持 source-report。剩下的 IP 问题原文是：剩下就是解决IP问题。登录账号也没有做法。相关阅读链接不提供这些缺口的正文。
