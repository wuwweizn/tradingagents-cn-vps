"""
分析执行工具（异步版本）
"""
import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web.utils.analysis_runner import run_stock_analysis, format_analysis_results


async def run_analysis_async(params: Dict[str, Any]) -> Dict[str, Any]:
    """异步执行分析"""
    # 在线程池中运行同步的分析函数
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        _run_analysis_sync,
        params
    )
    return result


def _run_analysis_sync(params: Dict[str, Any]) -> Dict[str, Any]:
    """同步执行分析（在线程池中运行）"""
    try:
        # 调用原有的分析函数
        raw_results = run_stock_analysis(
            stock_symbol=params["stock_symbol"],
            analysis_date=None,  # 使用当前日期
            analysts=params.get("analysts", []),
            research_depth=params.get("research_depth", "标准"),
            llm_provider=params.get("llm_provider", "dashscope"),
            llm_model=params.get("llm_model", "qwen-max"),
            market_type=params.get("market_type", "美股"),
            progress_callback=None
        )
        
        # 格式化结果
        formatted = format_analysis_results(raw_results)
        return formatted
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

