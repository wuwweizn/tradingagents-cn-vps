"""
股票分析路由
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import datetime as dt

from api.core.dependencies import get_current_user, require_permission
from api.utils.analysis_runner import run_analysis_async

router = APIRouter()


class AnalysisRequest(BaseModel):
    stock_symbol: str
    market_type: str = "美股"
    research_depth: str = "标准"
    analysts: List[str] = []
    llm_provider: str = "dashscope"
    llm_model: str = "qwen-max"
    include_sentiment: bool = True
    include_risk_assessment: bool = True
    custom_prompt: Optional[str] = None


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


# 存储运行中的分析任务
running_analyses: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_permission("analysis"))
):
    """启动股票分析"""
    username = current_user["username"]
    
    # 生成分析ID
    analysis_id = f"analysis_{username}_{uuid.uuid4().hex[:8]}_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 记录任务
    running_analyses[analysis_id] = {
        "status": "running",
        "user": username,
        "stock_symbol": request.stock_symbol,
        "start_time": dt.datetime.now().isoformat(),
        "progress": 0,
        "message": "分析已启动"
    }
    
    # 后台执行分析
    background_tasks.add_task(
        run_analysis_task,
        analysis_id,
        request.dict(),
        username
    )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="running",
        message="分析已启动"
    )


@router.get("/status/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取分析状态"""
    username = current_user["username"]
    
    # 检查分析是否属于当前用户
    if analysis_id not in running_analyses:
        raise HTTPException(status_code=404, detail="分析任务不存在")
    
    analysis = running_analyses[analysis_id]
    if analysis["user"] != username:
        raise HTTPException(status_code=403, detail="无权访问此分析")
    
    return analysis


@router.get("/result/{analysis_id}")
async def get_analysis_result(
    analysis_id: str,
    current_user: dict = Depends(require_permission("analysis"))
):
    """获取分析结果"""
    username = current_user["username"]
    
    if analysis_id not in running_analyses:
        raise HTTPException(status_code=404, detail="分析任务不存在")
    
    analysis = running_analyses[analysis_id]
    if analysis["user"] != username:
        raise HTTPException(status_code=403, detail="无权访问此分析")
    
    if analysis["status"] != "completed":
        raise HTTPException(status_code=400, detail="分析尚未完成")
    
    return analysis.get("result", {})


async def run_analysis_task(analysis_id: str, params: dict, username: str):
    """执行分析任务（后台任务）"""
    try:
        # 更新状态
        running_analyses[analysis_id]["status"] = "running"
        running_analyses[analysis_id]["message"] = "正在执行分析..."
        
        # 调用分析函数
        result = await run_analysis_async(params)
        
        # 更新结果
        running_analyses[analysis_id].update({
            "status": "completed",
            "result": result,
            "message": "分析完成",
            "completed_time": dt.datetime.now().isoformat()
        })
        
    except Exception as e:
        running_analyses[analysis_id].update({
            "status": "failed",
            "message": f"分析失败: {str(e)}",
            "error": str(e)
        })

