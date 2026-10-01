---
schema_version: 2
id: native-analysis-xfq-unidbg-native-compilation-xfq-undated-03
document_type: archive
scope:
  targets:
  - unknown
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: 知识星球：逆向学习交流
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
tags: []
original_date: 未知
archived_date: '2026-09-04'
---

# rand-srand

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 知识星球：逆向学习交流
> 原始发布时间: 未知
> 归档日期: 2026-09-04
> 分类: native-analysis
</details>
>
> class CRand: """模拟Android bionic libc的rand()/srand() BSD TYPE_3 random""" DEG = 31 SEP = 3 def __init__(self, seed=0): self.srand(seed) def srand(self, seed): self._state = [0] self.DEG self._state[0] = seed & 0xffffffff

## 正文

class CRand:
    """模拟Android bionic libc的rand()/srand() - BSD TYPE_3 random"""
    DEG = 31
    SEP = 3

    def __init__(self, seed=0):
        self.srand(seed)

    def srand(self, seed):
        self._state = [0] * self.DEG
        self._state[0] = seed & 0xffffffff
        for i in range(1, self.DEG):
            self._state[i] = (16807 * self._state[i-1]) % 0x7fffffff
            if self._state[i] < 0:
                self._state[i] += 0x7fffffff
        self._fptr = self.SEP
        self._rptr = 0
        for _ in range(self.DEG * 10):
            self.rand()

    def rand(self):
        self._state[self._fptr] = (self._state[self._fptr] + self._state[self._rptr]) & 0xffffffff
        result = (self._state[self._fptr] >> 1) & 0x7fffffff
        self._fptr += 1
        self._rptr += 1
        if self._fptr >= self.DEG:
            self._fptr = 0
        if self._rptr >= self.DEG:
            self._rptr = 0
        return result
