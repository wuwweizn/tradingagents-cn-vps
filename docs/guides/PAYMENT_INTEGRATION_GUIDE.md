# 支付接入指南

本指南将帮助您接入真实的支付功能，支持支付宝和微信支付。

## 前置准备

### 1. 安装支付SDK

```bash
# 支付宝SDK
pip install python-alipay-sdk

# 微信支付SDK（可选，根据需要）
pip install wechatpayv3
```

### 2. 获取支付账号

#### 支付宝
1. 注册支付宝开放平台账号: https://open.alipay.com/
2. 创建应用并获取：
   - APP ID
   - 应用私钥（RSA2）
   - 支付宝公钥
3. 配置回调地址: `https://your-domain.com/api/payment/notify/alipay`

#### 微信支付
1. 注册微信支付商户平台: https://pay.weixin.qq.com/
2. 获取：
   - 商户号（MCH ID）
   - API密钥
   - AppID 和 AppSecret（需要在微信公众平台获取）
3. 配置回调地址: `https://your-domain.com/api/payment/notify/wechat`

## 配置步骤

### 1. 在Web界面配置支付

1. 登录管理员账户
2. 进入「⚙️ 配置管理」→「支付配置」
3. 填写支付接口配置信息
4. 启用对应的支付方式

### 2. 配置回调地址

支付平台需要在您配置的回调地址上能够访问到回调处理接口。

**回调地址格式：**
- 支付宝: `https://your-domain.com/api/payment/notify/alipay`
- 微信支付: `https://your-domain.com/api/payment/notify/wechat`

## 实现真实支付SDK调用

### 支付宝实现示例

修改 `web/utils/payment_adapter.py` 中的 `AlipayAdapter` 类：

```python
from alipay import AliPay
from alipay.utils import AliPayConfig

class AlipayAdapter(PaymentAdapter):
    def __init__(self, config: Dict):
        super().__init__(config)
        # 初始化支付宝客户端
        self.alipay = AliPay(
            appid=self.app_id,
            app_notify_url=self.notify_url,
            app_private_key_string=config.get("app_private_key", ""),
            alipay_public_key_string=config.get("alipay_public_key", ""),
            sign_type="RSA2",
            debug=config.get("debug", False),
            config=AliPayConfig(timeout=15)
        )
    
    def create_payment(self, order_id: str, amount: float, subject: str, 
                      description: str = "", **kwargs):
        # 手机网站支付
        order_string = self.alipay.api_alipay_trade_wap_pay(
            out_trade_no=order_id,
            total_amount=str(amount),
            subject=subject,
            return_url=self.return_url,
            notify_url=self.notify_url
        )
        
        # 构建支付URL
        payment_url = f"{self.gateway}?{order_string}"
        
        return True, {
            "payment_url": payment_url,
            "order_id": order_id,
            "method": "get"
        }, None
    
    def verify_notify(self, request_data: Dict):
        # 验证签名
        signature = request_data.pop("sign", "")
        if not self.alipay.verify(request_data, signature):
            return False, None, "签名验证失败"
        
        # 处理订单
        order_id = request_data.get("out_trade_no")
        trade_status = request_data.get("trade_status")
        
        if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            return True, {
                "order_id": order_id,
                "trade_no": request_data.get("trade_no"),
                "amount": float(request_data.get("total_amount", 0)),
                "status": "paid"
            }, None
        else:
            return False, None, f"订单状态异常: {trade_status}"
```

### 微信支付实现示例

修改 `web/utils/payment_adapter.py` 中的 `WeChatPayAdapter` 类：

```python
from wechatpayv3 import WeChatPay, WeChatPayType

class WeChatPayAdapter(PaymentAdapter):
    def __init__(self, config: Dict):
        super().__init__(config)
        # 初始化微信支付客户端
        self.wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.NATIVE,  # 扫码支付
            mchid=self.mch_id,
            private_key=config.get("private_key", ""),
            cert_serial_no=config.get("cert_serial_no", ""),
            appid=self.app_id,
            notify_url=self.notify_url,
            cert_dir=config.get("cert_dir", ""),
            key=config.get("api_key", "")
        )
    
    def create_payment(self, order_id: str, amount: float, subject: str, 
                      description: str = "", **kwargs):
        # 创建订单
        code, message = self.wxpay.pay(
            description=subject,
            out_trade_no=order_id,
            amount={"total": int(amount * 100)},  # 转换为分
            payer={"openid": kwargs.get("openid", "")}
        )
        
        if code == 200:
            # 获取支付二维码
            qr_code = message.get("code_url", "")
            return True, {
                "qr_code": qr_code,
                "order_id": order_id,
                "method": "qrcode"
            }, None
        else:
            return False, None, message
    
    def verify_notify(self, request_data: Dict):
        # 验证签名和解密数据
        result = self.wxpay.callback(request_data.get("headers", {}), request_data.get("body", ""))
        
        if result:
            return True, {
                "order_id": result.get("out_trade_no"),
                "transaction_id": result.get("transaction_id"),
                "amount": float(result.get("amount", {}).get("total", 0)) / 100,
                "status": "paid"
            }, None
        else:
            return False, None, "验证失败"
```

## 设置回调API服务

由于Streamlit是Web应用，回调处理需要独立的API服务。有两种方案：

### 方案1: 使用Flask/FastAPI独立服务

创建一个独立的API服务处理回调：

```python
# api_server.py
from flask import Flask, request, jsonify
from web.api.payment_callback import handle_alipay_notify, handle_wechat_notify

app = Flask(__name__)

@app.route('/api/payment/notify/alipay', methods=['POST', 'GET'])
def alipay_notify():
    data = request.form.to_dict() if request.method == 'POST' else request.args.to_dict()
    result = handle_alipay_notify(data)
    return result.get("alipay_response", "fail")

@app.route('/api/payment/notify/wechat', methods=['POST'])
def wechat_notify():
    data = request.get_data(as_text=True)
    result = handle_wechat_notify({"body": data})
    return result.get("wechat_response", "")
```

### 方案2: 使用Streamlit的API功能

如果使用Streamlit Cloud或支持API的部署方式，可以创建API端点。

## 测试支付

1. **沙箱环境测试**
   - 支付宝和微信支付都提供沙箱测试环境
   - 先在沙箱环境中测试完整流程

2. **生产环境部署**
   - 确保回调地址可公网访问
   - 配置HTTPS（支付平台要求）
   - 验证回调签名

## 安全注意事项

1. **密钥安全**
   - 不要将密钥提交到代码仓库
   - 使用环境变量或密钥管理服务
   - 定期更换密钥

2. **回调验证**
   - 始终验证回调签名
   - 验证订单金额和状态
   - 防止重复处理

3. **日志记录**
   - 记录所有支付操作
   - 保存支付凭证
   - 便于对账和问题排查

## 常见问题

### Q: 回调地址无法访问？
A: 确保回调地址可公网访问，且支持HTTPS。

### Q: 签名验证失败？
A: 检查密钥配置是否正确，注意密钥格式（可能包含换行符）。

### Q: 支付成功但点数未到账？
A: 检查回调处理逻辑，确认订单状态更新和点数充值流程。

## 支持与帮助

如有问题，请查看：
- 支付宝开发文档: https://opendocs.alipay.com/
- 微信支付开发文档: https://pay.weixin.qq.com/wiki/doc/apiv3/index.shtml

