# TradingAgents-CN Docker 部署指南

## 🐳 Docker 架构

本项目已重构为前后端分离架构，使用 Docker Compose 统一管理：

- **API 服务**: FastAPI 后端 (端口 8000)
- **前端服务**: React + Nginx (端口 80)
- **MongoDB**: 数据库服务 (端口 27017)
- **Redis**: 缓存服务 (端口 6379)

## 🚀 快速启动

### 生产环境部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
docker-compose logs -f frontend
```

### 开发环境部署

```bash
# 启动开发环境（支持热重载）
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 或者单独启动某个服务
docker-compose -f docker-compose.dev.yml up frontend-dev
```

## 📋 服务说明

### API 服务

- **访问地址**: http://localhost:8000
- **API 文档**: http://localhost:8000/api/docs
- **健康检查**: http://localhost:8000/api/health

### 前端服务

- **访问地址**: http://localhost
- **开发模式**: http://localhost:3000 (仅开发环境)

### 管理工具

- **Redis Commander**: http://localhost:8081
- **Mongo Express**: http://localhost:8082 (需要 --profile management)

## 🔧 常用命令

### 构建镜像

```bash
# 构建所有镜像
docker-compose build

# 只构建API服务
docker-compose build api

# 只构建前端服务
docker-compose build frontend
```

### 启动/停止服务

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除数据卷（慎用！）
docker-compose down -v

# 重启服务
docker-compose restart api
docker-compose restart frontend
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f mongodb
docker-compose logs -f redis
```

### 进入容器

```bash
# 进入API容器
docker-compose exec api bash

# 进入前端容器
docker-compose exec frontend sh
```

## 🔐 环境变量配置

创建 `.env` 文件（参考 `.env.example`）：

```env
# API配置
JWT_SECRET_KEY=your-secret-key-change-in-production
DEBUG=false

# 数据库配置（Docker环境会自动使用容器内配置）
TRADINGAGENTS_MONGODB_URL=mongodb://admin:tradingagents123@mongodb:27017/tradingagents?authSource=admin
TRADINGAGENTS_REDIS_URL=redis://:tradingagents123@redis:6379

# LLM API Keys
DASHSCOPE_API_KEY=your-key
FINNHUB_API_KEY=your-key
```

## 📦 数据持久化

数据卷映射：

- `mongodb_data`: MongoDB 数据持久化
- `redis_data`: Redis 数据持久化
- `./logs`: 应用日志
- `./config`: 配置文件
- `./data`: 应用数据

## 🛠️ 开发模式

### 前端开发

```bash
# 启动前端开发服务器（支持热重载）
docker-compose -f docker-compose.dev.yml up frontend-dev

# 或本地运行（需要先启动API服务）
cd frontend
npm install
npm run dev
```

### API开发

```bash
# 启动API开发服务器（支持热重载）
docker-compose -f docker-compose.dev.yml up api

# 或本地运行
pip install -r requirements-api.txt
python -m api.main
```

## 🌐 网络配置

所有服务在 `tradingagents-network` 网络中，服务间可通过服务名访问：

- API: `http://api:8000`
- MongoDB: `mongodb:27017`
- Redis: `redis:6379`

## 🔍 故障排查

### 服务无法启动

```bash
# 检查服务状态
docker-compose ps

# 查看详细日志
docker-compose logs api
docker-compose logs frontend

# 检查网络连接
docker network inspect tradingagents-network
```

### 端口冲突

如果端口被占用，修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 将API端口改为8001
  - "8080:80"    # 将前端端口改为8080
```

### 数据卷权限问题

```bash
# 修复日志目录权限
sudo chown -R $(id -u):$(id -g) ./logs
sudo chown -R $(id -u):$(id -g) ./config
```

## 📝 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose build
docker-compose up -d

# 或者强制重建
docker-compose build --no-cache
docker-compose up -d
```

## 🎯 生产环境建议

1. **修改默认密码**: 更新 MongoDB 和 Redis 的密码
2. **配置HTTPS**: 使用 Nginx 反向代理配置SSL
3. **资源限制**: 在 `docker-compose.yml` 中添加资源限制
4. **日志轮转**: 配置日志收集和轮转
5. **备份策略**: 定期备份 MongoDB 和 Redis 数据

## 📚 更多信息

- API文档: http://localhost:8000/api/docs
- 前端源码: `frontend/`
- API源码: `api/`

