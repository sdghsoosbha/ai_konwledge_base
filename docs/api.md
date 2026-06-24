# API 接口说明

Swagger 地址：`http://localhost:8000/docs`

| 方法 | 路径 | 说明 | 是否需要登录 |
| --- | --- | --- | --- |
| POST | `/auth/register` | 注册用户 | 否 |
| POST | `/auth/login` | 登录并返回 JWT | 否 |
| POST | `/knowledge-bases` | 创建知识库 | 是 |
| GET | `/knowledge-bases` | 查看当前用户知识库 | 是 |
| POST | `/knowledge-bases/{kb_id}/documents` | 上传 TXT/MD/PDF 文档 | 是 |
| GET | `/knowledge-bases/{kb_id}/documents` | 查看知识库文档 | 是 |
| POST | `/knowledge-bases/{kb_id}/chat` | 基于知识库问答 | 是 |
| GET | `/chat/history` | 查看当前用户问答历史 | 是 |

## 认证方式

登录成功后复制 `access_token`，在 Swagger 右上角 `Authorize` 中填入：

```text
Bearer <access_token>
```

## 典型调用流程

1. `POST /auth/register` 注册账号。
2. `POST /auth/login` 获取 JWT。
3. `POST /knowledge-bases` 创建知识库。
4. `POST /knowledge-bases/{kb_id}/documents` 上传示例文档。
5. `POST /knowledge-bases/{kb_id}/chat` 提问。

