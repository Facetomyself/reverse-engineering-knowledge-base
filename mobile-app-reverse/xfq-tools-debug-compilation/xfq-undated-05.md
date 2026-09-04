# 你要注入的 JS 脚本内容

> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: mobile-app-reverse
>
> import frida import sys 你要注入的 JS 脚本内容 js_code = """ console.log("[ ] JS 脚本尝试注入当前子进程..."); function hook_mointor_native1() { Java.perform(function () { try { let SignatureService = Java.use("com.example.processsigndemo.Si

## 正文

import frida
import sys

# 你要注入的 JS 脚本内容
js_code = """
console.log("[*] JS 脚本尝试注入当前子进程...");

function hook_mointor_native1() {
    Java.perform(function () {
        try {
            let SignatureService = Java.use("com.example.processsigndemo.SignatureService");
            SignatureService["native1"].implementation = function (str) {
                console.log(`[->] native1 调用！, 原始参数: ${str}`);
                var retval = this["native1"](str);
                console.log(`[<-] native1 获得返回值: ${retval}`);
                return retval;
            };
            console.log("[+] ✅ 成功寻找到 SignatureService 并完成 Hook！");
        } catch(e) {
            console.log("[-] 当前子进程不是真正的算签进程（未找到对应类），无需脱机挂载。");
        }
    });
}
// 执行你的 Hook
hook_mointor_native1();
"""

def on_message(message, data):
    if message['type'] == 'send':
        print(f"[*] {message['payload']}")
    elif message['type'] == 'error':
        # Frida 内部的报错
        print(f"[-] JS Error: {message['stack']}")
    else:
        print(message)

# 监听到新进程被拉取时的回调
def on_spawned(spawn):
    print(f"[*] ⚡ 发现新进程从地下冒出来啦 -> {spawn.identifier} (PID: {spawn.pid})")
    
    # 只要进程名里带冒号 ':' 的，说明是衍生子进程！
    # （比如：com.example.processsigndemo:core 或是 :push 或是哪怕他改成 :test）
    if spawn.identifier != None and "processsigndemo" in spawn.identifier and ":" in spawn.identifier:
        print(f"[+] 🎯 捕获到目标衍生子进程: {spawn.identifier}，正在下钩子...")
        try:
            # 附加到该子进程
            session = device.attach(spawn.pid)
            script = session.create_script(js_code)
            script.on('message', on_message)
            script.load()
            print("[+] ✅ JS 脚本挂载流程执行完毕！")
        except Exception as e:
            print(f"[-] ❌ 附加子进程时发生异常: {e}")
            
    # 【非常关键】这里一定要释放掉拦截！主进程直接放行，子进程挂载后放行
    # 不然主进程的生命周期会被卡死在白屏，永远也跑不到拉起子进程的那一步
    device.resume(spawn.pid)

def main():
    global device
    # 获取 USB 连接的设备
    device = frida.get_usb_device()
    print("[*] 成功连接设备:", device.name)
    
    # 开启 Spawn Gating (新进程闸门拦截机制)
    device.enable_spawn_gating()
    print("[*] 已布下天罗地网（Spawn Gating），所有新进程都会经过盘查。")
    
    # 绑定回调事件
    device.on('spawn-added', on_spawned)

    # 满足你的要求：同时使用 Python 代码帮你把 App 强行拉启动！
    target_package = "com.example.processsigndemo"
    print(f"[*] 🚀 正在为你强行拉起应用主进程: {target_package} ...")
    try:
        # 手动通过 device.spawn() 拉起的进程默认是被挂起的。
        # 很多版本的 Frida 在此时不会对自己的调用再次触发 spawn-added 回调
        # 所以必须在 Python 主线程立刻把它放行解冻！
        pid = device.spawn([target_package])
        device.resume(pid)
        print(f"[*] 🔓 主进程 (PID: {pid}) 已拉起并解冻放行！")
    except Exception as e:
        print(f"[-] ❌ 拉起 App 失败（你是不是卸载了或者包名错啦）: {e}")

    print("[*] 正在静默监听衍生进程中... (主进程起来后你去划拉一下触发子进程)")
    print("[*] 按 Ctrl+C 退出程序...\n")
    try:
        sys.stdin.read()
    except KeyboardInterrupt:
        print("手动退出，再见！")

if __name__ == '__main__':
    main()
