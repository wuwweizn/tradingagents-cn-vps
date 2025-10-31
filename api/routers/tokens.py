"""
Token统计路由
"""
from fastapi import APIRouter, Depends
from api.core.dependencies import require_permission

router = APIRouter()


@router.get("/statistics")
async def get_token_statistics(
    current_user: dict = Depends(require_permission("config"))
):
    """获取Token使用统计"""
    # TODO: 实现Token统计
    return {"statistics": {}}

