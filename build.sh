#!/bin/bash
# 构建脚本

echo "🏗️  构建 TradingAgents-CN Docker 镜像..."

# 构建API镜像
echo "📦 构建 API 镜像..."
docker build -f Dockerfile.api -t tradingagents-cn-api:latest .

# 构建前端镜像
echo "📦 构建前端镜像..."
docker build -f Dockerfile.frontend -t tradingagents-cn-frontend:latest .

echo "✅ 构建完成！"
echo ""
echo "启动服务："
echo "  docker-compose up -d"
echo ""
echo "查看日志："
echo "  docker-compose logs -f"

