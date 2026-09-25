# 方法论：薄封装、整包 execjs、纯算，三种完成度

> 来源: `workspace/cv-cat` 各仓 README 与调用点（2026-08 至 2026-09 对照）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 公开仓看起来都是「Python API + static/*.js」。落地完成度要按调用点分：没有签名、execjs 整包、隔离运行器、纯算、设备 RPC。整包出参只能说明参数名和请求边界，不能写成纯算完成。

选型摘要见 [平台签名落地方法](./sign-landing-methods.md)。本篇给判定步骤。

## 五档

| 档 | 源码长什么样 | 能断言什么 | 不能断言什么 |
|----|----------------|------------|----------------|
| 边界壳 | Cookie + 头，无 sign 函数。汽车之家 JSONP、西瓜空的 `X-Bogus`、公众号 token 透传、Instagram 抽 `doc_id` | 请求打到哪、成功字段是什么 | 服务端不校验签名。空位只说明这版客户端没填 |
| 双写 | 头等于某个 Cookie 键。微博 XSRF、领英 JSESSIONID、X 的 ct0 | 源字段和包装 | 还有一层隐藏哈希 |
| execjs 整包 | `compile(static/foo.js)` 再 `call` 一个导出。知乎 `tv`、头条 `get_ab`、淘宝/闲鱼 `generate_sign` | 导出名、入参顺序、appKey 字面量 | 算法已还原，或换版本仍可用 |
| 隔离运行器 | 独立 Node、形状门、失败不降级。h5st server、frontier、websectiga | 出参 provenance 是 runtime | purecalc |
| 纯算 / RPC | 请求边界闭合后的 Python，或设备上的实例调用 | 当前窗口的边界格式，或当前进程的签名 | 跨版本、跨设备仍成立 |

TikTok 仓说明写明已经去掉整包 `static/tiktok.js`，HTTP 改在 Python。京东去掉 `static/JD.js`，改成未修改的 js_security 加常驻服务。小红书 Agent skill 里的 `xhs_main_260411.js` 仍是 2026-04 execjs，现行算法在 `xhs_core`。看到仓库名相同，要看这次调用编译的是哪一个文件。

## 判定流程

```text
find the function that puts the field on the wire
if it copies a cookie field:
    class = double_write
elif it calls execjs.compile(whole_file):
    class = execjs_bundle
    record export name and argument order
elif it spawns node with a shape check:
    class = oracle
elif it calls a Python signer whose inputs are query/body/host:
    class = purecalc_candidate
    still require oracle or capture diff before serverAccepted
elif it calls a device RPC:
    class = device_rpc
else:
    class = boundary_only
```

整包档下一步不是把 JS 粘进知识库。能钩到宿主原语就转入 [钩原语](./vmp-host-primitive-to-purecalc.md)；钩不到且体积大就转入 [预言机成本账](./purecalc-vs-oracle-cost.md)。

## 薄封装仍然有用的三件事

1. 参数名和谁先谁后。淘宝先有样例 sign 再覆盖，这个顺序本身要记，避免把样例 hex 当输出。
2. 端别字面量。appKey、aid 从 JS 或 query 里读出来，填进 [常量表](./endpoint-constant-table.md)。
3. 脏边界。淘宝文件里的 goofish URL 没有被调用。薄封装仓经常拷贝残留，调用点没走到的常量不进协议结论。

## 伪代码：完成度标签

```text
note(field):
    landing = classify(field)
    if landing == execjs_bundle:
        status = "boundary_known"
    elif landing == oracle and shape_ok:
        status = "localReproduced"
    elif landing == purecalc_candidate and diff_ok and business_json:
        status = "serverAccepted"
    else:
        status = "unproven"
```

`status = boundary_known` 足够指导下一次抓包，不够指导「算法已经结束」。
