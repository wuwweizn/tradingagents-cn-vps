# Docker 构建问题修复指南

## 问题诊断

如果遇到 `frontend/*` 文件找不到的错误，可能是以下原因：

1. **文件未同步到服务器**：本地创建的文件还没推送到Git或同步到服务器
2. **.dockerignore 排除了文件**：检查 `.dockerignore` 配置
3. **构建上下文问题**：确保在项目根目录执行构建

## 快速修复步骤

### 1. 确认文件存在

在服务器上检查：
```bash
ls -la frontend/
ls -la frontend/src/
ls -la frontend/package.json
```

### 2. 如果文件不存在，需要先创建

如果服务器上确实没有前端文件，需要：
1. 从Git拉取最新代码
2. 或者手动创建必要文件

### 3. 简化构建（如果前端还未完成）

如果前端还未完成，可以先注释掉前端服务，只构建API：

```yaml
# 在 docker-compose.yml 中注释掉 frontend 服务
```

### 4. 使用替代方案

如果前端文件确实不存在，可以：
- 先构建和运行API服务
- 前端服务稍后添加

## 当前状态检查

执行以下命令检查文件：

```bash
# 检查frontend目录
find . -name "frontend" -type d

# 检查前端文件
ls -la frontend/ 2>/dev/null || echo "frontend目录不存在"

# 检查关键文件
[ -f frontend/package.json ] && echo "✓ package.json存在" || echo "✗ package.json不存在"
[ -f frontend/vite.config.ts ] && echo "✓ vite.config.ts存在" || echo "✗ vite.config.ts不存在"
[ -d frontend/src ] && echo "✓ src目录存在" || echo "✗ src目录不存在"
```

