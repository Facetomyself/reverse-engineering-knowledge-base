# Jiagu 绕过分析报告

> 日期: 2026-07-02 ｜ 状态: **Frida spawn 注入成功，raise(9) 被拦截，进程存活**

## 一、libjiagu_vip.so 静态分析摘要

### 1.1 ELF 结构
- **文件大小**: 889,192 bytes
- **架构**: ARM64 (AArch64)
- **段结构**: 5 个 LOAD 段
  - LOAD[1]: RX, file offset 0x1000-0x1d910, vaddr 0x0-0x1c910 (主代码)
  - LOAD[2]: RW, file offset 0x1e790-0xcc89a, vaddr 0x2d790-0x2568f0
  - LOAD[7]: RX, file offset 0xcd000-0xd54f8, vaddr 0x257000-0x25f4f8 (**全零！运行时解密**)
  - LOAD[8]: RW, file offset 0xd5c20-0xd60a0
  - LOAD[9]: RW, file offset 0xd60a0-0xd9038
- **init_array**: 全零（24 bytes = 3 个函数指针），运行时动态填充
- **fini_array**: 全零（48 bytes = 6 个函数指针）

### 1.2 字符串混淆
- **所有反检测字符串**（"frida", "debug", "ptrace", "xposed", "hook"）均被 XOR(0xA5) 混淆
- 解密函数: `sub_6D34` — 使用 NEON SIMD XOR 进行批量解密，21 处引用
- 磁盘文件中无任何明文反检测关键词

### 1.3 关键符号
| 地址 | 名称 | 用途 |
|------|------|------|
| 0x8fe0 | `JNI_OoLoad` | 初始 JNI 入口 — mprotect 解保护 + getSoName 解析 |
| 0x9f6c | `_Z9__arm_a_1...` | JNI_OnLoad 包装 — 调用 sub_39AC + JavaVM::GetEnv |
| 0x6f60 | `DynCryptor::__arm_c_0` | **动态解密器** — 解密第二代码段 |
| 0x6D34 | `sub_6D34` | **XOR(0xA5) 批量混淆** — 21 xrefs |
| 0x2790 | `kill_0` | **kill PLT 桩** — 116 xrefs |
| 0x258a38 | `JNI_OnLoad` | JNI 入口（第二段，运行时解密） |

### 1.4 关键导入
| 导入 | 威胁等级 | 用途 |
|------|---------|------|
| `syscall` | 高 | 直接 syscall 绕过 libc hook |
| `prctl` | 高 | PR_SET_DUMPABLE, PR_SET_PTRACER |
| `kill` | 高 | 发送致命信号 |
| `dladdr` | 中 | 解析 SO 边界 |
| `dl_iterate_phdr` | 中 | 遍历所有加载的 SO |
| `inotify_init` | 中 | 文件监控 |
| `mmap/mprotect` | 中 | 内存保护操作 |

## 二、动态验证结果

### 2.1 Frida spawn 注入

**环境**: LDPlayer 9, Android 9, root
**Frida 版本**: 17.15.3 (宿主机 + frida-server)

**命令**:
```bash
frida -U -f com.qidian.QDReader -l survival_final.js
```

**结果**:
```
[OK] Frida spawn 成功
[OK] 7 个 native hook 安装完毕 (kill, tgkill, raise, exit, _exit, abort, syscall)
[OK] 2 个 Java hook 安装完毕 (Process.killProcess, System.exit)
[OK] Jiagu 检测到 Frida -> raise(SIGKILL=9) -> 被拦截!
[OK] 进程存活（PID 持续运行）
[WARN] Frida 在 ~5 秒后断连（Jiagu 使用其他机制断开）
```

### 2.2 关键 API 发现

Frida 17.15.3 JavaScript API:
- `Module` 仅有一个方法: `getGlobalExportByName`
- Module 对象 (如 libc) 有: `getExportByName`, `getSymbolByName`, `enumerateExports`
- `Interceptor` 有: `attach`, `replace`, `replaceFast`
- 没有 `Module.getExportByName()` 或 `Module.findExportByName()` — 需要用 `module.getExportByName()`

### 2.3 拦截日志
```
[SURVIVAL] raise(9) -> BLOCKED       # 第一次检测
[SURVIVAL] raise(9) -> BLOCKED       # 第二次检测（~3秒后）
Process terminated                    # Frida 断连（非进程死亡）
```

## 三、检测链推断

```
App 启动
  → libjiagu_vip.so 加载
    → JNI_OoLoad (0x8fe0): mprotect 解保护 + getSoName
    → DynCryptor (0x6f60): 解密第二代码段
    → JNI_OnLoad (0x258a38): 注册 StubApp native 方法
    → arm_a_1 (0x9f6c): sub_39AC → 启动反检测线程
      → Thread 1: 定时扫描 /proc/self/maps + dl_iterate_phdr
      → Thread 2: inotify 监控 /proc/self/
      → Thread 3: prctl 检查 ptrace 状态
      → 检测到 Frida → raise(SIGKILL) → 被拦截
      → 断开 Frida 连接 (prctl/close/ioctl)
```

## 四、已验证的绕过策略

### 4.1 [可用] Frida spawn + survival hooks（当前方案）
- Frida spawn 注入
- 7 个 native hook 拦截所有终止信号
- 2 个 Java hook 拦截 Java 层终止
- 进程持续运行
- **限制**: Frida 连接约 5 秒后断连

### 4.2 [不可用] APK 重打包 patch kill_0
- 重打包改变 APK 签名 → Jiagu Java 壳 (StubApp) 检测到 → native 方法注册失败
- `StubApp.interface20()` 调用时崩溃 (UnsatisfiedLinkError)

### 4.3 [不可用] LD_PRELOAD frida-gadget
- `setprop wrap.` 在 Android 9+ 被限制
- 直接 `adb shell LD_PRELOAD=... monkey` 无效（monkey 创建新进程不继承 env）

### 4.4 [待测试] Frida 窗口期内触发 QDSign
利用 spawn 后的 ~5 秒窗口:
1. 安装 QDSign hooks
2. 触发 HTTP 请求（如启动排行榜 API）
3. 在断连前捕获 QDSign 输入/输出

## 五、下一步

1. **P0**: 在 Frida 窗口期内触发 libfock.so 加载 + hook QDSign
2. **P1**: 逆向 Jiagu 断连机制（prctl close ioctl 哪个在阻断 Frida）
3. **P2**: 实现 Frida 连接持久化（使用 Interceptor.replace 替代 attach）
4. **P3**: 动态验证 fock_sn hex/binary 矛盾

## 六、文件

| 文件 | 说明 |
|------|------|
| `frida/hooks/survival_final.js` | 可用：完整 survival hook (7 native + 2 Java) |
| `frida/hooks/survival_keepalive.js` | 增强版：+prctl +close +pthread_kill hook |
| `frida/hooks/survival_v4.js` | Debug 用：Frida API 探测 |
| `frida/hooks/qdsign_hook.js` | QDSign hook (需 libfock.so 已加载) |
| `native/arm64-v8a/libjiagu_vip_patched.so` | 不可用：patch kill_0 导致 StubApp 失败 |
