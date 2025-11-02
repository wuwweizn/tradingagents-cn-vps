#!/usr/bin/env python3
"""
设置支付配置脚本
直接配置支付宝和微信支付的真实账号信息
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web.utils.payment_adapter import payment_manager


def setup_payment_config():
    """设置支付配置"""
    
    # 支付宝配置
    # 注意：私钥需要包含BEGIN和END标记
    alipay_private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCIuV/7cksvMfk7
Z5fdTZpak0G5+e13vfIcoXaSGC3lTJf+hxaWUamlUhExvmekVtRjaBDSA+FDtz3+
Y6KY5p3hoabT2IwkXPhgecI+Wme4R6PMf7yz4pvizg0x9ZRO3/2ruAp/UTm9m+Lt
P9sXFPqmZz0AxTv6s01w+VGbZbS73aCBYDh7SrfDnr9shBvUqQ9mTCn8QJvPGnK5
m3Xp75YOIkfBrzBsx5Fn+fHlDxcQLvPOBYV7zD9VBYo5uswsHIsLdvJl/1aNGXHk
Q8EyIhMMG7brRUKyWpeWuHoGrO0D+Zr6zGJK0B1g5qkwuPtc7EvsjAuIWnAYb5Oq
nlIRndWbAgMBAAECggEAW1UR9ANWjBFi/zblcLT9TlIeTuDQq/Ob/1owvckfJ5Sx
2BpfkUy9+azHxaX+z/4c5MbIrbJf0X9gD0Z5gJBVmTsGGXAHtebRGIldo496x9Q7
bElMQhI3thuVHvGA/+uLJiHMCV62Jp4yye+lKFcgVPaT/qbCuWb7bWNvC1K2l+Oq
Qaw+wVnAQJRwiu9ekQfLc2KX004qh5+8LAInrldpQGLslsnt1TH1sJIHkVkDRK5
hfG1THygUScgZwZgTN1U+MrpeznM3I85W2Kj2xbdXKdSigrAaQ2WIq8sJQ2SrqE
x/UzhhPsL2r6/Fpj3NXmg4UrrjHnGgYfhA4ilKXdS6EQKBgQDSS0J7vdjcDvxS4
6LtPtApQbPf5MqeTaVKHFdprzrsdnX2U+d+dnjabSqeCpRReqyMSvgR79LiaGJI
gK6EgmWl3eNZPM+VpUuRfKGs0FrtasyzN3CABtp4rL3YS6UVXa8ajtCwJOhGj52
YaUdk3Eoneh5dy7N80wEZw/yyrwOEmQKBgQCmcLGqiHmD1p3MPseqihdxDO347Z
8ocgw8ub3Rq0VDXGO9CASWg1QJZdtX7U4oQGZ7NqTIZdXNKcEKgBaDpo3XoSHvs
CvbCb8XFFX6H1lcIleISDoI03DAxDedlQibrWCaDCS+NHP/GnWBRjLOFQ1w0PntX
7fuveGt/ov7yxeYUwKBgF9eRBtMAIHjxehtVaEUAGEFa+aYoo7iFZije7zw+97q
5ho8+NnwLmSYZ2Be2d6NrJy/DvtLcK6+ufu5Z+uuGxz6oLUCj/2Ehd3H0KZHo0TS
T1zjQoC9GuzpIftqasZiwxtfMyL+ydveG5FYBUmnYXW/uu+8hnyQUIp3yCzck9L
ZAoGAFpe1hjCATiUTxmW/NKcKB455vxCCSjsw7g1Idu2IuVwRLdeox8WL4rqwy3
6q3UvgnVkNhSZNn0vLqGE6rSQunNaChMalLVZlWfyorwsSVi9TMmybdBc/dusroX
hZcshWFJMRacA0/qvYx3N/8flpmabERjR4AzBDMhsbZVJsIYECgYBefncW50TX8g
IVDq4afXbsagyio4J8dL4B010RkohVpmUVbzSpmdXeEVhgVe4dkvDWlNXFYl8bA
oOZIm9IqoHy1XG065An1u4dwfWcnDwM6aKX20D4AxZD3fw4WauJJ2oseQLQVi0v
EW7XCWtbuw1WCrV76Sepz1kxHBwsxEtrzw==
-----END RSA PRIVATE KEY-----"""
    
    alipay_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiLlf+3JLLzH5O2eX3U2a
WpNBufntd73yHKF2khgt5UyX/ocWllGppVIRMb5npFbUY2gQ0gPhQ7c9/mOimOad
4aGm09iMJFz4YHnCPlpnuEejzH+8s+Kb4s4NMfWUTt/9q7gKf1E5vZvi7T/bFxT
6pmc9AMU7+rNNcPlRm2W0u92ggWA4e0q3w56/bIQb1KkPZkwp/ECbzxpyuZt16e+
WDiJHwa8wbMeRZ/nx5Q8XEC7zzgWFe8w/VQWKObrMLByLC3byZf9WjRlx5EPBMi
ITDBu260VCslqXlrh6BqztA/ma+sxiStAdYOapMLj7XOxL7IwLiFpwGG+Tqp5SEZ
3VmwIDAQAB
-----END PUBLIC KEY-----"""
    
    alipay_config = {
        "enabled": True,
        "app_id": "2021006105603730",
        "app_secret": "",  # 支付宝不使用app_secret
        "app_private_key": alipay_private_key,
        "alipay_public_key": alipay_public_key,
        "gateway": "https://openapi.alipay.com/gateway.do",
        "notify_url": "",  # 需要根据实际部署地址填写
        "return_url": "",  # 需要根据实际部署地址填写
        "sign_type": "RSA2"
    }
    
    # 微信支付配置
    wechat_config = {
        "enabled": True,
        "app_id": "wx168f444c15a163a9",
        "app_secret": "35c9631f948e06daf846b5e08e5203f8",
        "mch_id": "1716671062",
        "api_key": "Liyong199105091221312EFEASDWfsdf",
        "gateway": "https://api.mch.weixin.qq.com",
        "notify_url": "",  # 需要根据实际部署地址填写
        "return_url": ""  # 需要根据实际部署地址填写
    }
    
    # 更新配置
    print("正在配置支付宝...")
    if payment_manager.update_config("alipay", alipay_config):
        print("✅ 支付宝配置已保存")
    else:
        print("❌ 支付宝配置保存失败")
    
    print("\n正在配置微信支付...")
    if payment_manager.update_config("wechat", wechat_config):
        print("✅ 微信支付配置已保存")
    else:
        print("❌ 微信支付配置保存失败")
    
    # 显示配置结果
    print("\n配置结果:")
    print("-" * 50)
    config = payment_manager.get_config()
    
    print("\n支付宝配置:")
    alipay = config.get("alipay", {})
    print(f"  启用状态: {'✅ 已启用' if alipay.get('enabled') else '❌ 未启用'}")
    print(f"  APP ID: {alipay.get('app_id', '')[:20]}...")
    print(f"  私钥: {'✅ 已配置' if alipay.get('app_private_key') else '❌ 未配置'}")
    print(f"  公钥: {'✅ 已配置' if alipay.get('alipay_public_key') else '❌ 未配置'}")
    
    print("\n微信支付配置:")
    wechat = config.get("wechat", {})
    print(f"  启用状态: {'✅ 已启用' if wechat.get('enabled') else '❌ 未启用'}")
    print(f"  APP ID: {wechat.get('app_id', '')}")
    print(f"  商户号: {wechat.get('mch_id', '')}")
    print(f"  API密钥: {'✅ 已配置' if wechat.get('api_key') else '❌ 未配置'}")
    
    print("\n⚠️ 注意:")
    print("1. 请务必在支付平台上配置回调地址")
    print("2. 回调地址示例:")
    print(f"   支付宝: https://your-domain.com/api/payment/notify/alipay")
    print(f"   微信支付: https://your-domain.com/api/payment/notify/wechat")
    print("3. 确保回调地址可公网访问且支持HTTPS")
    print("4. 配置完成后，需要在Web界面的「支付配置」中填写回调地址")


if __name__ == "__main__":
    setup_payment_config()

