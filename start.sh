#!/bin/bash
# 校园AI助手 - 快速启动脚本

echo "🎓 校园AI助手启动脚本"
echo "========================"

# 检查目录是否正确
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查Python环境
echo ""
echo "1️⃣ 检查后端环境..."
if ! command -v uv &> /dev/null; then
    echo "❌ 未找到uv，请先安装uv"
    exit 1
fi
echo "✅ uv已安装"

# 检查Node.js环境
echo ""
echo "2️⃣ 检查前端环境..."
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js，请先安装Node.js"
    exit 1
fi
echo "✅ Node.js已安装"

# 检查MySQL
echo ""
echo "3️⃣ 检查MySQL..."
if nc -z -w 2 localhost 3306; then
    echo "✅ MySQL端口开放"
else
    echo "⚠️ MySQL端口无法连接，请确认MySQL已启动"
    read -p "继续启动？[y/n] " -n 1 -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "停止启动"
        exit 1
    fi
fi

# 后端配置检查
echo ""
echo "4️⃣ 检查后端配置..."
cd backend
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "⚠️ 请编辑 backend/.env 填入真实配置！"
    echo "数据库连接配置已使用默认值，请注意修改"
fi
echo "✅ 配置文件已准备"

# 初始化数据库
echo ""
echo "5️⃣ 初始化数据库..."
uv run python -c "
import sys
sys.path.insert(0, 'src')
from campus_ai.core.database import engine
from campus_ai.models.user import Base
from campus_ai.models.map import Base as MapBase
from campus_ai.models.contest import Base as ContestBase
from campus_ai.models.knowledge import Base as KnowledgeBase
Base.metadata.create_all(bind=engine)
print('✅ 数据库表创建完成')
"
cd ..

echo ""
echo ""
echo "========================"
echo "🚀 启动准备已完成！"
echo ""
echo "请打开两个终端窗口，分别运行："
echo ""
echo "终端1 - 后端:"
echo "  cd backend"
echo "  uv run python -m campus_ai.main"
echo ""
echo "终端2 - 前端:"
echo "  cd frontend"
echo "  npm install  # 首次运行需要"
echo "  npm run dev"
echo ""
echo "访问地址："
echo "- 前端：http://localhost:5173"
echo "- 后端API文档：http://localhost:8000/docs"
echo ""
echo "📖 详细文档请查看 docs/启动指南.md"
