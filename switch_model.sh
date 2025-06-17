#!/bin/bash

# vLLM Model Switcher Script
# Usage: ./switch_model.sh <model_name> [max_model_len] [tensor_parallel_size]

set -e

ENV_FILE=".env"
BACKUP_FILE=".env.backup"

# Function to display available models
show_available_models() {
    echo "Available models (examples):"
    echo "1. microsoft/DialoGPT-small"
    echo "2. microsoft/DialoGPT-medium" 
    echo "3. microsoft/DialoGPT-large"
    echo "4. Qwen/Qwen2.5-0.5B-Instruct"
    echo "5. Qwen/Qwen2.5-1.5B-Instruct"
    echo "6. Qwen/Qwen1.5-MoE-A2.7B-Chat"
    echo "7. microsoft/phi-1_5"
    echo "8. microsoft/phi-2"
    echo ""
    echo "Or any other HuggingFace model compatible with vLLM"
}

# Function to update environment variable in .env file
update_env_var() {
    local var_name=$1
    local var_value=$2
    local file=$3
    
    if grep -q "^${var_name}=" "$file"; then
        # Update existing variable
        sed -i "s|^${var_name}=.*|${var_name}=${var_value}|" "$file"
    else
        # Add new variable
        echo "${var_name}=${var_value}" >> "$file"
    fi
}

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found!"
    exit 1
fi

# Parse arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <model_name> [max_model_len] [tensor_parallel_size]"
    echo ""
    show_available_models
    exit 1
fi

MODEL_NAME="$1"
MAX_MODEL_LEN="${2:-2048}"
TENSOR_PARALLEL_SIZE="${3:-1}"

echo "Switching to model: $MODEL_NAME"
echo "Max model length: $MAX_MODEL_LEN"
echo "Tensor parallel size: $TENSOR_PARALLEL_SIZE"

# Create backup of current .env file
cp "$ENV_FILE" "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

# Update the environment variables
update_env_var "VLLM_MODEL" "$MODEL_NAME" "$ENV_FILE"
update_env_var "VLLM_MAX_MODEL_LEN" "$MAX_MODEL_LEN" "$ENV_FILE"
update_env_var "VLLM_TENSOR_PARALLEL_SIZE" "$TENSOR_PARALLEL_SIZE" "$ENV_FILE"

echo "Environment variables updated!"
echo ""
echo "Current model configuration:"
grep "VLLM_MODEL=" "$ENV_FILE"
grep "VLLM_MAX_MODEL_LEN=" "$ENV_FILE"
grep "VLLM_TENSOR_PARALLEL_SIZE=" "$ENV_FILE"
echo ""

# Ask if user wants to restart the services
read -p "Do you want to restart the vLLM service now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Restarting vLLM server..."
    docker compose stop vllm-server
    docker compose up -d vllm-server
    echo "vLLM server restarted with new model!"
else
    echo "Model configuration updated. Run 'docker compose restart vllm-server' when ready."
fi
