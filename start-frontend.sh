#!/bin/bash
# 校园AI助手 - 前端启动脚本

echo "🚀 启动前端服务..."
cd frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

echo ""
echo "🌐 访问地址："
echo "- 前端应用: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

npm run dev
