"""
点数套餐管理模块
管理员配置点数套餐
"""

import streamlit as st
import time
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from web.utils.points_package_manager import points_package_manager
    from web.utils.auth_manager import auth_manager
except ImportError:
    from utils.points_package_manager import points_package_manager
    from utils.auth_manager import auth_manager


def render_points_package_management():
    """渲染点数套餐管理页面"""
    st.title("💰 点数套餐管理")
    st.markdown("---")
    
    # 权限检查
    if not auth_manager or not auth_manager.check_permission("admin"):
        st.error("❌ 只有管理员可以管理点数套餐")
        return
    
    # 选项卡
    tab1, tab2, tab3 = st.tabs(["📦 套餐配置", "📋 订单管理", "📊 统计信息"])
    
    with tab1:
        render_packages_config()
    
    with tab2:
        render_orders_management()
    
    with tab3:
        render_statistics()


def render_packages_config():
    """渲染套餐配置"""
    st.subheader("📦 点数套餐配置")
    
    packages = points_package_manager.get_packages(enabled_only=False)
    
    # 显示当前套餐
    st.markdown("**当前套餐列表**")
    if packages:
        for pkg in packages:
            render_package_item(pkg)
    else:
        st.info("暂无套餐配置")
    
    st.markdown("---")
    
    # 添加新套餐
    st.subheader("➕ 添加新套餐")
    with st.form("add_package_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("套餐ID", placeholder="例如: basic, premium")
            new_name = st.text_input("套餐名称", placeholder="例如: 基础套餐")
            new_points = st.number_input("基础点数", min_value=1, value=100, step=10)
        with col2:
            new_bonus = st.number_input("赠送点数", min_value=0, value=0, step=10)
            new_price = st.number_input("价格", min_value=0.0, value=10.0, step=1.0, format="%.2f")
            new_currency = st.selectbox("货币", ["CNY", "USD", "EUR"], index=0)
        
        new_description = st.text_area("套餐描述", placeholder="例如: 适合偶尔使用的用户")
        new_enabled = st.checkbox("启用套餐", value=True)
        
        if st.form_submit_button("添加套餐", type="primary"):
            if new_id and new_name and new_points and new_price:
                package = {
                    "id": new_id,
                    "name": new_name,
                    "points": int(new_points),
                    "bonus": int(new_bonus),
                    "price": float(new_price),
                    "currency": new_currency,
                    "description": new_description or "",
                    "enabled": new_enabled
                }
                if points_package_manager.add_package(package):
                    st.success(f"✅ 套餐 '{new_name}' 添加成功")
                    st.rerun()
                else:
                    st.error("❌ 添加失败，套餐ID可能已存在")
            else:
                st.error("❌ 请填写所有必需字段")
    
    st.markdown("---")
    
    # 重置为默认套餐
    if st.button("🔄 重置为默认套餐", help="恢复系统默认的点数套餐配置"):
        if points_package_manager.reset_to_default():
            st.success("✅ 已重置为默认套餐")
            st.rerun()
        else:
            st.error("❌ 重置失败")


def render_package_item(pkg: dict):
    """渲染单个套餐项"""
    package_id = pkg.get("id")
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            st.markdown(f"**{pkg.get('name')}** ({package_id})")
            st.caption(pkg.get('description', ''))
        
        with col2:
            points = pkg.get('points', 0)
            bonus = pkg.get('bonus', 0)
            total = points + bonus
            currency_symbol = "¥" if pkg.get('currency') == "CNY" else "$"
            if bonus > 0:
                st.markdown(f"{total} 点（{points} + 🎁{bonus}）")
            else:
                st.markdown(f"{total} 点")
            st.caption(f"{currency_symbol}{pkg.get('price', 0):.2f}")
        
        with col3:
            status = "✅ 启用" if pkg.get('enabled', True) else "❌ 禁用"
            st.markdown(status)
        
        with col4:
            if st.button("编辑", key=f"edit_{package_id}"):
                st.session_state[f"editing_package_{package_id}"] = True
        
        # 编辑表单
        if st.session_state.get(f"editing_package_{package_id}", False):
            with st.expander(f"编辑套餐: {pkg.get('name')}", expanded=True):
                with st.form(f"edit_form_{package_id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("套餐名称", value=pkg.get('name', ''))
                        edit_points = st.number_input("基础点数", min_value=1, value=pkg.get('points', 100), step=10)
                        edit_price = st.number_input("价格", min_value=0.0, value=pkg.get('price', 0.0), step=1.0, format="%.2f")
                    with col2:
                        edit_bonus = st.number_input("赠送点数", min_value=0, value=pkg.get('bonus', 0), step=10)
                        edit_currency = st.selectbox("货币", ["CNY", "USD", "EUR"], 
                                                   index=["CNY", "USD", "EUR"].index(pkg.get('currency', 'CNY')))
                        edit_enabled = st.checkbox("启用", value=pkg.get('enabled', True))
                    
                    edit_description = st.text_area("描述", value=pkg.get('description', ''))
                    
                    col_save, col_cancel, col_delete = st.columns([1, 1, 1])
                    with col_save:
                        if st.form_submit_button("保存", type="primary"):
                            updates = {
                                "name": edit_name,
                                "points": int(edit_points),
                                "bonus": int(edit_bonus),
                                "price": float(edit_price),
                                "currency": edit_currency,
                                "description": edit_description,
                                "enabled": edit_enabled
                            }
                            if points_package_manager.update_package(package_id, updates):
                                st.success("✅ 保存成功")
                                st.session_state.pop(f"editing_package_{package_id}", None)
                                st.rerun()
                    
                    with col_cancel:
                        if st.form_submit_button("取消"):
                            st.session_state.pop(f"editing_package_{package_id}", None)
                            st.rerun()
                    
                    with col_delete:
                        if st.form_submit_button("删除", type="secondary"):
                            if points_package_manager.delete_package(package_id):
                                st.success("✅ 删除成功")
                                st.session_state.pop(f"editing_package_{package_id}", None)
                                st.rerun()
        
        st.markdown("---")


def render_orders_management():
    """渲染订单管理"""
    st.subheader("📋 订单管理")
    
    orders = points_package_manager.get_all_orders(limit=100)
    
    if not orders:
        st.info("📝 暂无订单记录")
        return
    
    # 筛选功能
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("订单状态", ["全部", "待支付", "已支付", "已完成", "已取消"], key="status_filter")
    with col2:
        username_filter = st.text_input("用户名筛选", placeholder="输入用户名")
    
    # 筛选订单
    filtered_orders = orders
    if status_filter != "全部":
        status_map = {"待支付": "pending", "已支付": "paid", "已完成": "completed", "已取消": "cancelled"}
        filtered_orders = [o for o in filtered_orders if o.get('status') == status_map.get(status_filter)]
    if username_filter:
        filtered_orders = [o for o in filtered_orders if username_filter.lower() in o.get('username', '').lower()]
    
    # 显示订单
    for order in filtered_orders:
        with st.expander(f"订单 {order['order_id']} - {order.get('username')} - {order.get('package_name')}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"**用户名**: {order.get('username')}")
                st.markdown(f"**套餐**: {order.get('package_name')}")
            
            with col2:
                st.markdown(f"**点数**: {order.get('total_points')} 点")
                currency_symbol = "¥" if order.get('currency') == "CNY" else "$"
                st.markdown(f"**金额**: {currency_symbol}{order.get('price', 0):.2f}")
            
            with col3:
                status = order.get('status', 'pending')
                status_map = {
                    'pending': '⏳ 待支付',
                    'paid': '✅ 已支付',
                    'completed': '✅ 已完成',
                    'cancelled': '❌ 已取消'
                }
                st.markdown(f"**状态**: {status_map.get(status, status)}")
            
            with col4:
                if status == "pending":
                    if st.button("✅ 确认支付", key=f"confirm_{order['order_id']}"):
                        # 确认支付并充值点数
                        if complete_order_manual(order['order_id'], order):
                            st.success("✅ 订单已确认并完成充值")
                            st.rerun()
                elif status == "paid":
                    st.info("已支付，等待完成")
                else:
                    st.info("订单已完成")
            
            # 订单时间
            created_at = order.get('created_at', 0)
            if created_at:
                from datetime import datetime
                dt = datetime.fromtimestamp(created_at)
                st.caption(f"📅 下单时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")


def complete_order_manual(order_id: str, order: dict) -> bool:
    """手动完成订单（管理员操作）"""
    try:
        # 先增加用户点数
        username = order.get('username')
        total_points = order.get('total_points', 0)
        if auth_manager.add_user_points(username, total_points):
            # 完成订单
            if points_package_manager.complete_order(order_id):
                # 更新订单状态为已完成
                points_package_manager.update_order_status(order_id, "completed", completed_at=time.time())
                return True
        return False
    except Exception as e:
        st.error(f"❌ 完成订单失败: {e}")
        return False


def render_statistics():
    """渲染统计信息"""
    st.subheader("📊 点数销售统计")
    
    orders = points_package_manager.get_all_orders()
    
    if not orders:
        st.info("📝 暂无统计数据")
        return
    
    # 统计计算
    total_orders = len(orders)
    completed_orders = len([o for o in orders if o.get('status') in ['paid', 'completed']])
    total_revenue = sum(o.get('price', 0) for o in orders if o.get('status') in ['paid', 'completed'])
    total_points_sold = sum(o.get('total_points', 0) for o in orders if o.get('status') in ['paid', 'completed'])
    
    # 显示统计指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总订单数", total_orders)
    with col2:
        st.metric("已完成订单", completed_orders)
    with col3:
        st.metric("总营收", f"¥{total_revenue:.2f}")
    with col4:
        st.metric("已售点数", f"{total_points_sold:,}")
    
    st.markdown("---")
    
    # 按套餐统计
    st.markdown("**按套餐统计**")
    package_stats = {}
    for order in orders:
        if order.get('status') in ['paid', 'completed']:
            pkg_id = order.get('package_id')
            if pkg_id not in package_stats:
                package_stats[pkg_id] = {"count": 0, "revenue": 0, "points": 0}
            package_stats[pkg_id]["count"] += 1
            package_stats[pkg_id]["revenue"] += order.get('price', 0)
            package_stats[pkg_id]["points"] += order.get('total_points', 0)
    
    if package_stats:
        import pandas as pd
        stats_data = []
        for pkg_id, stats in package_stats.items():
            pkg = points_package_manager.get_package(pkg_id)
            stats_data.append({
                "套餐": pkg.get('name', pkg_id) if pkg else pkg_id,
                "订单数": stats["count"],
                "营收": f"¥{stats['revenue']:.2f}",
                "售出点数": stats["points"]
            })
        df = pd.DataFrame(stats_data)
        st.dataframe(df, use_container_width=True)


def main():
    """主函数"""
    render_points_package_management()


if __name__ == "__main__":
    main()

