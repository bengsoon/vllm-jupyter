#!/usr/bin/env python3
"""
Simple test script for vLLM API connectivity and basic inference.
"""

import requests
import json
import time
import argparse
from typing import Dict, Any, Optional


def test_vllm_connection(
    base_url: str = "http://localhost:8000",
    api_key: str = "your-api-key-here"
) -> bool:
    """Test if vLLM server is accessible."""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ vLLM server is healthy and accessible")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to server: {e}")
        return False


def get_available_models(
    base_url: str = "http://localhost:8000",
    api_key: str = "your-api-key-here"
) -> Optional[Dict[str, Any]]:
    """Get list of available models."""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/v1/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Available models:")
            for model in models.get('data', []):
                print(f"   - {model['id']}")
            return models
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting models: {e}")
        return None


def test_inference(
    prompt: str,
    base_url: str = "http://localhost:8000",
    api_key: str = "your-api-key-here",
    model_name: str = "chatbot",
    max_tokens: int = 100
) -> Optional[Dict[str, Any]]:
    """Test a single inference request."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": False
        }
        
        print(f"🔄 Testing inference with prompt: '{prompt}'")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            inference_time = end_time - start_time
            
            print("✅ Inference successful!")
            print(f"   Response: {result['choices'][0]['message']['content']}")
            print(f"   Time: {inference_time:.2f} seconds")
            print(f"   Tokens: {result['usage']['total_tokens']}")
            
            return result
        else:
            print(f"❌ Inference failed: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during inference: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Test vLLM API connectivity and inference")
    parser.add_argument("--url", default="http://localhost:8000", help="vLLM server URL")
    parser.add_argument("--api-key", default="your-api-key-here", help="API key")
    parser.add_argument("--model", default="chatbot", help="Model name")
    parser.add_argument("--prompt", default="Hello! How are you today?", help="Test prompt")
    parser.add_argument("--max-tokens", type=int, default=100, help="Maximum tokens")
    
    args = parser.parse_args()
    
    print("🧪 vLLM API Test Script")
    print("=" * 50)
    print(f"Server URL: {args.url}")
    print(f"Model: {args.model}")
    print("")
    
    # Test 1: Health check
    print("1️⃣ Testing server connectivity...")
    if not test_vllm_connection(args.url, args.api_key):
        print("❌ Cannot connect to server. Exiting.")
        return 1
    
    print("")
    
    # Test 2: Get models
    print("2️⃣ Getting available models...")
    models = get_available_models(args.url, args.api_key)
    
    print("")
    
    # Test 3: Single inference
    print("3️⃣ Testing inference...")
    result = test_inference(
        args.prompt,
        args.url,
        args.api_key,
        args.model,
        args.max_tokens
    )
    
    if result:
        print("")
        print("🎉 All tests passed! Your vLLM server is working correctly.")
        return 0
    else:
        print("")
        print("❌ Inference test failed. Check your configuration.")
        return 1


if __name__ == "__main__":
    exit(main())
