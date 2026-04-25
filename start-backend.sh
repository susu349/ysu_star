#!/bin/bash
# 校园AI助手 - 后端启动脚本

echo "🚀 启动后端服务..."
cd backend

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
fi

# 初始化数据库
echo "📊 初始化数据库..."
uv run python -c "
import sys
sys.path.insert(0, 'src')
try:
    from campus_ai.core.database import engine
    from campus_ai.models.user import Base
    from campus_ai.models.map import Base as MapBase
    from campus_ai.models.contest import Base as ContestBase
    from campus_ai.models.knowledge import Base as KnowledgeBase
    Base.metadata.create_all(bind=engine)
    print('✅ 数据库初始化成功')
except Exception as e:
    print(f'❌ 数据库初始化失败: {e}')
    sys.exit(1)
"

echo "🌐 启动后端服务..."
echo ""
echo "📖 访问地址："
echo "- API文档: http://localhost:8000/docs"
echo "- API首页: http://localhost:8000/"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

uv run python -m campus_ai.main
