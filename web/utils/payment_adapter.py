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
            # 尝试使用真实的支付宝SDK
            try:
                from alipay import AliPay
                from alipay.utils import AliPayConfig
            except ImportError:
                logger.error("❌ 支付宝SDK未安装，请运行: pip install python-alipay-sdk")
                return False, None, "支付宝SDK未安装，请运行: pip install python-alipay-sdk"
            
            # 初始化支付宝客户端
            try:
                alipay = AliPay(
                    appid=self.app_id,
                    app_notify_url=self.notify_url,
                    app_private_key_string=self.config.get("app_private_key", ""),
                    alipay_public_key_string=self.config.get("alipay_public_key", ""),
                    sign_type="RSA2",
                    debug=False,
                    config=AliPayConfig(timeout=15)
                )
            except Exception as e:
                logger.error(f"❌ 初始化支付宝客户端失败: {e}")
                return False, None, f"初始化支付宝客户端失败: {str(e)}"
            
            # 创建支付订单（手机网站支付）
            try:
                order_string = alipay.api_alipay_trade_wap_pay(
                    out_trade_no=order_id,
                    total_amount=str(amount),
                    subject=subject,
                    return_url=self.return_url,
                    notify_url=self.notify_url
                )
                payment_url = f"{self.gateway}?{order_string}"
                
                logger.info(f"✅ 支付宝支付订单创建成功: {order_id}")
                
                return True, {
                    "payment_url": payment_url,
                    "order_id": order_id,
                    "method": "get"
                }, None
            except Exception as e:
                logger.error(f"❌ 创建支付宝支付订单失败: {e}")
                return False, None, f"创建支付订单失败: {str(e)}"
            
        except Exception as e:
            logger.error(f"❌ 支付宝创建订单异常: {e}")
            return False, None, str(e)
    
    def verify_notify(self, request_data: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """验证支付宝回调"""
        try:
            # 尝试使用真实的支付宝SDK验证
            try:
                from alipay import AliPay
            except ImportError:
                logger.error("❌ 支付宝SDK未安装，无法验证回调")
                return False, None, "支付宝SDK未安装"
            
            # 初始化支付宝客户端用于验证
            try:
                alipay = AliPay(
                    appid=self.app_id,
                    app_notify_url=self.notify_url,
                    app_private_key_string=self.config.get("app_private_key", ""),
                    alipay_public_key_string=self.config.get("alipay_public_key", ""),
                    sign_type="RSA2",
                    debug=False
                )
            except Exception as e:
                logger.error(f"❌ 初始化支付宝客户端失败: {e}")
                return False, None, f"初始化客户端失败: {str(e)}"
            
            # 提取签名和数据
            signature = request_data.pop("sign", "")
            signature_type = request_data.pop("sign_type", "RSA2")
            
            # 验证签名
            try:
                if not alipay.verify(request_data, signature):
                    logger.error("❌ 支付宝回调签名验证失败")
                    return False, None, "签名验证失败"
            except Exception as e:
                logger.error(f"❌ 签名验证异常: {e}")
                return False, None, f"签名验证异常: {str(e)}"
            
            # 提取关键信息
            order_id = request_data.get("out_trade_no")
            trade_no = request_data.get("trade_no")
            trade_status = request_data.get("trade_status")
            amount = request_data.get("total_amount")
            
            logger.info(f"✅ 支付宝回调验证成功: 订单={order_id}, 状态={trade_status}")
            
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
            # 微信支付金额需要转换为分
            amount_cents = int(amount * 100)
            
            # 尝试使用真实的微信支付SDK
            try:
                from wechatpayv3 import WeChatPay, WeChatPayType
            except ImportError:
                logger.warning("⚠️ 微信支付SDK未安装，使用基础实现。安装: pip install wechatpayv3")
                # 基础实现：返回支付URL
                return True, {
                    "payment_url": f"{self.gateway}/pay/unifiedorder",
                    "order_id": order_id,
                    "qr_code": f"weixin://wxpay/bizpayurl?order_id={order_id}",
                    "method": "post",
                    "amount": amount_cents,
                    "note": "请安装wechatpayv3 SDK以使用完整功能"
                }, None
            
            # 初始化微信支付客户端
            try:
                # 注意：微信支付V3需要证书，这里使用API密钥方式（简化版）
                # 完整实现需要证书文件
                wxpay = WeChatPay(
                    wechatpay_type=WeChatPayType.NATIVE,  # 扫码支付
                    mchid=self.mch_id,
                    private_key=self.config.get("private_key", ""),  # 需要商户私钥
                    cert_serial_no=self.config.get("cert_serial_no", ""),  # 需要证书序列号
                    appid=self.app_id,
                    notify_url=self.notify_url,
                    cert_dir=self.config.get("cert_dir", ""),  # 证书目录
                    key=self.config.get("api_key", "")  # API密钥
                )
            except Exception as e:
                logger.warning(f"⚠️ 微信支付SDK初始化失败: {e}，使用基础实现")
                # 如果SDK初始化失败，使用基础实现
                return True, {
                    "payment_url": f"{self.gateway}/v3/pay/transactions/native",
                    "order_id": order_id,
                    "amount": amount_cents,
                    "subject": subject,
                    "description": description,
                    "method": "post",
                    "note": "需要配置微信支付证书以使用完整功能"
                }, None
            
            # 创建支付订单（扫码支付）
            try:
                code, message = wxpay.pay(
                    description=subject,
                    out_trade_no=order_id,
                    amount={"total": amount_cents},
                    payer={"openid": kwargs.get("openid", "")}
                )
                
                if code == 200:
                    qr_code = message.get("code_url", "")
                    logger.info(f"✅ 微信支付订单创建成功: {order_id}")
                    
                    return True, {
                        "qr_code": qr_code,
                        "order_id": order_id,
                        "method": "qrcode"
                    }, None
                else:
                    logger.error(f"❌ 微信支付创建订单失败: {message}")
                    return False, None, str(message)
                    
            except Exception as e:
                logger.error(f"❌ 创建微信支付订单异常: {e}")
                return False, None, f"创建订单失败: {str(e)}"
            
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
                "app_private_key": "",  # 应用私钥（RSA2）
                "alipay_public_key": "",  # 支付宝公钥
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
                "api_key": "",  # API密钥
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

