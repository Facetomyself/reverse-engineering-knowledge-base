
一、目标：
-----

*   目标：启动chromium时，浏览器将不再使用加密方式存储cookie，而是改用明文方式存储。以便于实现异地cookie同步或共享

> 阅读此篇博客前，请确保已具备chromium编译基础。

二、浅析cookie存储方式：
---------------

*   众所周知，chromium的cookie存储位置是`user-data-dir/Default/Network/Cookies`，这个文件没有后缀，但实际是个sqlite库文件，可以使用sqlite打开。  
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/1e90a30801954f73b6d343a86174232f.png)

> 可以看到，默认情况下chromium的cookie存储格式都是加密后的二进制BLOB格式数据。

*   cookie生成密文需要密钥，秘钥的位置在`user-data-dir/Local State`中，这个文件也没有后缀，但实际是个json文件，其中`encrypted_key`这个关键字中记录这这串秘钥信息。  
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/09c9fb5609724712b67885e9e1a310e0.png)
*   由于每次更换电脑，或者切换浏览器环境，chromium都会随机生成一个新的密钥，因此不同环境终端chromium的cookie是无法共享的。

> 所以**在A点登录后，将cookie文件复制给B，B是无法直接拿来使用的**，因为不同环境cookie密钥不同。为了解决这个问题，cookie明文是个不错的解决办法。

三、修改chromium源码：
---------------

*   打开：`/net/extras/sqlite/sqlite_persistent_cookie_store.cc`

##### 1.加入头部引用：

```c
#include <iostream>
#include "base/command_line.h"
```

##### 2.修改位置一：

*   找到代码：

```c
  if (cur_version == 23) {
    SCOPED_UMA_HISTOGRAM_TIMER("Cookie.TimeDatabaseMigrationToV24");
    sql::Transaction transaction(db());
    if (!transaction.Begin()) {
      return std::nullopt;
    }

    if (crypto_) {
      sql::Statement select_smt, update_smt;

      select_smt.Assign(db()->GetCachedStatement(
          SQL_FROM_HERE,
          "SELECT rowid, host_key, encrypted_value, value FROM cookies"));
```

*   替换为：

```c
  if (cur_version == 23) {
    SCOPED_UMA_HISTOGRAM_TIMER("Cookie.TimeDatabaseMigrationToV24");
    sql::Transaction transaction(db());
    if (!transaction.Begin()) {
      return std::nullopt;
    }

    if (crypto_) {
// 开始追加 ===================
    }
    if (!crypto_) {
// 结束追加 ===================
      sql::Statement select_smt, update_smt;

      select_smt.Assign(db()->GetCachedStatement(
          SQL_FROM_HERE,
          "SELECT rowid, host_key, encrypted_value, value FROM cookies"));
```

##### 3.修改位置二：

*   找到代码：

```c
      switch (po->op()) {
        case PendingOperation::COOKIE_ADD:
          add_statement.Reset(true);
          add_statement.BindTime(0, po->cc().CreationDate());
          add_statement.BindString(1, po->cc().Domain());
          add_statement.BindString(2, serialized_partition_key->TopLevelSite());
          add_statement.BindString(3, po->cc().Name());
          if (crypto_) {
            std::string encrypted_value;
            if (!crypto_->EncryptString(
                    base::StrCat({crypto::SHA256HashString(po->cc().Domain()),
                                  po->cc().Value()}),
                    &encrypted_value)) {
              DLOG(WARNING) << "Could not encrypt a cookie, skipping add.";
              RecordCookieCommitProblem(CookieCommitProblem::kEncryptFailed);
              continue;
            }
```

*   替换为：

```c
      switch (po->op()) {
        case PendingOperation::COOKIE_ADD:
          add_statement.Reset(true);
          add_statement.BindTime(0, po->cc().CreationDate());
          add_statement.BindString(1, po->cc().Domain());
          add_statement.BindString(2, serialized_partition_key->TopLevelSite());
          add_statement.BindString(3, po->cc().Name());
          if (crypto_) {
// 开始追加 ===================
    }
    if (!crypto_) {
// 结束追加 ===================
            std::string encrypted_value;
            if (!crypto_->EncryptString(
                    base::StrCat({crypto::SHA256HashString(po->cc().Domain()),
                                  po->cc().Value()}),
                    &encrypted_value)) {
              DLOG(WARNING) << "Could not encrypt a cookie, skipping add.";
              RecordCookieCommitProblem(CookieCommitProblem::kEncryptFailed);
              continue;
            }
```

##### 4.编译

```bash
ninja -C out/Default chrome
```

四、成果测试：
-------

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/53e6a73c9fb54c4293e83f6d8f6edee3.png)

*   运行`./chrome.exe`后，可以看到，cookie全部存到了value列，而不是之前的encrypted\_value列了。值的内容变成了正常文本，也不再是之前的BLOB二进制数据了。

> 现在将A点的Cookies文件直接复制给B点，B端发现可以直接**正常保持登录状态**了。

五、安全提醒：
-----

*   使用cookie明文存储便于上传云端实现异地同步，但需注意明文存储存在泄密风险。
*   如有更优的解决方案，欢迎留言分享。

