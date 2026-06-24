# AI 知识库项目说明

这个项目是一个基于 FastAPI 的 AI 知识库后端系统。它使用 PostgreSQL 保存用户、知识库、文档和问答记录，并使用 pgvector 保存文本向量。

用户可以注册账号并登录。登录后，用户可以创建自己的知识库，上传 TXT、Markdown 或 PDF 文档。系统会解析文档内容，把长文本切分为多个片段，然后调用 Ollama 本地 embedding 模型生成向量。

当用户提问时，系统会先把问题转换为向量，再使用 pgvector 在文档片段中检索最相关的内容。检索到的片段会和用户问题一起组成提示词，发送给 Ollama 本地对话模型，最后返回回答和引用片段。

这个项目的核心技术包括 FastAPI、SQLAlchemy、PostgreSQL、pgvector、JWT、Docker Compose 和 Ollama。它适合作为初级后端、Python 后端、AI 应用开发方向的简历项目。

项目没有实现复杂的团队协作和角色权限，第一版重点是把后端接口、数据库设计、权限隔离、文档处理和 RAG 流程做完整。

