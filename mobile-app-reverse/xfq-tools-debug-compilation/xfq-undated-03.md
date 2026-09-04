# hook frida检测

> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: mobile-app-reverse
>
> function hook_dlopen() { var android_dlopen_ext = Module.findExportByName(null, "android_dlopen_ext"); console.log("addr_android_dlopen_ext", android_dlopen_ext); Interceptor.attach(android_dlopen_ext, { onEnter: functio

## 正文

function hook_dlopen() {
    var android_dlopen_ext = Module.findExportByName(null, "android_dlopen_ext");
    console.log("addr_android_dlopen_ext", android_dlopen_ext);
    Interceptor.attach(android_dlopen_ext, {
        onEnter: function (args) {
            var pathptr = args[0];
            if (pathptr != null && pathptr != undefined) {
                var path = ptr(pathptr).readCString();
                console.log("android_dlopen_ext:", path)
            }
        },
        onLeave: function (retvel) {
        }
    })
}

// hook_dlopen()

function patch_func_nop(addr) {
    Memory.patchCode(addr, 8, function (code) {
        // code.writeByteArray([0xE0, 0x03, 0x00, 0xAA]);
        code.writeByteArray([0xC0, 0x03, 0x5F, 0xD6]);  // ret
    });
}

function hook_pth() {
    var pth_create = Module.findExportByName("libc.so", "pthread_create");
    console.log("[pth_create]", pth_create);
    Interceptor.attach(pth_create, {
        onEnter: function (args) {
            var module = Process.findModuleByAddress(args[2]);
            if (module != null) {
                console.log("开启线程-->", module.name, args[2].sub(module.base));
                if (module.name.indexOf("libmsaoaidsec.so") != -1) {
                    patch_func_nop(module.base.add(0x1c544));
                    patch_func_nop(module.base.add(0x1b8d4));
                    patch_func_nop(module.base.add(0x26e5c));

                }
            }
        },
        onLeave: function (retval) {
        }
    });

}

function hook_remove(so_name) {
    Interceptor.attach(Module.findExportByName(null, "android_dlopen_ext"), {
        onEnter: function (args) {
            var pathptr = args[0];
            if (pathptr !== undefined && pathptr != null) {
                var path = ptr(pathptr).readCString();
                if (args[0].readCString() != null && args[0].readCString().indexOf("libmsaoaidsec.so") >= 0) {
                    hook_pth()
                }
            }
        },
        onLeave: function (retval) {
        }
    });
}

function main() {
    hook_remove('libmsaoaidsec.so')
}

setImmediate(main)

// frida -U -f com.max.xiaoheihe -l "hook frida检测.js"
