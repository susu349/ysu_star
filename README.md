# 校园AI助手

智能校园生活服务平台，提供RAG知识检索、赛事推荐与组队、智慧地图、校园论坛等功能。

## 技术栈

### 后端
- Python 3.11+
- FastAPI - Web框架
- uv - 包管理
- SQLAlchemy - ORM
- MySQL/MariaDB - 关系型数据库
- Milvus - 向量数据库
- JWT - 身份认证

### 前端
- Vue 3
- Vue Router - 路由
- Pinia - 状态管理
- Axios - HTTP客户端
- Vite - 构建工具

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- MariaDB/MySQL 10.0+
- Docker & Docker Compose

### 1. 克隆项目

```bash
cd ysustar
```

### 2. 启动 Milvus 向量数据库

```bash
docker compose up -d
```

### 3. 初始化数据库

```bash
cd backend
python ../scripts/init_db.py
```

### 4. 后端设置

```bash
cd backend

# 安装依赖
uv sync

# 启动开发服务器
uv run python -m campus_ai.main
```

后端API文档: http://localhost:8000/docs

### 5. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问: http://localhost:3000

## 项目结构

```
campus-ai-assistant/
├── backend/              # Python后端
│   ├── src/
│   │   └── campus_ai/
│   │       ├── core/    # 核心配置与工具
│   │       ├── models/  # 数据模型
│   │       ├── schemas/ # API Schema
│   │       ├── services/# 业务逻辑
│   │       ├── api/     # API路由
│   │       └── tasks/   # 定时任务
│   └── tests/
├── frontend/             # Vue3前端
│   ├── src/
│   │   ├── api/         # API调用
│   │   ├── store/       # 状态管理
│   │   ├── router/      # 路由配置
│   │   ├── components/  # 组件
│   │   └── views/       # 页面
├── scripts/              # 辅助脚本
├── docs/                 # 项目文档
└── docker-compose.yml    # Milvus配置
```

## 开发计划

- [x] 项目初始化
- [x] 用户认证模块
- [ ] RAG校园知识检索
- [ ] 赛事推荐与组队
- [ ] 智慧地图
- [ ] 校园论坛

## 许可证

MIT
