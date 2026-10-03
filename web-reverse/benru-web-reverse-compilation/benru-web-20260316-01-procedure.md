---
schema_version: 2
id: grok-web-reverse-benru-web-20260316-01
document_type: procedure
original_date: "2026-03-16"
archived_date: "2026-10-02"
scope:
  targets: [babel]
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-web-20260316-01.md#六综合案例还原一个真实的混淆字符串"
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: 只记录来源点名的四个 Babel 包，以及 StringLiteral.extra 与 value 的关系。未安装，也未核对当前主版本还导出这些入口。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 步骤只按来源已写的四步整理。非字符串数组元素、重复绑定和动态解密不在这四步里。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 通过条件是作者贴出的 generate 结果。本轮没有运行 Babel。作者对数组是否仍带编码的两句话不一致。
relations:
  - type: derived_from
    target: "./benru-web-20260316-01.md#六综合案例还原一个真实的混淆字符串"
tags: [babel, string-literal, ast]
---

# Babel 常量字符串还原的四步顺序

这份流程只回答：来源如何用 Babel 还原十六进制或 Unicode 字面量、常量 `+` 拼接，以及字符串数组的数字下标。它不运行脚本，不覆盖控制流平坦化，也不把 `vm` 执行收成步骤。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 包 | `npm install @babel/parser @babel/traverse @babel/generator @babel/types`。quote: npm install @babel/parser @babel/traverse @babel/generator @babel/types | 导入失败走 F1 |
| 脚本文件 | 来源要新建 `还原字符串.js`。quote: 还原字符串.js | 没有可解析源码走 F1 |
| 字面量形态 | 还原点是删掉 `extra`，让生成器用 `value`。quote: 用  ` value  ` 来生成代码 | 节点不是字符串字面量时，这步没有依据 |

来源还写了 `npm init -y`。这是作者的环境说明，不是本轮已安装的清单。

<a id="steps"></a>
## 步骤与分支

下表只整理来源综合案例里已经编号的四步。

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 遍历 `VariableDeclarator`，只收集标识符加数组。来源把这一步写成收集数组。quote: 第一步：收集数组。元素是字符串字面量时先删除 extra。quote: delete elem.extra; | 名字到元素值的 Map | 元素不是字符串字面量时来源返回 null，该槽不替换，走 F2 |
| S2 | 遍历 `MemberExpression`。来源把这一步写成替换数组成员访问。quote: 第二步：替换数组成员访问 | 成员表达式变成字符串字面量 | 下标越界或值为 null 时来源不替换。quote: elements[index] !== null |
| S3 | 再遍历 `StringLiteral` 并删除 extra。quote: 第三步：还原十六进制/Unicode字符串（删除extra） | 生成器改用 `value`。quote: delete path.node.extra; | 没有字符串节点则这步为空，仍进入 S4 |
| S4 | 在 `BinaryExpression` 的 `exit` 上合并拼接。quote: 第四步：合并字符串拼接。运算符不是 `+` 就返回。quote: if (node.operator !== '+') return; | 内层先折成一个字面量 | 不是两个字符串字面量则保持原表达式，验收只看作者样例 |

来源要求用 `exit`，以便子节点先被替换。quote: 确保子节点先被处理。前文单独的拼接示例里，第二个 `else if` 的条件与第一个 `if` 相同。quote: else if (t.isStringLiteral(node.left) && t.isStringLiteral(node.right))。那个分支没有写出新规则，不能当成额外合并能力。

<a id="outputs"></a>
## 输出

来源写运行 `generate(ast).code` 后打印：

quote: var url = 'https://api.example.com';

quote: var key = 'ABCD';

同一段还展示数组已变成明文片段 `['https://', 'api.', 'example', '.com']`。紧接着作者又写数组本身还保留编码。quote: 数组本身还是保留了编码。这两句都只是来源文本，本卡不选择其中一句当运行结果。

<a id="acceptance"></a>
## 验收

| 编号 | 通过条件 | 反例 |
|---|---|---|
| A1 | 作者把综合样例的 `url` 印成 `https://api.example.com`，把 `key` 印成 `ABCD` | 本轮没有 generate 输出，不能把 A1 勾成已通过 |
| A2 | 拼接小节作者写结果是 `Hello World`。quote: var str = 'Hello World'; | 运算符不是 `+`，或任一侧不是字符串字面量时，来源的替换条件不成立 |
| A3 | 数组下标被替换后再走拼接，作者写最终 `url` 会变成完整字符串。quote: 'https://api.example.com' | 第 356 行又说数组仍保留编码。数组明文与这句冲突时，不把数组清理当成已验收 |

A1 到 A3 都停在 source-report。

<a id="failure-exits"></a>
## 失败出口

F1：四个包或待还原源码缺失时停止，不把讲解里的打印当成还原结果。

F2：来源写前四种可以用这套 AST 处理；第五种可能要算常量表达式，第六种要模拟执行或静态分析。quote: 第6种则需要模拟执行或静态分析。数组元素不是字符串字面量时来源返回 null。quote: return null;。多个引用点或元素本身是表达式时，来源写需要更多处理。quote: 数组元素本身也是表达式。这些情况走停止，不沿用四步的通过条件。

F3：动态解密若改走 Node `vm`，来源写恶意操作可能危害系统，并建议只在可控环境使用。quote: 如果代码中有恶意操作可能会危害系统。本流程不把 `vm.runInContext` 收成步骤；材料只剩动态函数时停止，不声称字符串已还原。
