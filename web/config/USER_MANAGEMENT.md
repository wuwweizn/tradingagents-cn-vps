# 用户管理说明

## 概述

TradingAgents-CN 使用基于文件的用户认证系统，用户信息存储在 `users.json` 文件中。

## 用户配置文件

用户配置文件位置：`web/config/users.json`

## 用户角色和权限

### 管理员 (admin)
- 权限：`["analysis", "config", "admin", "batch_analysis"]`
- 可以进行股票分析
- 可以访问系统配置
- 可以管理用户和系统
- 可以使用批量分析功能

### 普通用户 (user)
- 权限：`["analysis"]`
- 只能进行股票分析
- 无法访问系统配置和管理功能
- 无法使用批量分析功能（需要管理员分配 `batch_analysis` 权限）

### 权限说明

系统支持以下权限：

- **analysis**: 单股票分析权限（所有用户默认拥有）
- **batch_analysis**: 批量分析权限（需管理员分配）
- **config**: 配置管理权限（仅管理员）
- **admin**: 管理员权限（用户管理、系统管理等，仅管理员）

## 安全特性

- 密码使用 SHA-256 哈希存储
- 会话超时机制（1小时）
- 权限分级控制
- 登录日志记录

## 添加新用户

1. 编辑 `web/config/users.json` 文件
2. 添加新用户条目，格式如下：

```json
{
  "新用户名": {
    "password_hash": "密码的SHA-256哈希值",
    "role": "user",
    "permissions": ["analysis"],
    "created_at": 时间戳
  }
}
```

### 分配批量分析权限

如果需要给用户分配批量分析权限，在权限列表中添加 `"batch_analysis"`：

```json
{
  "新用户名": {
    "password_hash": "密码的SHA-256哈希值",
    "role": "user",
    "permissions": ["analysis", "batch_analysis"],
    "created_at": 时间戳
  }
}
```

或者通过Web界面在"👥 会员管理"页面中编辑用户权限，勾选"batch_analysis"权限。

## 注意事项

- 请妥善保管用户配置文件
- 定期更新密码
- 不要在日志或代码中暴露密码信息
- 建议在生产环境中更改默认账户密码

## 技术支持

如需技术支持，请联系系统管理员。