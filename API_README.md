# TradingAgents-CN API 后端

## 架构说明

本项目已重构为前后端分离架构：
- **后端**: FastAPI (Python)
- **前端**: React + TypeScript + Vite

## 快速开始

### 后端启动

1. 安装依赖：
```bash
pip install -r requirements-api.txt
pip install -e .  # 安装项目主依赖
```

2. 启动API服务：
```bash
python -m api.main
```

或使用uvicorn：
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

3. 访问API文档：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 前端启动

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

3. 访问前端：http://localhost:3000

## API 接口说明

### 认证接口

- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/logout` - 登出
- `POST /api/auth/change-password` - 修改密码

### 分析接口

- `POST /api/analysis/start` - 启动股票分析
- `GET /api/analysis/status/{analysis_id}` - 查询分析状态
- `GET /api/analysis/result/{analysis_id}` - 获取分析结果

### 批量分析

- `POST /api/batch/start` - 启动批量分析
- `GET /api/batch/status/{batch_id}` - 查询批量分析状态

## 开发计划

- [x] 基础API框架
- [x] 用户认证
- [ ] 分析任务管理
- [ ] WebSocket实时进度
- [ ] 批量分析完整实现
- [ ] 配置管理
- [ ] Token统计
- [ ] 前端完整功能

## 注意事项

1. 后端使用JWT token进行认证
2. 前端需要配置API代理（已在vite.config.ts中配置）
3. 所有原有功能将逐步迁移到新架构

