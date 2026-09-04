# 函数花指令.js

> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: mobile-app-reverse
>
> const parser = require("@babel/parser"); const traverse = require("@babel/traverse").default; const types = require("@babel/types"); const generator = require("@babel/generator").default; let jscode = ''; // // 1 fix // 

## 正文

const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const types = require("@babel/types");
const generator = require("@babel/generator").default;

let jscode = '';

// // 1 fix
// jscode = `let i = 1;
// const doubleIt = (x) => x + x;
// const result = doubleIt(i++);`

// // 2 fix -> 放弃内联
// jscode = `const y = 10;
// const fn = (val) => {
//   const y = 100;
//   return val * y;
// };
// const result = fn(y + 1);`;

// // 3 (不想写了)
// jscode = `const obj = {
//   factor: 10,
//   method: function(x) {
//     return x * this.factor;
//   }
// };
// const result = obj.method(5);`

// // 3.2 fix -> 放弃内联
// jscode = `function outer() {
//     const fn = (a) => arguments[0] + arguments[1] + arguments[2] + arguments[3]; // 注意：箭头函数转换后会变成 function(a){ return arguments[0] }
//     const result = fn(10, 20, 30);
//     // 期望结果: 10
// }`;

// // 4 fix
// jscode = `const x = 1, y = 2;
// const createObj = (b) => ({ b });
// const result = createObj(x + y);`;

// // 5 fix
// jscode = `const factorial = (n) => (n <= 1 ? 1 : n * factorial(n - 1));
// const result = factorial(3);`;

// // 6 -> fix
// jscode = `let tax = 10;
// tax += funx(666);
// const addWithTax = (price) => price + tax; // 这里的 tax 应该指向全局的 10
// function calculate() {
//   let tax = 5; // 遮蔽了全局 tax
//   const result = addWithTax(100); // 期望结果是 110
// }`;

// // 7 -> fix
// jscode = `function add(a, b=1) {
// return a + b;
// };
// add(1);`

// 8 -> fix
jscode = `const process = function (a) {
    return (a => a * 2)(arguments[0]);
};
const result = process(20); `

// // 9 -> fix
// jscode = `const process = function (a, b) {
//     return (a => a * 2)(a) * b.a;
// };
// const result = process(20); `

// // 10 -> fix
// jscode = `// Input
// let multiply = (a, b) => a * b;
// const result1 = multiply(2, 3);
// multiply = (a, b) => a + b; // 函数被重新赋值
// const result2 = multiply(2, 3);`

// // 11 -> fix
// jscode = `let x = 0;
// const add = (a) => a + a;
// const result = add(++x);`;

let ast = parser.parse(jscode, {
    sourceType: 'module'
});
let code = ``;

const cfg = {
    ast,
    code
}

////////////////////////////////////////////////////

const update_ast = function (cfg) {
    cfg.code = generator(cfg.ast).code;
    cfg.ast = parser.parse(cfg.code);
}

const is_literal = function (node, include_undefined) {
    if (types.isLiteral(node) || include_undefined && types.isIdentifier(node, {
        name: 'undefined'
    })) return true;
    if (types.isUnaryExpression(node)) return is_literal(node.argument);
    if (types.isBinaryExpression(node)) return is_literal(node.left) && is_literal(node.right)
    return false;
};

const check_callexpr = function (
    callexpr_path,
    func_expr_path,
) {
    const func_body = func_expr_path.get('body');
    if (!func_body.isBlockStatement()) return;
    if (func_body.node.body.length !== 1) return;
    const return_stmt = func_body.get('body.0');
    if (!return_stmt.isReturnStatement()) return;
    const arg_expr_path = return_stmt.get('argument');
    if (
        arg_expr_path.isSequenceExpression()
    ) return;

    return {
        callexpr_path,
        func_expr_path,
        return_stmt,
        arg_expr_path
    }
}

const do_callexpr_replace = function (
    info,
    origin_callee_binding
) {
    // 判断是不是只有一行, 并且这行语句是 return 语句
    const callexpr_path = info.callexpr_path;
    const func_expr_path = info.func_expr_path;
    const return_stmt = info.return_stmt;
    const arg_expr_path = info.arg_expr_path;

    if (
        arg_expr_path.isSequenceExpression()
    ) return;

    const block_path = func_expr_path.get('body');

    let go_stop = false;

    // 看看是不是递归调用
    if (origin_callee_binding) {
        block_path.traverse({
            CallExpression: function (path) {
                const callee = path.get('callee');
                if (!callee.isIdentifier()) return;
                if (callee.scope.getBinding(callee.node.name) !== origin_callee_binding) return;
                go_stop = true;
                path.stop();
            },

        });

        if (go_stop) return;
    }

    const args = [...callexpr_path.node.arguments];
    const params = func_expr_path.get('params');
    const arg_count = args.length;

    func_expr_path.traverse({
        AssignmentExpression: function (path) {
            go_stop = true;
            path.stop();
        }
    });

    if (go_stop) return;

    // 防止 UpdateExpression
    for (const aarg of callexpr_path.get('arguments')) {
        if (
            aarg.isArrayExpression()
            || aarg.isObjectExpression()
        ) return;

        callexpr_path.traverse({
            UpdateExpression: function (update_expr_path) {
                if (update_expr_path !== aarg) return;
                go_stop = true;
                update_expr_path.stop();
            }
        });

        if (go_stop) return;
    }

    // 处理有默认参数和无默认参数的问题
    for (let i in params) {
        // function(a)
        // function(a = 0)
        const p = params[i].node;
        if (!types.isIdentifier(p) && !types.isAssignmentPattern(p)) return;
        if (Number(i) >= arg_count) {
            args.push(!types.isAssignmentPattern(p) ? types.identifier('undefined') : p.right)
        }
    }
    
    // 解决 arguments 访问问题
    block_path.traverse({
        MemberExpression: {
            exit: function (path) {
                if (go_stop) {
                    path.stop();
                    return;
                }
                const object_path = path.get('object');
                if (object_path.isIdentifier({
                    name: 'arguments'
                })) {
                    const property_path = path.get('property');
                    if (property_path.isIdentifier()) {
                        go_stop = true;
                        path.stop();
                    }
                    else if (is_literal(property_path.node)) {
                        const index = eval(property_path + '');

                        if (
                            typeof index !== 'number'
                            || Number.isNaN(index)
                            || Infinity === index
                            || -Infinity === index
                        ) {
                            go_stop = false;
                            path.stop();
                        }
                        else {
                            if (index < params.length) {
                                path.replaceWith(params[index].node);
                            }
                            else if (index < arg_count) {
                                path.replaceWith(args[index]);
                            }
                            else {
                                path.replaceWith(types.identifier('undefined'));
                            }

                            path.scope.crawl();
                        }
                    }
                    else {
                        go_stop = false;
                        path.stop();
                    }
                }
            }
        },
        Identifier: function (path) {
            if (go_stop) {
                path.stop();
                return;
            }

            // 看看这个是不是在外变量
            const binding = block_path.scope.bindings[path.node.name];
            if (!binding) {
                if (!block_path.scope.getBinding(path.node.name)) return;
                go_stop = true;
                path.stop();
            }
        }
    });

    if (go_stop) return;

    for (let i in params) {
        const param = params[i];
        const id_path = param.isIdentifier() ? param : param.get('left');
        const binding = func_expr_path.scope.getBinding(id_path.node.name);
        const arg = args[i];

        let count = 0;

        for (const ref of binding.referencePaths) {
            if (ref.key === 'left') {
                if (ref.parentPath.isAssignmentExpression()) break;
            }
            else if (ref.key === 'id') {
                if (ref.parentPath.isVariableDeclarator()) break;
            }
            else if (ref.key === 'property') {
                if (ref.parentPath.isMemberExpression()) {
                    if (!ref.parentPath.node.computed) break;
                }
            }

            const bbinding = ref.scope.getBinding(ref.node.name);
            if (!bbinding) break;

            if (bbinding !== binding) break;

            ref.replaceWith(arg);

            count++;

        }

        if (count !== binding.referencePaths.length) return;
    }

    // 替换
    callexpr_path.replaceWith(return_stmt.node.argument);
    return true;
}

// 统一化代码
traverse(cfg.ast, {
    ArrowFunctionExpression: {
        enter: function (path) {
            path.replaceWith(types.functionExpression(
                null,
                path.node.params,
                types.isBlockStatement(path.node.body)
                    ?
                    path.node.body
                    :
                    types.blockStatement([types.returnStatement(path.node.body)])
            ))
        }
    }
});

update_ast(cfg);

// 处理嵌套问题
traverse(cfg.ast, {
    FunctionExpression: {
        exit: function (path) {
            const parent_path = path.parentPath;
            // 不是自执行函数
            if (!parent_path.isCallExpression()) return;
            if (path.key !== 'callee') return;

            const info = check_callexpr(parent_path, path);

            if (!info) return;

            do_callexpr_replace(info);

            parent_path.scope.crawl();
        }
    }
});

// 全部替换
traverse(cfg.ast, {
    CallExpression: {
        exit: function (path) {
            const callee_path = path.get('callee');
            // callee 一定是标识符
            if (!callee_path.isIdentifier()) return;
            const binding = path.scope.getBinding(callee_path.node.name);
            if (!binding) return;
            if (binding.kind === 'param') return;
            if (binding.constantViolations.length > 0) return;

            const where_path = binding.path;
            let cache = callee_path.node;
            let new_func;

            if (binding.kind === 'hoisted') {
                new_func = structuredClone(where_path.node);
            } else {
                if (!where_path.isVariableDeclarator()) return;
                new_func = structuredClone(where_path.get('init').node);
            }

            callee_path.replaceWith(types.functionExpression(
                null,
                new_func.params,
                new_func.body
            ));

            const info = check_callexpr(path, callee_path);

            if (!info) {
                callee_path.replaceWith(cache);
                callee_path.skip();
                return;
            }

            if (!do_callexpr_replace(info, binding)) {
                callee_path.replaceWith(cache);
                callee_path.skip();
            }
        }
    }
});

////////////////////////////////////////////////////

console.log(generator(cfg.ast, {
    // compact: true,
}).code);
