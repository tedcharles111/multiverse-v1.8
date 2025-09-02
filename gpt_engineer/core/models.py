"""
Model configuration for Multiverse AI Web Builder.

This module defines the AI models used by the web builder, specifically
the DeepSeek models available through OpenRouter.
"""

# Primary and fallback models for DeepSeek via OpenRouter
MODEL_PRIMARY = "deepseek/deepseek-r1-0528:free"
MODEL_FALLBACK = "deepseek/deepseek-r1-0528-qwen3-8b:free"

# OpenRouter API configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_CHAT_ENDPOINT = f"{OPENROUTER_BASE_URL}/chat/completions"

# Default model parameters
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TOP_P = 1.0