"""
OpenRouter API wrapper for DeepSeek and Qwen models.

This module provides a wrapper function to interact with OpenRouter's API
using DeepSeek and Qwen models with proper fallback handling.
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional

# Model configurations with token limits
MODELS = {
    'primary': {
        'name': 'deepseek/deepseek-r1-0528:free',
        'max_tokens': 1800,
        'context_limit': 128000
    },
    'reasoning_fallback': {
        'name': 'qwen/qwen3-30b-a3b:free', 
        'max_tokens': 1800,
        'context_limit': 130000
    },
    'coding_fallback': {
        'name': 'qwen/qwen-2.5-coder-32b-instruct:free',
        'max_tokens': 1800,
        'context_limit': 128000
    },
    'final_fallback': {
        'name': 'qwen/qwen3-coder:free',
        'max_tokens': 1800,
        'context_limit': 127000
    }
}

OPENROUTER_CHAT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars ≈ 1 token)"""
    return len(text) // 4


def truncate_messages_if_needed(messages: List[Dict[str, str]], max_context: int) -> List[Dict[str, str]]:
    """Truncate messages if they exceed context limit"""
    total_tokens = sum(estimate_tokens(msg.get('content', '')) for msg in messages)
    
    if total_tokens <= max_context:
        return messages
    
    # Keep system message and truncate from the middle
    if len(messages) <= 2:
        return messages
    
    system_msg = messages[0] if messages[0].get('role') == 'system' else None
    user_msg = messages[-1] if messages[-1].get('role') == 'user' else None
    
    result = []
    if system_msg:
        result.append(system_msg)
    if user_msg and user_msg != system_msg:
        result.append(user_msg)
    
    return result


def call_openrouter(
    messages: List[Dict[str, str]], 
    model_type: str = 'primary',
    max_tokens: int = 1800,
    temperature: float = 0.1,
    is_reasoning: bool = False
) -> Dict[str, Any]:
    """
    Call OpenRouter API with DeepSeek/Qwen models and fallback handling.
    
    Parameters
    ----------
    messages : List[Dict[str, str]]
        List of message dictionaries with 'role' and 'content' keys
    model_type : str
        Type of model to use ('primary', 'reasoning_fallback', 'coding_fallback', 'final_fallback')
    max_tokens : int
        Maximum tokens to generate (capped at 1800)
    temperature : float
        Temperature for generation
    is_reasoning : bool
        Whether this is for reasoning (affects model selection)
        
    Returns
    -------
    Dict[str, Any]
        API response with additional '_used_model' and '_fallback_used' fields
        
    Raises
    ------
    Exception
        If all models fail
    """
    
    # Get API key from environment
    api_key = os.getenv('OPENROUTER_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_KEY environment variable not set")
    
    # Ensure max_tokens doesn't exceed limit
    max_tokens = min(max_tokens, 1800)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://multiverse-ai.com",
        "X-Title": "Multiverse AI Web Builder"
    }
    
    # Determine model order based on task type
    if is_reasoning:
        model_order = ['primary', 'reasoning_fallback', 'final_fallback']
    else:
        model_order = ['primary', 'coding_fallback', 'final_fallback']
    
    last_error = None
    
    for i, model_key in enumerate(model_order):
        model_config = MODELS[model_key]
        
        # Truncate messages if needed for this model's context limit
        truncated_messages = truncate_messages_if_needed(messages, model_config['context_limit'])
        
        payload = {
            "model": model_config['name'],
            "messages": truncated_messages,
            "max_tokens": min(max_tokens, model_config['max_tokens']),
            "temperature": temperature,
            "top_p": 1.0,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        try:
            print(f"🤖 Trying model: {model_config['name']} (attempt {i+1}/{len(model_order)})")
            
            response = requests.post(
                OPENROUTER_CHAT_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                result['_used_model'] = model_config['name']
                result['_fallback_used'] = i > 0
                result['_attempt'] = i + 1
                
                if i > 0:
                    print(f"⚠️  Used fallback model: {model_config['name']}")
                else:
                    print(f"✅ Successfully used primary model: {model_config['name']}")
                
                return result
            
            # Handle specific error codes
            if response.status_code in [404, 429, 503, 502]:
                error_msg = f"Model {model_config['name']} unavailable (HTTP {response.status_code})"
                print(f"⚠️  {error_msg}")
                last_error = error_msg
                continue
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ {error_msg}")
                last_error = error_msg
                continue
                
        except requests.exceptions.Timeout:
            error_msg = f"Timeout with model {model_config['name']}"
            print(f"⏰ {error_msg}")
            last_error = error_msg
            continue
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed with {model_config['name']}: {str(e)}"
            print(f"❌ {error_msg}")
            last_error = error_msg
            continue
    
    # If we get here, all models failed
    raise Exception(f"All models failed. Last error: {last_error}")


def call_openrouter_reasoning(messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """Wrapper for reasoning tasks"""
    return call_openrouter(messages, is_reasoning=True, **kwargs)


def call_openrouter_coding(messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """Wrapper for coding tasks"""
    return call_openrouter(messages, is_reasoning=False, **kwargs)


def test_openrouter_connection():
    """
    Test the OpenRouter connection with all models.
    
    Returns
    -------
    bool
        True if at least one model works, False otherwise
    """
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'hello' and return only JSON: {\"status\":\"ok\"}"}
    ]
    
    print("🧪 Testing OpenRouter connection with all models...")
    
    working_models = []
    
    for model_key, model_config in MODELS.items():
        try:
            print(f"Testing {model_config['name']}...")
            result = call_openrouter(test_messages, model_type=model_key)
            print(f"✅ {model_config['name']} - Working")
            working_models.append(model_config['name'])
        except Exception as e:
            print(f"❌ {model_config['name']} - Failed: {str(e)}")
    
    if working_models:
        print(f"🎉 {len(working_models)} model(s) working: {', '.join(working_models)}")
        return True
    else:
        print("💥 No models are working - check your OPENROUTER_KEY")
        return False


if __name__ == "__main__":
    # Test connection on startup
    print("🚀 Starting Multiverse AI Web Builder...")
    print("🔧 Testing OpenRouter connection...")
    
    if test_openrouter_connection():
        print("✅ OpenRouter connection successful!")
    else:
        print("⚠️  OpenRouter connection failed - check your OPENROUTER_KEY")
    
    print("🌐 Server starting...")