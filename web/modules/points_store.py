"""
点数商城模块
用户购买点数的页面
"""

import streamlit as st
import time
from pathlib import Path
import sys
import time as time_module

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from web.utils.points_package_manager import points_package_manager
    from web.utils.auth_manager import auth_manager
    from web.utils.payment_adapter import payment_manager
except ImportError:
    from utils.points_package_manager import points_package_manager
    from utils.auth_manager import auth_manager
    from utils.payment_adapter import payment_manager


def render_points_store():
    """渲染点数商城页面"""
    st.title("💰 点数商城")
    st.markdown("---")
    
    # 检查用户是否登录
    if not auth_manager or not auth_manager.is_authenticated():
        st.error("❌ 请先登录")
        return
    
    current_user = auth_manager.get_current_user()
    username = current_user.get("username") if current_user else None
    current_points = current_user.get("points", 0) if current_user else 0
    
    # 显示当前点数
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💎 当前点数", f"{current_points}")
    with col2:
        st.metric("👤 用户名", username)
    with col3:
        if st.button("🔄 刷新点数", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # 获取可用套餐
    packages = points_package_manager.get_packages(enabled_only=True)
    
    if not packages:
        st.warning("⚠️ 暂无可用的点数套餐，请联系管理员")
        return
    
    # 显示套餐卡片
    st.subheader("📦 可选套餐")
    
    # 按价格排序
    packages_sorted = sorted(packages, key=lambda x: x.get("price", 0))
    
    # 每行显示2个套餐
    cols = st.columns(2)
    for idx, package in enumerate(packages_sorted):
        col = cols[idx % 2]
        with col:
            render_package_card(package, username, current_points)
    
    st.markdown("---")
    
    # 显示购买历史
    render_order_history(username)


def render_package_card(package: dict, username: str, current_points: int):
    """渲染套餐卡片"""
    package_id = package.get("id")
    name = package.get("name", "未知套餐")
    points = package.get("points", 0)
    bonus = package.get("bonus", 0)
    total_points = points + bonus
    price = package.get("price", 0)
    currency = package.get("currency", "CNY")
    description = package.get("description", "")
    
    # 计算每点价格
    price_per_point = price / total_points if total_points > 0 else 0
    
    with st.container():
        # 套餐名称和价格
        st.markdown(f"### {name}")
        
        # 点数信息
        if bonus > 0:
            st.markdown(f"""
            **💎 获得点数**: {points} 点 + 🎁 赠送 {bonus} 点 = **{total_points} 点**
            """)
        else:
            st.markdown(f"**💎 获得点数**: {total_points} 点")
        
        # 价格
        currency_symbol = "¥" if currency == "CNY" else "$" if currency == "USD" else "€"
        st.markdown(f"**💰 价格**: {currency_symbol}{price:.2f}")
        
        # 每点价格
        st.caption(f"≈ {currency_symbol}{price_per_point:.3f}/点")
        
        # 描述
        if description:
            st.info(f"💡 {description}")
        
        # 购买按钮
        if st.button(f"🛒 立即购买", key=f"buy_{package_id}", use_container_width=True):
            handle_purchase(package_id, username, package)
        
        st.markdown("---")


def handle_purchase(package_id: str, username: str, package: dict):
    """处理购买"""
    # 创建订单
    order = points_package_manager.create_order(username, package_id, payment_method="manual")
    
    if not order:
        st.error("❌ 创建订单失败，请重试")
        return
    
    # 显示订单确认对话框
    st.session_state[f"show_order_confirm_{package_id}"] = order
    
    # 使用模态对话框确认
    with st.expander(f"📋 订单确认 - {order['order_id']}", expanded=True):
        st.markdown(f"""
        **订单信息**:
        - 订单号: `{order['order_id']}`
        - 套餐: {order['package_name']}
        - 获得点数: {order['total_points']} 点（含赠送 {order['bonus']} 点）
        - 金额: ¥{order['price']:.2f}
        """)
        
        # 支付方式选择
        available_methods = payment_manager.get_available_payment_methods()
        payment_options = []
        
        # 添加真实支付方式
        for method in available_methods:
            method_name = "💰 支付宝" if method == "alipay" else "💚 微信支付"
            payment_options.append((method_name, method))
        
        # 添加测试支付方式
        payment_options.append(("模拟支付（测试用）", "mock"))
        payment_options.append(("手动确认（管理员审核）", "manual"))
        
        # 构建选择框选项
        payment_labels = [opt[0] for opt in payment_options]
        selected_index = st.selectbox(
            "支付方式",
            range(len(payment_labels)),
            format_func=lambda x: payment_labels[x],
            key=f"payment_{package_id}"
        )
        selected_payment = payment_options[selected_index][1]
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 确认支付", key=f"confirm_{package_id}", type="primary", use_container_width=True):
                if selected_payment == "mock":
                    # 模拟支付流程
                    complete_purchase(order['order_id'], username, order)
                elif selected_payment == "manual":
                    # 手动确认流程（需要管理员审核）
                    st.info("📝 订单已创建，等待管理员审核确认。审核通过后，点数将自动充值到您的账户。")
                    st.session_state.pop(f"show_order_confirm_{package_id}", None)
                else:
                    # 真实支付流程
                    handle_real_payment(selected_payment, order, username)
        
        with col2:
            if st.button("❌ 取消", key=f"cancel_{package_id}", use_container_width=True):
                st.session_state.pop(f"show_order_confirm_{package_id}", None)
                st.rerun()


def complete_purchase(order_id: str, username: str, order: dict):
    """完成购买（充值点数）"""
    try:
        # 完成订单
        if points_package_manager.complete_order(order_id):
            # 增加用户点数
            total_points = order.get("total_points", 0)
            if auth_manager.add_user_points(username, total_points):
                st.success(f"✅ 充值成功！已为您充值 {total_points} 点")
                st.balloons()
                # 更新订单状态为已完成
                points_package_manager.complete_order(order_id)
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 充值点数失败，请联系管理员")
        else:
            st.error("❌ 订单处理失败，请重试")
    except Exception as e:
        st.error(f"❌ 充值失败: {e}")


def handle_real_payment(payment_method: str, order: dict, username: str):
    """处理真实支付"""
    try:
        order_id = order['order_id']
        amount = order['price']
        subject = f"点数充值 - {order['package_name']}"
        description = f"购买 {order['total_points']} 点（含赠送 {order['bonus']} 点）"
        
        # 创建支付订单
        success, payment_info, error = payment_manager.create_payment(
            payment_method, 
            order_id, 
            amount, 
            subject, 
            description
        )
        
        if not success:
            st.error(f"❌ 创建支付订单失败: {error}")
            return
        
        # 更新订单的支付方式
        points_package_manager.update_order_status(
            order_id,
            "pending",
            payment_method=payment_method,
            payment_info=payment_info
        )
        
        # 显示支付链接或二维码
        payment_url = payment_info.get("payment_url")
        qr_code = payment_info.get("qr_code")
        
        st.success(f"✅ 支付订单已创建，请完成支付")
        
        if payment_url:
            st.markdown(f"### 🔗 支付链接")
            st.markdown(f"[点击跳转到支付页面]({payment_url})")
            
            # 在Streamlit中直接跳转
            st.markdown(f"""
            <script>
            window.open('{payment_url}', '_blank');
            </script>
            """, unsafe_allow_html=True)
        
        if qr_code:
            st.markdown(f"### 📱 扫码支付")
            # 这里可以集成二维码生成库，如 qrcode
            st.info(f"扫码支付: {qr_code}")
        
        st.info("""
        💡 **支付说明**:
        - 支付完成后，点数将自动充值到您的账户
        - 如未及时到账，请联系管理员
        - 您可以在"购买历史"中查看订单状态
        """)
        
        st.session_state.pop(f"show_order_confirm_{order['package_id']}", None)
        
    except Exception as e:
        st.error(f"❌ 支付处理失败: {e}")


def render_order_history(username: str):
    """渲染订单历史"""
    st.subheader("📜 购买历史")
    
    orders = points_package_manager.get_user_orders(username, limit=20)
    
    if not orders:
        st.info("📝 暂无购买记录")
        return
    
    # 显示订单列表
    for order in orders:
        with st.expander(f"订单 {order['order_id']} - {order.get('package_name', '未知套餐')}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**点数**: {order['total_points']} 点")
                if order.get('bonus', 0) > 0:
                    st.caption(f"（含赠送 {order['bonus']} 点）")
            
            with col2:
                currency_symbol = "¥" if order.get('currency') == "CNY" else "$"
                st.markdown(f"**金额**: {currency_symbol}{order['price']:.2f}")
            
            with col3:
                status = order.get('status', 'pending')
                status_map = {
                    'pending': '⏳ 待支付',
                    'paid': '✅ 已支付',
                    'completed': '✅ 已完成',
                    'cancelled': '❌ 已取消'
                }
                st.markdown(f"**状态**: {status_map.get(status, status)}")
            
            # 订单时间
            created_at = order.get('created_at', 0)
            if created_at:
                from datetime import datetime
                dt = datetime.fromtimestamp(created_at)
                st.caption(f"📅 下单时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """主函数"""
    render_points_store()


if __name__ == "__main__":
    main()

