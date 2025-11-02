# 支付配置完成指南

## ✅ 已完成的配置

支付系统已经成功配置了您的真实支付账号信息：

### 支付宝配置
- ✅ APP ID: 2021006105603730
- ✅ 应用私钥: 已配置
- ✅ 支付宝公钥: 已配置
- ✅ 支付状态: 已启用

### 微信支付配置
- ✅ APP ID: wx168f444c15a163a9
- ✅ 商户号: 1716671062
- ✅ API密钥: 已配置
- ✅ APP Secret: 已配置
- ✅ 支付状态: 已启用

## 📋 下一步操作

### 1. 配置回调地址（重要！）

支付平台需要在您的服务器上配置回调地址，用于接收支付结果通知。

#### 方式1: 在Web界面配置（推荐）

1. 登录管理员账户
2. 进入「⚙️ 配置管理」→「支付配置」
3. 分别填写支付宝和微信支付的回调地址：
   - **回调通知地址**: `https://your-domain.com/api/payment/notify/{method}`
     - 支付宝: `https://your-domain.com/api/payment/notify/alipay`
     - 微信支付: `https://your-domain.com/api/payment/notify/wechat`
   - **返回地址**: `https://your-domain.com/points/store`（支付完成后的跳转地址）

#### 方式2: 直接编辑配置文件

编辑 `web/config/payment_config.json`：

```json
{
  "alipay": {
    "notify_url": "https://your-domain.com/api/payment/notify/alipay",
    "return_url": "https://your-domain.com/points/store"
  },
  "wechat": {
    "notify_url": "https://your-domain.com/api/payment/notify/wechat",
    "return_url": "https://your-domain.com/points/store"
  }
}
```

### 2. 启动支付回调API服务

支付回调需要一个独立的API服务器来处理支付平台的通知。

```bash
# 启动回调API服务器
python web/api_server.py

# 或指定端口
PAYMENT_API_PORT=8888 python web/api_server.py
```

**注意**: 如果使用Nginx等反向代理，需要将回调地址的请求转发到API服务器。

### 3. 在支付平台配置回调地址

#### 支付宝开放平台
1. 登录 https://open.alipay.com/
2. 进入应用管理
3. 配置"服务器异步通知页面路径"和"页面跳转同步通知页面路径"
   - 异步通知: `https://your-domain.com/api/payment/notify/alipay`
   - 同步通知: `https://your-domain.com/points/store`

#### 微信支付商户平台
1. 登录 https://pay.weixin.qq.com/
2. 进入"产品中心" → "开发配置"
3. 配置"支付回调URL": `https://your-domain.com/api/payment/notify/wechat`

### 4. 安装支付SDK（如需真实支付）

如果需要接入真实的支付功能，需要安装对应的SDK：

```bash
# 支付宝SDK
pip install python-alipay-sdk

# 微信支付SDK（可选）
pip install wechatpayv3

# API服务器依赖
pip install Flask
```

### 5. 实现真实SDK调用

当前支付适配器使用的是示例代码。要接入真实支付，需要：

1. 修改 `web/utils/payment_adapter.py`
2. 取消注释并实现真实的SDK调用代码
3. 参考 `docs/guides/PAYMENT_INTEGRATION_GUIDE.md` 中的详细实现示例

## 🔒 安全注意事项

1. **密钥安全**
   - 配置文件包含敏感信息，请确保文件权限设置正确
   - 不要将配置文件提交到公开的代码仓库
   - 建议使用环境变量或密钥管理服务

2. **回调验证**
   - 真实SDK会自动验证回调签名
   - 确保回调地址使用HTTPS（支付平台要求）

3. **订单验证**
   - 验证订单金额
   - 防止重复处理订单
   - 记录所有支付操作日志

## 🧪 测试建议

1. **沙箱环境测试**
   - 先在支付宝和微信支付的沙箱环境中测试
   - 验证完整的支付流程

2. **生产环境部署**
   - 确保回调地址可公网访问
   - 配置HTTPS证书
   - 测试真实支付流程

## 📞 支持与帮助

- 支付宝开发文档: https://opendocs.alipay.com/
- 微信支付开发文档: https://pay.weixin.qq.com/wiki/doc/apiv3/index.shtml
- 详细接入指南: `docs/guides/PAYMENT_INTEGRATION_GUIDE.md`

## ✨ 配置验证

运行以下命令验证配置是否正确：

```bash
python scripts/setup_payment_config.py
```

如果配置正确，会显示：
- ✅ 支付宝配置已保存
- ✅ 微信支付配置已保存

然后可以在Web界面的「💰 点数商城」中测试支付功能。

