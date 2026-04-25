# 校园AI助手

智能校园生活服务平台，提供RAG知识检索、赛事推荐与组队、智慧地图、校园论坛等功能。

## 技术栈

### 后端
- Python 3.11+
- FastAPI - Web框架
- uv - 包管理
- SQLAlchemy - ORM
- MySQL/MariaDB - 关系型数据库
- Milvus - 向量数据库（可选）
- JWT - 身份认证

### 前端
- Vue 3
- Vue Router - 路由
- Pinia - 状态管理
- Axios - HTTP客户端
- Leaflet - 地图库
- Vite - 构建工具

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- MariaDB/MySQL 10.0+
- Docker & Docker Compose（可选，用于Milvus）

### 1. 克隆项目

```bash
cd ysustar
```

### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑.env文件，填入真实配置
```

### 3. 数据库设置

#### MySQL数据库

确保MySQL/MariaDB已启动，创建数据库：

```sql
CREATE DATABASE campus_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Milvus向量数据库（可选）

```bash
cd ..  # 回到项目根目录
docker compose up -d
```

### 4. 后端设置

```bash
cd backend

# 安装依赖
uv sync

# 初始化数据库
uv run python -m scripts.init_db

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

前端访问: http://localhost:5173

## 项目结构

```
ysustar/
├── backend/              # Python后端
│   ├── src/
│   │   └── campus_ai/
│   │       ├── core/    # 核心配置与工具
│   │       ├── models/  # 数据模型
│   │       ├── schemas/ # API Schema
│   │       ├── services/# 业务逻辑
│   │       ├── api/     # API路由
│   │       └── tasks/   # 定时任务
│   ├── scripts/         # 辅助脚本
│   └── tests/           # 测试
├── frontend/            # Vue3前端
│   ├── src/
│   │   ├── api/         # API调用
│   │   ├── store/       # 状态管理
│   │   ├── router/      # 路由配置
│   │   ├── components/  # 组件
│   │   └── views/       # 页面
├── docs/                # 项目文档
├── 知识库/             # 知识库原始数据
├── 智慧地图/           # 地图相关数据和脚本
├── docker-compose.yml   # Milvus配置
└── README.md
```

## 功能模块

### ✅ 用户认证与权限
- 学号/工号注册登录
- JWT Token认证
- 角色权限管理（学生/教师/管理员）
- 个人资料管理

### ✅ RAG校园知识检索
- 校园知识问答
- 知识库管理
- 文档解析与向量化

### ✅ 赛事推荐与组队
- 赛事爬取与处理
- AI智能推荐
- 团队组建与任务管理
- 极简信息展示

### ✅ 智慧地图
- 校园地图展示
- 地点打卡
- 评论与互动
- 话题标签

### 🏗️ 校园论坛
- 分区发帖
- 内容审核
- 点赞与评论
- 热门推荐

## 文档

详细文档请查阅 `docs/` 目录：

- `docs/README.md` - 文档索引导航
- `docs/01-系统总体架构.md` - 系统架构介绍
- `docs/system/` - 系统层详细设计
- `docs/modules/` - 业务模块设计（含落地步骤）
- `docs/workflows/` - 业务流程
- `docs/data/` - 数据标准
- `docs/deployment/` - 部署指南

## 开发指南

### 后端开发

```bash
cd backend
uv sync  # 安装依赖
uv run pytest  # 运行测试
uv run python -m black src/  # 代码格式化
uv run ruff check src/  # 代码检查
```

### 前端开发

```bash
cd frontend
npm install  # 安装依赖
npm run dev  # 开发服务
npm run build  # 生产构建
```

## 配置说明

主要环境变量（见 backend/.env.example）：

- `MYSQL_*` - MySQL数据库配置
- `MILVUS_*` - Milvus向量数据库配置（可选）
- `JWT_SECRET_KEY` - JWT密钥（必须修改！）
- `LLM_*` - LLM配置
- `EMBEDDING_*` - 向量模型配置

## 开发计划

- [x] 项目初始化
- [x] 用户认证模块
- [x] RAG校园知识检索
- [x] 赛事推荐与组队
- [x] 智慧地图
- [ ] 校园论坛（待完善）

## 贡献指南

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

MIT
