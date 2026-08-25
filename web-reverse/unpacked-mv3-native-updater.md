# 未上架 MV3 扩展的本机更新器架构

> 来源: `workspace/mouchenjie-ai-plugin`
> 原始发布时间: 2026-08-24
> 归档日期: 2026-08-24
> 分类: web-reverse
>
> 把「开发者模式加载已解压扩展 + 绿色更新器 EXE + 自定义 URL 协议唤醒」拆成可复用的五层打包合同，便于自有插件做 sideload 分发，而不是照抄 Chrome Web Store 上架流程。

## 这篇解决什么问题

Chrome Web Store 上架要审权限、要过审核窗口、很难按周热更新。国内电商类工具常见另一条路：

1. 用户用开发者模式加载一个**未打包的 MV3 目录**。
2. 旁边放一个**绿色 Windows 更新器**。
3. 网页或扩展用**自定义协议**把更新器拉起来。
4. 更新器从对象存储拉 zip，原地覆盖扩展目录。
5. 账号、次数、会员走网站，不放进安装包。

这不是「把 crx 藏进安装器」。它把分发面拆开：安装包只负责把目录放到磁盘并教会浏览器加载；业务授权完全在服务端。自己做插件打包时，先选这五层里哪些要自建，哪些可以省略。

证据来自谋臣界电商 AI 工具的官方更新器与渠道包 v2.2.9（扩展 `manifest.json` 的 `version` 仍是 `2.0`）。下文用该样本当实例，合同本身不绑定该产品。

## 五层模型

```
[5] 账号面        网站登录 / token / 次数 / 金币
[4] 浏览器加载面  chrome://extensions 开发者模式 → 加载已解压目录
[3] 扩展目录面    manifest.json + dist/ + assets/  （zip 内唯一内容）
[2] 本机更新面    绿色 EXE：注册协议、拉包、覆盖目录、回报进度
[1] 渠道面        版本清单 API + 对象存储 zip
```

| 层 | 职责 | 不该承担 |
|----|------|----------|
| 渠道 | 给出「当前该下哪个 zip」和不可变对象地址 | 浏览器加载、会员判定 |
| 本机更新 | 把 zip 变成磁盘上的扩展目录；多位置同步 | 改 `manifest.json` 业务逻辑 |
| 扩展目录 | 可被 Chrome/Edge/360 直接 Load unpacked | 混入更新器 exe、`_metadata`、本机配置 |
| 浏览器加载 | 一次人工加载；之后靠覆盖文件 + 重启生效 | 静默安装到 Profile（无企业策略时做不到） |
| 账号 | 登录态、配额、付费 | 绑死在某个扩展目录路径 |

谋臣界把 1–4 做在更新器里，5 完全放在 `pay.*` 网站。自有插件可以只做 3+4（每次发 zip，用户自己覆盖），也可以补 1+2 做成自动更新。

## 渠道面：版本清单与 zip

更新器并不内嵌扩展。它先 GET 一份工具清单，再按固定规则选一条记录下载。

实例（静态还原 + 实测）：

| 项 | 合同 |
|----|------|
| 清单接口 | `GET /?s=Home.DownloadShow.getTool` |
| 鉴权 | 无登录；浏览器 UA + `Accept: application/json` |
| 成功 | `ret == 200`，列表在 `data.data` |
| 选择规则 | 优先 `id == 2`（浏览器插件渠道），否则列表第一项 |
| 包体 | 对象存储 zip，根下只有 `extension/` |
| 渠道版本 | 清单字段 `version`（例：`v2.2.9`） |
| 扩展版本 | `manifest.json` 的 `version`（例：`2.0`） |

打包要点：

- **渠道版本和 manifest 版本分开。** 清单给用户看「这次更新到哪」；Chrome 只认 manifest。两者漂移时，更新器 UI 和扩展页会报不同数字，要在发版清单里写清楚。
- **zip 只装扩展目录。** 更新器 exe、说明 txt、`config.json`、`update.log` 放在 zip 外面，和扩展目录并列。
- **不要把 Chrome 生成的 `_metadata/` 打进 zip。** 那是某台机器 Load unpacked 之后的规则编译缓存，换机器加载会成噪音。
- 清单可以同时挂 Windows 更新器 zip、Mac 手工包、实验 crx。更新器客户端写死选哪条 `id`，不要靠「列表第一项」当生产规则。

## 本机更新面：绿色 EXE

样本是 PyInstaller onefile、Python 3.8、未加密归档，入口 `mcj_update_tool`。对自有打包更有用的是它的职责切分，而不是语言选型。

| 模块 | 职责 |
|------|------|
| 主程序 | 工作目录 = exe 所在目录；拉清单、下载、解压、覆盖 |
| 协议注册 | `HKCU\SOFTWARE\Classes\<protocol>`，无需管理员 |
| 位置登记 | `%USERPROFILE%\.mcj_update_tool\plugin_locations.json`，一份用户级登记表记住多份安装 |
| 分发器 | `--dispatch` 按登记表批量更新所有副本 |
| 进度服务 | `127.0.0.1:<port>`，给扩展轮询 `taskId` |
| 指纹 | 本机标识哈希；下载清单接口不携带（实例如此） |

覆盖规则要显式排除：

```text
更新器.exe
使用说明.txt
config.json
update.log
```

否则一次「更新插件」会把更新器自己覆盖掉，或把用户配置冲掉。

协议唤醒命令行应保持稳定：

```text
"<updater.exe>" --dispatch --protocol "%1"
```

新协议名与旧协议名要并存一段时间。实例里生产只注册 `mcjupdatev2`，仍能解析旧 `mcjupdate://`。协议升级等于改注册表项，用户若只更新扩展目录、没跑过新 exe，网页唤醒会失败。

代理纪律：更新器若 `trust_env=False`，系统代理/VPN 不会自动走。文档必须写「更新时先关代理」，否则会被当成故障。TLS `verify=False` 能让公司证书环境过关，但把中间人窗口打开，自有打包不要学这一条。

## 协议唤醒与本机进度

扩展自己不能静默写磁盘上的其它文件。sideload 架构用自定义协议把控制交还本机进程：

```
扩展/网页
  → 打开 myextupdate://update?taskId=...&fromVersion=...&targetVersion=...
  → Windows 按 HKCU 启动更新器
  → 更新器在 127.0.0.1 写下进度
  → 扩展轮询同一 taskId
  → 成功后提示重启浏览器
```

| 方案 | 适用 | 代价 |
|------|------|------|
| 自定义 URL 协议 | 扩展和官网都能唤醒；无需 Native Messaging host 清单 | 第一次要跑 exe 写 HKCU；部分浏览器对自定义协议有提示 |
| Native Messaging | Chrome 官方推荐的扩展↔本机通道 | 要装 host json + 注册表；官网网页唤醒不了 |
| 只发 zip、人工覆盖 | 最小实现 | 没有进度、没有多位置同步 |

进度口选端口时避开常见本机服务。实例用 `18765`，与 Reqable MCP 默认 report 口冲突，同机只能活一个。TTL 要短：最终状态留两分钟够扩展读 `success/failed`，不要常驻 HTTP。

`taskId` 必须由扩展生成并出现在协议 URL 里。没有 taskId 的唤醒可以当「用户双击 exe」走弹窗，不要开进度服务。

## 扩展目录面：可 Load unpacked 的合同

渠道 zip 解开后，目录内必须能直接看到 `manifest.json`。实例布局：

```
extension/
  manifest.json
  rules.json
  assets/          图标、注入脚本、站点辅助脚本
  dist/
    background/index.mjs
    contentScripts/index.global.js
    popup|options|sidepanel/index.html
    assets/*       带 hash 的打包产物
    update/js/     负责协议唤醒和脚本注入的薄入口
```

MV3 要点（实例实测）：

- `manifest_version: 3`，`background.service_worker` 指向打包后的 mjs。
- popup/options 的 HTML 用根路径 `/dist/assets/...`。在扩展页里 `/` 是 `chrome-extension://<id>/`，能解析；不要改成相对 `../assets` 除非构建链一起改。
- content script 先注入薄入口，再 `chrome.runtime.getURL` 拉大包，或按远程 `cdnBase` 热更新。这是「扩展目录不变、业务包可换」的次级通道，和渠道 zip 是两层更新。
- `host_permissions: *://*/*` 加上 DNR、cookies、scripting，是电商工具常见配置，也是 CWS 审核最痛的点。sideload 等于用安装摩擦换权限自由度。
- 发布 zip **删除 `_metadata/`**。加载后 Chrome 会自己再生成。

浏览器加载步骤保持一句话：

1. 打开扩展管理页，打开开发者模式。
2. 「加载已解压的扩展程序」，选含 `manifest.json` 的目录。
3. 覆盖文件后**重启浏览器**，不要假设 service worker 会自动吃到全部新文件。

Mac 没有这份 Win 更新器时，渠道清单应另给手工 zip，说明同一套加载步骤。

## 账号面与安装面分离

实例里会员、次数、金币全部是网站接口 + `chrome.storage` 里的 `userToken`。安装包不含卡密、不含可用的离线授权文件。

这对打包的含义：

- 更新失败不等于没会员；没登录不等于安装坏了。文档和 UI 要拆开这两类错误。
- 不要把「能加载」宣传成「能免登录用完全功能」。
- 提取安装架构时不要把账号接口误当成必须打进 zip 的东西。

## 给自己的插件：最小到完整

### 最小（只做第 3、4 层）

```text
dist-extension/
  manifest.json
  ...
README.txt   如何开发者模式加载
```

发版 = 打 zip。用户解压后加载或覆盖原目录。适合内部工具、迭代极快、用户不超过几十人。

### 标准（加上第 1、2 层）

```text
my-plugin/
  快捷更新.exe                 绿色更新器
  使用说明.txt
  安装包：my-plugin/           扩展目录（首次可空，由更新器拉）
  config.json                  首次运行后生成
```

发版清单：

1. 构建 MV3 到 `dist-extension/`，确认 Load unpacked 能打开 popup。
2. 打 zip，根目录只有扩展文件，无 `_metadata`、无 exe。
3. 上传对象存储，得到不可变 URL。
4. 更新清单 API：新 `version`、`url`、稳定 `id`。
5. 如改了协议名或 exe 行为，必须发新更新器；只更 zip 不够。

### 协议与目录命名

- 协议名用自己的前缀，避免和别人的 `mcjupdatev2` 一类冲突。
- 协议只注册 HKCU。
- 扩展目录名对用户可见，更新器内部用相对路径，不要写死盘符。
- 多副本用用户级 JSON 登记 exe 路径和插件目录，更新走 `--dispatch`。

## 提取检查表

拿到别人的「快捷更新 + 安装包」或自有发版目录时，按这个表还原架构（skill `extension-install-architecture` 会自动扫一遍）：

| 检查 | 看什么 |
|------|--------|
| 分发模型 | CWS `update_url` / unpacked / 自定义协议 / Native Messaging |
| 渠道 | 版本清单 URL、zip 根是否只有 `extension/` |
| 更新器 | PyInstaller/NSIS/Inno；工作目录；覆盖排除列表 |
| 协议 | HKCU 项、open 命令行、v1/v2 兼容 |
| 进度口 | `127.0.0.1:port`、taskId、TTL |
| 扩展合同 | MV3、SW 路径、HTML 根路径、是否含 `_metadata` |
| 账号面 | 是否与安装面分离 |

不要把这张表当成授权绕过清单。安装架构提取到「目录如何落到磁盘、如何被加载」为止。

## 实例对照（谋臣界）

| 合同项 | 实例值 |
|--------|--------|
| 更新器 | PE32+ PyInstaller 3.8 onefile，入口 `mcj_update_tool` |
| 协议 | 生产 `mcjupdatev2://`，兼容解析 `mcjupdate://` |
| 进度 | `127.0.0.1:18765`，最终状态 TTL 120s |
| 清单 | `Home.DownloadShow.getTool`，选 `id==2` |
| 渠道包 | `v2.2.9` zip，SHA-256 `57d6c5e33fa9ad4a9d34f76ebdec1fdc9f300d50fe54914fd89f27684c1d260b` |
| 扩展 | MV3 名称「谋臣界」，manifest `2.0` |
| 账号 | `userToken` + 网站接口，不在 zip 内 |

原始样本与解包目录留在 `workspace/mouchenjie-ai-plugin/`，不进本知识库。

## Quick Reference

| 主题 | 要点 |
|------|------|
| 为什么 sideload | 避开 CWS 权限审核，换一次「加载已解压」的人工成本 |
| zip 内容 | 只有扩展；exe 和配置在 zip 外 |
| 唤醒 | 自定义协议 > Native Messaging（若还要官网按钮） |
| 生效 | 覆盖目录后重启浏览器 |
| 版本 | 渠道版本 ≠ manifest 版本，发版说明里写两行 |
| 端口 | 本机进度口不要复用抓包/MCP 默认端口 |
| 账号 | 安装成功 ≠ 已登录 |
