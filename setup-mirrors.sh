#!/bin/bash

echo "======================================"
echo "   配置清华镜像源"
echo "======================================"
echo ""

# 1. 配置 Docker 镜像源（需要 sudo）
echo "1. 配置 Docker 镜像源..."
if [ -d /etc/docker ]; then
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.tuna.tsinghua.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
    echo "✅ Docker 镜像源已配置"
    echo "   重启 Docker 服务以生效: sudo systemctl restart docker"
else
    echo "⚠️  跳过 Docker 配置（未找到 /etc/docker）"
fi
echo ""

# 2. 配置 uv/Python 镜像源
echo "2. 配置 uv/Python 镜像源..."
if command -v uv &> /dev/null; then
    uv pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    echo "✅ uv 镜像源已配置为清华源"
else
    echo "⚠️  uv 未安装，跳过 uv 配置"
fi
echo ""

# 3. 配置 npm 镜像源
echo "3. 配置 npm 镜像源..."
if command -v npm &> /dev/null; then
    npm config set registry https://registry.npmmirror.com
    echo "✅ npm 镜像源已配置为 npmmirror"
else
    echo "⚠️  npm 未安装，跳过 npm 配置"
fi
echo ""

# 4. 创建 pip.conf（备用）
echo "4. 创建 pip 配置文件..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf <<EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
echo "✅ ~/.pip/pip.conf 已创建"
echo ""

echo "======================================"
echo "🎉 镜像源配置完成！"
echo "======================================"
echo ""
echo "建议操作："
echo "  - 重启 Docker: sudo systemctl restart docker"
echo "  - 然后重新运行: ./setup.sh"
echo ""
