# 瑞数/瑞树 RS6 动态 JS（Firefox/Gecko 侧重）

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 瑞数/瑞树 RS6 类动态 JS 链路：动态挑战页、动态 cookie、XHR/fetch 请求后缀与业务接口放行验证，侧重 Firefox/Gecko 证据。

## 命中特征

- 首次业务页返回 HTTP 412 或跳到短挑战页，挑战页再加载伪装成站点一方资源的动态脚本
- 动态脚本路径形如 `/<random>/<random>.js` 形态，不同会话或不同轮次可能变化
- HTML 中存在 `r='m'` 的 meta 或内联脚本，meta content 会参与动态 JS 环境
- Cookie 中出现同一随机前缀的 O/P/enable 组合
- 业务请求 URL 被自动追加动态 query 后缀；该后缀通常出现在 XHR.open 或 fetch 边界，不是业务 JS 直接拼接
- 业务 POST 成功响应才算验收（如 JSON 含业务数据字段）；只生成 cookie/后缀不算完成
- 动态代码大体积混淆、反调试 debugger 检测、native toString 检测；外部补环境禁止进入 VMP/opcode/handler 插桩

## 标准流程

```text
1. 从真实 412 或业务页 HTML 抽取所有 r='m' 片段，先移除 HTML 注释
   （IE 条件注释脚本在 Firefox/Gecko 下不会执行）
2. 按页面顺序执行：前置 r='m' 内联脚本 → 当前动态静态脚本 → 后置 r='m' 内联脚本
3. document.currentScript.src 必须来自当前会话动态脚本，不硬编码旧路径
4. 将 r='m' 的 meta content 映射进本地宿主（可能经全局别名读取），并支持 live 输入覆盖
5. 挑战阶段只生成并回填挑战 cookie，不提前触发业务 XHR 后缀边界
6. 挑战成功后按真实链路先访问站点首页建立服务端会话，再访问业务页
7. 再生成最终请求后缀并 POST 业务接口
8. 翻页或多次请求时保留同一真实会话 cookie，但每一页都重新生成动态后缀
```

## 观察优先级

1. 浏览器证据为 Firefox/Gecko 时不能用 Chrome 指纹兜底；HTTP 客户端优先使用与证据一致的 Firefox 指纹
2. 特征点：`window.ActiveXObject` 属性存在但值为 undefined（属性缺失与存在但 undefined 不是同一件事）；document.all 按 Firefox callable/HTMLAllCollection 行为处理
3. Navigator 按 prototype getter 模型补齐；PDF mimeTypes/plugins、pdfViewerEnabled、doNotTrack、oscpu 等以 descriptor 为准
4. 常见外层缺口：BarProp、locationbar/menubar/personalbar/scrollbars/statusbar/toolbar、窗口尺寸、matchMedia、createEvent、scrollingElement
5. 不默认补 `window.chrome`、`webkitRequestFileSystem`、`webkitPersistentStorage`、`navigator.connection`、`navigator.deviceMemory`，除非证据明确存在
6. meta 闭环：返回 HTMLMetaElement 后继续追踪其读取点（content/getAttribute("r")/parentNode/currentScript.src/全局别名）
7. 若命中 IndexedDB、window.external、navigator.locks，按浏览器证据最小补齐观测链路与原型形态

## 常见坑

- 离线后缀成功不等于真实会话放行，live 仍可能 400/拦截
- 按 Chrome 思路补宿主，忽略浏览器证据是 Firefox/Gecko
- 硬编码旧动态脚本路径、旧 meta content 或旧 cookie
- 挑战阶段提前触发业务 XHR wrapper，污染挑战 cookie 或让流程错位
- HTMLAnchorElement href/pathname 缺失导致 XHR open wrapper 已安装但不追加后缀
- DOM 原型链与 Symbol.toStringTag 不像真实 DOM 时，动态 JS 走异常分支
- 只停在 cookie/后缀生成，不验证真实业务 POST 的 HTTP 200 与业务数据
- 子进程读取 JSON 遇到编码乱码，测试脚本应固定 UTF-8 编码

## 验证口径

- 本地语法检查通过；离线生成目标 cookie 与固定长度业务后缀
- live 完整链路返回 HTTP 200，响应体含业务字段；翻页使用同一真实会话循环页码，每页重新生成后缀，多页返回不同业务数据
- 最终以真实业务接口为准，不只看本地 ok 状态
