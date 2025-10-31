"""
支付回调处理API
处理支付宝和微信支付的异步回调通知
"""

import json
import logging
import time
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from web.utils.payment_adapter import payment_manager
    from web.utils.points_package_manager import points_package_manager
    from web.utils.auth_manager import auth_manager
except ImportError:
    from utils.payment_adapter import payment_manager
    from utils.points_package_manager import points_package_manager
    from utils.auth_manager import auth_manager

logger = logging.getLogger(__name__)


def handle_alipay_notify(request_data: dict) -> dict:
    """
    处理支付宝回调通知
    
    Args:
        request_data: 支付宝回调的请求数据
        
    Returns:
        处理结果字典
    """
    try:
        # 验证回调
        success, order_info, error = payment_manager.verify_notify("alipay", request_data)
        
        if not success:
            logger.error(f"❌ 支付宝回调验证失败: {error}")
            return {
                "success": False,
                "message": error or "验证失败"
            }
        
        # 处理订单
        order_id = order_info.get("order_id")
        if not order_id:
            return {
                "success": False,
                "message": "订单号缺失"
            }
        
        # 完成订单和充值点数
        result = complete_order_and_recharge(order_id, order_info)
        
        if result:
            # 返回支付宝要求的格式
            return {
                "success": True,
                "alipay_response": "success"  # 支付宝要求返回 "success"
            }
        else:
            return {
                "success": False,
                "message": "订单处理失败",
                "alipay_response": "fail"
            }
            
    except Exception as e:
        logger.error(f"❌ 处理支付宝回调异常: {e}")
        return {
            "success": False,
            "message": str(e),
            "alipay_response": "fail"
        }


def handle_wechat_notify(request_data: dict) -> dict:
    """
    处理微信支付回调通知
    
    Args:
        request_data: 微信支付回调的请求数据
        
    Returns:
        处理结果字典
    """
    try:
        # 验证回调
        success, order_info, error = payment_manager.verify_notify("wechat", request_data)
        
        if not success:
            logger.error(f"❌ 微信支付回调验证失败: {error}")
            return {
                "success": False,
                "message": error or "验证失败",
                "wechat_response": "<xml><return_code><![CDATA[FAIL]]></return_code></xml>"
            }
        
        # 处理订单
        order_id = order_info.get("order_id")
        if not order_id:
            return {
                "success": False,
                "message": "订单号缺失",
                "wechat_response": "<xml><return_code><![CDATA[FAIL]]></return_code></xml>"
            }
        
        # 完成订单和充值点数
        result = complete_order_and_recharge(order_id, order_info)
        
        if result:
            # 返回微信支付要求的XML格式
            return {
                "success": True,
                "wechat_response": "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"
            }
        else:
            return {
                "success": False,
                "message": "订单处理失败",
                "wechat_response": "<xml><return_code><![CDATA[FAIL]]></return_code></xml>"
            }
            
    except Exception as e:
        logger.error(f"❌ 处理微信支付回调异常: {e}")
        return {
            "success": False,
            "message": str(e),
            "wechat_response": "<xml><return_code><![CDATA[FAIL]]></return_code></xml>"
        }


def complete_order_and_recharge(order_id: str, order_info: dict) -> bool:
    """
    完成订单并充值点数
    
    Args:
        order_id: 订单号
        order_info: 订单信息
        
    Returns:
        是否成功
    """
    try:
        # 获取订单
        orders = points_package_manager.get_all_orders(limit=10000)
        order = None
        for o in orders:
            if o.get("order_id") == order_id:
                order = o
                break
        
        if not order:
            logger.error(f"❌ 订单不存在: {order_id}")
            return False
        
        # 检查订单状态
        if order.get("status") != "pending":
            logger.warning(f"⚠️ 订单状态异常: {order.get('status')}")
            return False
        
        # 完成订单
        if points_package_manager.complete_order(order_id):
            # 充值点数
            username = order.get("username")
            total_points = order.get("total_points", 0)
            
            if auth_manager.add_user_points(username, total_points):
                # 更新订单状态为已完成
                points_package_manager.update_order_status(
                    order_id, 
                    "completed", 
                    completed_at=time.time()
                )
                logger.info(f"✅ 订单 {order_id} 支付成功，已为用户 {username} 充值 {total_points} 点")
                return True
            else:
                logger.error(f"❌ 充值点数失败: {username}, {total_points}")
                return False
        else:
            logger.error(f"❌ 完成订单失败: {order_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 完成订单和充值异常: {e}")
        return False


# 注意：这个模块主要用于外部API调用
# 如果使用Streamlit，需要创建独立的API服务或使用Streamlit的API功能

