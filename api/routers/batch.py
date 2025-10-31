"""
批量分析路由
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from api.core.dependencies import require_permission

router = APIRouter()


class BatchAnalysisRequest(BaseModel):
    stock_symbols: List[str]
    market_type: str = "美股"
    research_depth: str = "标准"
    analysts: List[str] = []
    llm_provider: str = "dashscope"
    llm_model: str = "qwen-max"


@router.post("/start")
async def start_batch_analysis(
    request: BatchAnalysisRequest,
    current_user: dict = Depends(require_permission("batch_analysis"))
):
    """启动批量分析"""
    # TODO: 实现批量分析逻辑
    return {"message": "批量分析功能开发中", "batch_id": "batch_123"}


@router.get("/status/{batch_id}")
async def get_batch_status(
    batch_id: str,
    current_user: dict = Depends(require_permission("batch_analysis"))
):
    """获取批量分析状态"""
    # TODO: 实现状态查询
    return {"status": "running", "progress": 0}

