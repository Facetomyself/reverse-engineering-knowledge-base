# 04-追doCommandNative参数

> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: native-analysis
>
> function hook_dlopen(targetSoName) { // dlopen主要是 hook native函数中加载别的so的，典型的如加固或者系统级别的so； Interceptor.attach(Module.findExportByName(null, "dlopen"), { onEnter: function (args) { this.fileName = args[0].readCString(); con

## 正文

function hook_dlopen(targetSoName) {
    // dlopen主要是 hook native函数中加载别的so的，典型的如加固或者系统级别的so；
    Interceptor.attach(Module.findExportByName(null, "dlopen"), {
        onEnter: function (args) {
            this.fileName = args[0].readCString();
            console.log(`[+] dlopen onEnter ==> ${this.fileName}`);
            if (!targetSoName || this.fileName.indexOf(targetSoName) >= 0) {
                this.isMatch = true;
            }
        },
        onLeave: function (retval) {
            console.log(`[-] dlopen onLeave <== ${this.fileName}`);
            if (this.isMatch) {
                let address_JNI_OnLoad = Module.getExportByName(this.fileName, 'JNI_OnLoad');
                console.warn(`[*] found JNI_OnLoad in ${this.fileName}, address is at ${address_JNI_OnLoad}`);
                hook_mointor_doCommandNative();
            }
        }   
    });
    // android_dlopen_ext，现在一般都用这个；因为system.loadlibrary/load底层就是调用这个函数的；还有native层有的也会引入这个导出函数然后调用；
    // 详细源码分析请看: https://t.zsxq.com/BSZKj
    Interceptor.attach(Module.findExportByName(null, "android_dlopen_ext"), {
        onEnter: function (args) {
            this.fileName = args[0].readCString();
            console.log(`[+] dlopen onEnter ==> ${this.fileName}`);
            if (!targetSoName || this.fileName.indexOf(targetSoName) >= 0) {
                this.isMatch = true;
            }
        }, 
        onLeave: function (retval) {
            console.log(`[-] dlopen onLeave <== ${this.fileName}`);
            if (this.isMatch) {
                let address_JNI_OnLoad = Module.getExportByName(this.fileName, 'JNI_OnLoad');
                console.warn(`[*] found JNI_OnLoad in ${this.fileName}, address is at ${address_JNI_OnLoad}`);
                hook_mointor_doCommandNative();
            }
        }
    });
}

// Smali signature: doCommandNative(I[Ljava/lang/Object;)Ljava/lang/Object;
function hook_mointor_doCommandNative(){
    Java.perform(function () {
        findCorrectClassLoader("com.kuaishou.android.security.internal.dispatch.JNICLibrary");
        let com_kuaishou_android_security_internal_dispatch_JNICLibrary = Java.use("com.kuaishou.android.security.internal.dispatch.JNICLibrary");
        com_kuaishou_android_security_internal_dispatch_JNICLibrary["doCommandNative"].implementation = function (i4, objArr) {
            console.log(`[->] com_kuaishou_android_security_internal_dispatch_JNICLibrary.doCommandNative is called! args are as follows:\n    ->i4= ${i4}\n    ->objArr= ${objArr}`);
                showObjectArray(objArr, "objArr");
            var retval = this["doCommandNative"](i4, objArr);
            // showJavaStacks();
            console.log(`[<-] com_kuaishou_android_security_internal_dispatch_JNICLibrary.doCommandNative ended! \n    retval= ${retval}`);
            return retval;
        };
    });
    // 辅助函数1: 打印调用栈
    function showJavaStacks() {
        console.log(Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new()));
    };
    // 辅助函数2: 打印对象数组
    function showObjectArray(objArr, name) {
        if (objArr == null) return;
        var length = objArr.length;
        console.log(name + ' length: ' + length);
        for (let i = 0; i < length; i++) {
            var item = objArr[i];
            if (item != null && item.getClass().getName() === "[B") {
                var str = Java.use('java.lang.String').$new(Java.array('byte', item)).toString();
                console.log('  [' + i + '] = (byte[]) ' + str);
            } else {
                console.log('  [' + i + '] = ' + (item != null ? item.toString() : 'null'));
            }
        }
    }
    console.warn(`[*] hook_mointor_doCommandNative is injected!`);
};

hook_dlopen("libkwsgmain.so");

function findCorrectClassLoader(className) {
    console.log("[*] Attempting to find correct ClassLoader...");
    let foundLoaders = []; 
    Java.enumerateClassLoaders({
        onMatch: function(loader) {
            try {
                if (loader.findClass(className)) {
                    console.log("[+] Found correct ClassLoader");
                    foundLoaders.push(loader); 
                }
            } catch (e) {}
        },
        onComplete: function() {
            if (foundLoaders.length === 0) {
                console.warn("[*] Could not find correct ClassLoader, using default!");
            } else {
                console.log("[*] Found " + foundLoaders.length + " ClassLoader(s)");
            }
        }
    });
    return foundLoaders.length > 0 ? foundLoaders[foundLoaders.length - 1] : null;
}
function setClassloader(loader) {
    if (loader) {
        Java.classFactory.loader = loader;
        console.log("[+] ClassLoader set successfully");
    } else {
        console.warn("[-] Cannot set null ClassLoader");
    }
}
