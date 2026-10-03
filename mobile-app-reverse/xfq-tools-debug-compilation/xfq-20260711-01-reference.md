---
schema_version: 2
id: scrcpy-capture-flag-reference
document_type: reference
original_date: '2026-07-11'
archived_date: '2026-10-02'
scope:
  targets:
    - scrcpy
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260711-01.md#scrcpy常用命令"
    basis: source-report
  - id: s2
    ref: "./xfq-20260711-01.md#只录制不弹窗口"
    basis: source-report
  - id: s3
    ref: "./xfq-20260711-01.md#录制画面--系统播放声音手机也继续出声"
    basis: source-report
  - id: s4
    ref: "./xfq-20260711-01.md#强制要求音频可用没音频就失败"
    basis: source-report
  - id: s5
    ref: "./xfq-20260711-01.md#只录音频不录画面"
    basis: source-report
  - id: s6
    ref: "./xfq-20260711-01.md#录制-mkv兼容性有时比-mp4-更稳"
    basis: source-report
  - id: s7
    ref: "./xfq-20260711-01.md#自动化录证据画面声音"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源点名的 scrcpy 命令入口和官方文档位置。示例里的设备序列号未转写，也未在本机执行。
  - name: parameters
    anchor: parameters
    sources: [s2, s3, s4, s5, s6]
    basis: source-report
    limits: 旗标含义只来自各节标题和命令中出现的开关。作者声明这不是完整旗标表，未对照当前 scrcpy 版本。
  - name: decision-flow
    anchor: decision-flow
    sources: [s4, s7]
    basis: source-report
    limits: 「最常用这两个」和「没音频就失败」是来源建议，不是本轮录制的验收结果。缺环境前提和独立验收，不建成流程卡。
relations:
  - type: derived_from
    target: "./xfq-20260711-01.md#scrcpy常用命令"
tags:
  - scrcpy
  - source-report
---

# scrcpy 常见录制与音频旗标

这张卡只回答：来源列出的常见 scrcpy 旗标各自声明了什么效果，以及作者默认把「看手机」和「自动化录证据」分成哪两条。不处理 FLAG_SECURE 黑屏或点击事件伪装。设备序列号不进入本卡。完整旗标以来源指向的官方文档为准。本轮没有运行 scrcpy。

<a id="interfaces"></a>
## 命令入口

来源把接口收成 `scrcpy` 命令，并用 `-s` 指定设备。更全的说明被指向 Genymobile/scrcpy 仓库的 `doc` 目录：`https://github.com/Genymobile/scrcpy/tree/master/doc`。作者写明下面只列常见项。

<a id="parameters"></a>
## 参数机制

只录不显示窗口时，命令带 `--no-window --record out.mp4`。要同时留下系统播放声、并且手机继续出声，来源加上 `--audio-source=playback`、`--audio-dup` 和 `--audio-codec=aac`。`--require-audio` 被写成没有音频就失败。

投屏但不录制时只加 `--audio-source=playback --audio-dup`，不带 `--record`。只录音频时用 `--no-video`、`--record audio.m4a`、`--record-format=m4a`，音频源和编码仍是 playback 与 aac。

降低分辨率是 `--max-size=1280`。视频码率是 `--video-bit-rate=8M`。帧率是 `--max-fps=30`。关闭电脑端播放、只保留录制是 `--no-playback --record out.mp4`。查看显示用 `--list-displays`，指定显示用 `--display-id=0`，窗口置顶用 `--always-on-top`。

mkv 那一组仍是 `--no-window` 加 `--record out.mkv`、`--record-format=mkv`，以及 playback、`--audio-dup`。标题写的是兼容性有时比 mp4 更稳，没有给出失败样本。

<a id="decision-flow"></a>
## 两条默认用法

来源建议最常用的只有两条：看手机时只做普通投屏；自动化录证据时不弹窗口，记录画面和声音，并带 `--audio-source=playback --audio-dup --audio-codec=aac --require-audio`。后一条把「没音频」留成失败，而不是静默录出无声文件。其他旗标是按需开关，来源没有排成更长的分支。

## 验证与限制

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 常见命令之外，来源要求去官方 doc 目录，并声明这里只列常见项。 | s1，第 40 行 | source-report | 这篇命令摘录 | 未核对文档目录与现行版本文档是否一致。 |
| C2 | 不弹窗录制使用 `--no-window --record out.mp4`；系统播放声且手机仍出声时再加 playback、`--audio-dup`、aac。 | s2、s3，第 46、48、52-54 行 | source-report | 来源列出的录制组合 | 未生成本地录像。序列号未转写。 |
| C3 | `--require-audio` 表示没有音频就失败。 | s4，第 56、63 行 | source-report | 来源对这一旗标的说明 | 未观察缺音频时的退出码。 |
| C4 | 只录音频用 `--no-video` 与 m4a；mkv 被写成有时比 mp4 更稳。 | s5、s6，第 68、70、72、97、101 行 | source-report | 来源的容器选择 | 「有时更稳」没有对照样本。 |
| C5 | 作者默认只保留「看手机」和「带 require-audio 的无窗口录证据」。 | s7，第 105、107、110、112 行 | source-report | 来源自己的使用建议 | 不是通用验收标准，也没有本次录制产物。 |

分辨率、码率、帧率、`--no-playback`、display 和 `--always-on-top` 只有标题级说明，见来源第 76-95 行。AOSP 上绕过投屏黑屏或伪装点击的笔记不是这些旗标，不并入本卡。
