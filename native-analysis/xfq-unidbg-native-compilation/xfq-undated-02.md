# HashFinder.java

> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: native-analysis
>
> package base.plugin; import com.github.unidbg.Emulator; import com.github.unidbg.Module; import com.github.unidbg.arm.backend.Backend; import com.github.unidbg.arm.backend.WriteHook; import unicorn.Arm64Const; import uni

## 正文

package base.plugin;

import com.github.unidbg.Emulator;
import com.github.unidbg.Module;
import com.github.unidbg.arm.backend.Backend;
import com.github.unidbg.arm.backend.WriteHook;
import unicorn.Arm64Const;
import unicorn.ArmConst; // 必须导入这个

import java.util.*;

public class HashFinder {
    private final Emulator<?> emulator;
    private final Module module;
    private final Backend backend;

    private final Map<Long, Long> watchList = new LinkedHashMap<Long, Long>(100, 0.75f, true) {
        @Override protected boolean removeEldestEntry(Map.Entry<Long, Long> eldest) { return size() > 100; }
    };

    private final Map<Long, Integer> noiseAccount = new HashMap<>();
    private final Set<Long> blackList = new HashSet<>();
    private long lastLogAddr = -1;

    public HashFinder(Emulator<?> emulator, Module module) {
        this.emulator = emulator;
        this.module = module;
        this.backend = emulator.getBackend();
    }

    public void startSearch() {
        backend.hook_add_new(new WriteHook() {
            @Override
            public void hook(Backend backend, long address, int size, long value, Object user) {
                long pc = emulator.getContext().getPCPointer().peer;
                long lr = emulator.getContext().getLRPointer().peer;
                // 允许两种情况：
                // 1) 当前写入指令就在目标模块内
                // 2) 当前写入来自 libc memcpy/memset 等，但返回地址仍落在目标模块内
                if (!isInModule(pc) && !isInModule(lr)) return;

                if (containsByte(value, size, 0x80)) {
                    long preciseAddr = findByteAddr(address, value, size, 0x80);
                    if (!blackList.contains(preciseAddr)) {
                        watchList.put(preciseAddr, pc);
                    }
                }

                if (!watchList.isEmpty() && containsByte(value, size, 0x00)) {
                    for (long zeroAddr : findAllByteAddr(address, value, size, 0x00)) {
                        checkWatchList(zeroAddr);
                    }
                }
            }
            @Override public void onAttach(com.github.unidbg.arm.backend.UnHook unHook) {}
            @Override public void detach() {}
        }, 1, 0, null);
    }

    private void checkWatchList(long currentAddr) {
        watchList.entrySet().removeIf(entry -> {
            long padAddr = entry.getKey();
            if (currentAddr > padAddr && currentAddr < padAddr + 128) {
                return tryFinalReport(padAddr, entry.getValue());
            }
            return false;
        });
    }

    private boolean tryFinalReport(long padAddr, long pc) {
        try {
            byte[] tail = backend.mem_read(padAddr, 64);
            if ((tail[0] & 0xFF) != 0x80) return false;

            int zeroCount = 0;
            for (int i = 1; i < tail.length; i++) {
                if (tail[i] == 0) zeroCount++;
                else break;
            }

            if (zeroCount < 8) {
                int hits = noiseAccount.getOrDefault(padAddr, 0) + 1;
                noiseAccount.put(padAddr, hits);
                if (hits > 5) {
                    blackList.add(padAddr);
                }
                return false;
            }

            if (padAddr == lastLogAddr) return true;

            doDump(padAddr, pc, zeroCount);
            lastLogAddr = padAddr;
            return true;

        } catch (Exception ignored) {}
        return false;
    }

    private void doDump(long padAddr, long pc, int zeros) {

        System.out.println(String.format("\n\u001B[32m[★] HASH DETECTED | PC: %s | LR: %s | Zeros: %d\u001B[0m",
                emulator.getContext().getPCPointer().toString(), emulator.getContext().getLRPointer().toString(), zeros));
        // 保持 16 字节对齐
        long start = (padAddr - 32) & ~0xF;
        int totalLen = 128;

        try {
            byte[] data = backend.mem_read(start, totalLen);
            for (int i = 0; i < data.length; i += 16) {
                StringBuilder hex = new StringBuilder();
                StringBuilder ascii = new StringBuilder();

                for (int j = 0; j < 16; j++) {
                    int index = i + j;
                    if (index >= data.length) break;

                    long cur = start + index;
                    int b = data[index] & 0xFF;
                    char c = (b >= 32 && b <= 126) ? (char) b : '.';

                    // 判断是否属于 Padding 区域 (0x80 开始及其后的 zeros)
                    boolean isPadding = (cur >= padAddr && cur <= padAddr + zeros);

                    if (isPadding) {
                        // Hex 部分标红
                        hex.append(String.format("\u001B[31m%02x\u001B[0m ", b));
                        // ASCII 部分标红
                        ascii.append(String.format("\u001B[31m%c\u001B[0m", c));
                    } else {
                        hex.append(String.format("%02x ", b));
                        ascii.append(c);
                    }
                }
                // 格式化输出：地址 + Hex + ASCII
                System.out.println(String.format("0x%08x  %s |%s|", start + i, hex.toString(), ascii.toString()));
            }
        } catch (Exception e) {}
        System.out.println("------------------------------------------------------------------");
    }

    private boolean isInModule(long addr) {
        return addr >= module.base && addr < module.base + module.size;
    }

    private long findByteAddr(long baseAddr, long value, int size, int target) {
        for (int i = 0; i < size; i++) {
            if (((value >> (i * 8)) & 0xFF) == target) return baseAddr + i;
        }
        return baseAddr;
    }

    private List<Long> findAllByteAddr(long baseAddr, long value, int size, int target) {
        List<Long> addrs = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            if (((value >> (i * 8)) & 0xFF) == target) {
                addrs.add(baseAddr + i);
            }
        }
        return addrs;
    }

    private boolean containsByte(long value, int size, int target) {
        for (int i = 0; i < size; i++) {
            if (((value >> (i * 8)) & 0xFF) == target) return true;
        }
        return false;
    }
}
