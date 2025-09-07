"""
Model configuration for Multiverse AI Web Builder.

This module defines the AI models used by the web builder, specifically
the DeepSeek and Qwen models available through OpenRouter with proper fallbacks.
"""

# Primary model for both reasoning and coding
MODEL_PRIMARY = "deepseek/deepseek-r1-0528:free"

# Fallback models for different tasks
MODEL_REASONING_FALLBACK = "qwen/qwen3-30b-a3b:free"
MODEL_CODING_FALLBACK = "qwen/qwen-2.5-coder-32b-instruct:free"
MODEL_FINAL_FALLBACK = "qwen/qwen3-coder:free"

# OpenRouter API configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_CHAT_ENDPOINT = f"{OPENROUTER_BASE_URL}/chat/completions"

# Model parameters
DEFAULT_MAX_TOKENS = 1800  # Conservative limit
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TOP_P = 1.0

# Context limits for each model
CONTEXT_LIMITS = {
    MODEL_PRIMARY: 128000,
    MODEL_REASONING_FALLBACK: 131000,
    MODEL_CODING_FALLBACK: 128000,
    MODEL_FINAL_FALLBACK: 128000
}

# Model selection strategy
def get_model_for_task(task_type: str = 'coding') -> str:
    """
    Get the appropriate model for a specific task.
    
    Parameters
    ----------
    task_type : str
        Type of task ('reasoning' or 'coding')
        
    Returns
    -------
    str
        Model name to use
    """
    if task_type == 'reasoning':
        return MODEL_PRIMARY  # Start with primary for both
    else:
        return MODEL_PRIMARY  # Start with primary for both