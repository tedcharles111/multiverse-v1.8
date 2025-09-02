"""
OpenRouter API wrapper for DeepSeek models.

This module provides a wrapper function to interact with OpenRouter's API
using DeepSeek models as primary and fallback options.
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional
from gpt_engineer.core.models import (
    MODEL_PRIMARY, 
    MODEL_FALLBACK, 
    OPENROUTER_CHAT_ENDPOINT,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE
)


def call_openrouter(
    messages: List[Dict[str, str]], 
    model: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE
) -> Dict[str, Any]:
    """
    Call OpenRouter API with DeepSeek models.
    
    Parameters
    ----------
    messages : List[Dict[str, str]]
        List of message dictionaries with 'role' and 'content' keys
    model : Optional[str]
        Specific model to use, defaults to MODEL_PRIMARY
    max_tokens : int
        Maximum tokens to generate
    temperature : float
        Temperature for generation
        
    Returns
    -------
    Dict[str, Any]
        API response with additional '_used_model' field
        
    Raises
    ------
    Exception
        If both primary and fallback models fail
    """
    
    # Get API key from environment
    api_key = os.getenv('OPENROUTER_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_KEY environment variable not set")
    
    # Use provided model or default to primary
    target_model = model or MODEL_PRIMARY
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://multiverse-ai.com",
        "X-Title": "Multiverse AI Web Builder"
    }
    
    payload = {
        "model": target_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 1.0,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    
    try:
        # Try primary model
        print(f"🤖 Calling OpenRouter with model: {target_model}")
        response = requests.post(
            OPENROUTER_CHAT_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            result['_used_model'] = target_model
            print(f"✅ Successfully used model: {target_model}")
            return result
        
        # If primary model fails and we haven't tried fallback yet
        if target_model == MODEL_PRIMARY and response.status_code in [404, 429, 503]:
            print(f"⚠️  Primary model {MODEL_PRIMARY} unavailable, trying fallback...")
            
            # Try fallback model
            payload["model"] = MODEL_FALLBACK
            response = requests.post(
                OPENROUTER_CHAT_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                result['_used_model'] = MODEL_FALLBACK
                print(f"✅ Successfully used fallback model: {MODEL_FALLBACK}")
                return result
        
        # If we get here, both models failed
        error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
        
    except requests.exceptions.Timeout:
        error_msg = "OpenRouter API request timed out"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f"OpenRouter API request failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)


def test_openrouter_connection():
    """
    Test the OpenRouter connection with a simple message.
    
    Returns
    -------
    bool
        True if connection successful, False otherwise
    """
    try:
        messages = [
            {"role": "system", "content": "You are an expert assistant."},
            {"role": "user", "content": "Say 'hello' and return only JSON: {\"ok\":true}"}
        ]
        
        result = call_openrouter(messages)
        print(f"🧪 Test result: {result}")
        print(f"🤖 Used model: {result.get('_used_model', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
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