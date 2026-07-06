
### 一、什么是Shadow DOM

*   `Shadow DOM`是一种在web开发中用于封装HTML标记、样式和行为的技术，以避免组件间的样式和脚本冲突。
*   它允许开发者将网页的一部分隐藏在一个独立的作用域内，从而实现更加模块化和可维护的代码结构

### 二、js操作Shadow DOM

```js
// 获取宿主元素
const host = document.getElementById('main');

// 创建一个Shadow Root
const shadowRoot = host.attachShadow({mode: 'open'});

// 在Shadow DOM中添加内容
shadowRoot.innerHTML = `<style>:host { display: block; }</style><p>Hello, Shadow DOM!</p>`;

// 访问Shadow DOM中的内容
const shadowContent = host.shadowRoot.querySelector('p').textContent;
console.log(shadowContent); // 输出: Hello, Shadow DOM!
```

> 注意：这里`attachShadow`函数的mode参数有2种，open和closed。

*   当mode设置为open时，Shadow DOM是相对开放的。这意味着外部的JavaScript代码可以通过宿主元素的`shadowRoot`属性访问Shadow DOM。这种访问权限允许开发者读取和修改Shadow DOM的结构和内容。
*   当mode设置为closed时，Shadow DOM对外部JavaScript是不可访问的。这意味着宿主元素`的shadowRoot`属性在外部代码中将会返回null，从而无法直接访问或操作Shadow DOM的内容。

### 三、如何获取closed的shadowRoot里的内容

*   网络上的数据如果不想让我们获取的话，一定会是使用closed模式，让我们无法js访问。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/373d2e6f8f9a4f648fea9bd7af6ec957.png)

*   但这里我们现在就是要获取closed的数据里面的内容怎么办呢？这里我提供一个解决方案：修改chromium源码，使`shadowRoot`的mode强行变为open。

###### 1.找到源码：

*   打开：`\third_party\blink\renderer\core\dom\element.cc`
    
*   找到：
    

```c
ShadowRoot* Element::attachShadow(const ShadowRootInit* shadow_root_init_dict,
                                  ExceptionState& exception_state) {
  DCHECK(shadow_root_init_dict->hasMode());
  String mode_string = shadow_root_init_dict->mode();
```

###### 2.替换为：

```c
ShadowRoot* Element::attachShadow(const ShadowRootInit* shadow_root_init_dict,
                                  ExceptionState& exception_state) {
  DCHECK(shadow_root_init_dict->hasMode());
  //String mode_string = shadow_root_init_dict->mode();
  mode_string = "open";
```

###### 3.编译：

```c
ninja -C out/Default chrome
```

> 编译完成后，可以发现所有的shadowRoot状态全部变成open啦。

### 四、还可以优化

*   由于有些站会做反爬检测，如果发现`shadowRoot`返回的不是null后，就返回一些错误信息。
*   优化思路是给Element新增一个魔改后的`shadowRoot2`属性，这样网站继续检测`shadowRoot`不会有问题。

* * *

### 五、追加：给Element追加shadowRoot2属性

*   既然要新增一个属性，上面的`attachShadow()`函数我们就可以不要了。
*   下面是如何新增一个属性`shadowRoot2`。

###### 1.修改 `\third_party\blink\renderer\core\dom\element.cc`

```c
ShadowRoot* Element::OpenShadowRoot() const {
  ShadowRoot* root = GetShadowRoot();
  return root && root->GetMode() == ShadowRootMode::kOpen ? root : nullptr;
}

// 追加====================
ShadowRoot* Element::OpenShadowRoot2() const {
  ShadowRoot* root = GetShadowRoot();
  return root;
}
// 结束追加====================
```

###### 2.修改：`\third_party\blink\renderer\core\dom\element.h`

```c
ShadowRoot* OpenShadowRoot() const;
  // 追加一行 ===================
  ShadowRoot* OpenShadowRoot2() const;
  // 结束追加 ===========================
```

###### 3.修改：`\third_party\blink\renderer\core\dom\element.idl`

```c
[RaisesException, MeasureAs=ElementAttachShadow] ShadowRoot attachShadow(ShadowRootInit shadowRootInitDict);
[PerWorldBindings, ImplementedAs=OpenShadowRoot] readonly attribute ShadowRoot? shadowRoot;
//追加一行 ===================
[PerWorldBindings, ImplementedAs=OpenShadowRoot2] readonly attribute ShadowRoot? shadowRoot2;
//结束追加 ===========================
```

###### 4.编译：

```c
ninja -C out/Default chrome
```

> 注意：编译较慢。
