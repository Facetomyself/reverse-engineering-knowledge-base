---
schema_version: 2
id: salsa20-state-quarter-round
document_type: reference
original_date: '2026-02-16'
archived_date: '2026-10-02'
scope:
  targets: [Salsa20]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20260216-01.md#1-状态矩阵初始化
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留矩阵位置、四分之一轮移位、双轮下标、feedforward 和变种识别句。ChaCha 的操作顺序不在本卡展开。
  - name: validation
    anchor: boundaries
    sources: [s1]
    basis: source-report
    limits: 与 pycryptodome 一致是作者自述。代码压缩包不在正文，本轮没有运行。
relations:
  - type: derived_from
    target: ./xfq-20260216-01.md#1-状态矩阵初始化
tags: [salsa20, arx, source-report]
---

# Salsa20 的状态矩阵与变种识别

这份参考卡回答：讲义里的 Salsa20 把常量、密钥、nonce 和计数器放在矩阵的哪些字上，四分之一轮的移位是多少，以及怎样从常量、计数器宽度和轮数看出非标准填法。它不是可运行实现，也不收录示例密钥。来源是 [Salsa20 流密码实现讲义](./xfq-20260216-01.md#1-状态矩阵初始化)。

<a id="parameters"></a>
## 参数

参数表把状态大小写成 `64 字节 (16个32位字)`，Salsa20 一列的密钥长度是 `32 字节固定`。标准填法在后文写成 `8字节 Nonce + 8字节 Counter`。Key Setup 被概括成 `把原料摆进矩阵`，核心是 `20 轮 ARX`。

矩阵是 `4×4 的 32 位字矩阵`。对角常量是 `"expand 32-byte k"`，位置 `[0,5,10,15]`。代码 `SIGMA = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]`，再 `x[0], x[5], x[10], x[15] = SIGMA`。计数器占 `x[8]` 与 `x[9]`，nonce 占 `x[6]` 与 `x[7]`，都按小端 `struct.unpack('<I', ...)` 读入。

四分之一轮的移位依次是 7、9、13、18：

- `x[b] ^= self._rotl((x[a] + x[d]) & 0xFFFFFFFF, 7)`
- `x[c] ^= self._rotl((x[b] + x[a]) & 0xFFFFFFFF, 9)`
- `x[d] ^= self._rotl((x[c] + x[b]) & 0xFFFFFFFF, 13)`
- `x[a] ^= self._rotl((x[d] + x[c]) & 0xFFFFFFFF, 18)`

外层 `for round_num in range(10)`。列轮第 0 列是 `(0, 4, 8, 12)`，第 1 列是 `(5, 9, 13, 1)`。行轮第 0 行是 `(0, 1, 2, 3)`，第 1 行是 `(5, 6, 7, 4)`。搅拌后 `x[i] = (x[i] + initial[i]) & 0xFFFFFFFF`。作者解释 `如果不加,攻击者知道输出后可以反推回初始状态`。输出 `按小端序展开成 64 字节`。下一块是 `counter+1`。

变种识别集中在矩阵填法。`如果 Counter 只有 1 个字(32位),那大概率是改了 Nonce 长度`。16 字节密钥改用 `"expand 16-byte k"`。常量被改时，`搜索 0x61707865 (expa),如果找不到但看到类似的代码结构`。轮数上单列了 `Salsa20/8 (8轮)` 和 `Salsa20/12 (12轮)`。移位魔改写的是 `修改移位量(7/9/13/18)`。

<a id="boundaries"></a>
## 验证与限制

测试段写 `标准库验证: ✅ 与 pycryptodome 一致`，并给出 `密文(hex):          cbd147c16cc65e1b`。这是作者的对照结论。`代码文件和md都在星球文章的压缩包内`，压缩包不在正文。中间轮的矩阵也只是讲义贴出的过程值。ChaCha 只写到 `具体细节见下一篇 ChaCha20 文档`，本卡不展开那一篇的对角轮。示例密钥不进入本卡。本轮没有运行这段 Python。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 状态 `64 字节 (16个32位字)`，密钥格为 `32 字节固定`，标准是 `8字节 Nonce + 8字节 Counter`。 | s1 第 72、75、311 行 | source-report | 讲义参数表和后文标准句 | 表被拆成逐行，第 74 行是另一列的 `1-256 字节` |
| C2 | 常量 `"expand 32-byte k"` 在 `[0,5,10,15]`，`SIGMA` 以 `0x61707865` 开头。 | s1 第 125、132、133 行 | source-report | 32 字节密钥的矩阵 | 16 字节常量是另一句 |
| C3 | 计数器是 `x[8]` 与 `x[9]`，nonce 是 `x[6]` 与 `x[7]`。 | s1 第 136–136 行 | source-report | 标准 8+8 填法 | 未重排其他变种 |
| C4 | 四分之一轮移位写在 `, 7`、`, 9`、`, 13`、`, 18` 四行，外层 `range(10)`。第 1 列是 `5, 9, 13, 1`。 | s1 第 174-177、187、190 行 | source-report | 20 轮里的列轮 | 未重算轮中矩阵 |
| C5 | 结束后 `x[i] = (x[i] + initial[i]) & 0xFFFFFFFF`，再 `按小端序展开成 64 字节`，然后 `counter+1`。 | s1 第 229、242、273 行 | source-report | 一块密钥流 | 示例密钥不入卡 |
| C6 | `Counter 只有 1 个字(32位)` 时多半改了 nonce。16 字节密钥用 `"expand 16-byte k"`。找不到 `0x61707865` 时可能改了常量。 | s1 第 314、316、324 行 | source-report | 讲义中的识别句 | 不是闭合的判定流程 |
| C7 | 作者写 `与 pycryptodome 一致`，密文为 `cbd147c16cc65e1b`。代码则是 `代码文件和md都在星球文章的压缩包内`。 | s1 第 39、113、270 行 | source-report | 作者贴出的 8 字节结果 | 压缩包不在正文，本轮未运行 |
