# HTTPS快速配置指南

## 🚀 快速开始

### Linux服务器

1. **运行自动化脚本**
   ```bash
   sudo bash scripts/setup_https.sh
   ```

2. **手动配置（如果需要）**
   - 参考: `docs/guides/HTTPS_SETUP_GUIDE.md`

### Windows服务器

Windows上通常使用IIS或Apache，配置较复杂，建议：

1. **使用反向代理软件**
   - Caddy（自动HTTPS）
   - IIS（需要证书）

2. **使用云服务商代理**
   - 阿里云/腾讯云等提供HTTPS代理服务

## 📋 配置步骤

### 1. 安装Nginx

```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 2. 申请SSL证书

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 申请证书（自动配置）
sudo certbot --nginx -d gpfxp.miaowu086.online
```

### 3. 配置Nginx

```bash
# 复制配置文件
sudo cp nginx/gpfxp.miaowu086.online.conf /etc/nginx/sites-available/

# 启用配置
sudo ln -s /etc/nginx/sites-available/gpfxp.miaowu086.online.conf /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 4. 更新支付回调地址

```bash
python scripts/update_payment_callback_urls_https.py
```

### 5. 在支付平台更新回调地址

- **支付宝**: `https://gpfxp.miaowu086.online/api/payment/notify/alipay`
- **微信支付**: `https://gpfxp.miaowu086.online/api/payment/notify/wechat`

## ✅ 验证

1. 访问 `https://gpfxp.miaowu086.online`
2. 确认浏览器显示🔒锁图标
3. 测试支付功能是否正常

## 📚 详细文档

完整配置指南: `docs/guides/HTTPS_SETUP_GUIDE.md`

