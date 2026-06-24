# 数据库表设计

本项目使用 PostgreSQL + pgvector。API 启动时会执行 `CREATE EXTENSION IF NOT EXISTS vector`，并自动创建数据表。

## users

用户表，保存登录账号和密码哈希。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| username | varchar(64) | 用户名，唯一 |
| password_hash | varchar(255) | bcrypt 密码哈希 |
| created_at | timestamptz | 创建时间 |

## knowledge_bases

知识库表，每个知识库只属于一个用户。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| name | varchar(120) | 知识库名称 |
| description | text | 描述 |
| user_id | integer | 所属用户 |
| created_at | timestamptz | 创建时间 |

## documents

文档表，记录上传文件及处理状态。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| filename | varchar(255) | 文件名 |
| file_type | varchar(20) | txt、md、pdf |
| status | varchar(20) | processing、processed、failed |
| chunk_count | integer | 文档切分数量 |
| error_message | text | 失败原因 |
| knowledge_base_id | integer | 所属知识库 |
| created_at | timestamptz | 创建时间 |

## document_chunks

文档分块表，用 pgvector 保存 embedding。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| document_id | integer | 所属文档 |
| chunk_index | integer | 分块序号 |
| content | text | 分块文本 |
| chunk_metadata | jsonb | 页码、文本位置等元数据 |
| embedding | vector(768) | Ollama embedding 向量 |
| created_at | timestamptz | 创建时间 |

## chat_records

问答记录表，保存问题、回答和引用片段。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| user_id | integer | 提问用户 |
| knowledge_base_id | integer | 知识库 |
| question | text | 用户问题 |
| answer | text | 模型回答 |
| source_chunks | jsonb | Top K 引用片段 |
| created_at | timestamptz | 创建时间 |

