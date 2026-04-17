#!/bin/bash

# 校园AI助手项目启动脚本 - 简化版

echo "======================================"
echo "   校园AI助手 - 项目初始化"
echo "======================================"
echo ""

# 检查 uv
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，请先安装 uv"
    exit 1
fi
echo "✅ uv 已安装"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi
echo "✅ Node.js 已安装"

echo ""
echo "======================================"
echo "步骤 1: 安装后端依赖"
echo "======================================"
cd backend
uv sync

echo ""
echo "======================================"
echo "步骤 2: 初始化数据库"
echo "======================================"
uv run python ../scripts/init_db.py

echo ""
echo "======================================"
echo "步骤 3: 安装前端依赖"
echo "======================================"
cd ../frontend
npm install

echo ""
echo "======================================"
echo "🎉 项目初始化完成！"
echo "======================================"
echo ""
echo "启动项目："
echo ""
echo "1. 后端（新终端）："
echo "   cd backend && uv run python -m campus_ai.main"
echo ""
echo "2. 前端（新终端）："
echo "   cd frontend && npm run dev"
echo ""
echo "访问地址："
echo "  - 前端: http://localhost:3000"
echo "  - 后端API文档: http://localhost:8000/docs"
echo ""
