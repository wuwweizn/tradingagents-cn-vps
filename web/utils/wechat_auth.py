"""
微信登录工具模块
提供微信OAuth2.0网页授权登录功能
"""

import os
import json
import requests
import hashlib
import time
from typing import Dict, Optional, Tuple
from urllib.parse import quote, urlencode
import streamlit as st

from tradingagents.utils.logging_manager import get_logger
logger = get_logger('wechat_auth')


class WeChatAuth:
    """微信登录认证类"""
    
    # 微信开放平台API端点
    AUTHORIZE_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"
    ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
    REFRESH_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
    USER_INFO_URL = "https://api.weixin.qq.com/sns/userinfo"
    
    def __init__(self):
        """初始化微信认证配置"""
        # 从环境变量读取微信配置
        self.app_id = os.getenv("WECHAT_APP_ID", "")
        self.app_secret = os.getenv("WECHAT_APP_SECRET", "")
        self.redirect_uri = os.getenv("WECHAT_REDIRECT_URI", "")
        
        # 检查配置是否完整
        if not all([self.app_id, self.app_secret, self.redirect_uri]):
            logger.warning("⚠️ 微信登录配置不完整，请设置 WECHAT_APP_ID、WECHAT_APP_SECRET 和 WECHAT_REDIRECT_URI")
    
    def is_configured(self) -> bool:
        """检查微信登录是否已配置"""
        return all([self.app_id, self.app_secret, self.redirect_uri])
    
    def get_authorize_url(self, state: Optional[str] = None) -> str:
        """
        生成微信授权URL
        
        Args:
            state: 状态参数，用于防止CSRF攻击
            
        Returns:
            授权URL
        """
        if not self.is_configured():
            raise ValueError("微信登录未配置，请设置环境变量")
        
        if not state:
            # 生成随机state参数
            state = hashlib.md5(f"{time.time()}_{st.session_state.get('session_id', 'default')}".encode()).hexdigest()[:16]
        
        params = {
            "appid": self.app_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "snsapi_userinfo",  # 获取用户基本信息
            "state": state
        }
        
        url = f"{self.AUTHORIZE_URL}?{urlencode(params)}#wechat_redirect"
        return url
    
    def get_access_token(self, code: str) -> Tuple[bool, Dict]:
        """
        通过授权码获取access_token
        
        Args:
            code: 微信回调返回的授权码
            
        Returns:
            (是否成功, 返回数据)
        """
        if not self.is_configured():
            return False, {"errcode": -1, "errmsg": "微信登录未配置"}
        
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.get(self.ACCESS_TOKEN_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "errcode" in data:
                logger.error(f"❌ 获取access_token失败: {data.get('errmsg', '未知错误')}")
                return False, data
            
            logger.info("✅ 成功获取access_token")
            return True, data
            
        except requests.RequestException as e:
            logger.error(f"❌ 请求access_token失败: {e}")
            return False, {"errcode": -1, "errmsg": str(e)}
    
    def get_user_info(self, access_token: str, openid: str) -> Tuple[bool, Dict]:
        """
        获取用户信息
        
        Args:
            access_token: 访问令牌
            openid: 用户唯一标识
            
        Returns:
            (是否成功, 用户信息)
        """
        if not self.is_configured():
            return False, {"errcode": -1, "errmsg": "微信登录未配置"}
        
        params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }
        
        try:
            response = requests.get(self.USER_INFO_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "errcode" in data:
                logger.error(f"❌ 获取用户信息失败: {data.get('errmsg', '未知错误')}")
                return False, data
            
            logger.info(f"✅ 成功获取用户信息: {data.get('nickname', 'Unknown')}")
            return True, data
            
        except requests.RequestException as e:
            logger.error(f"❌ 请求用户信息失败: {e}")
            return False, {"errcode": -1, "errmsg": str(e)}
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, Dict]:
        """
        刷新access_token
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            (是否成功, 返回数据)
        """
        if not self.is_configured():
            return False, {"errcode": -1, "errmsg": "微信登录未配置"}
        
        params = {
            "appid": self.app_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        try:
            response = requests.get(self.REFRESH_TOKEN_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "errcode" in data:
                logger.error(f"❌ 刷新access_token失败: {data.get('errmsg', '未知错误')}")
                return False, data
            
            logger.info("✅ 成功刷新access_token")
            return True, data
            
        except requests.RequestException as e:
            logger.error(f"❌ 请求刷新token失败: {e}")
            return False, {"errcode": -1, "errmsg": str(e)}
    
    def complete_login(self, code: str) -> Tuple[bool, Optional[Dict]]:
        """
        完成微信登录流程
        
        Args:
            code: 微信回调返回的授权码
            
        Returns:
            (是否成功, 用户信息字典，包含openid, nickname, headimgurl等)
        """
        # 1. 获取access_token
        success, token_data = self.get_access_token(code)
        if not success:
            return False, None
        
        access_token = token_data.get("access_token")
        openid = token_data.get("openid")
        refresh_token = token_data.get("refresh_token")
        
        if not access_token or not openid:
            logger.error("❌ access_token或openid为空")
            return False, None
        
        # 2. 获取用户信息
        success, user_info = self.get_user_info(access_token, openid)
        if not success:
            return False, None
        
        # 3. 返回完整的用户信息
        result = {
            "openid": openid,
            "unionid": user_info.get("unionid", ""),  # 可选，需要unionid需要额外配置
            "nickname": user_info.get("nickname", ""),
            "headimgurl": user_info.get("headimgurl", ""),
            "sex": user_info.get("sex", 0),  # 0未知，1男，2女
            "province": user_info.get("province", ""),
            "city": user_info.get("city", ""),
            "country": user_info.get("country", ""),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": token_data.get("expires_in", 7200)
        }
        
        logger.info(f"✅ 微信登录成功: {result.get('nickname', openid)}")
        return True, result


# 创建全局实例
wechat_auth = WeChatAuth()
