---
schema_version: 2
id: com-lawyee-querydoc-des3-reference
document_type: reference
original_date: '2020-05-07'
archived_date: '2026-10-02'
scope:
  targets:
    - com.lawyee
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-app-20200507-01.md#某文app逆向抓取分析"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留来源写明的字段名、base64 外壳和 3DES-CBC 形状。类名中段是星号，ciphertext 没有纯算式，样本设备号不收录。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 调用顺序来自来源的 jadx 与 Frida 叙述。星号遮住的包名段不能当成完整类名，本次没有运行这些钩子。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20200507-01.md#某文app逆向抓取分析"
tags:
  - com-lawyee
  - des3
  - source-report
---

# com.lawyee 查询请求的 base64 体和 3DES 响应

这张卡只回答：来源如何描述包名以 `com.lawyee` 开头的文书查询请求，以及响应 `content` 的 3DES 形状。不提供设备号，也不把来源的 RPC 服务改写成发包客户端。

<a id="parameters"></a>
## 请求字段和响应解密

抓包被收成四条：URL 不变，headers 没有加密，POST 数据以 `request=` 开头且像 base64，返回值分成 `serectkey` 和 `content`（来源拼写如此）。后文称对加密后的 request 做 `base64.decode()`，结果与构造出的参数一致，所以外壳按来源结论是 base64。

| 字段 | 来源写法 | 限制 |
|---|---|---|
| id | 年月日时分秒，脚本用 `%Y%m%d%H%M%S` | 没有时区 |
| command | 固定，脚本里是 `queryDoc` | 只看到这一条命令 |
| pageNum / pageSize | 页码和每页条数 | 来源示例是 1 和 20，没有上限 |
| sortFields | 固定 `s50:desc` | 没有其他排序 |
| ciphertext | `d.a()` 的返回值 | 没有公式 |
| devtype | 脚本里是 `1` | 只出现这一处 |
| devid | 来源称设备号且本次不变 | 样本原值不收录 |
| queryCondition | `key` 为 `s21`，value 为关键词 | 没有其他 key |

编码是 JSON 的 UTF-8 字节做 base64，再拼到 `request=` 后面。

响应侧：`m.a` 被写成 3DES 加密，`m.b` 是解密。iv 来自第一个 `a` 方法，格式 `yyyyMMdd`。key 和 content 都来自响应。Python 形态是 `DES3.MODE_CBC`，key 与 iv 都走 `encode()`，密文先 base64 再 `unpad` 到 `DES3.block_size`。来源没有写 key 的字节长度。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | body 以 request= 开头，返回分成 serectkey 与 content | s1 第 52 行「data是一个以request=开头的一长串加密字符，返回值是由两部分组成，一个serectkey，一个content」 | source-report | 这次抓包 | 主机名不在正文 |
| C2 | id 取当前年月日时分秒 | s1 第 174 行「id = time.strftime("%Y%m%d%H%M%S")」 | source-report | 来源脚本 | 未运行 |
| C3 | command、sortFields、条件 key 分别为 queryDoc、s50:desc、s21 | s1 第 182 行「"command":"queryDoc"」「"sortFields":"s50:desc"」「"key":"s21"」 | source-report | 来源脚本 | 同行的设备号原值不收录 |
| C4 | m.a 加密、m.b 解密，iv 为 yyyyMMdd | s1 第 202 行「m.a(str,str1,str2)是des3加密函数，m.b是解密函数」 | source-report | util.m | 类名中段是星号 |
| C5 | 模式为 DES3.MODE_CBC | s1 第 244 行「mode=DES3.MODE_CBC」 | source-report | 来源给出的 Python 形态 | 未复现 |

<a id="request-chain"></a>
## 从日志函数到解密函数

脱壳用 xposed 加 fdex2，来源称只有一个 dex。jadx 搜 `request` 有两百多条，改搜带引号或冒号的赋值形式后，进入 `b`，传入 `str.getBytes()`。`g.b` 被当成日志函数。

Hook 点是 `com.lawyee.***.util.g` 的 `b(String,String)`。来源称这里的 str 就是 request 加密前的明文。ciphertext 另算：`ciphertext = d.a()`，RPC 目标是 `com.lawyee.****.util.d` 的 `a()`。另一条路是 RPC 调用 `c.a().b` 直接拿 POST data，来源选择自己做 base64。

响应 Hook `com.lawyee.***.util.m` 的 `b(String,String,String)`。来源把 params1、params2、params3 分别写成 content、key、iv。

正文没有失败时停止的出口，外链图也不能代替输入输出，所以不建流程。

## 验证与限制

接口主机、样本设备号、`d.a()` 的纯算式都不在这张卡里。起点 SO 的 3DES 是另一个 target。本次只读文本，没有运行 Frida 或解密代码。
