
### (附加)浏览器魔改-绕过无限debugger

### 一、目标

> 做爬虫的小伙伴在做js逆向时，基本第一关就是先遇到无限debugger，这里我们通过改源码的方式永久绕过它。  
> 说明：过debugger只要never pause here就可以了。大家可以尝试着改着玩玩。

*   目标1：使debugger关键字变得无效。
*   目标2：新增debuggel关键字，代替原有的debugger功能。

### 二、如何使debugger关键字变得无效

*   假设你已经编译成功了，我在[第一篇文章](https://blog.csdn.net/w1101662433/article/details/137949705)写了如何编译chromium的大概流程。
*   打开chromium源码文件：`\v8\src\parsing\keywords-gen.h`

###### 1.找到：

```c
{"debugger", Token::kDebugger},
```

###### 2.替换为：

```c
//{"debugger", Token::kDebugger},
{"debugger", Token::kFalseLiteral},
```

###### 3.编译：

```c
ninja  -C  out/Default chrome
```

> 注意：这里编译成功后，debugger关键字就等于false了，再也不能用于调试了。

### 三、新增debuggel关键字

*   还是这个文件：`\v8\src\parsing\keywords-gen.h`

##### 1.找到一大长串列表的最后一行：

```c
{"", Token::kIdentifier}};
```

替换为：

```c
//{"", Token::kIdentifier}};
{"debuggel", Token::kDebugger}};
```

> 注意：上面的debugger关键字设置等于false的修改也要保留。

##### 2.找到：

```c
static const unsigned char kPerfectKeywordLengthTable[128] = {
    0,  0, 0, 3, 3, 5, 6, 3, 7, 4, 6, 6, 8, 3, 0, 5, 3, 4, 7, 5, 9, 4,
    5,  3, 4, 6, 2, 7, 4, 6, 7, 8, 4, 5, 5, 2, 3, 8, 6, 7, 6, 5, 9, 10,
    10, 5, 4, 4, 0, 2, 0, 5, 0, 6, 2, 0, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0,
    0,  0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

```

最后一个数字替换为8，就是：

```c
static const unsigned char kPerfectKeywordLengthTable[128] = {
    0,  0, 0, 3, 3, 5, 6, 3, 7, 4, 6, 6, 8, 3, 0, 5, 3, 4, 7, 5, 9, 4,
    5,  3, 4, 6, 2, 7, 4, 6, 7, 8, 4, 5, 5, 2, 3, 8, 6, 7, 6, 5, 9, 10,
    10, 5, 4, 4, 0, 2, 0, 5, 0, 6, 2, 0, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0,
    0,  0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8};
    // 这个8代指debuggel的长度是8。
```

##### 3.找到：

```c
inline Token::Value PerfectKeywordHash::GetToken(const char* str, int len) {
  if (base::IsInRange(len, MIN_WORD_LENGTH, MAX_WORD_LENGTH)) {
    unsigned int key = Hash(str, len) & 0x7f;

```

替换为：

```c
inline Token::Value PerfectKeywordHash::GetToken(const char* str, int len) {
  if (base::IsInRange(len, MIN_WORD_LENGTH, MAX_WORD_LENGTH)) {
    unsigned int key = Hash(str, len) & 0x7f;
		
	//追加
	if (len >= 8 && strncmp(str, "debuggel", 8) == 0) {
      key = 127; // 127代指刚刚改掉的最后一行
    }
```

###### 4.编译：

```c
ninja  -C  out/Default chrome
```

> 注意：编译成功后，就可以使用debuggel代替原有的debugger调试功能了。

### 四、效果

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0301305822bf427396cd572e2d0184e5.png)
