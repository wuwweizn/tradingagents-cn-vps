"""
模型点数配置管理器
用于管理不同模型的点数消耗配置
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ModelPointsManager:
    """模型点数管理器"""
    
    def __init__(self):
        # 配置文件路径
        config_dir = Path(__file__).parent.parent / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = config_dir / "model_points.json"
        
        # 默认配置（格式：provider:model_name -> points）
        self.default_points = {
            # DashScope 模型
            "dashscope:qwen-turbo": 1,
            "dashscope:qwen-plus-latest": 2,
            "dashscope:qwen-max": 3,
            
            # DeepSeek 模型
            "deepseek:deepseek-chat": 1,
            
            # Google 模型
            "google:gemini-2.5-pro": 5,
            "google:gemini-2.5-flash": 2,
            "google:gemini-2.5-flash-lite": 1,
            "google:gemini-2.5-pro-002": 5,
            "google:gemini-2.5-flash-002": 2,
            "google:gemini-2.0-flash": 2,
            "google:gemini-1.5-pro": 3,
            "google:gemini-1.5-flash": 1,
            
            # OpenAI 模型
            "openai:gpt-4o": 4,
            "openai:gpt-4o-mini": 2,
            "openai:gpt-4-turbo": 3,
            "openai:gpt-4": 3,
            "openai:gpt-3.5-turbo": 1,
            
            # OpenRouter 模型（通用格式：openrouter:provider/model）
            "openrouter:openai/gpt-4o-2024-11-20": 4,
            "openrouter:openai/gpt-4o-mini": 2,
            "openrouter:openai/o1-pro": 5,
            "openrouter:openai/o1-mini": 3,
            "openrouter:openai/o3-pro": 6,
            "openrouter:openai/o3-mini": 4,
            "openrouter:anthropic/claude-opus-4": 6,
            "openrouter:anthropic/claude-sonnet-4": 4,
            "openrouter:anthropic/claude-haiku-4": 2,
            "openrouter:anthropic/claude-3.5-sonnet": 3,
            "openrouter:anthropic/claude-3.5-haiku": 1,
            "openrouter:meta-llama/llama-4-maverick": 5,
            "openrouter:meta-llama/llama-4-scout": 4,
            "openrouter:google/gemini-2.5-pro": 5,
            "openrouter:google/gemini-2.5-flash": 2,
            
            # SiliconFlow 模型
            "siliconflow:Qwen/Qwen3-30B-A3B-Thinking-2507": 3,
            "siliconflow:Qwen/Qwen3-235B-A22B-Thinking-2507": 5,
            "siliconflow:deepseek-ai/DeepSeek-R1": 4,
            
            # Qianfan 模型
            "qianfan:ernie-3.5-8k": 2,
            "qianfan:ernie-4.0-turbo-8k": 4,
            "qianfan:ERNIE-Speed-8K": 1,
            "qianfan:ERNIE-Lite-8K": 1,
            
            # Custom OpenAI 模型（默认）
            "custom_openai:gpt-4o": 4,
            "custom_openai:gpt-4o-mini": 2,
        }
        
        # 确保配置文件存在
        self._ensure_config_file()
    
    def _ensure_config_file(self):
        """确保配置文件存在"""
        if not self.config_file.exists():
            # 创建默认配置
            self._save_config(self.default_points.copy())
            logger.info(f"✅ 创建默认模型点数配置文件: {self.config_file}")
    
    def _load_config(self) -> Dict[str, int]:
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置（如果新模型没有配置，使用默认值）
                    merged_config = self.default_points.copy()
                    merged_config.update(config)
                    return merged_config
            return self.default_points.copy()
        except Exception as e:
            logger.error(f"❌ 加载模型点数配置失败: {e}")
            return self.default_points.copy()
    
    def _save_config(self, config: Dict[str, int]) -> bool:
        """保存配置"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"❌ 保存模型点数配置失败: {e}")
            return False
    
    def get_model_key(self, provider: str, model: str, category: Optional[str] = None) -> str:
        """
        获取模型配置键
        
        Args:
            provider: 提供商（dashscope, google, openai等）
            model: 模型名称
            category: 模型类别（主要用于openrouter）
            
        Returns:
            配置键（格式：provider:model 或 provider:category/model）
        """
        if provider == "openrouter" and category:
            # OpenRouter格式：openrouter:category/model
            return f"{provider}:{category}/{model}"
        else:
            # 其他格式：provider:model
            return f"{provider}:{model}"
    
    def get_points(self, provider: str, model: str, category: Optional[str] = None) -> int:
        """
        获取模型消耗的点数
        
        Args:
            provider: 提供商
            model: 模型名称
            category: 模型类别（主要用于openrouter）
            
        Returns:
            消耗的点数，如果未配置则返回默认值1
        """
        config = self._load_config()
        model_key = self.get_model_key(provider, model, category)
        points = config.get(model_key, 1)  # 默认1点
        logger.debug(f"🔍 模型 {model_key} 消耗点数: {points}")
        return points
    
    def set_points(self, provider: str, model: str, points: int, category: Optional[str] = None) -> bool:
        """
        设置模型消耗的点数
        
        Args:
            provider: 提供商
            model: 模型名称
            points: 消耗的点数
            category: 模型类别（主要用于openrouter）
            
        Returns:
            是否保存成功
        """
        config = self._load_config()
        model_key = self.get_model_key(provider, model, category)
        config[model_key] = max(1, int(points))  # 至少1点
        return self._save_config(config)
    
    def get_all_configs(self) -> Dict[str, int]:
        """获取所有模型点数配置"""
        return self._load_config()
    
    def update_configs(self, configs: Dict[str, int]) -> bool:
        """批量更新配置"""
        current_config = self._load_config()
        current_config.update(configs)
        return self._save_config(current_config)
    
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        return self._save_config(self.default_points.copy())


# 全局实例
model_points_manager = ModelPointsManager()

