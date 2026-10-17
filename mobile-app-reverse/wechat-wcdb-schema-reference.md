---
schema_version: 2
id: wechat-wcdb-schema-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [wechat-windows]
  client: windows
  version: "4.1"
  observed_at: unknown
sources:
  - id: s1
    ref: ./wechat-wcdb-schema.md#source-body
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只登记来源列出的库角色和关键表名。行数是一份本地库的计数。未打开数据库，未核对 4.1 之后是否改表。
relations:
  - type: derived_from
    target: ./wechat-wcdb-schema.md#source-body
  - type: supplements
    target: ./wechat-wcdb-cipher-reference.md#parameters
tags: [wechat, wcdb, schema]
---

# 微信 4.1 本地库各文件放什么

这张卡只回答：来源的 18 个已解密库里，消息、联系人、会话和朋友圈各在哪个文件。完整 `CREATE TABLE` 在 [来源归档](./wechat-wcdb-schema.md#source-body)。页加密不在本卡。

<a id="interfaces"></a>
## 库与关键表

来源目录是 `Documents\xwechat_files\<wxid>\db_storage`。18 个文件、合计 413 张表是那次清点的数字。

| 库 | 来源赋予的用途 | 检索时先看的表 |
|---|---|---|
| `message_0.db` | 聊天记录主体，按会话分表 | `Msg_<hash>` 同构表；`Name2Id` |
| `message_fts.db` | 消息全文索引 | FTS5 虚表 |
| `message_resource.db` | 消息关联资源 | `MessageResourceInfo`、`MessageResourceDetail` |
| `contact.db` | 联系人、群、群成员 | `contact`、`chat_room`、`chatroom_member` |
| `session.db` | 会话列表、未读、草稿 | `SessionTable`、`SessionDraft` |
| `sns.db` | 朋友圈 | `SnsTimeLine` |
| `biz_message_0.db` | 公众号/服务号消息 | `Msg_<hash>` |
| `media_0.db` | 媒体索引，来源点了语音 | `VoiceInfo` |
| `general.db` | 配置与杂项 | 来源在此库里还列了红包、转发等表 |

`Msg_*` 的列里同时有 `message_content`、`source` 和 `WCDB_CT_message_content`、`WCDB_CT_source`。压缩标记的含义在加密参考里，不在本卡解释成密钥。

`SessionTable` 以 `username` 为主键，并带 `unread_count`、`summary`、`draft`、`last_timestamp`。`SnsTimeLine` 的列是 `tid`、`user_name`、`content`、`pack_info_buf`。这些列名来自那份建表语句，不表示字段里有可公开的内容样本。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 聊天正文在 `message_0.db` 的按会话 `Msg_*` 表，不在 `session.db` | s1 清单和 message/session 节 | source-report | 该次 4.1 导出 | 行数不可外推 |
| C2 | 会话列表未读和草稿在 `session.db`，朋友圈时间线在 `sns.db` | s1 | source-report | 同上 | 未查询这些表 |
| C3 | 联系人和群成员在 `contact.db` | s1 contact 节 | source-report | 同上 | `extra_buffer` 未解析 |

## 验证与限制

没有 parameters 或 request-chain。FTS 分表、表情、收藏、硬链接和头像库的列定义留在归档，避免本卡变成第二份全量 schema。解密见 [页加密参考](./wechat-wcdb-cipher-reference.md#parameters)。
