"""
用户管理路由
"""
from fastapi import APIRouter, Depends
from api.core.dependencies import require_permission

router = APIRouter()


@router.get("/")
async def list_users(current_user: dict = Depends(require_permission("admin"))):
    """列出所有用户"""
    # TODO: 实现用户列表
    return {"users": []}

