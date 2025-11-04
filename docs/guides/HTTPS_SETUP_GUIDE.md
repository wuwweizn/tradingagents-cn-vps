# HTTPS配置指南

本指南将帮助您为支付系统配置HTTPS，以满足支付平台的安全要求。

## 方案选择

### 方案1: Nginx反向代理（推荐）
- ✅ 性能好，稳定性高
- ✅ 可以同时代理Streamlit和Flask API
- ✅ 支持SSL终止
- ✅ 易于配置和管理

### 方案2: 直接在应用层启用HTTPS
- ⚠️ Streamlit本身不支持HTTPS
- ✅ Flask可以直接启用HTTPS
- ⚠️ 需要为每个服务单独配置证书

## 方案1: 使用Nginx反向代理

### 1. 安装Nginx

**Windows:**
```bash
# 使用chocolatey安装
choco install nginx

# 或下载安装包
# https://nginx.org/en/download.html
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install nginx
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install nginx
# 或
sudo dnf install nginx
```

### 2. 获取SSL证书

#### 选项A: Let's Encrypt免费证书（推荐）

```bash
# 安装Certbot
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx

# 申请证书（自动配置Nginx）
sudo certbot --nginx -d gpfxp.miaowu086.online

# 证书会自动续期，但建议设置定时任务
sudo certbot renew --dry-run
```

#### 选项B: 购买商业SSL证书

1. 从CA（证书颁发机构）购买证书
2. 获取证书文件（.crt）和私钥文件（.key）
3. 保存到 `/etc/nginx/ssl/` 目录

#### 选项C: 自签名证书（仅用于测试，生产环境不建议）

```bash
# 生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/gpfxp.miaowu086.online.key \
  -out /etc/nginx/ssl/gpfxp.miaowu086.online.crt
```

### 3. 配置Nginx

创建配置文件 `/etc/nginx/sites-available/gpfxp.miaowu086.online`:

```nginx
# HTTP重定向到HTTPS
server {
    listen 80;
    server_name gpfxp.miaowu086.online;
    
    # Let's Encrypt验证
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # 重定向所有HTTP请求到HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name gpfxp.miaowu086.online;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/gpfxp.miaowu086.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gpfxp.miaowu086.online/privkey.pem;
    
    # SSL优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 日志
    access_log /var/log/nginx/gpfxp.access.log;
    error_log /var/log/nginx/gpfxp.error.log;

    # 代理Streamlit Web应用
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # 代理支付回调API
    location /api/payment/ {
        proxy_pass http://localhost:8888;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 4. 启用配置并重启Nginx

```bash
# 创建符号链接（如果使用sites-available）
sudo ln -s /etc/nginx/sites-available/gpfxp.miaowu086.online /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
# 或
sudo service nginx restart
```

## 方案2: Flask直接启用HTTPS

如果只使用Flask API服务器，可以直接启用HTTPS：

```python
# 修改 web/api_server.py
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=443,
        ssl_context=('/path/to/cert.pem', '/path/to/key.pem')
    )
```

## 更新支付回调地址

配置HTTPS后，需要更新支付回调地址：

```bash
# 使用脚本更新为HTTPS地址
python scripts/update_payment_callback_urls_https.py
```

或在Web界面「⚙️ 配置管理」→「支付配置」中手动更新：
- 支付宝回调: `https://gpfxp.miaowu086.online/api/payment/notify/alipay`
- 微信支付回调: `https://gpfxp.miaowu086.online/api/payment/notify/wechat`

## 验证HTTPS配置

1. **检查SSL证书**
   ```bash
   openssl s_client -connect gpfxp.miaowu086.online:443
   ```

2. **在线测试**
   - 访问 https://www.ssllabs.com/ssltest/
   - 输入域名进行测试

3. **浏览器访问**
   - 访问 `https://gpfxp.miaowu086.online`
   - 确认显示🔒锁图标

## 防火墙配置

确保开放HTTPS端口：

```bash
# Ubuntu/Debian
sudo ufw allow 443/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 证书自动续期（Let's Encrypt）

Let's Encrypt证书有效期90天，设置自动续期：

```bash
# 编辑crontab
sudo crontab -e

# 添加定时任务（每月1号检查续期）
0 0 1 * * certbot renew --quiet && nginx -s reload
```

## 常见问题

### 1. 证书申请失败

**问题**: 域名无法验证

**解决**:
- 确保域名DNS解析正确
- 确保80端口可访问（Let's Encrypt验证需要）
- 检查防火墙设置

### 2. Nginx配置测试失败

**问题**: `nginx -t` 报错

**解决**:
- 检查配置文件语法
- 检查证书路径是否正确
- 检查文件权限

### 3. 支付回调失败

**问题**: 支付平台无法访问回调地址

**解决**:
- 确认HTTPS地址可公网访问
- 检查Nginx配置中的代理设置
- 确认Flask API服务器运行正常

## 安全建议

1. **使用强密码**: 保护服务器和证书私钥
2. **定期更新**: 保持Nginx和SSL库更新
3. **监控证书**: 设置证书到期提醒
4. **日志审计**: 定期检查Nginx访问日志
5. **备份配置**: 备份Nginx配置和证书文件

## 测试清单

- [ ] Nginx安装成功
- [ ] SSL证书获取成功
- [ ] Nginx配置测试通过
- [ ] HTTPS访问正常（浏览器显示🔒）
- [ ] Streamlit应用通过HTTPS可访问
- [ ] 支付回调API通过HTTPS可访问
- [ ] 支付平台回调地址更新为HTTPS
- [ ] 证书自动续期配置完成

