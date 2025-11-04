#!/usr/bin/env python3
"""
更新支付回调地址为HTTPS
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web.utils.payment_adapter import payment_manager

# 域名配置（HTTPS）
DOMAIN = "https://gpfxp.miaowu086.online"


def update_callback_urls_https():
    """更新支付回调地址为HTTPS"""
    
    print(f"正在更新支付回调地址为HTTPS，使用域名: {DOMAIN}")
    print("-" * 50)
    
    # 支付宝配置
    alipay_config = {
        "notify_url": f"{DOMAIN}/api/payment/notify/alipay",
        "return_url": f"{DOMAIN}/points/store"
    }
    
    print("\n支付宝回调地址:")
    print(f"  通知地址: {alipay_config['notify_url']}")
    print(f"  返回地址: {alipay_config['return_url']}")
    
    if payment_manager.update_config("alipay", alipay_config):
        print("✅ 支付宝回调地址已更新为HTTPS")
    else:
        print("❌ 支付宝回调地址更新失败")
    
    # 微信支付配置
    wechat_config = {
        "notify_url": f"{DOMAIN}/api/payment/notify/wechat",
        "return_url": f"{DOMAIN}/points/store"
    }
    
    print("\n微信支付回调地址:")
    print(f"  通知地址: {wechat_config['notify_url']}")
    print(f"  返回地址: {wechat_config['return_url']}")
    
    if payment_manager.update_config("wechat", wechat_config):
        print("✅ 微信支付回调地址已更新为HTTPS")
    else:
        print("❌ 微信支付回调地址更新失败")
    
    # 显示更新后的配置
    print("\n" + "=" * 50)
    print("更新后的配置:")
    print("=" * 50)
    
    config = payment_manager.get_config()
    
    print("\n支付宝配置:")
    alipay = config.get("alipay", {})
    print(f"  启用状态: {'✅ 已启用' if alipay.get('enabled') else '❌ 未启用'}")
    print(f"  回调通知地址: {alipay.get('notify_url', '未配置')}")
    print(f"  返回地址: {alipay.get('return_url', '未配置')}")
    
    print("\n微信支付配置:")
    wechat = config.get("wechat", {})
    print(f"  启用状态: {'✅ 已启用' if wechat.get('enabled') else '❌ 未启用'}")
    print(f"  回调通知地址: {wechat.get('notify_url', '未配置')}")
    print(f"  返回地址: {wechat.get('return_url', '未配置')}")
    
    print("\n⚠️ 重要提醒:")
    print("1. 确保HTTPS已配置完成（Nginx + SSL证书）")
    print("2. 在支付平台上更新回调地址为HTTPS")
    print("3. 确保回调API服务器正常运行")
    print("4. 测试HTTPS访问是否正常")


if __name__ == "__main__":
    update_callback_urls_https()

