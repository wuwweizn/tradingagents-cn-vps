"""
支付适配器
支持多种支付方式的统一接口
"""

import json
import logging
import hashlib
import hmac
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from abc import ABC, abstractmethod
import urllib.parse

# 注意：真实支付功能需要安装对应的SDK
# 支付宝: pip install python-alipay-sdk
# 微信支付: pip install wechatpayv3

logger = logging.getLogger(__name__)


class PaymentAdapter(ABC):
    """支付适配器基类"""
    
    def __init__(self, config: Dict):
        """
        初始化支付适配器
        
        Args:
            config: 支付配置字典，包含 app_id, app_secret, notify_url 等
        """
        self.config = config
        self.app_id = config.get("app_id", "")
        self.app_secret = config.get("app_secret", "")
        self.notify_url = config.get("notify_url", "")
        self.return_url = config.get("return_url", "")
        self.enabled = config.get("enabled", False)
    
    @abstractmethod
    def create_payment(self, order_id: str, amount: float, subject: str, 
                      description: str = "", **kwargs) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        创建支付订单
        
        Args:
            order_id: 订单号
            amount: 支付金额
            subject: 订单标题
            description: 订单描述
            **kwargs: 其他参数
            
        Returns:
            (成功标志, 支付信息字典, 错误信息)
        """
        pass
    
    @abstractmethod
    def verify_notify(self, request_data: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        验证支付回调
        
        Args:
            request_data: 回调请求数据
            
        Returns:
            (验证成功标志, 订单信息字典, 错误信息)
        """
        pass
    
    @abstractmethod
    def query_order(self, order_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        查询订单状态
        
        Args:
            order_id: 订单号
            
        Returns:
            (成功标志, 订单信息字典, 错误信息)
        """
        pass


class AlipayAdapter(PaymentAdapter):
    """支付宝支付适配器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.gateway = config.get("gateway", "https://openapi.alipay.com/gateway.do")
        self.format = "JSON"
        self.charset = "utf-8"
        self.sign_type = "RSA2"
        self.version = "1.0"
    
    def create_payment(self, order_id: str, amount: float, subject: str,
                      description: str = "", **kwargs) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        创建支付宝支付订单
        返回支付URL或二维码链接
        """
        try:
            # 构建支付参数
            biz_content = {
                "out_trade_no": order_id,
                "total_amount": f"{amount:.2f}",
                "subject": subject,
                "body": description or subject,
                "product_code": "QUICK_MSECURITY_PAY",  # 手机网站支付
            }
            
            # 这里应该调用支付宝API创建订单
            # 由于需要真实的支付宝SDK，这里提供一个框架
            
            # 实际实现需要使用 alipay-sdk-python
            # 安装: pip install python-alipay-sdk
            # 
            # from alipay import AliPay
            # from alipay.utils import AliPayConfig
            # 
            # alipay = AliPay(
            #     appid=self.app_id,
            #     app_notify_url=self.notify_url,
            #     app_private_key_string=self.config.get("app_private_key", ""),
            #     alipay_public_key_string=self.config.get("alipay_public_key", ""),
            #     sign_type="RSA2",
            #     debug=False,
            #     config=AliPayConfig(timeout=15)
            # )
            # 
            # order_string = alipay.api_alipay_trade_wap_pay(
            #     out_trade_no=order_id,
            #     total_amount=str(amount),
            #     subject=subject,
            #     return_url=self.return_url,
            #     notify_url=self.notify_url
            # )
            # payment_url = f"{self.gateway}?{order_string}"
            
            # 临时示例（需要替换为真实实现）
            payment_url = f"{self.gateway}?order_id={order_id}&amount={amount}"
            
            # TODO: 替换为真实的支付宝SDK调用
            logger.warning("⚠️ 使用示例支付URL，请接入真实支付宝SDK")
            
            return True, {
                "payment_url": payment_url,
                "order_id": order_id,
                "method": "get"  # 或 "post"
            }, None
            
        except Exception as e:
            logger.error(f"❌ 支付宝创建订单失败: {e}")
            return False, None, str(e)
    
    def verify_notify(self, request_data: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """验证支付宝回调"""
        try:
            # 实际实现需要使用支付宝的签名验证
            # 安装: pip install python-alipay-sdk
            # 
            # from alipay import AliPay
            # alipay = AliPay(...)  # 初始化客户端
            # 
            # # 验证签名
            # signature = request_data.pop("sign", "")
            # if not alipay.verify(request_data, signature):
            #     return False, None, "签名验证失败"
            
            # 提取关键信息
            order_id = request_data.get("out_trade_no")
            trade_no = request_data.get("trade_no")
            trade_status = request_data.get("trade_status")
            amount = request_data.get("total_amount")
            
            # TODO: 实现真实的签名验证
            logger.warning("⚠️ 未实现签名验证，请接入真实支付宝SDK")
            
            # 验证订单状态
            if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
                return True, {
                    "order_id": order_id,
                    "trade_no": trade_no,
                    "amount": float(amount) if amount else 0,
                    "status": "paid"
                }, None
            else:
                return False, None, f"订单状态异常: {trade_status}"
                
        except Exception as e:
            logger.error(f"❌ 支付宝回调验证失败: {e}")
            return False, None, str(e)
    
    def query_order(self, order_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """查询支付宝订单"""
        try:
            # 实际实现需要使用支付宝SDK查询订单
            # 这里提供一个框架
            
            return True, {
                "order_id": order_id,
                "status": "unknown"
            }, None
            
        except Exception as e:
            logger.error(f"❌ 查询支付宝订单失败: {e}")
            return False, None, str(e)


class WeChatPayAdapter(PaymentAdapter):
    """微信支付适配器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.mch_id = config.get("mch_id", "")  # 商户号
        self.gateway = config.get("gateway", "https://api.mch.weixin.qq.com")
    
    def create_payment(self, order_id: str, amount: float, subject: str,
                      description: str = "", **kwargs) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """创建微信支付订单"""
        try:
            # 构建支付参数
            # 实际实现需要使用微信支付SDK
            # from wechatpayv3 import WeChatPay
            
            # 微信支付金额需要转换为分
            amount_cents = int(amount * 100)
            
            # 创建支付订单（需要真实实现）
            payment_url = f"{self.gateway}/pay/unifiedorder"
            
            return True, {
                "payment_url": payment_url,
                "order_id": order_id,
                "qr_code": f"weixin://wxpay/bizpayurl?order_id={order_id}",  # 示例
                "method": "post"
            }, None
            
        except Exception as e:
            logger.error(f"❌ 微信支付创建订单失败: {e}")
            return False, None, str(e)
    
    def verify_notify(self, request_data: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """验证微信支付回调"""
        try:
            # 实际实现需要使用微信支付的签名验证
            # 提取关键信息
            order_id = request_data.get("out_trade_no")
            transaction_id = request_data.get("transaction_id")
            return_code = request_data.get("return_code")
            result_code = request_data.get("result_code")
            amount = request_data.get("total_fee")
            
            # 验证签名
            # if not verify_sign(request_data):
            #     return False, None, "签名验证失败"
            
            if return_code == "SUCCESS" and result_code == "SUCCESS":
                return True, {
                    "order_id": order_id,
                    "transaction_id": transaction_id,
                    "amount": float(amount) / 100 if amount else 0,  # 转换为元
                    "status": "paid"
                }, None
            else:
                return False, None, f"支付失败: {return_code}/{result_code}"
                
        except Exception as e:
            logger.error(f"❌ 微信支付回调验证失败: {e}")
            return False, None, str(e)
    
    def query_order(self, order_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """查询微信支付订单"""
        try:
            # 实际实现需要使用微信支付SDK查询订单
            return True, {
                "order_id": order_id,
                "status": "unknown"
            }, None
            
        except Exception as e:
            logger.error(f"❌ 查询微信支付订单失败: {e}")
            return False, None, str(e)


class PaymentManager:
    """支付管理器"""
    
    def __init__(self):
        config_dir = Path(__file__).parent.parent / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = config_dir / "payment_config.json"
        
        # 默认配置
        self.default_config = {
            "alipay": {
                "enabled": False,
                "app_id": "",
                "app_secret": "",
                "gateway": "https://openapi.alipay.com/gateway.do",
                "notify_url": "",
                "return_url": "",
                "sign_type": "RSA2"
            },
            "wechat": {
                "enabled": False,
                "app_id": "",
                "app_secret": "",
                "mch_id": "",
                "gateway": "https://api.mch.weixin.qq.com",
                "notify_url": "",
                "return_url": ""
            }
        }
        
        self._ensure_config_file()
        self._adapters = {}
        self._load_adapters()
    
    def _ensure_config_file(self):
        """确保配置文件存在"""
        if not self.config_file.exists():
            self._save_config(self.default_config.copy())
            logger.info(f"✅ 创建支付配置文件: {self.config_file}")
    
    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    merged = self.default_config.copy()
                    merged.update(config)
                    return merged
            return self.default_config.copy()
        except Exception as e:
            logger.error(f"❌ 加载支付配置失败: {e}")
            return self.default_config.copy()
    
    def _save_config(self, config: Dict) -> bool:
        """保存配置"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"❌ 保存支付配置失败: {e}")
            return False
    
    def _load_adapters(self):
        """加载支付适配器"""
        config = self._load_config()
        
        if config.get("alipay", {}).get("enabled", False):
            self._adapters["alipay"] = AlipayAdapter(config.get("alipay", {}))
        
        if config.get("wechat", {}).get("enabled", False):
            self._adapters["wechat"] = WeChatPayAdapter(config.get("wechat", {}))
    
    def get_available_payment_methods(self) -> list:
        """获取可用的支付方式"""
        return list(self._adapters.keys())
    
    def get_adapter(self, method: str) -> Optional[PaymentAdapter]:
        """获取支付适配器"""
        return self._adapters.get(method)
    
    def create_payment(self, method: str, order_id: str, amount: float, 
                      subject: str, description: str = "") -> Tuple[bool, Optional[Dict], Optional[str]]:
        """创建支付"""
        adapter = self.get_adapter(method)
        if not adapter:
            return False, None, f"支付方式 {method} 不可用或未配置"
        
        return adapter.create_payment(order_id, amount, subject, description)
    
    def verify_notify(self, method: str, request_data: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """验证支付回调"""
        adapter = self.get_adapter(method)
        if not adapter:
            return False, None, f"支付方式 {method} 不可用或未配置"
        
        return adapter.verify_notify(request_data)
    
    def query_order(self, method: str, order_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """查询订单"""
        adapter = self.get_adapter(method)
        if not adapter:
            return False, None, f"支付方式 {method} 不可用或未配置"
        
        return adapter.query_order(order_id)
    
    def update_config(self, method: str, config: Dict) -> bool:
        """更新支付配置"""
        current_config = self._load_config()
        if method in current_config:
            current_config[method].update(config)
            if self._save_config(current_config):
                self._load_adapters()  # 重新加载适配器
                return True
        return False
    
    def get_config(self, method: str = None) -> Dict:
        """获取支付配置"""
        config = self._load_config()
        if method:
            return config.get(method, {})
        return config


# 全局实例
payment_manager = PaymentManager()

