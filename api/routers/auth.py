"""
认证相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path
import time
import hashlib

from api.core.config import settings
from api.core.security import verify_password, create_access_token, verify_token
from api.core.dependencies import get_current_user
from datetime import timedelta

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


def _load_users() -> dict:
    """加载用户数据"""
    users_file = settings.USERS_FILE
    if users_file.exists():
        with open(users_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def _hash_password(password: str) -> str:
    """SHA256密码哈希（兼容旧系统）"""
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录"""
    users = _load_users()
    
    if request.username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    user_info = users[request.username]
    stored_hash = user_info.get("password_hash")
    
    # 验证密码
    if not verify_password(request.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建token
    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 返回用户信息（不包含密码）
    user_data = {
        "username": request.username,
        "role": user_info.get("role", "user"),
        "permissions": user_info.get("permissions", []),
        "points": user_info.get("points", 0),
    }
    
    return LoginResponse(
        access_token=access_token,
        user=user_data
    )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/logout")
async def logout():
    """登出（JWT是无状态的，这里只是返回成功）"""
    return {"message": "登出成功"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """修改密码"""
    users = _load_users()
    username = current_user["username"]
    
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_info = users[username]
    
    # 验证旧密码
    if not verify_password(request.old_password, user_info["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="旧密码错误"
        )
    
    # 更新密码
    users[username]["password_hash"] = _hash_password(request.new_password)
    
    # 保存用户数据
    settings.USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    return {"message": "密码修改成功"}

