# gadget_trace

> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: mobile-app-reverse
>
> 'use strict'; / com.xiaofeng.qbdi Gadget trace example. Normal flow: adb s 13081FDD4002VL push bin/libxfqtrace.so /data/local/tmp/libxfqtrace.so adb s 13081FDD4002VL shell su c 'mkdir p /data/data/com.xiaofeng.qbdi/files

## 正文

'use strict';

/*
 * com.xiaofeng.qbdi Gadget trace example.
 *
 * Normal flow:
 *   adb -s 13081FDD4002VL push bin/libxfqtrace.so /data/local/tmp/libxfqtrace.so
 *   adb -s 13081FDD4002VL shell su -c 'mkdir -p /data/data/com.xiaofeng.qbdi/files && cp /data/local/tmp/libxfqtrace.so /data/data/com.xiaofeng.qbdi/libxfqtrace.so && chmod 755 /data/data/com.xiaofeng.qbdi/libxfqtrace.so'
 *   adb -s 13081FDD4002VL forward tcp:14725 tcp:14725
 *   frida -H 127.0.0.1:14725 -n Gadget -l examples/com.xiaofeng.qbdi/gadget_trace.js
 */

const CONFIG = {
  package: 'com.xiaofeng.qbdi',
  target: {
    type: 'func',
    so_name: 'libxftest.so',
    offset: '0x20adc'
  },
  options: {
    inline_hook_backend: 2,
    out_format: 'traceui',
    lz4_compression: {
      enable: true,
      level: 0
    },
    stop_condition: {
      max_traces: 1
    },
    hook_format: {
      args: 'cstr',
      ret: 'hex',
      naming_source: 0,
      naming_index: 0
    }
  },
  demo: {
    enable_java_trigger: true,
    trigger_arg: 'hello_svc_test',
    trigger_delay_ms: 500
  }
};

const RTLD_NOW = 2;
const ENGINE_PATHS = [
  '/data/data/' + CONFIG.package + '/libxfqtrace.so',
  '/data/data/' + CONFIG.package + '/files/libxfqtrace.so',
  '/data/user/0/' + CONFIG.package + '/files/libxfqtrace.so',
  '/data/local/tmp/libxfqtrace.so'
];

function log(msg) {
  console.log('[xfqtrace] ' + msg);
}

function ptrIsNull(p) {
  return !p || p.isNull();
}

function pathEndsWithName(path, name) {
  return !!path && path.length > name.length &&
    path.substring(path.length - name.length - 1) === '/' + name;
}

function dirname(path) {
  const idx = path ? path.lastIndexOf('/') : -1;
  return idx >= 0 ? path.substring(0, idx) : '';
}

function readCStringSafe(p) {
  try {
    return ptrIsNull(p) ? '' : p.readCString();
  } catch (_) {
    return '';
  }
}

const dlopenAddr = Module.findExportByName(null, 'dlopen');
const androidDlopenExtAddr = Module.findExportByName(null, 'android_dlopen_ext');
const dlsymAddr = Module.findExportByName(null, 'dlsym');
const dlerrorAddr = Module.findExportByName(null, 'dlerror');

if (!dlopenAddr || !androidDlopenExtAddr || !dlsymAddr) {
  throw new Error('dlopen/android_dlopen_ext/dlsym not found');
}

const dlopenFn = new NativeFunction(dlopenAddr, 'pointer', ['pointer', 'int']);
const dlsymFn = new NativeFunction(dlsymAddr, 'pointer', ['pointer', 'pointer']);
const dlerrorFn = dlerrorAddr ? new NativeFunction(dlerrorAddr, 'pointer', []) : null;

let fopenFn = null;
let fgetsFn = null;
let fcloseFn = null;
let loaderDlopenFn = null;
let loaderAndroidDlopenExtFn = null;
let engineHandle = null;
let doneCallback = null;
let armed = false;
let arming = false;
let targetPathHint = null;
let listeners = [];

function dlerrorString() {
  try {
    const p = dlerrorFn ? dlerrorFn() : ptr(0);
    return ptrIsNull(p) ? '' : ': ' + p.readCString();
  } catch (_) {
    return '';
  }
}

function findLinkerSymbol(name) {
  const names = [name, '__dl__' + name];
  for (const n of names) {
    try {
      const p = Module.findExportByName(null, n);
      if (p) return p;
    } catch (_) {}
  }

  for (const m of Process.enumerateModules()) {
    if (m.name !== 'linker64' && m.name !== 'linker' && (!m.path || m.path.indexOf('/linker') === -1)) {
      continue;
    }
    try {
      for (const s of m.enumerateSymbols()) {
        if (s.name === name || s.name === '__dl__' + name) return s.address;
      }
    } catch (_) {}
  }
  return null;
}

function tryPlainDlopen(path) {
  const h = dlopenFn(Memory.allocUtf8String(path), RTLD_NOW);
  if (!ptrIsNull(h)) {
    engineHandle = h;
    log('engine loaded: ' + path + ' handle=' + h);
    return true;
  }
  log('dlopen failed: ' + path + dlerrorString());
  return false;
}

function tryLoaderAndroidDlopenExt(path, callerAddr) {
  if (loaderAndroidDlopenExtFn === null) {
    const p = findLinkerSymbol('__loader_android_dlopen_ext');
    loaderAndroidDlopenExtFn = p ? new NativeFunction(p, 'pointer', ['pointer', 'int', 'pointer', 'pointer']) : false;
    log(loaderAndroidDlopenExtFn ? '__loader_android_dlopen_ext ready: ' + p : '__loader_android_dlopen_ext not found');
  }
  if (!loaderAndroidDlopenExtFn) return false;

  const h = loaderAndroidDlopenExtFn(Memory.allocUtf8String(path), RTLD_NOW, ptr(0), callerAddr);
  if (!ptrIsNull(h)) {
    engineHandle = h;
    log('engine loaded via __loader_android_dlopen_ext: ' + path + ' handle=' + h + ' caller=' + callerAddr);
    return true;
  }
  log('__loader_android_dlopen_ext failed: ' + path + ' caller=' + callerAddr + dlerrorString());
  return false;
}

function tryLoaderDlopen(path, callerAddr) {
  if (loaderDlopenFn === null) {
    const p = findLinkerSymbol('__loader_dlopen');
    loaderDlopenFn = p ? new NativeFunction(p, 'pointer', ['pointer', 'int', 'pointer']) : false;
    log(loaderDlopenFn ? '__loader_dlopen ready: ' + p : '__loader_dlopen not found');
  }
  if (!loaderDlopenFn) return false;

  const h = loaderDlopenFn(Memory.allocUtf8String(path), RTLD_NOW, callerAddr);
  if (!ptrIsNull(h)) {
    engineHandle = h;
    log('engine loaded via __loader_dlopen: ' + path + ' handle=' + h + ' caller=' + callerAddr);
    return true;
  }
  log('__loader_dlopen failed: ' + path + ' caller=' + callerAddr + dlerrorString());
  return false;
}

function uniqPaths(paths) {
  const out = [];
  for (const p of paths) {
    if (p && out.indexOf(p) === -1) out.push(p);
  }
  return out;
}

function loadEngine(targetMod) {
  if (engineHandle) return true;

  const paths = ENGINE_PATHS.slice();
  if (targetMod && targetMod.path) {
    paths.unshift(dirname(targetMod.path) + '/libxfqtrace.so');
  }

  const candidates = uniqPaths(paths);
  for (const p of candidates) {
    if (tryPlainDlopen(p)) return true;
  }

  if (targetMod && targetMod.base && !targetMod.base.isNull()) {
    for (const p of candidates) {
      if (tryLoaderAndroidDlopenExt(p, targetMod.base)) return true;
      if (tryLoaderDlopen(p, targetMod.base)) return true;
    }
  }

  return false;
}

function api(name, ret, args) {
  const p = dlsymFn(engineHandle, Memory.allocUtf8String(name));
  if (ptrIsNull(p)) throw new Error('dlsym failed: ' + name);
  return new NativeFunction(p, ret, args);
}

function initFopen() {
  if (fopenFn !== null) return !!fopenFn;
  const fopenAddr = Module.findExportByName(null, 'fopen');
  const fgetsAddr = Module.findExportByName(null, 'fgets');
  const fcloseAddr = Module.findExportByName(null, 'fclose');
  if (!fopenAddr || !fgetsAddr || !fcloseAddr) {
    fopenFn = false;
    return false;
  }
  fopenFn = new NativeFunction(fopenAddr, 'pointer', ['pointer', 'pointer']);
  fgetsFn = new NativeFunction(fgetsAddr, 'pointer', ['pointer', 'int', 'pointer']);
  fcloseFn = new NativeFunction(fcloseAddr, 'int', ['pointer']);
  return true;
}

function findTargetFromMaps() {
  if (!initFopen()) return null;

  const name = CONFIG.target.so_name;
  const f = fopenFn(Memory.allocUtf8String('/proc/self/maps'), Memory.allocUtf8String('r'));
  if (ptrIsNull(f)) return null;

  const buf = Memory.alloc(4096);
  try {
    while (!ptrIsNull(fgetsFn(buf, 4096, f))) {
      const line = buf.readCString();
      if (line.indexOf('/' + name) === -1) continue;

      const cols = line.trim().split(/\s+/);
      if (cols.length < 6) continue;

      const path = cols.slice(5).join(' ');
      if (!pathEndsWithName(path, name)) continue;

      const base = ptr('0x' + cols[0].split('-')[0]);
      fcloseFn(f);
      return { name: name, path: path, base: base };
    }
  } catch (_) {}

  try { fcloseFn(f); } catch (_) {}
  return null;
}

function findTargetModule() {
  const name = CONFIG.target.so_name;

  const fromMaps = findTargetFromMaps();
  if (fromMaps) return fromMaps;

  for (const m of Process.enumerateModules()) {
    if ((m.name === name || pathEndsWithName(m.path, name)) && pathEndsWithName(m.path, name)) {
      return m;
    }
  }

  const direct = Process.findModuleByName(name);
  if (direct && (!direct.path || pathEndsWithName(direct.path, name))) return direct;
  return null;
}

function buildTraceConfig(base) {
  const target = {};
  for (const k in CONFIG.target) target[k] = CONFIG.target[k];
  target.base = base.toString();

  return JSON.stringify({
    target: target,
    options: CONFIG.options || {}
  });
}

function detachLoadWatchers() {
  for (const l of listeners) {
    try { l.detach(); } catch (_) {}
  }
  listeners = [];
}

function triggerDemo() {
  if (!CONFIG.demo || !CONFIG.demo.enable_java_trigger) return;

  setTimeout(function () {
    Java.perform(function () {
      try {
        const MainActivity = Java.use('com.xiaofeng.qbdi.MainActivity');
        const arg = CONFIG.demo.trigger_arg || 'hello_svc_test';
        const ok = MainActivity.triggerAllTests(arg);
        log('triggered nativeRunAllTests => ' + ok);
      } catch (e) {
        log('Java trigger failed: ' + e);
      }
    });
  }, CONFIG.demo.trigger_delay_ms || 500);
}

function armTrace() {
  if (armed || arming) return;
  arming = true;

  try {
    const mod = findTargetModule();
    if (!mod) {
      log(CONFIG.target.so_name + ' not loaded');
      return;
    }

    const targetPath = targetPathHint || mod.path;
    if (targetPath && !pathEndsWithName(targetPath, CONFIG.target.so_name)) {
      log('ignore mismatched target path: ' + targetPath);
      return;
    }

    if (!loadEngine(mod)) {
      log('load libxfqtrace.so failed');
      return;
    }

    const configure = api('xfqtrace_configure', 'int', ['pointer']);
    const start = api('xfqtrace_start', 'int', []);
    const stop = api('xfqtrace_stop', 'void', []);
    const getLastError = api('xfqtrace_get_last_error', 'pointer', []);
    const setDoneCallback = api('xfqtrace_set_done_callback', 'void', ['pointer']);

    doneCallback = new NativeCallback(function () {
      log('trace done');
      send({ type: 'trace_done' });
    }, 'void', []);
    setDoneCallback(doneCallback);

    const json = buildTraceConfig(mod.base);
    log(CONFIG.target.so_name + ' @ ' + mod.base + (mod.path ? ' path=' + mod.path : ''));
    log('config: ' + json);

    let rc = configure(Memory.allocUtf8String(json));
    if (rc !== 0) {
      log('configure failed: ' + readCStringSafe(getLastError()));
      setDoneCallback(ptr(0));
      doneCallback = null;
      return;
    }

    rc = start();
    if (rc !== 0) {
      log('start failed: ' + readCStringSafe(getLastError()));
      try { stop(); } catch (_) {}
      setDoneCallback(ptr(0));
      doneCallback = null;
      return;
    }

    armed = true;
    detachLoadWatchers();
    log('trace armed! ' + CONFIG.target.so_name + '+' + CONFIG.target.offset);
    triggerDemo();
  } catch (e) {
    log('armTrace failed: ' + e.stack || e);
  } finally {
    arming = false;
  }
}

function watchOneDlopen(addr, name) {
  if (!addr) return;
  const listener = Interceptor.attach(addr, {
    onEnter(args) {
      this.hit = false;
      try {
        const path = readCStringSafe(args[0]);
        this.hit = path.indexOf(CONFIG.target.so_name) !== -1;
        if (this.hit) targetPathHint = path;
      } catch (_) {}
    },
    onLeave(retval) {
      if (this.hit && !ptrIsNull(retval)) {
        log('detected load by ' + name + ': ' + CONFIG.target.so_name);
        setTimeout(armTrace, 0);
      }
    }
  });
  listeners.push(listener);
  log('watch ' + name);
}

function main() {
  if (findTargetModule()) {
    log(CONFIG.target.so_name + ' already loaded');
    setTimeout(armTrace, 0);
  } else {
    watchOneDlopen(androidDlopenExtAddr, 'android_dlopen_ext');
    watchOneDlopen(dlopenAddr, 'dlopen');
    log('waiting for ' + CONFIG.target.so_name + ' ...');
  }
}

rpc.exports = {
  stop() {
    try {
      detachLoadWatchers();
      if (engineHandle) {
        try { api('xfqtrace_stop', 'void', [])(); } catch (_) {}
        try { api('xfqtrace_set_done_callback', 'void', ['pointer'])(ptr(0)); } catch (_) {}
      }
      doneCallback = null;
      log('xfqtrace stopped');
    } catch (e) {
      log('stop failed: ' + e);
    }
  }
};

main();
