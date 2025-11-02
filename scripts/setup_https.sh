#!/bin/bash
# HTTPS配置脚本（Linux）

set -e

DOMAIN="gpfxp.miaowu086.online"
NGINX_CONFIG="/etc/nginx/sites-available/${DOMAIN}"

echo "=========================================="
echo "HTTPS配置脚本"
echo "域名: ${DOMAIN}"
echo "=========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

# 1. 检查Nginx是否安装
echo ""
echo "1. 检查Nginx..."
if ! command -v nginx &> /dev/null; then
    echo "📦 安装Nginx..."
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y nginx
    elif command -v yum &> /dev/null; then
        yum install -y nginx
    else
        echo "❌ 无法自动安装Nginx，请手动安装"
        exit 1
    fi
else
    echo "✅ Nginx已安装"
fi

# 2. 复制Nginx配置
echo ""
echo "2. 配置Nginx..."
if [ -f "nginx/${DOMAIN}.conf" ]; then
    cp "nginx/${DOMAIN}.conf" "${NGINX_CONFIG}"
    echo "✅ Nginx配置已复制"
else
    echo "⚠️  Nginx配置文件不存在，请手动配置"
fi

# 3. 创建符号链接
echo ""
echo "3. 启用Nginx配置..."
if [ -d "/etc/nginx/sites-enabled" ]; then
    ln -sf "${NGINX_CONFIG}" "/etc/nginx/sites-enabled/${DOMAIN}"
    echo "✅ 配置已启用"
fi

# 4. 测试Nginx配置
echo ""
echo "4. 测试Nginx配置..."
nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Nginx配置测试通过"
else
    echo "❌ Nginx配置测试失败，请检查配置"
    exit 1
fi

# 5. 安装Certbot（用于Let's Encrypt）
echo ""
echo "5. 检查Certbot..."
if ! command -v certbot &> /dev/null; then
    echo "📦 安装Certbot..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y certbot python3-certbot-nginx
    elif command -v yum &> /dev/null; then
        yum install -y certbot python3-certbot-nginx
    else
        echo "⚠️  无法自动安装Certbot，请手动安装"
    fi
else
    echo "✅ Certbot已安装"
fi

# 6. 申请SSL证书
echo ""
echo "6. 申请SSL证书..."
echo "⚠️  注意：需要确保域名DNS解析正确，且80端口可访问"
read -p "是否现在申请Let's Encrypt证书? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d ${DOMAIN}
    if [ $? -eq 0 ]; then
        echo "✅ SSL证书申请成功"
    else
        echo "❌ SSL证书申请失败，请检查："
        echo "   1. 域名DNS解析是否正确"
        echo "   2. 80端口是否开放"
        echo "   3. 防火墙设置"
    fi
else
    echo "⏭️  跳过证书申请，请稍后手动运行:"
    echo "   certbot --nginx -d ${DOMAIN}"
fi

# 7. 重启Nginx
echo ""
echo "7. 重启Nginx..."
systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx已重启"
else
    echo "❌ Nginx重启失败"
    exit 1
fi

# 8. 更新支付回调地址
echo ""
echo "8. 更新支付回调地址为HTTPS..."
if [ -f "scripts/update_payment_callback_urls_https.py" ]; then
    python3 scripts/update_payment_callback_urls_https.py
else
    echo "⚠️  更新脚本不存在，请手动更新支付回调地址"
fi

echo ""
echo "=========================================="
echo "✅ HTTPS配置完成！"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 访问 https://${DOMAIN} 验证HTTPS是否正常"
echo "2. 在支付平台更新回调地址为HTTPS"
echo "3. 确保Streamlit应用运行在 localhost:8501"
echo "4. 确保支付回调API运行在 localhost:8888"
echo ""

