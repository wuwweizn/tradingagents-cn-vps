# 支付配置快速指南

## 一、准备工作

### 1. 安装支付SDK

```bash
# 支付宝SDK
pip install python-alipay-sdk

# 微信支付SDK（可选）
pip install wechatpayv3

# API服务器依赖（用于回调处理）
pip install Flask
```

### 2. 获取支付账号凭证

#### 支付宝
1. 访问 https://open.alipay.com/
2. 注册并创建应用
3. 获取：
   - APP ID
   - 应用私钥（下载或生成RSA2密钥）
   - 支付宝公钥（在开放平台获取）

#### 微信支付
1. 访问 https://pay.weixin.qq.com/
2. 注册商户账号并完成认证
3. 获取：
   - 商户号（MCH ID）
   - API密钥
   - AppID 和 AppSecret（微信公众平台）

## 二、配置支付接口

### 方式1: Web界面配置（推荐）

1. 登录管理员账户
2. 进入「⚙️ 配置管理」→「支付配置」
3. 填写相应支付方式的配置信息
4. 启用支付方式

### 方式2: 手动配置

编辑 `web/config/payment_config.json`:

```json
{
  "alipay": {
    "enabled": true,
    "app_id": "你的APP_ID",
    "app_secret": "你的应用私钥",
    "app_private_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----",
    "alipay_public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
    "gateway": "https://openapi.alipay.com/gateway.do",
    "notify_url": "https://your-domain.com/api/payment/notify/alipay",
    "return_url": "https://your-domain.com/points/store"
  },
  "wechat": {
    "enabled": true,
    "app_id": "你的APP_ID",
    "app_secret": "你的APP_SECRET",
    "mch_id": "你的商户号",
    "api_key": "你的API密钥",
    "gateway": "https://api.mch.weixin.qq.com",
    "notify_url": "https://your-domain.com/api/payment/notify/wechat",
    "return_url": "https://your-domain.com/points/store"
  }
}
```

## 三、实现真实SDK调用

### 支付宝实现

修改 `web/utils/payment_adapter.py` 中的 `AlipayAdapter.create_payment()` 方法：

```python
from alipay import AliPay
from alipay.utils import AliPayConfig

def create_payment(self, order_id: str, amount: float, subject: str, 
                  description: str = "", **kwargs):
    # 初始化支付宝客户端
    alipay = AliPay(
        appid=self.app_id,
        app_notify_url=self.notify_url,
        app_private_key_string=self.config.get("app_private_key", ""),
        alipay_public_key_string=self.config.get("alipay_public_key", ""),
        sign_type="RSA2",
        debug=False,
        config=AliPayConfig(timeout=15)
    )
    
    # 创建支付订单
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=order_id,
        total_amount=str(amount),
        subject=subject,
        return_url=self.return_url,
        notify_url=self.notify_url
    )
    
    payment_url = f"{self.gateway}?{order_string}"
    
    return True, {
        "payment_url": payment_url,
        "order_id": order_id,
        "method": "get"
    }, None
```

### 微信支付实现

修改 `web/utils/payment_adapter.py` 中的 `WeChatPayAdapter.create_payment()` 方法：

```python
from wechatpayv3 import WeChatPay, WeChatPayType

def create_payment(self, order_id: str, amount: float, subject: str, 
                  description: str = "", **kwargs):
    # 初始化微信支付客户端
    wxpay = WeChatPay(
        wechatpay_type=WeChatPayType.NATIVE,
        mchid=self.mch_id,
        private_key=self.config.get("private_key", ""),
        cert_serial_no=self.config.get("cert_serial_no", ""),
        appid=self.app_id,
        notify_url=self.notify_url,
        cert_dir=self.config.get("cert_dir", ""),
        key=self.config.get("api_key", "")
    )
    
    # 创建订单
    code, message = wxpay.pay(
        description=subject,
        out_trade_no=order_id,
        amount={"total": int(amount * 100)},
        payer={"openid": kwargs.get("openid", "")}
    )
    
    if code == 200:
        qr_code = message.get("code_url", "")
        return True, {
            "qr_code": qr_code,
            "order_id": order_id,
            "method": "qrcode"
        }, None
    else:
        return False, None, message
```

## 四、启动回调API服务

支付平台需要回调地址来处理支付结果。有两种方式：

### 方式1: 独立API服务器（推荐）

```bash
# 启动独立的Flask服务器
python web/api_server.py

# 或使用环境变量配置
PAYMENT_API_PORT=8888 PAYMENT_API_HOST=0.0.0.0 python web/api_server.py
```

### 方式2: 使用Nginx反向代理

如果有Nginx，可以配置反向代理到API服务器。

## 五、测试流程

1. **沙箱测试**
   - 使用支付宝和微信支付的沙箱环境
   - 在沙箱中完成完整支付流程测试

2. **生产环境**
   - 确保回调地址可公网访问
   - 配置HTTPS（必需）
   - 测试真实支付流程

## 六、安全建议

1. **密钥管理**
   - 使用环境变量存储敏感信息
   - 不要在代码中硬编码密钥
   - 定期更换密钥

2. **回调验证**
   - 始终验证回调签名
   - 验证订单金额和状态
   - 防止重复处理订单

3. **日志记录**
   - 记录所有支付操作
   - 保存支付凭证
   - 便于对账和问题排查

## 常见问题

**Q: 回调地址无法访问？**
A: 确保回调地址可公网访问，支持HTTPS，且端口正确。

**Q: 签名验证失败？**
A: 检查密钥格式是否正确（注意换行符），确保使用正确的签名算法。

**Q: 支付成功但点数未到账？**
A: 检查回调处理逻辑，确认订单状态更新和点数充值流程。

## 技术支持

- 支付宝开发文档: https://opendocs.alipay.com/
- 微信支付开发文档: https://pay.weixin.qq.com/wiki/doc/apiv3/index.shtml

