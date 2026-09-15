# Nuitka onefile：外层 payload 与第二层 native 主程序

> 来源: `workspace/weixin_download` 样本取证
> 原始发布时间: 2026-07-08 至 2026-07-16
> 归档日期: 2026-09-15
> 分类: native-analysis
>
> Windows Nuitka onefile 不是 PyInstaller PYZ。外层 EXE 用 `RT_RCDATA` 高熵 blob（本样本前缀 `KAY` + Zstandard）放出第二层 native Python 主程序；内层仍链 `python3xx.dll`，没有可 `uncompyle6` 的 `.pyc` 全集。后续只做 constants / 协议字符串 / 定向 xref，不宣称无损恢复源码。

## 适用与不适用

适用：Windows GUI/CUI 的 Nuitka `--onefile` 分发，strings 命中 `NUITKA_ONEFILE_PARENT`、`onefile_%PID%_%TIME%`、`__nuitka_version__`。

不适用：PyInstaller `PYZ` / `MEI`（另案，如 `juji-assistant` 静态恢复）；普通 CPython zipapp；已经是目录版 Nuitka（无 onefile bootstrap）。

完成门：抽出内层主程序并核对 SHA-256；能从 constants 窗口稳定读出业务 URL/字段。**不是**还原 `.py` 源码。L4 triage-only 对内层字节码成立。

## 外层：onefile bootstrap

本样本（微信公众号批量下载工具 4.6）形状，可当检查清单：

| 观察 | 含义 |
|------|------|
| PE32+ x86-64，Windows GUI | 外层只是释放器 |
| strings：`NUITKA_ONEFILE_PARENT`、`onefile_%PID%_%TIME%` | onefile 运行时目录约定 |
| `.rsrc` `RT_RCDATA 10/27/0` 约 34 MiB 高熵 | 压缩 payload，不是明文 ZIP |
| payload 前缀 `KAY`，从偏移 3 起可按 Zstandard 解压 | 魔数 + 压缩；换样本先核魔数，不要假定永远是 zstd |
| 解压后出现第二层 `*.exe` + 一堆 DLL/PYD | 真正业务在内层 |

探测顺序（项目脚本在 `scripts/recovery/`，换项目时只复用步骤）：

```text
pe_probe          确认 PE、Nuitka 字符串、节区
extract_resources 抽出 RT_RCDATA
probe_payload     扫 KAY / zstd / MZ / PK 魔数
decompress        按核过的编解码出 blob
extract_payload_full 落到项目 payload_extracted_full/，禁止写到仓库外
```

原始 EXE、payload、解压树只留 owning workspace，进 `evidence-manifest.json`，不进 Git。

## 内层：仍然是 Nuitka native

完整抽取本样本得到 128 个运行时文件（85 DLL、41 PYD、1 PEM + 第二层主程序）。内层：

- 大量导入 `python310.dll` API
- strings 命中原模块名（本样本 `wechatdownload.py`、`mcp_server.py`）和 `__nuitka_version__`
- **不能**当普通 `.pyc` 用反编译器出源

因此主线是：

```text
内层 EXE
  -> rabin2/IDA 字符串与常量池
  -> 按协议 URL 切片做 context window
  -> 函数名 / 伪代码骨架
  -> 用 live HTTP 验证字段，而不是猜完整 Python
```

定向窗口示例：从 `profile_ext?action=getmsg`、`pass_ticket=`、`general_msg_list` 做 xref，比全量 Hex-Rays 更便宜。协议面见 [微信公众号 HTTP 接口面](../protocols/wechat-mp-http-surface.md)。

## 不要做的

- 把 onefile 外层当业务程序去修导入表、找 OEP 当脱壳完成。
- 对内层声称「已完整还原源码」。
- 把解压目录提交 Git，或用固定盘符写脚本。
- 把 Nuitka 的 `KAY`+zstd 套到下一个样本之前不重新核魔数。
- 和 PyInstaller `pyinstxtractor` 混用同一条流水线。

## 和后续落地的关系

取证脚本不是运行时依赖。协议客户端应 clean-room 按字段重写（本仓库对应 `weixin_protocol_reproducer.py`），只把 frozen constants 当 oracle。归档运行时（身份、claim、MCP job）见 [HTTP 归档运行时](../collection-engineering/weixin-http-archive-runtime.md)。
