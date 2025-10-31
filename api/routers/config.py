"""
配置管理路由
"""
from fastapi import APIRouter, Depends
from api.core.dependencies import require_permission

router = APIRouter()


@router.get("/models")
async def get_models(current_user: dict = Depends(require_permission("config"))):
    """获取模型配置"""
    # TODO: 实现模型配置读取
    return {"models": []}


@router.put("/models/{model_id}")
async def update_model(
    model_id: str,
    current_user: dict = Depends(require_permission("config"))
):
    """更新模型配置"""
    # TODO: 实现模型配置更新
    return {"message": "配置已更新"}

