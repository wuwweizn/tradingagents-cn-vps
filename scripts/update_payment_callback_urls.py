#!/usr/bin/env python3
"""
更新支付回调地址脚本
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web.utils.payment_adapter import payment_manager

# 域名配置
DOMAIN = "http://gpfxp.miaowu086.online"


def update_callback_urls():
    """更新支付回调地址"""
    
    print(f"正在更新支付回调地址，使用域名: {DOMAIN}")
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
        print("✅ 支付宝回调地址已更新")
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
        print("✅ 微信支付回调地址已更新")
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
    print("1. 请确保回调API服务器已启动: python web/api_server.py")
    print("2. 在支付平台上配置相同的回调地址")
    print("3. 确保域名可以公网访问且支持HTTP/HTTPS")


if __name__ == "__main__":
    update_callback_urls()

