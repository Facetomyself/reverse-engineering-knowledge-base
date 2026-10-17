---
schema_version: 2
id: wechat-wcdb-schema
document_type: archive
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [wechat-windows]
  client: windows
  version: "4.1"
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: "微信 4.1 本地数据库结构参考"
    reason: "原始材料未提供作者名或可公开定位的链接"

source_completeness: complete
relations: []
tags: [wechat, wcdb, sqlite, schema]
---

# 微信 4.1 本地数据库结构参考

来源列出一份已解密本地目录里的 18 个库和建表语句。行数是那一份数据的计数，不是版本常量。

## 清洗与完整性说明

SQL 和行数按原文保留。没有消息正文、wxid 或密钥。无图。

<a id="source-body"></a>
## 来源正文

共 18 个已解密数据库，数据目录 `Documents\xwechat_files\<wxid>\db_storage`。

## 一、数据库清单

| 数据库 | 大小 | 表 | 视图 | 索引 | 用途 |
|---|---:|---:|---:|---:|---|
| `biz_message_0.db` | 9MB | 108 | 0 | 420 | 公众号/服务号消息 |
| `bizchat.db` | 28KB | 4 | 0 | 0 | 企业微信会话 |
| `chatbot_message.db` | 76KB | 3 | 0 | 14 | AI 助手会话消息 |
| `contact.db` | 6MB | 15 | 0 | 4 | 联系人、群、群成员 |
| `contact_fts.db` | 3MB | 37 | 0 | 3 | 联系人全文索引 |
| `emoticon.db` | 2MB | 7 | 0 | 9 | 表情包 |
| `favorite.db` | 256KB | 6 | 0 | 15 | 收藏内容 |
| `favorite_fts.db` | 84KB | 7 | 0 | 0 | 收藏全文索引 |
| `general.db` | 7MB | 22 | 0 | 21 | 通用配置与杂项 |
| `hardlink.db` | 768KB | 8 | 0 | 10 | 文件硬链接映射 |
| `head_image.db` | 4MB | 1 | 0 | 0 | 头像缓存索引 |
| `media_0.db` | 1MB | 3 | 0 | 2 | 媒体文件索引（语音等） |
| `message_0.db` | 53MB | 106 | 0 | 409 | 聊天记录主体（按会话分表） |
| `message_fts.db` | 13MB | 60 | 0 | 0 | 消息全文索引（FTS5） |
| `message_resource.db` | 6MB | 6 | 0 | 13 | 消息关联资源（文件、引用等） |
| `session.db` | 120KB | 7 | 0 | 4 | 会话列表、未读、草稿 |
| `sns.db` | 684KB | 12 | 0 | 9 | 朋友圈 |
| `third_app_icon.db` | 12KB | 1 | 0 | 0 |  |

合计 413 张表。

## 二、表结构

### `biz_message_0.db`

**105 张同构表** — `Msg_022a80769c993e88d17a970755c7978b`, `Msg_02e7e31a0ad7f6c543de537a71328325`, `Msg_03bbbc131de7fa2f8b53f67eff5abc89` …

其中 `Msg_022a80769c993e88d17a970755c7978b` — 29 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, server_id INTEGER, local_type INTEGER, sort_seq INTEGER, real_sender_id INTEGER, create_time INTEGER, status INTEGER, upload_status INTEGER, download_status INTEGER, server_seq INTEGER, origin_source INTEGER, source TEXT, message_content TEXT, compress_content TEXT, packed_info_data BLOB, WCDB_CT_message_content INTEGER DEFAULT NULL, WCDB_CT_source INTEGER DEFAULT NULL)
```

**`Name2Id`** — 121 行

```sql
CREATE TABLE <name>(user_name TEXT PRIMARY KEY, is_session INTEGER)
```

**`TimeStamp`** — 1 行

```sql
CREATE TABLE <name>(timestamp INTEGER)
```

**`wcdb_builtin_compression_record`** — 0 行

```sql
CREATE TABLE <name>(tableName TEXT PRIMARY KEY, columns TEXT NOT NULL, rowid INTEGER) WITHOUT ROWID
```

### `bizchat.db`

**`chat_group`** — 1 行

```sql
CREATE TABLE <name>(id INTEGER PRIMARY KEY, group_id TEXT, brand_user_name TEXT, type INTEGER, version INTEGER, bit_flag INTEGER, max_member_count INTEGER, chat_name TEXT, owner_id TEXT, head_img_url TEXT, user_list TEXT, add_member_url TEXT, reserved0 INTEGER, reserved1 INTEGER, reserved2 TEXT, reserved3 TEXT)
```

**`my_user_info`** — 1 行

```sql
CREATE TABLE <name>(brand_user_name TEXT PRIMARY KEY, user_id TEXT)
```

**`name2id`** — 3 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY)
```

**`user_info`** — 2 行

```sql
CREATE TABLE <name>(id INTEGER PRIMARY KEY, user_id TEXT, brand_user_name TEXT, user_name TEXT, version INTEGER, bit_flag INTEGER, head_img_url TEXT, profile_url TEXT, add_member_url TEXT, reserved0 INTEGER, reserved1 INTEGER, reserved2 TEXT, reserved3 TEXT)
```

### `chatbot_message.db`

**`chatbot_message`** — 0 行

```sql
CREATE TABLE <name>(svrid INTEGER, create_time INTEGER, dialogue_id INTEGER, ui_state_id INTEGER DEFAULT 0, app_ui_state INTEGER DEFAULT 0, direction INTEGER DEFAULT 0, type INTEGER DEFAULT 0, trace_msgid TEXT, card_wraplist_buffer BLOB, extra_info_buffer BLOB, bypass_info_buffer BLOB)
```

**`chatbot_message_v1`** — 0 行

```sql
CREATE TABLE <name>(svrid INTEGER, create_time INTEGER, dialogue_id INTEGER, qa_seq INTEGER, ui_state_id INTEGER DEFAULT 0, app_ui_state INTEGER DEFAULT 0, direction INTEGER DEFAULT 0, type INTEGER DEFAULT 0, db_sync_seq INTEGER, trace_msgid TEXT, card_wraplist_buffer BLOB, extra_info_buffer BLOB, bypass_info_buffer BLOB)
```

**`chatbot_session`** — 0 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY, source_type INTEGER DEFAULT 0, open_scene INTEGER DEFAULT 0, timestamp INTEGER, tagid INTEGER DEFAULT 0, title TEXT, extra_info BLOB)
```

### `contact.db`

**`biz_info`** — 226 行

```sql
CREATE TABLE <name>(id INTEGER PRIMARY KEY, username TEXT, type INTEGER, accept_type INTEGER, child_type INTEGER, home_url TEXT, version INTEGER, sync_version TEXT, external_info TEXT, brand_info TEXT, brand_icon_url TEXT, brand_list TEXT, brand_flag INTEGER, belong TEXT, ext_buffer BLOB)
```

**`chat_room`** — 50 行

```sql
CREATE TABLE <name>(id INTEGER PRIMARY KEY, username TEXT, owner TEXT, ext_buffer BLOB)
```

**`chat_room_info_detail`** — 50 行

```sql
CREATE TABLE <name>(room_id_ INTEGER PRIMARY KEY, username_ TEXT, announcement_ TEXT, announcement_editor_ TEXT, announcement_publish_time_ INTEGER, chat_room_status_ INTEGER, xml_announcement_ TEXT, ext_buffer_ BLOB)
```

**`chatroom_member`** — 8,801 行

```sql
CREATE TABLE <name>(room_id INTEGER, member_id INTEGER, CONSTRAINT room_member UNIQUE(room_id, member_id))
```

**2 张同构表** — `contact`, `stranger`

其中 `contact` — 9,055 行

```sql
CREATE TABLE <name>(id INTEGER PRIMARY KEY, username TEXT, local_type INTEGER, alias TEXT, encrypt_username TEXT, flag INTEGER, delete_flag INTEGER, verify_flag INTEGER, remark TEXT, remark_quan_pin TEXT, remark_pin_yin_initial TEXT, nick_name TEXT, pin_yin_initial TEXT, quan_pin TEXT, big_head_url TEXT, small_head_url TEXT, head_img_md5 TEXT, chat_room_notify INTEGER, is_in_chat_room INTEGER, description TEXT, extra_buffer BLOB, chat_room_type INTEGER)
```

**`contact_label`** — 20 行

```sql
CREATE TABLE <name>(label_id_ INTEGER PRIMARY KEY, label_name_ TEXT, sort_order_ INTEGER)
```

**2 张同构表** — `encrypt_name2id`, `name2id`

其中 `encrypt_name2id` — 0 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY)
```

**`openim_acct_type`** — 1 行

```sql
CREATE TABLE <name>(lang_id INTEGER, acc_type_id TEXT, update_time INTEGER, ext_buffer BLOB, CONSTRAINT accTypeId_langId PRIMARY KEY(acc_type_id, lang_id))
```

**`openim_appid`** — 1 行

```sql
CREATE TABLE <name>(lang_id INTEGER, app_id TEXT, acct_type_id TEXT, update_time INTEGER, ext_buffer BLOB, CONSTRAINT appId_langId PRIMARY KEY(app_id, lang_id))
```

**`openim_wording`** — 28 行

```sql
CREATE TABLE <name>(lang_id INTEGER, app_id TEXT, wording_id TEXT, wording TEXT, pinyin TEXT, quan_pin TEXT, update_time INTEGER, ext_buffer BLOB, CONSTRAINT appId_langId_wordingId PRIMARY KEY(app_id, lang_id, wording_id))
```

**`oplog`** — 0 行

```sql
CREATE TABLE <name>(id INTEGER PRIMARY KEY ASC AUTOINCREMENT, buffer BLOB)
```

**2 张同构表** — `stranger_ticket_info`, `ticket_info`

其中 `stranger_ticket_info` — 0 行

```sql
CREATE TABLE <name>(id INTEGER PRIMARY KEY, ticket TEXT)
```

### `contact_fts.db`

**`chatroom_member_fts_v3`** — 8,801 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin enable_special_char', a_group_remark, room_id UNINDEXED, member_id UNINDEXED)
```

**`chatroom_member_fts_v3_aux`** — 8,801 行

```sql
CREATE TABLE <name>(room_id INTEGER, member_id INTEGER, CONSTRAINT room_member UNIQUE(room_id, member_id))
```

**`chatroom_member_fts_v3_config`** — 1 行

```sql
CREATE TABLE 'chatroom_member_fts_v3_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`chatroom_member_fts_v3_content`** — 8,801 行

```sql
CREATE TABLE 'chatroom_member_fts_v3_content'(id INTEGER PRIMARY KEY, c0, c1, c2)
```

**`chatroom_member_fts_v3_data`** — 31 行

```sql
CREATE TABLE 'chatroom_member_fts_v3_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`chatroom_member_fts_v3_docsize`** — 8,801 行

```sql
CREATE TABLE 'chatroom_member_fts_v3_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`chatroom_member_fts_v3_idx`** — 29 行

```sql
CREATE TABLE 'chatroom_member_fts_v3_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`contact_fts_pinyin_v5`** — 9,034 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_origin', content='contact_fts_v5', search_key, local_type UNINDEXED)
```

**`contact_fts_pinyin_v5_config`** — 1 行

```sql
CREATE TABLE 'contact_fts_pinyin_v5_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`contact_fts_pinyin_v5_data`** — 86 行

```sql
CREATE TABLE 'contact_fts_pinyin_v5_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`contact_fts_pinyin_v5_docsize`** — 9,034 行

```sql
CREATE TABLE 'contact_fts_pinyin_v5_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`contact_fts_pinyin_v5_idx`** — 66 行

```sql
CREATE TABLE 'contact_fts_pinyin_v5_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`contact_fts_v5`** — 9,034 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin enable_special_char enable_num_token', search_key, local_type UNINDEXED)
```

**`contact_fts_v5_config`** — 1 行

```sql
CREATE TABLE 'contact_fts_v5_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`contact_fts_v5_content`** — 9,034 行

```sql
CREATE TABLE 'contact_fts_v5_content'(id INTEGER PRIMARY KEY, c0, c1)
```

**`contact_fts_v5_data`** — 80 行

```sql
CREATE TABLE 'contact_fts_v5_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`contact_fts_v5_docsize`** — 9,034 行

```sql
CREATE TABLE 'contact_fts_v5_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`contact_fts_v5_idx`** — 61 行

```sql
CREATE TABLE 'contact_fts_v5_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`db_info`** — 4 行

```sql
CREATE TABLE <name>(Key TEXT PRIMARY KEY, ValueInt64 INTEGER, ValueDouble REAL, ValueStdStr TEXT, ValueBlob BLOB)
```

**`name2id`** — 10,663 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY)
```

**`search_dict_fts_v1`** — 6 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin enable_special_char', content='search_dict_v1', content, update_time UNINDEXED, click_type UNINDEXED)
```

**`search_dict_fts_v1_config`** — 1 行

```sql
CREATE TABLE 'search_dict_fts_v1_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`search_dict_fts_v1_data`** — 8 行

```sql
CREATE TABLE 'search_dict_fts_v1_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`search_dict_fts_v1_docsize`** — 6 行

```sql
CREATE TABLE 'search_dict_fts_v1_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`search_dict_fts_v1_idx`** — 6 行

```sql
CREATE TABLE 'search_dict_fts_v1_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`search_dict_v1`** — 6 行

```sql
CREATE TABLE <name>(content TEXT PRIMARY KEY, update_time INTEGER, click_type INTEGER)
```

**`wa_contact_fts_pinyin_v1`** — 1,628 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_origin enable_special_char', content='wa_contact_fts_v1', search_key, time UNINDEXED)
```

**`wa_contact_fts_pinyin_v1_config`** — 1 行

```sql
CREATE TABLE 'wa_contact_fts_pinyin_v1_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`wa_contact_fts_pinyin_v1_data`** — 24 行

```sql
CREATE TABLE 'wa_contact_fts_pinyin_v1_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`wa_contact_fts_pinyin_v1_docsize`** — 1,628 行

```sql
CREATE TABLE 'wa_contact_fts_pinyin_v1_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`wa_contact_fts_pinyin_v1_idx`** — 22 行

```sql
CREATE TABLE 'wa_contact_fts_pinyin_v1_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`wa_contact_fts_v1`** — 1,628 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin enable_special_char', search_key, time UNINDEXED)
```

**`wa_contact_fts_v1_config`** — 1 行

```sql
CREATE TABLE 'wa_contact_fts_v1_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`wa_contact_fts_v1_content`** — 1,628 行

```sql
CREATE TABLE 'wa_contact_fts_v1_content'(id INTEGER PRIMARY KEY, c0, c1)
```

**`wa_contact_fts_v1_data`** — 17 行

```sql
CREATE TABLE 'wa_contact_fts_v1_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`wa_contact_fts_v1_docsize`** — 1,628 行

```sql
CREATE TABLE 'wa_contact_fts_v1_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`wa_contact_fts_v1_idx`** — 15 行

```sql
CREATE TABLE 'wa_contact_fts_v1_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

### `emoticon.db`

**2 张同构表** — `kCustomEmoticonOrderTable`, `kFavEmoticonOrderTable`

其中 `kCustomEmoticonOrderTable` — 0 行

```sql
CREATE TABLE <name>(md5 TEXT)
```

**`kExpressRecentUseEemoticonTable`** — 1 行

```sql
CREATE TABLE <name>(Key TEXT PRIMARY KEY, ValueInt64 INTEGER, ValueDouble REAL, ValueStdStr TEXT, ValueBlob BLOB)
```

**`kNonStoreEmoticonTable`** — 831 行

```sql
CREATE TABLE <name>(type INTEGER, md5 TEXT, caption TEXT, product_id TEXT, aes_key TEXT, thumb_url TEXT, tp_url TEXT, auth_key TEXT, cdn_url TEXT, extern_url TEXT, extern_md5 TEXT, encrypt_url TEXT, designer_id TEXT, activity_id TEXT)
```

**`kStoreEmoticonCaptionsTable`** — 1,088 行

```sql
CREATE TABLE <name>(package_id_ TEXT, md5_ TEXT, language_ TEXT, caption_ TEXT)
```

**`kStoreEmoticonFilesTable`** — 152 行

```sql
CREATE TABLE <name>(package_id_ TEXT, md5_ TEXT, type_ INTEGER, sort_order_ INTEGER, emoticon_size_ INTEGER, emoticon_offset_ INTEGER, thumb_size_ INTEGER, thumb_offset_ INTEGER)
```

**`kStoreEmoticonPackageTable`** — 13 行

```sql
CREATE TABLE <name>(package_id_ TEXT, package_name_ TEXT, payment_status_ INTEGER, download_status_ INTEGER, install_time_ INTEGER, remove_time_ INTEGER, sort_order_ INTEGER, introduction_ TEXT, full_description_ TEXT, copyright_ TEXT, author_ TEXT, store_icon_url_ TEXT, panel_url_ TEXT)
```

### `favorite.db`

**`Name2Id`** — 57 行

```sql
CREATE TABLE <name>(user_name TEXT PRIMARY KEY)
```

**2 张同构表** — `buff`, `config`

其中 `buff` — 0 行

```sql
CREATE TABLE <name>(Key TEXT PRIMARY KEY, ValueInt64 INTEGER, ValueDouble REAL, ValueStdStr TEXT, ValueBlob BLOB)
```

**`fav_bind_tag_db_item`** — 3 行

```sql
CREATE TABLE <name>(tag_local_id INTEGER, tag_server_id INTEGER, fav_local_id INTEGER, fav_server_id INTEGER, op_code INTEGER, CONSTRAINT _TAGLOCALID_FAVLOCALID UNIQUE(tag_local_id, fav_local_id))
```

**`fav_db_item`** — 125 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, server_id INTEGER, type INTEGER, update_seq INTEGER, flag INTEGER, update_time INTEGER, version INTEGER, content TEXT, source_id TEXT, sync_status INTEGER, upload_status INTEGER, upload_error_code INTEGER, trans_res_status INTEGER, trans_res_error_code INTEGER, fromusr TEXT, fromusr_id INTEGER, realchatname TEXT, realchatname_id INTEGER, ext_buf TEXT)
```

**`fav_tag_db_item`** — 3 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, server_id INTEGER, name TEXT, seq INTEGER)
```

### `favorite_fts.db`

**`fav_fts_v1`** — 101 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin', content, local_id UNINDEXED, update_time UNINDEXED, type UNINDEXED)
```

**`fav_fts_v1_config`** — 1 行

```sql
CREATE TABLE 'fav_fts_v1_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`fav_fts_v1_content`** — 101 行

```sql
CREATE TABLE 'fav_fts_v1_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3)
```

**`fav_fts_v1_data`** — 15 行

```sql
CREATE TABLE 'fav_fts_v1_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`fav_fts_v1_docsize`** — 101 行

```sql
CREATE TABLE 'fav_fts_v1_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`fav_fts_v1_idx`** — 13 行

```sql
CREATE TABLE 'fav_fts_v1_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`table_info`** — 4 行

```sql
CREATE TABLE <name>(Key TEXT PRIMARY KEY, ValueInt64 INTEGER, ValueDouble REAL, ValueStdStr TEXT, ValueBlob BLOB)
```

### `general.db`

**`FMessageTable`** — 8 行

```sql
CREATE TABLE <name>(user_name_ TEXT, type_ INTEGER, timestamp_ INTEGER, encrypt_user_name_ TEXT, content_ TEXT, is_sender_ INTEGER, ticket_ TEXT, scene_ INTEGER, fmessage_detail_buf_ TEXT, remark_ TEXT, label_ids_ TEXT)
```

**`ForwardRecent`** — 1 行

```sql
CREATE TABLE <name>(username TEXT, forward_time INTEGER)
```

**`SearchRecent`** — 2 行

```sql
CREATE TABLE <name>(username TEXT, query TEXT, score INTEGER, last_click_time INTEGER, CONSTRAINT _query_username UNIQUE(query, username))
```

**`WeAppBizAttrSyncBufferTableV02`** — 1,648 行

```sql
CREATE TABLE <name>(user_name TEXT PRIMARY KEY, last_update_time INTEGER, version TEXT)
```

**`biz_pay_status`** — 0 行

```sql
CREATE TABLE <name>(url_id TEXT, is_charge_appmsg INTEGER, is_paid INTEGER, friend_pay_count_str TEXT)
```

**`biz_subscribe_status`** — 22 行

```sql
CREATE TABLE <name>(biz_username TEXT, template_id TEXT, is_subscribe INTEGER)
```

**2 张同构表** — `brand_search_record`, `websearch_record`

其中 `brand_search_record` — 0 行

```sql
CREATE TABLE <name>(keyword TEXT PRIMARY KEY, pay_load_ TEXT, create_time INTEGER)
```

**`groupPayTable`** — 0 行

```sql
CREATE TABLE <name>(bill_no TEXT PRIMARY KEY, session_name TEXT, message_local_id INTEGER, message_create_time INTEGER)
```

**`handoff_remind_v0`** — 0 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, item_id TEXT, head_icon TEXT, title TEXT, desc_type TEXT, create_time INTEGER, start_time INTEGER, expire_time INTEGER, biz_type INTEGER, version INTEGER, url TEXT, extra_info TEXT)
```

**`ilink_voip`** — 0 行

```sql
CREATE TABLE <name>(wx_chatroom_ TEXT PRIMARY KEY, millsecond_ INTEGER, group_id_ TEXT, room_id_ INTEGER, room_key_ INTEGER, route_id_ INTEGER, voice_status_ INTEGER, talker_create_user_ TEXT, not_friend_user_list_ TEXT, members_ TEXT, is_ilink_ INTEGER, ever_quit_chatroom_ INTEGER)
```

**`redEnvelopeTable`** — 19 行

```sql
CREATE TABLE <name>(message_server_id INTEGER PRIMARY KEY, session_name TEXT, sender_user_name TEXT, native_url TEXT, send_id TEXT, scene_id INTEGER, hb_status INTEGER, hb_type INTEGER, receive_status INTEGER)
```

**2 张同构表** — `reddot`, `reddot_last_notify`

其中 `reddot` — 0 行

```sql
CREATE TABLE <name>(tips_uuid TEXT PRIMARY KEY, tips_content TEXT)
```

**`reddot_record`** — 2 行

```sql
CREATE TABLE <name>(business_type INTEGER PRIMARY KEY, record_content TEXT)
```

**`revokebatchmessage`** — 2 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id INTEGER, msg_unique_id TEXT, session_name TEXT, msg_local_id INTEGER, msg_create_time INTEGER)
```

**`revokemessage`** — 0 行

```sql
CREATE TABLE <name>(to_user_name TEXT, svr_id INTEGER, message_type INTEGER, revoke_time INTEGER, content TEXT, at_user_list TEXT)
```

**`teenager_apply_access_agree_info`** — 0 行

```sql
CREATE TABLE <name>(access_content_key TEXT PRIMARY KEY, access_content_type INTEGER, agree_time INTEGER)
```

**`transferTable`** — 60 行

```sql
CREATE TABLE <name>(transfer_id TEXT PRIMARY KEY, transcation_id TEXT, message_server_id INTEGER, second_message_server_id INTEGER, session_name TEXT, pay_sub_type INTEGER, pay_receiver TEXT, pay_payer TEXT, begin_transfer_time INTEGER, last_modified_time INTEGER, invalid_time INTEGER, last_update_time INTEGER, delay_confirm_flag INTEGER, bubble_clicked_flag INTEGER)
```

**`wacontact`** — 1,648 行

```sql
CREATE TABLE <name>(user_name TEXT PRIMARY KEY, type INTEGER, brand_icon_url TEXT, external_info TEXT, contact_pack_data BLOB, wx_app_opt INTEGER, head_image_status TEXT, app_id TEXT)
```

**`wcfinderlivestatus`** — 2 行

```sql
CREATE TABLE <name>(finder_live_id INTEGER, finder_username TEXT, finder_export_id TEXT, live_status INTEGER, replay_status INTEGER, charge_flag INTEGER)
```

**`wcfinderuserpage`** — 5 行

```sql
CREATE TABLE <name>(username TEXT, extra_buffer BLOB)
```

### `hardlink.db`

**`db_info`** — 4 行

```sql
CREATE TABLE <name>(Key TEXT PRIMARY KEY, ValueInt64 INTEGER, ValueDouble REAL, ValueStdStr TEXT, ValueBlob BLOB)
```

**`dir2id`** — 59 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY)
```

**2 张同构表** — `file_checkpoint_v4`, `video_checkpoint_v4`

其中 `file_checkpoint_v4` — 0 行

```sql
CREATE TABLE <name>(month_id INTEGER PRIMARY KEY ASC)
```

**3 张同构表** — `file_hardlink_info_v4`, `image_hardlink_info_v4`, `video_hardlink_info_v4`

其中 `file_hardlink_info_v4` — 185 行

```sql
CREATE TABLE <name>(md5_hash INTEGER, md5 TEXT, type INTEGER, file_name TEXT, file_size INTEGER, modify_time INTEGER, dir1 INTEGER, dir2 INTEGER, _rowid_ INTEGER PRIMARY KEY ASC, extra_buffer BLOB)
```

**`talker_checkpoint_v4`** — 4 行

```sql
CREATE TABLE <name>(talker_id INTEGER PRIMARY KEY ASC, month_id INTEGER)
```

### `head_image.db`

**`head_image`** — 686 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY, md5 TEXT, image_buffer BLOB, update_time INTEGER)
```

### `media_0.db`

**`Name2Id`** — 12 行

```sql
CREATE TABLE <name>(user_name TEXT PRIMARY KEY)
```

**`TimeStamp`** — 1 行

```sql
CREATE TABLE <name>(timestamp INTEGER)
```

**`VoiceInfo`** — 89 行

```sql
CREATE TABLE <name>(chat_name_id INTEGER, create_time INTEGER, local_id INTEGER, svr_id INTEGER, voice_data BLOB, data_index TEXT DEFAULT '0')
```

### `message_0.db`

**`MessageGroupTimeInfo`** — 0 行

```sql
CREATE TABLE <name>(chatname_id INTEGER, group_id TEXT, create_time INTEGER, initial_sort_seq INTEGER, birth_time INTEGER)
```

**102 张同构表** — `Msg_03459dfa2954c640212e0840cf941d30`, `Msg_05e0c6ef76411344a5d8a9f7c8d47781`, `Msg_06ac27d100260b35e44d0b8245087f89` …

其中 `Msg_03459dfa2954c640212e0840cf941d30` — 0 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, server_id INTEGER, local_type INTEGER, sort_seq INTEGER, real_sender_id INTEGER, create_time INTEGER, status INTEGER, upload_status INTEGER, download_status INTEGER, server_seq INTEGER, origin_source INTEGER, source TEXT, message_content TEXT, compress_content TEXT, packed_info_data BLOB, WCDB_CT_message_content INTEGER DEFAULT NULL, WCDB_CT_source INTEGER DEFAULT NULL)
```

**`Name2Id`** — 1,408 行

```sql
CREATE TABLE <name>(user_name TEXT PRIMARY KEY, is_session INTEGER)
```

**`TimeStamp`** — 1 行

```sql
CREATE TABLE <name>(timestamp INTEGER)
```

**`wcdb_builtin_compression_record`** — 0 行

```sql
CREATE TABLE <name>(tableName TEXT PRIMARY KEY, columns TEXT NOT NULL, rowid INTEGER) WITHOUT ROWID
```

### `message_fts.db`

**`ImgFts0V0`** — 0 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin', content='ImgFtsAux0V0', acontent, message_local_id UNINDEXED, sort_seq UNINDEXED, local_type UNINDEXED, session_id UNINDEXED, sender_id UNINDEXED, create_time UNINDEXED)
```

**`ImgFts0V0_config`** — 1 行

```sql
CREATE TABLE 'ImgFts0V0_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`ImgFts0V0_data`** — 2 行

```sql
CREATE TABLE 'ImgFts0V0_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`ImgFts0V0_docsize`** — 0 行

```sql
CREATE TABLE 'ImgFts0V0_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`ImgFts0V0_idx`** — 0 行

```sql
CREATE TABLE 'ImgFts0V0_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`ImgFts1V0`** — 0 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin', content='ImgFtsAux1V0', acontent, message_local_id UNINDEXED, sort_seq UNINDEXED, local_type UNINDEXED, session_id UNINDEXED, sender_id UNINDEXED, create_time UNINDEXED)
```

**`ImgFts1V0_config`** — 1 行

```sql
CREATE TABLE 'ImgFts1V0_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`ImgFts1V0_data`** — 2 行

```sql
CREATE TABLE 'ImgFts1V0_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`ImgFts1V0_docsize`** — 0 行

```sql
CREATE TABLE 'ImgFts1V0_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`ImgFts1V0_idx`** — 0 行

```sql
CREATE TABLE 'ImgFts1V0_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`ImgFts2V0`** — 0 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin', content='ImgFtsAux2V0', acontent, message_local_id UNINDEXED, sort_seq UNINDEXED, local_type UNINDEXED, session_id UNINDEXED, sender_id UNINDEXED, create_time UNINDEXED)
```

**`ImgFts2V0_config`** — 1 行

```sql
CREATE TABLE 'ImgFts2V0_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`ImgFts2V0_data`** — 2 行

```sql
CREATE TABLE 'ImgFts2V0_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`ImgFts2V0_docsize`** — 0 行

```sql
CREATE TABLE 'ImgFts2V0_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`ImgFts2V0_idx`** — 0 行

```sql
CREATE TABLE 'ImgFts2V0_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`ImgFts3V0`** — 0 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin', content='ImgFtsAux3V0', acontent, message_local_id UNINDEXED, sort_seq UNINDEXED, local_type UNINDEXED, session_id UNINDEXED, sender_id UNINDEXED, create_time UNINDEXED)
```

**`ImgFts3V0_config`** — 1 行

```sql
CREATE TABLE 'ImgFts3V0_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`ImgFts3V0_data`** — 2 行

```sql
CREATE TABLE 'ImgFts3V0_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`ImgFts3V0_docsize`** — 0 行

```sql
CREATE TABLE 'ImgFts3V0_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`ImgFts3V0_idx`** — 0 行

```sql
CREATE TABLE 'ImgFts3V0_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**4 张同构表** — `ImgFtsAux0V0`, `ImgFtsAux1V0`, `ImgFtsAux2V0` …

其中 `ImgFtsAux0V0` — 0 行

```sql
CREATE TABLE <name>(acontent TEXT, message_local_id INTEGER, sort_seq INTEGER, local_type INTEGER, session_id INTEGER, sender_id INTEGER, create_time INTEGER, CONSTRAINT sessionId_localId_createtime PRIMARY KEY(session_id, message_local_id, sort_seq))
```

**`ImgFtsV0`** — 0 行

```sql
CREATE TABLE <name>(session_id INTEGER, local_id INTEGER, create_time INTEGER, sort_seq INTEGER, CONSTRAINT sessionId_localId_createtime PRIMARY KEY(session_id, local_id, sort_seq))
```

**3 张同构表** — `ImgRangeV0`, `message_fts_v4_range`, `table_info`

其中 `ImgRangeV0` — 0 行

```sql
CREATE TABLE <name>(db_time_stamp INTEGER, start_local_id INTEGER, end_local_id INTEGER, session_id INTEGER, CONSTRAINT sessionId_dbTime PRIMARY KEY(session_id, db_time_stamp))
```

**`ImgTableInfo`** — 0 行

```sql
CREATE TABLE <name>(Key TEXT PRIMARY KEY, ValueInt64 INTEGER, ValueDouble REAL, ValueStdStr TEXT, ValueBlob BLOB)
```

**2 张同构表** — `deleteImgFtsV0`, `message_fts_v4_session_delete_info`

其中 `deleteImgFtsV0` — 0 行

```sql
CREATE TABLE <name>(session_id INTEGER, start_local_id INTEGER, end_local_id INTEGER, db_time_stamp INTEGER, CONSTRAINT sessionId_dbtime PRIMARY KEY(session_id, db_time_stamp))
```

**4 张同构表** — `message_fts_v4_0`, `message_fts_v4_1`, `message_fts_v4_2` …

其中 `message_fts_v4_0` — 26,118 行

```sql
CREATE VIRTUAL TABLE <name> USING fts5(tokenize = 'MMFtsTokenizer disable_pinyin', acontent, message_local_id UNINDEXED, sort_seq UNINDEXED, local_type UNINDEXED, session_id UNINDEXED, sender_id UNINDEXED, create_time UNINDEXED)
```

**`message_fts_v4_0_config`** — 1 行

```sql
CREATE TABLE 'message_fts_v4_0_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`message_fts_v4_0_content`** — 26,118 行

```sql
CREATE TABLE 'message_fts_v4_0_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4, c5, c6)
```

**`message_fts_v4_0_data`** — 257 行

```sql
CREATE TABLE 'message_fts_v4_0_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`message_fts_v4_0_docsize`** — 26,118 行

```sql
CREATE TABLE 'message_fts_v4_0_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`message_fts_v4_0_idx`** — 245 行

```sql
CREATE TABLE 'message_fts_v4_0_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`message_fts_v4_1_config`** — 1 行

```sql
CREATE TABLE 'message_fts_v4_1_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`message_fts_v4_1_content`** — 30,670 行

```sql
CREATE TABLE 'message_fts_v4_1_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4, c5, c6)
```

**`message_fts_v4_1_data`** — 365 行

```sql
CREATE TABLE 'message_fts_v4_1_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`message_fts_v4_1_docsize`** — 30,670 行

```sql
CREATE TABLE 'message_fts_v4_1_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`message_fts_v4_1_idx`** — 346 行

```sql
CREATE TABLE 'message_fts_v4_1_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`message_fts_v4_2_config`** — 1 行

```sql
CREATE TABLE 'message_fts_v4_2_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`message_fts_v4_2_content`** — 5,135 行

```sql
CREATE TABLE 'message_fts_v4_2_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4, c5, c6)
```

**`message_fts_v4_2_data`** — 76 行

```sql
CREATE TABLE 'message_fts_v4_2_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`message_fts_v4_2_docsize`** — 5,135 行

```sql
CREATE TABLE 'message_fts_v4_2_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`message_fts_v4_2_idx`** — 74 行

```sql
CREATE TABLE 'message_fts_v4_2_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**`message_fts_v4_3_config`** — 1 行

```sql
CREATE TABLE 'message_fts_v4_3_config'(k PRIMARY KEY, v) WITHOUT ROWID
```

**`message_fts_v4_3_content`** — 12,634 行

```sql
CREATE TABLE 'message_fts_v4_3_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4, c5, c6)
```

**`message_fts_v4_3_data`** — 120 行

```sql
CREATE TABLE 'message_fts_v4_3_data'(id INTEGER PRIMARY KEY, block BLOB)
```

**`message_fts_v4_3_docsize`** — 12,634 行

```sql
CREATE TABLE 'message_fts_v4_3_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
```

**`message_fts_v4_3_idx`** — 118 行

```sql
CREATE TABLE 'message_fts_v4_3_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
```

**4 张同构表** — `message_fts_v4_aux_0`, `message_fts_v4_aux_1`, `message_fts_v4_aux_2` …

其中 `message_fts_v4_aux_0` — 26,118 行

```sql
CREATE TABLE <name>(message_local_id INTEGER, sort_seq INTEGER, session_id INTEGER, CONSTRAINT sessionId_localId_sortseq PRIMARY KEY(session_id, message_local_id, sort_seq))
```

**`name2id`** — 1,340 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY)
```

### `message_resource.db`

**2 张同构表** — `ChatName2Id`, `SenderName2Id`

其中 `ChatName2Id` — 103 行

```sql
CREATE TABLE <name>(user_name TEXT PRIMARY KEY, update_time INTEGER)
```

**`FtsDeleteInfo`** — 0 行

```sql
CREATE TABLE <name>(session_id INTEGER, max_message_id INTEGER)
```

**`FtsRange`** — 204 行

```sql
CREATE TABLE <name>(session_id INTEGER, db_time_stamp INTEGER, start_local_id INTEGER, end_local_id INTEGER, range_type INTEGER, CONSTRAINT _CHAT_TIME_TYPE UNIQUE(session_id, db_time_stamp, range_type))
```

**`MessageResourceDetail`** — 45,789 行

```sql
CREATE TABLE <name>(resource_id INTEGER PRIMARY KEY AUTOINCREMENT, message_id INTEGER, type INTEGER, size INTEGER, create_time INTEGER, access_time INTEGER, status INTEGER, data_index TEXT, packed_info BLOB)
```

**`MessageResourceInfo`** — 16,948 行

```sql
CREATE TABLE <name>(message_id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, sender_id INTEGER, message_local_type INTEGER, message_create_time INTEGER, message_local_id INTEGER, message_svr_id INTEGER, message_origin_source INTEGER, packed_info BLOB)
```

### `session.db`

**`Name2Id`** — 210 行

```sql
CREATE TABLE <name>(user_name TEXT PRIMARY KEY)
```

**`SessionDeleteTable`** — 0 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY, delete_time INTEGER)
```

**`SessionDraft`** — 0 行

```sql
CREATE TABLE <name>(username TEXT, window_id TEXT, timestamp INTEGER, draft_data BLOB)
```

**`SessionNoContactInfoTable`** — 0 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY, session_title TEXT)
```

**`SessionTable`** — 230 行

```sql
CREATE TABLE <name>(username TEXT PRIMARY KEY, type INTEGER, unread_count INTEGER, unread_first_msg_srv_id INTEGER, unread_first_pat_msg_local_id INTEGER, unread_first_pat_msg_sort_seq INTEGER, is_hidden INTEGER, summary TEXT, draft TEXT, status INTEGER, last_timestamp INTEGER, sort_timestamp INTEGER, last_clear_unread_timestamp INTEGER, last_msg_locald_id INTEGER, last_msg_type INTEGER, last_msg_sub_type INTEGER, last_msg_sender TEXT, last_sender_display_name TEXT, last_msg_ext_type INTEGER)
```

**`SessionUnreadListTable_1`** — 58 行

```sql
CREATE TABLE <name>(username_id INTEGER, server_id INTEGER, create_time INTEGER, local_id INTEGER, CONSTRAINT _NameId_ServerId PRIMARY KEY(username_id, server_id))
```

**`SessionUnreadStatTable_1`** — 0 行

```sql
CREATE TABLE <name>(username_id INTEGER, unread_stat INTEGER, CONSTRAINT _NameId PRIMARY KEY(username_id))
```

### `sns.db`

**`SnsAdTimeLine`** — 2 行

```sql
CREATE TABLE <name>(tid INTEGER PRIMARY KEY DESC, username TEXT, content TEXT, create_time INTEGER, ad_content TEXT, ad_create_time INTEGER, exposure_time INTEGER, exposure_count INTEGER, remind_source_info TEXT, remind_self_info TEXT, extra_data TEXT)
```

**2 张同构表** — `SnsDraft`, `SnsPublishTask`

其中 `SnsDraft` — 0 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, create_time INTEGER, ui_type INTEGER, content TEXT, client_id TEXT, status INTEGER)
```

**`SnsErrorMessage`** — 0 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, error_type INTEGER, creat_time INTEGER, tid INTEGER, packed_info_data TEXT)
```

**`SnsIgnoredDataItem`** — 0 行

```sql
CREATE TABLE <name>(tid INTEGER PRIMARY KEY)
```

**`SnsMainTimeLineBreakFlag`** — 89 行

```sql
CREATE TABLE <name>(tid INTEGER, tid_heigh_bit INTEGER, tid_low_bit INTEGER, break_flag INTEGER, CONSTRAINT _heigh_low_bit_tid PRIMARY KEY(tid_heigh_bit DESC, tid_low_bit DESC))
```

**`SnsMessage_tmp3`** — 3 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, create_time INTEGER, type INTEGER, feed_id INTEGER, is_unread INTEGER, from_username TEXT, from_nickname TEXT, to_username TEXT, to_nickname TEXT, content TEXT, serialized_comment_buf BLOB, serialized_ref_buf BLOB, comment_id INTEGER, client_id TEXT, comment64_id INTEGER, comment_flag INTEGER, del_status INTEGER, is_relative_me INTEGER)
```

**`SnsNoteVoice`** — 0 行

```sql
CREATE TABLE <name>(tid INTEGER, data_id TEXT, buff TEXT, CONSTRAINT _tid_data_id PRIMARY KEY(tid, data_id))
```

**`SnsPendingDraftDeletionTable`** — 0 行

```sql
CREATE TABLE <name>(local_id INTEGER PRIMARY KEY AUTOINCREMENT, create_time INTEGER, ui_type INTEGER, content TEXT, client_id TEXT, status INTEGER, tid TEXT)
```

**`SnsTimeLine`** — 98 行

```sql
CREATE TABLE <name>(tid INTEGER PRIMARY KEY DESC, user_name TEXT, content TEXT, pack_info_buf TEXT)
```

**`SnsTopItem_1`** — 506 行

```sql
CREATE TABLE <name>(tid INTEGER, username TEXT, summary TEXT, create_time INTEGER, last_read_time INTEGER, is_read INTEGER)
```

**`SnsUserTimeLineBreakFlagV2`** — 1 行

```sql
CREATE TABLE <name>(tid INTEGER, tid_heigh_bit INTEGER, tid_low_bit INTEGER, break_flag INTEGER, user_name TEXT)
```

### `third_app_icon.db`

**`third_app_icon`** — 0 行

```sql
CREATE TABLE <name>(app_key TEXT PRIMARY KEY, icon_url_md5 TEXT, image_buffer BLOB, update_time INTEGER)
```

## 复用边界

表名和列名可当 4.1 来源样本的结构索引。行数、哈希表名片段只属于那次导出。解密参数不在本篇。
