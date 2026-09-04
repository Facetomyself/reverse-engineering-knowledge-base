# 逗号表达式.js

> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: mobile-app-reverse
>
> const parser = require("@babel/parser"); const traverse = require("@babel/traverse").default; const types = require("@babel/types"); const generator = require("@babel/generator").default; const is_literal = function (nod

## 正文

const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const types = require("@babel/types");
const generator = require("@babel/generator").default;

const is_literal = function (node, include_undefined) {
    if (types.isLiteral(node) || include_undefined && types.isIdentifier(node, {
        name: 'undefined'
    })) return true;
    if (types.isUnaryExpression(node)) return is_literal(node.argument);
    if (types.isBinaryExpression(node)) return is_literal(node.left) && is_literal(node.right)
    return false;
};
const UpdateAST = function (cfg) {
    cfg.code = generator(cfg.ast).code;
    cfg.ast = parser.parse(cfg.code);
};
const extract_stmt_find_insert_path = function (path) {
    let
        children = path,
        current = path.parentPath,
        parent
        ;

    let flags = [];

    while (true) {

        // 特殊情况, 没有父节点了. 一般是 current 为 Program 的 path`
        if (!current.parentPath) {
            return null;
        }

        parent = current.parentPath;

        ///////////////////////////

        if (
            current.isAssignmentExpression()
        ) {

            if (parent.isExpressionStatement()) {
                flags.push('create_expr_stmt');
            } else {
                if (!parent.isSequenceExpression()) {
                    flags.push('create_sequence_expr');
                }
            }

            return {
                flags,
                path: current
            };
        }

        if (
            current.isStatement() 
            && !current.isWhileStatement() 
            && !current.isDoWhileStatement()
        ) {
            flags.push("create_expr_stmt");
            return {
                flags,
                path: current
            };
        }

        ///////////////////////////

        children = current;
        current = parent;

        // 已经是全局
        if (current.isProgram()) {
            flags.push('create_expr_stmt');
            return {
                flags,
                path: children
            };
        }

    }

};
const FixSequenceExpression_extract_stmt = function (sequence_path, options) {

    const parent_path = sequence_path.parentPath;
    const expressions = sequence_path.node.expressions;

    if (
        // ["a", (d = ["H", "u", "A", "S", "T"], "m")]
        parent_path.isArrayExpression()
        // b = (d = ["H", "u", "A", "S", "T"], c = ["a", "m"], "I")
        || parent_path.isAssignmentExpression()
        // !(U = ["Z", "H", 2], 0)
        || parent_path.isUnaryExpression()
        || parent_path.isExpressionStatement()
        || parent_path.isReturnStatement()
        || (parent_path.isBinaryExpression() && sequence_path.key === 'left')
        || (parent_path.isLogicalExpression() && sequence_path.key === 'left')
        || ((
            parent_path.isIfStatement() 
            || parent_path.isWhileStatement()
        ) && sequence_path.key === 'test')
        || (parent_path.isForStatement() && sequence_path.key === 'init')
        || (parent_path.isSwitchStatement() && sequence_path.key === 'discriminant')
    ) {

        const find = extract_stmt_find_insert_path(sequence_path);

        if (find) {

            let target = find.path;
            const insert_before = find.flags.includes('create_expr_stmt');

            // 看看都需要哪些操作
            if (find.flags.includes('create_sequence_expr')) {
                // 需要创建一个 SequenceExpression 包含住
                target.replaceWith(types.sequenceExpression([target.node]));
                target = target.get('expressions')[0];
            }

            let expr;
            while (expressions.length > 1) {
                // 弹出第一个元素
                expr = expressions.shift();

                if (
                    (options.literal && is_literal(expr, true))
                    || (options.identifier && types.isIdentifier(expr))
                    || (options.memberexpr && types.isMemberExpression(expr))
                ) {
                    delete expr;
                    continue;
                }

                if (
                    insert_before
                ) {
                    target.insertBefore(types.expressionStatement(expr));
                } else {
                    target.parentPath.node[target.listKey].splice(target.parentPath.node[target.listKey].indexOf(target.node), 0, expr);
                }
            }

            sequence_path.replaceWith(expressions[0]);
            return true;
        }

        return;
    }

    if (
        parent_path.isCallExpression()
        || (parent_path.isMemberExpression() && sequence_path.key === 'property')
        || (parent_path.isVariableDeclarator() && sequence_path.key === 'init')
    ) {
        // 这里暂时只做过滤掉字面量
        let i = 0;
        while (i < expressions.length - 1) {

            const expr = expressions[i];

            if (
                (options.literal && is_literal(expr, true))
                || (options.identifier && types.isIdentifier(expr))
                || (options.memberexpr && types.isMemberExpression(expr))
            ) {
                expressions.splice(i, 1);
                continue;
            }

            i++;
        }

        expressions.length === 1 && sequence_path.replaceWith(expressions[0]);

        return true;
    }

    // debugger;
};
const FixSequenceExpression = function (my_params) {

    const options = {
        literal: Boolean(my_params.filter_literal),
        identifier: Boolean(my_params.filter_identifier),
        memberexpr: Boolean(my_params.filter_memberexpr),
    }

    return function FixSequenceExpression(cfg) {
        traverse(cfg.ast, {
            SequenceExpression: {
                exit: function (path) {
                    FixSequenceExpression_extract_stmt(path, options) && path.scope.crawl();
                },
            }
        });

        UpdateAST(cfg);
    }
};

let code = `var a, b, c, d;\na = [(b = (c = ["a", (d = ["H", "u", "A", "S", "T"], "m")], "I"), "H"), "e", "l", "l", "o"];`;
const cfg = {
    ast: parser.parse(code),
    code
};
FixSequenceExpression({
    filter_literal: true,
    filter_identifier: false,
    filter_memberexpr: true
})(cfg);
console.log(generator(cfg.ast).code)
