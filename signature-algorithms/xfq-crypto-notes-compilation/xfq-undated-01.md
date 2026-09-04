# mt19937伪随机.py

> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: signature-algorithms
>
> class MT19937: def __init__(self, seed): self.mt = [0] 624 self.mt[0] = seed self.mti = 0 for i in range(1, 624): self.mt[i] = self._int32(1812433253 (self.mt[i 1] ^ self.mt[i 1] 30) + i) @staticmethod def _int32(x): ret

## 正文

class MT19937:
    def __init__(self, seed):
        self.mt = [0] * 624
        self.mt[0] = seed
        self.mti = 0
        for i in range(1, 624):
            self.mt[i] = self._int32(1812433253 * (self.mt[i - 1] ^ self.mt[i - 1] >> 30) + i)

    @staticmethod
    def _int32(x):
        return int(0xFFFFFFFF & x)

    def extract_number(self):
        if self.mti == 0:
            self.twist()
        y = self.mt[self.mti]
        y = y ^ y >> 11
        y = y ^ y << 7 & 2636928640
        y = y ^ y << 15 & 4022730752
        y = y ^ y >> 18
        self.mti = (self.mti + 1) % 624
        return  self._int32(y)

    def twist(self):
        for i in range(0, 624):
            y = self._int32((self.mt[i] & 0x80000000) + (self.mt[(i + 1) % 624] & 0x7fffffff))
            self.mt[i] = (y >> 1) ^ self.mt[(i + 397) % 624]

            if y % 2 != 0:
                self.mt[i] = self.mt[i] ^ 0x9908b0df

if __name__ == "__main__":
    seed = 0xF0000000
    mt19937_obj = MT19937(seed)
    for i in range(10):
        raw = mt19937_obj.extract_number()
        print(f"{i:02d}: raw32={raw:#010x}")
