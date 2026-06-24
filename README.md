# AI 知识库后端系统

一个适合简历展示的 FastAPI 后端项目：支持用户注册登录、创建个人知识库、上传 TXT/MD/PDF 文档、文档切分与向量化、pgvector 相似度检索，并通过 Ollama 本地模型完成知识库问答。

## 技术栈

- FastAPI：后端 API 与 Swagger 文档
- SQLAlchemy：ORM 与数据库访问
- PostgreSQL + pgvector：关系数据与向量检索
- Ollama：本地 embedding 模型和对话模型
- JWT：登录认证与用户数据隔离
- Docker Compose：一键启动 API、数据库和 Ollama

## 本地启动

如果需要自定义配置，可以复制环境变量文件：

```powershell
copy .env.example .env
```

默认配置已写入 `docker-compose.yml`，可以直接启动服务：

```powershell
docker compose up --build
```

首次启动后，在另一个终端拉取模型：

```powershell
docker compose exec ollama ollama pull qwen2.5:1.5b
docker compose exec ollama ollama pull nomic-embed-text
```

Swagger 地址：

```text
http://localhost:8000/docs
```

## 环境变量

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/knowledge_base
JWT_SECRET_KEY=change-me
JWT_EXPIRE_MINUTES=1440
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_CHAT_MODEL=qwen2.5:1.5b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

## 核心接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/auth/register` | 注册用户 |
| POST | `/auth/login` | 登录并返回 JWT |
| POST | `/knowledge-bases` | 创建知识库 |
| GET | `/knowledge-bases` | 查看当前用户知识库 |
| POST | `/knowledge-bases/{kb_id}/documents` | 上传 TXT/MD/PDF 文档 |
| GET | `/knowledge-bases/{kb_id}/documents` | 查看文档列表 |
| POST | `/knowledge-bases/{kb_id}/chat` | 基于知识库提问 |
| GET | `/chat/history` | 查看问答历史 |

## 数据库表设计

项目包含 5 张核心表：

- `users`：用户账号、密码哈希、创建时间
- `knowledge_bases`：知识库名称、描述、所属用户
- `documents`：文件名、文件类型、处理状态、所属知识库
- `document_chunks`：文本片段、metadata、pgvector 向量
- `chat_records`：问题、回答、引用片段、所属用户和知识库

详细说明见 `docs/database-design.md`。

## RAG 流程

1. 用户上传文档。
2. 后端解析 TXT/MD/PDF 文本。
3. 按固定长度切分成多个 chunk。
4. 调用 Ollama `nomic-embed-text` 生成 embedding。
5. 将文本片段和向量写入 PostgreSQL + pgvector。
6. 用户提问时，对问题生成向量。
7. 用 pgvector 检索 Top 5 相关片段。
8. 将片段和问题组成 prompt，调用 Ollama `qwen2.5:1.5b` 生成回答。

## 演示材料

示例文档：`samples/demo_knowledge.md`

示例问题：

- 这个项目用了哪些核心技术？
- 上传文档后系统如何完成知识库问答？
- 为什么要使用 pgvector？

## 测试

本地安装依赖后运行：

```powershell
pip install -r requirements.txt
pytest
```

推荐手动验证：

- 注册新用户成功，重复用户名失败。
- 登录成功返回 JWT，密码错误失败。
- 未带 JWT 调用知识库接口返回 `401`。
- 用户 A 不能访问用户 B 的知识库。
- 上传 TXT、MD、PDF 后，文档状态变为 `processed`。
- 上传不支持的文件类型返回 `400`。
- 提问接口返回回答，并包含 `sources` 引用片段。
- Ollama 未启动或模型未拉取时返回 `503`。

## 简历描述

AI 知识库后端系统：基于 FastAPI、PostgreSQL、pgvector 和 Ollama 实现个人知识库问答系统，支持 JWT 登录认证、用户数据隔离、TXT/MD/PDF 文档上传、文本切分、向量化入库、相似度检索和 RAG 问答；使用 Docker Compose 编排 API、数据库和本地大模型服务，并编写 README、接口说明和数据库表设计文档。

## 常见问题排查

如果提问或上传文档返回 `503`：

- 确认 Ollama 容器正在运行：`docker compose ps`
- 确认模型已拉取：`docker compose exec ollama ollama list`
- 拉取模型：`docker compose exec ollama ollama pull qwen2.5:1.5b`
- 拉取 embedding 模型：`docker compose exec ollama ollama pull nomic-embed-text`

如果 API 启动失败：

- 查看日志：`docker compose logs api`
- 确认 Postgres 健康：`docker compose ps`
- 确认 `.env` 文件存在，并且 `DATABASE_URL` 使用 compose 内部地址 `postgres`

如果 PDF 上传后没有内容：

- 该 PDF 可能是扫描件图片，不包含可提取文本。
- 第一版没有接入 OCR，可以改用 TXT/MD 文档演示。

## 请求流图

```mermaid
flowchart TD
    A[用户 / Swagger / PowerShell] --> B[FastAPI app main.py]
    B --> C[API 路由层 app/api]

    C --> D1[/auth/register 注册/]
    D1 --> E1[写入 users 表]

    C --> D2[/auth/login 登录/]
    D2 --> E2[校验密码]
    E2 --> F2[返回 JWT Token]

    C --> D3[/knowledge-bases 创建知识库/]
    D3 --> G1[验证 Token]
    G1 --> E3[写入 knowledge_bases 表]

    C --> D4[/documents 上传文档/]
    D4 --> G2[验证知识库归属]
    G2 --> H1[file_parser 解析 TXT/MD/PDF]
    H1 --> H2[text_splitter 文本切块]
    H2 --> H3[Ollama 生成 embedding]
    H3 --> E4[写入 documents 和 document_chunks 表]

    C --> D5[/chat 提问/]
    D5 --> G3[验证 Token 和知识库归属]
    G3 --> H4[Ollama 生成问题向量]
    H4 --> H5[pgvector 相似度检索]
    H5 --> H6[rag.py 组装 Prompt]
    H6 --> H7[Ollama 生成回答]
    H7 --> E5[写入 chat_records 表]
    E5 --> Z[返回回答和引用片段]

```
