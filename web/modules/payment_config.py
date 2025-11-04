"""
支付配置管理模块
管理员配置支付接口
"""

import streamlit as st
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from web.utils.payment_adapter import payment_manager
    from web.utils.auth_manager import auth_manager
except ImportError:
    from utils.payment_adapter import payment_manager
    from utils.auth_manager import auth_manager


def render_payment_config():
    """渲染支付配置页面"""
    st.title("💳 支付配置")
    st.markdown("---")
    
    # 权限检查
    if not auth_manager or not auth_manager.check_permission("admin"):
        st.error("❌ 只有管理员可以配置支付接口")
        return
    
    st.info("""
    💡 **支付配置说明**:
    - 配置支付宝或微信支付的API密钥和回调地址
    - 回调地址格式: `https://your-domain.com/api/payment/notify/{method}`
    - 配置完成后，用户可以在点数商城使用真实支付
    """)
    
    # 获取当前配置
    config = payment_manager.get_config()
    
    # 支付宝配置
    st.subheader("💰 支付宝配置")
    alipay_config = config.get("alipay", {})
    
    with st.form("alipay_config_form"):
        col1, col2 = st.columns(2)
        with col1:
            alipay_enabled = st.checkbox("启用支付宝支付", value=alipay_config.get("enabled", False))
            alipay_app_id = st.text_input("APP ID", value=alipay_config.get("app_id", ""), type="default")
        
        with col2:
            alipay_gateway = st.text_input("网关地址", value=alipay_config.get("gateway", "https://openapi.alipay.com/gateway.do"))
        
        # 密钥配置
        st.markdown("**密钥配置**")
        col1, col2 = st.columns(2)
        with col1:
            alipay_private_key = st.text_area(
                "应用私钥 (RSA2)", 
                value=alipay_config.get("app_private_key", ""),
                height=150,
                help="应用私钥，格式为：-----BEGIN RSA PRIVATE KEY-----...-----END RSA PRIVATE KEY-----"
            )
        with col2:
            alipay_public_key = st.text_area(
                "支付宝公钥", 
                value=alipay_config.get("alipay_public_key", ""),
                height=150,
                help="支付宝公钥，从开放平台获取"
            )
        
        # 回调地址配置
        st.markdown("**回调地址配置**")
        col1, col2 = st.columns(2)
        with col1:
            alipay_notify_url = st.text_input("回调通知地址", value=alipay_config.get("notify_url", ""))
        with col2:
            alipay_return_url = st.text_input("返回地址", value=alipay_config.get("return_url", ""))
        
        if st.form_submit_button("保存支付宝配置", type="primary"):
            new_config = {
                "enabled": alipay_enabled,
                "app_id": alipay_app_id,
                "app_private_key": alipay_private_key,
                "alipay_public_key": alipay_public_key,
                "gateway": alipay_gateway,
                "notify_url": alipay_notify_url,
                "return_url": alipay_return_url,
                "sign_type": "RSA2"
            }
            if payment_manager.update_config("alipay", new_config):
                st.success("✅ 支付宝配置已保存")
                st.rerun()
            else:
                st.error("❌ 保存失败")
    
    st.markdown("---")
    
    # 微信支付配置
    st.subheader("💚 微信支付配置")
    wechat_config = config.get("wechat", {})
    
    with st.form("wechat_config_form"):
        col1, col2 = st.columns(2)
        with col1:
            wechat_enabled = st.checkbox("启用微信支付", value=wechat_config.get("enabled", False))
            wechat_app_id = st.text_input("APP ID (应用ID)", value=wechat_config.get("app_id", ""), type="default")
            wechat_app_secret = st.text_input("APP Secret (应用密钥)", value=wechat_config.get("app_secret", ""), type="password")
            wechat_mch_id = st.text_input("商户号 (MCH ID)", value=wechat_config.get("mch_id", ""), type="default")
        
        with col2:
            wechat_api_key = st.text_input("API密钥", value=wechat_config.get("api_key", ""), type="password", help="商户平台的API密钥")
            wechat_gateway = st.text_input("网关地址", value=wechat_config.get("gateway", "https://api.mch.weixin.qq.com"))
        
        # 回调地址配置
        st.markdown("**回调地址配置**")
        col1, col2 = st.columns(2)
        with col1:
            wechat_notify_url = st.text_input("回调通知地址", value=wechat_config.get("notify_url", ""))
        with col2:
            wechat_return_url = st.text_input("返回地址", value=wechat_config.get("return_url", ""))
        
        if st.form_submit_button("保存微信支付配置", type="primary"):
            new_config = {
                "enabled": wechat_enabled,
                "app_id": wechat_app_id,
                "app_secret": wechat_app_secret,
                "mch_id": wechat_mch_id,
                "api_key": wechat_api_key,
                "gateway": wechat_gateway,
                "notify_url": wechat_notify_url,
                "return_url": wechat_return_url
            }
            if payment_manager.update_config("wechat", new_config):
                st.success("✅ 微信支付配置已保存")
                st.rerun()
            else:
                st.error("❌ 保存失败")
    
    st.markdown("---")
    
    # 配置说明
    st.subheader("📖 配置说明")
    with st.expander("支付宝配置指南", expanded=False):
        st.markdown("""
        ### 支付宝配置步骤
        
        1. **注册支付宝开放平台账号**
           - 访问: https://open.alipay.com/
           - 注册企业或个体工商户账号
        
        2. **创建应用**
           - 登录开放平台
           - 创建"网页&移动应用"
           - 获取 APP ID
        
        3. **配置密钥**
           - 生成RSA2密钥对
           - 上传公钥到支付宝平台
           - 保存私钥用于签名
        
        4. **配置回调地址**
           - 回调通知地址: `https://your-domain.com/api/payment/notify/alipay`
           - 返回地址: `https://your-domain.com/points/store`
        
        5. **上线应用**
           - 提交审核
           - 审核通过后上线
        """)
    
    with st.expander("微信支付配置指南", expanded=False):
        st.markdown("""
        ### 微信支付配置步骤
        
        1. **注册微信支付商户平台**
           - 访问: https://pay.weixin.qq.com/
           - 注册并完成企业认证
        
        2. **获取商户信息**
           - 商户号 (MCH ID)
           - API密钥 (API Key)
        
        3. **配置应用**
           - 在微信公众平台注册应用
           - 获取 AppID 和 AppSecret
           - 关联微信支付商户号
        
        4. **配置回调地址**
           - 回调通知地址: `https://your-domain.com/api/payment/notify/wechat`
           - 返回地址: `https://your-domain.com/points/store`
        
        5. **配置支付域名**
           - 在商户平台配置支付授权目录
           - 确保域名已备案（国内）
        """)
    
    # 可用支付方式
    st.subheader("✅ 可用支付方式")
    available_methods = payment_manager.get_available_payment_methods()
    if available_methods:
        for method in available_methods:
            method_name = "💰 支付宝" if method == "alipay" else "💚 微信支付"
            st.success(f"{method_name}: 已启用")
    else:
        st.warning("⚠️ 暂无已启用的支付方式，请先配置并启用")


def main():
    """主函数"""
    render_payment_config()


if __name__ == "__main__":
    main()

