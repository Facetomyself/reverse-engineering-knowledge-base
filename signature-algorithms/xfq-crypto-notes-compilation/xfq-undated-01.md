---
schema_version: 2
id: signature-algorithms-xfq-crypto-notes-compilation-xfq-undated-01
document_type: reference
scope:
  targets:
  - MT19937 pseudorandom generator implementation
  client: algorithm analysis
  version: source code listing; revision unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: 知识星球：逆向学习交流
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
modules:
- name: parameters
  anchor: mt19937-state-transition
  sources: [s1]
  basis: source-report
  limits: 本文代码仅来源自述；seed 输出未在本轮执行，也未与标准测试向量对照。
tags: [mt19937, prng, seed, tempering]
original_date: 未知
archived_date: '2026-09-04'
---

# mt19937伪随机.py

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: signature-algorithms
</details>
>
> class MT19937: def __init__(self, seed): self.mt = [0] 624 self.mt[0] = seed self.mti = 0 for i in range(1, 624): self.mt[i] = self._int32(1812433253 (self.mt[i 1] ^ self.mt[i 1] 30) + i) @staticmethod def _int32(x): ret

<a id="mt19937-state-transition"></a>
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

## 可复用提炼：MT19937 的状态转换分层

阅读或对照实现时可把代码拆成三段：624 项状态与 seed 扩展；`twist` 的偏移 397、最高位/低 31 位拼接及奇数条件常量；`extract_number` 的四步 tempering。这样能把状态转移和输出整形分开检查。

本文给出一个 seed 示例入口，但没有附运行输出或标准测试向量对照；因此仅是来源代码参考，不声明实现已通过 MT19937 一致性验证，也不把它与密码学安全随机数用途混淆。
