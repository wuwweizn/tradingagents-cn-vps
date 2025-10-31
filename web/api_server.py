#!/usr/bin/env python3
"""
支付回调API服务器
独立运行，用于处理支付平台的回调通知
"""

from flask import Flask, request, jsonify
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web.api.payment_callback import handle_alipay_notify, handle_wechat_notify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/api/payment/notify/alipay', methods=['POST', 'GET'])
def alipay_notify():
    """处理支付宝回调"""
    try:
        # 支付宝回调可能是GET或POST
        if request.method == 'POST':
            data = request.form.to_dict()
        else:
            data = request.args.to_dict()
        
        logger.info(f"📥 收到支付宝回调: {data}")
        
        result = handle_alipay_notify(data)
        
        # 支付宝要求返回 "success" 或 "fail"
        response_text = result.get("alipay_response", "fail")
        logger.info(f"📤 支付宝回调响应: {response_text}")
        
        return response_text, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        logger.error(f"❌ 处理支付宝回调异常: {e}")
        return "fail", 500


@app.route('/api/payment/notify/wechat', methods=['POST'])
def wechat_notify():
    """处理微信支付回调"""
    try:
        # 微信支付回调是XML格式
        xml_data = request.get_data(as_text=True)
        headers = dict(request.headers)
        
        logger.info(f"📥 收到微信支付回调: {xml_data[:200]}...")
        
        # 解析XML数据（简化处理）
        # 实际应该使用XML解析库
        request_data = {
            "body": xml_data,
            "headers": headers
        }
        
        result = handle_wechat_notify(request_data)
        
        # 微信支付要求返回XML格式
        response_xml = result.get("wechat_response", 
                           "<xml><return_code><![CDATA[FAIL]]></return_code></xml>")
        logger.info(f"📤 微信支付回调响应: {response_xml}")
        
        return response_xml, 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        logger.error(f"❌ 处理微信支付回调异常: {e}")
        return "<xml><return_code><![CDATA[FAIL]]></return_code></xml>", 500


@app.route('/api/payment/status/<order_id>', methods=['GET'])
def check_order_status(order_id):
    """查询订单支付状态（用于前端轮询）"""
    try:
        from web.utils.points_package_manager import points_package_manager
        
        orders = points_package_manager.get_all_orders(limit=10000)
        order = None
        for o in orders:
            if o.get("order_id") == order_id:
                order = o
                break
        
        if not order:
            return jsonify({"success": False, "message": "订单不存在"}), 404
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "status": order.get("status", "unknown"),
            "points": order.get("total_points", 0)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 查询订单状态失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    import os
    port = int(os.getenv('PAYMENT_API_PORT', 8888))
    host = os.getenv('PAYMENT_API_HOST', '0.0.0.0')
    
    logger.info(f"🚀 启动支付回调API服务器: http://{host}:{port}")
    logger.info(f"📋 支付宝回调地址: http://{host}:{port}/api/payment/notify/alipay")
    logger.info(f"📋 微信支付回调地址: http://{host}:{port}/api/payment/notify/wechat")
    
    app.run(host=host, port=port, debug=False)

