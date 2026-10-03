---
schema_version: 2
id: xfq-undated-06-call-inline
document_type: reference
original_date: unknown
archived_date: '2026-09-04'
scope:
  targets: [babel-single-return-call-inline]
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-undated-06.md#函数花指令js
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只读脚本文本。当前赋值只有注释标成 8 的那一例；其余例子在注释里，期望结果没有断言。没有 Babel 版本，也没有打印结果。内联失败时，只有标识符调用那一趟会把 callee 换回去。
relations:
  - type: derived_from
    target: ./xfq-undated-06.md#函数花指令js
tags: [babel, call-inline, single-return]
---

# 单返回函数调用何时内联、何时放弃

这张卡只回答这份 Babel 脚本的取舍：箭头函数先改成函数表达式，然后只内联「函数体恰好一条 return，且返回值不是逗号表达式」的调用。自执行函数和标识符调用走同一套中止条件，但失败时的回滚不一样。没有和期望值比较的输出，所以不是 procedure。依据保持 source-report。

<a id="decision-flow"></a>
## 内联取舍

依赖是 `@babel/parser`、`traverse`、`types`、`generator`。解析用 `sourceType: 'module'`。真正赋给 `jscode` 的只有这一例：函数体里立刻调用箭头函数，并把 `arguments[0]` 传进去。注释里的 2 和 3.2 写了「放弃内联」，3.2 和 6 写了期望结果，那些行都不是正在执行的代码。

第一趟把 `ArrowFunctionExpression` 换成 `functionExpression`。体不是块时，包成一条 return。接着 `update_ast` 用 generator 打出代码再解析，后面的遍历看不到箭头函数。

第二趟在 `FunctionExpression` 的 exit：父节点必须是 `CallExpression`，且当前节点的 key 是 `callee`。通过 `check_callexpr` 后调用 `do_callexpr_replace(info)`，不传原来的 binding。这一趟没有把 callee 换回去。

第三趟在 `CallExpression` 的 exit：callee 必须是标识符；binding 缺失、`kind === 'param'`、或 `constantViolations.length > 0` 都直接返回。`hoisted` 克隆整个函数节点，否则初始化必须是 `VariableDeclarator`，只克隆 init。然后把 callee 临时换成无名字的 `functionExpression`。`check_callexpr` 失败，或 `do_callexpr_replace(info, binding)` 没有成功，就把 callee 换回缓存并 `skip`。

`check_callexpr` 要求体是块、块里恰好一条语句、这条是 return，并且返回值不是 `SequenceExpression`。

`do_callexpr_replace` 在这些情况下停：返回值仍是逗号表达式；传了原 binding 且体内还有解析到同一个 binding 的调用；体内出现 `AssignmentExpression`；某个实参本身是数组或对象字面量；某个实参节点本身就是 `UpdateExpression`（比较的是路径等于该实参，不是实参内部的更新）；形参既不是标识符也不是赋值模式。形参个数多于实参时，用 `undefined` 或默认值的右侧补进 args。`arguments` 的属性如果是标识符，停止；如果是字面量下标，按形参、实参或 `undefined` 替换；属性既不是标识符也不是这套字面量时，把 `go_stop` 设为 false 并停下这次遍历，这本身不构成后面的中止。标识符不在函数体自己的 bindings 里、但 `getBinding` 找得到时停止。每个形参的引用若不能全部换成对应实参（赋值左侧、变量声明的 id、非计算属性会中断计数），整次替换返回。通过之后，调用被换成 return 的参数，并返回 true。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 正在执行的输入是把 arguments[0] 交给立即调用的箭头函数 | `return (a => a * 2)(arguments[0]);` | s1 ./xfq-undated-06.md:99 | source-report | 外层 process(20) 在后面两行，注释里的其他例子不执行 |
| C2 | 注释写放弃内联，但该例不在运行路径 | `// // 2 fix -> 放弃内联` | s1 ./xfq-undated-06.md:49 | source-report | 没有说明放弃的是哪一条守卫 |
| C3 | 期望结果写在注释里 | `//     // 期望结果: 10` | s1 ./xfq-undated-06.md:70 | source-report | 脚本没有比较打印值和这个数 |
| C4 | 解析成 module | `sourceType: 'module'` | s1 ./xfq-undated-06.md:122 | source-report | 没有 Babel 版本 |
| C5 | 只接受恰好一条语句的函数体 | `if (func_body.node.body.length !== 1) return;` | s1 ./xfq-undated-06.md:153 | source-report | 上一行还要求体是块 |
| C6 | 返回值是逗号表达式则不内联 | `arg_expr_path.isSequenceExpression()` | s1 ./xfq-undated-06.md:158 | source-report | 替换函数里对同一判断又写了一次 |
| C7 | 递归到同一个 binding 则停 | `if (callee.scope.getBinding(callee.node.name) !== origin_callee_binding) return;` | s1 ./xfq-undated-06.md:193 | source-report | 自执行那一趟没有传入这个 binding |
| C8 | 体内赋值表达式会停 | `AssignmentExpression: function (path) {` | s1 ./xfq-undated-06.md:208 | source-report | 下一行才把 go_stop 设为 true |
| C9 | 实参本身是数组字面量则返回 | `aarg.isArrayExpression()` | s1 ./xfq-undated-06.md:219 | source-report | 同一条件还有对象字面量 |
| C10 | UpdateExpression 只在路径等于该实参时停 | `if (update_expr_path !== aarg) return;` | s1 ./xfq-undated-06.md:225 | source-report | 实参内部的更新表达式不会因为这行停下 |
| C11 | 形参只能是标识符或默认值 | `if (!types.isIdentifier(p) && !types.isAssignmentPattern(p)) return;` | s1 ./xfq-undated-06.md:239 | source-report | 没有 rest 或解构的替换 |
| C12 | 缺少的实参补 undefined 或默认值右侧 | `args.push(!types.isAssignmentPattern(p) ? types.identifier('undefined') : p.right)` | s1 ./xfq-undated-06.md:241 | source-report | 只在下标不少于已有实参个数时 |
| C13 | arguments 的标识符属性会停 | `if (property_path.isIdentifier()) {` | s1 ./xfq-undated-06.md:258 | source-report | 对象必须已经是 arguments |
| C14 | 字面量下标小于形参个数时换成形参节点 | `if (index < params.length) {` | s1 ./xfq-undated-06.md:275 | source-report | 下标来自 eval(property_path + '') |
| C15 | 非标识符也非这套字面量时 go_stop 被写成 false | `go_stop = false;` | s1 ./xfq-undated-06.md:289 | source-report | 同文件前面还有一次 false；这行不负责中止后续替换 |
| C16 | 外层 getBinding 找得到而体绑定没有时返回 | `if (!block_path.scope.getBinding(path.node.name)) return;` | s1 ./xfq-undated-06.md:304 | source-report | 两头都找不到则继续 |
| C17 | 引用没有全部替换则放弃 | `if (count !== binding.referencePaths.length) return;` | s1 ./xfq-undated-06.md:345 | source-report | 赋值左侧、声明 id、非计算属性会提前 break |
| C18 | 成功时调用换成 return 的参数 | `callexpr_path.replaceWith(return_stmt.node.argument);` | s1 ./xfq-undated-06.md:349 | source-report | 下一行才 return true |
| C19 | 箭头函数被换成 functionExpression | `path.replaceWith(types.functionExpression(` | s1 ./xfq-undated-06.md:357 | source-report | 非块体会被包成 return，发生在重新解析之前 |
| C20 | 自执行只处理 key 为 callee 的函数 | `if (path.key !== 'callee') return;` | s1 ./xfq-undated-06.md:379 | source-report | 上一行还要求父节点是 CallExpression |
| C21 | 自执行替换不传原 binding | `do_callexpr_replace(info);` | s1 ./xfq-undated-06.md:385 | source-report | 没有包在成功判断里 |
| C22 | 有 constantViolations 的绑定不内联 | `if (binding.constantViolations.length > 0) return;` | s1 ./xfq-undated-06.md:402 | source-report | 标识符调用这一趟才有 |
| C23 | hoisted 克隆整个函数节点 | `if (binding.kind === 'hoisted') {` | s1 ./xfq-undated-06.md:408 | source-report | else 分支要求 VariableDeclarator |
| C24 | 非 hoisted 的初始化不是声明则返回 | `if (!where_path.isVariableDeclarator()) return;` | s1 ./xfq-undated-06.md:411 | source-report | 成功分支克隆的是 init |
| C25 | 标识符内联失败会把 callee 换回缓存 | `callee_path.replaceWith(cache);` | s1 ./xfq-undated-06.md:430 | source-report | check_callexpr 失败时上一分支也会换回 |
| C26 | 脚本的结尾是打印生成代码 | `console.log(generator(cfg.ast, {` | s1 ./xfq-undated-06.md:439 | source-report | 没有期望字符串 |

## 验证与限制

不把注释里的「期望结果: 10」或「期望结果是 110」当成这一脚本的验收。不把 `// 8 -> fix` 当成已经跑通。`update_expr_path !== aarg` 说明实参内部的自增不会走这条中止。`arguments` 属性落到 else 时 `go_stop = false`，不能读成「一律拒绝」。自执行失败不会换回 callee，标识符调用会。没有本地运行，不知道 `process(20)` 打印出来的代码。逗号表达式本身不在这里拆开，返回值一旦是 `SequenceExpression` 就放弃内联。
