# 技巧：隔离 Node 运行器的进程合同

> 来源: `workspace/cv-cat`（acrawler、TikTok frontier/Shop、京东 h5st server、小红书 websectiga、闲鱼 tfstk）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 预言机不是 `execjs.compile` 整包然后叫一个函数名。对照仓里能复用的是进程合同：输入怎么送、成功长什么样、失败时日志不回显秘密、超时和形状不对都算失败。

成本分流见 [纯算与预言机](./purecalc-vs-oracle-cost.md)。

## 合同表

| 运行器 | 输入 | 成功 | 失败 |
|--------|------|------|------|
| 抖音 acrawler | 环境变量：nonce、Cookie、URL、UA、显式时钟 | stdout 最后一行 JSON，`sig` 以 `_` 开头，退出码 0 | 异常不包含 stdout。无假签名 |
| TikTok frontier | stdin 一行 JSON，`mode=frontier_sign`，可选 32 hex stub | 最后一行以 `{"ok":` 开头，`X-Bogus` 长度 16 | 超时、无合格行、长度不对，都是 `SignerError` |
| TikTok Shop | stdin 一个 JSON，含有序 headers 和预签 URL | stdout JSON 含 `bsid`，长度合同 382 | 日志只留异常类型，不回显 stdin |
| 京东 h5st | stdin 每行 `{"id","params","appId"}` | 同行 `{"ok":true,"result":{h5st,...}}` | `BAD_JSON`。库用 `vm.runInThisContext` 跑在 env 布置好的全局上，不能 `require` 浏览器脚本 |
| 小红书 websectiga | stdin JSON：`code`、UA、platform、pageUrl | 30 秒内最后一行 JSON，值为 64 hex | 非 0 退出码抛错 |
| 闲鱼 tfstk | `subprocess` 调 `node gen_tfstk.js` | 进程输出写入 Cookie `tfstk` | 失败不造随机值 |

时钟要显式传入。acrawler 注释写明：不传时钟时，VM 里的 `Date` 会走另一条分支，可能在返回 JSON 之前就中止。

## 伪代码

```text
run(runner, payload, timeout):
    proc = spawn(node, runner, stdin=json_line(payload), env=explicit_clock)
    line = last_json_line(proc.stdout)
    if proc.returncode != 0 or not shape_ok(line):
        log(error_class_only)              # no cookie, no stdin
        raise RunnerFailed
    return line.value

shape_ok(line):
    acrawler: sig startswith "_"
    frontier: len(X-Bogus) == 16
    shop: len(bsid) == EXPECTED
    h5st: ok and result.h5st split [3] startswith "tk03"   # checked in Python after
    websectiga: 64 hex
```

京东把库常驻，是因为冷启动比签名本身慢两个数量级。每次请求新拉起 232KB 脚本，会把「签名慢」和「签名错」混在一起。常驻之后仍要按画像刷 token 缓存，换 Cookie 不能沿用上一份 tk03。

## 和 execjs 整包的差别

`execjs.compile(open("static/foo.js"))` 然后 `call("tv")` 没有形状门、没有「失败不回显」、也没有显式时钟。它适合看导出函数名。一旦出参要当 runtime 证据，就换成上面这种运行器：最后一行 JSON、长度或前缀、超时、日志脱敏。

两个运行器不要共用一个 `sign.js`。TikTok HTTP frontier 和 Shop OEC 各有自己的脚本路径。混用会让长度合同对到错误的算法上。
