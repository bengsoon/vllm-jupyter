# Model Switching Guide

This guide explains how to easily switch between different language models in your vLLM Docker setup.

## 🚀 Quick Model Switch

### Method 1: Using the Switch Script (Recommended)
The `switch_model.sh` script provides the fastest way to change models:

```bash
# Switch to a different model with default settings
./switch_model.sh microsoft/DialoGPT-small

# Switch with custom max sequence length
./switch_model.sh Qwen/Qwen2.5-1.5B-Instruct 4096

# Switch with custom parameters (model, max_len, tensor_parallel_size)
./switch_model.sh meta-llama/Llama-2-7b-chat-hf 2048 1

# View available pre-configured models
./switch_model.sh --list

# Get help and usage information
./switch_model.sh --help
```

### Method 2: Manual .env Editing
For more control over configuration:

1. Edit the `.env` file:
   ```bash
   nano .env  # or use your preferred editor
   ```

2. Change the relevant variables:
   ```bash
   VLLM_MODEL=microsoft/DialoGPT-medium
   VLLM_MAX_MODEL_LEN=2048
   VLLM_TENSOR_PARALLEL_SIZE=1
   ```

3. Restart the vLLM server:
   ```bash
   docker compose restart vllm-server
   ```

### Method 3: Using Pre-configured Model Templates
1. Check `model_configs.txt` for pre-configured model settings
2. Copy the desired configuration to your `.env` file
3. Restart the vLLM server

## ⚙️ Model Configuration Variables

| Variable | Description | Example Values |
|----------|-------------|----------------|
| `VLLM_MODEL` | HuggingFace model name or local path | `microsoft/DialoGPT-medium` |
| `VLLM_MAX_MODEL_LEN` | Maximum sequence length | `2048`, `4096`, `8192` |
| `VLLM_TENSOR_PARALLEL_SIZE` | Number of GPUs to use | `1` (single GPU), `2`, `4` |
| `VLLM_SERVED_MODEL_NAME` | Name used in API calls | `chatbot`, `assistant` |
| `VLLM_DTYPE` | Data type for inference | `auto`, `float16`, `bfloat16` |
| `VLLM_GPU_MEMORY_UTILIZATION` | GPU memory usage ratio | `0.9` (90%), `0.8` (80%) |

## 🖥️ GPU Memory Considerations

### Memory Requirements by Model Size

| Model Size | Approx. VRAM | Recommended Max Length | Example Models |
|------------|---------------|------------------------|----------------|
| 0.1-0.5B   | 1-2 GB       | 4096-8192             | `gpt2`, `microsoft/DialoGPT-small` |
| 0.5-1.5B   | 2-4 GB       | 4096-8192             | `microsoft/DialoGPT-medium`, `Qwen/Qwen2.5-1.5B` |
| 1.5-3B     | 4-8 GB       | 2048-4096             | `microsoft/DialoGPT-large`, `Qwen/Qwen2.5-3B` |
| 7B         | 14-16 GB     | 2048-4096             | `meta-llama/Llama-2-7b-chat-hf` |
| 13B        | 26-30 GB     | 1024-2048             | `meta-llama/Llama-2-13b-chat-hf` |

### Memory Optimization Tips

1. **Reduce sequence length**: Lower `VLLM_MAX_MODEL_LEN` to save memory
2. **Use efficient data types**: Set `VLLM_DTYPE=float16` for memory savings
3. **Adjust GPU utilization**: Set `VLLM_GPU_MEMORY_UTILIZATION=0.8` to reserve memory
4. **Use quantized models**: Look for GPTQ or AWQ quantized versions
## 🔧 Troubleshooting

### Common Issues and Solutions

#### Out of Memory Errors
```
RuntimeError: CUDA out of memory
```
**Solutions:**
1. Reduce `VLLM_MAX_MODEL_LEN` (try 1024, 2048)
2. Switch to a smaller model
3. Use `VLLM_DTYPE=float16` for memory savings
4. Lower `VLLM_GPU_MEMORY_UTILIZATION=0.7`

#### Model Loading Errors
```
OSError: [Model] does not appear to be a valid git repository
```
**Solutions:**
1. Check internet connection
2. Verify model name spelling
3. For gated models, ensure you have access and use authentication
4. Try downloading the model manually first

#### Server Not Starting
```
Address already in use
```
**Solutions:**
1. Check if another vLLM instance is running: `docker ps`
2. Stop existing containers: `docker compose down`
3. Change port in docker-compose.yml if needed

#### Performance Issues
**Solutions:**
1. Monitor GPU usage: `nvidia-smi`
2. Adjust batch size in your inference code
3. Use tensor parallelism for multi-GPU setups
4. Consider using a different model architecture

## 🎯 Popular Model Recommendations

### 💬 For Chat/Conversation:
- **`microsoft/DialoGPT-medium`** - Good general purpose, moderate resource usage
- **`Qwen/Qwen2.5-1.5B-Instruct`** - Modern, instruction-tuned, efficient
- **`microsoft/DialoGPT-large`** - Better quality, higher resource usage
- **`meta-llama/Llama-2-7b-chat-hf`** - High quality, requires GPU with 16GB+ VRAM

### 👨‍💻 For Code Generation:
- **`microsoft/phi-2`** - Excellent for code generation, 2.7B parameters
- **`Qwen/Qwen2.5-Coder-1.5B-Instruct`** - Specialized for coding tasks
- **`codellama/CodeLlama-7b-Instruct-hf`** - Meta's code-focused model

### ⚡ For Efficiency/Speed:
- **`microsoft/DialoGPT-small`** - Minimal resource usage, fast inference
- **`Qwen/Qwen1.5-MoE-A2.7B-Chat`** - Mixture of Experts architecture
- **`TinyLlama/TinyLlama-1.1B-Chat-v1.0`** - Very lightweight, good for testing

### 🎨 For Creative Writing:
- **`microsoft/DialoGPT-large`** - Good for creative tasks
- **`NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO`** - High quality, needs significant resources

## 🔄 Model Switching Workflow

1. **Check Available Resources:**
   ```bash
   nvidia-smi  # Check GPU memory
   ```

2. **Choose Appropriate Model:**
   - Use the memory requirements table above
   - Consider your use case (chat, code, creative writing)

3. **Switch Model:**
   ```bash
   ./switch_model.sh your-chosen-model
   ```

4. **Validate Configuration:**
   ```bash
   python validate_config.py
   ```

5. **Test the Model:**
   ```bash
   python test_vllm_api.py
   ```

6. **Monitor Performance:**
   - Check GPU usage: `nvidia-smi`
   - Test inference speed with your typical workload
   - Adjust parameters if needed

## 📚 Additional Resources

- **HuggingFace Model Hub**: https://huggingface.co/models
- **vLLM Documentation**: https://docs.vllm.ai/
- **Model Performance Benchmarks**: Check the model cards on HuggingFace
- **GPU Requirements Calculator**: Use tools like `transformers-cli` to estimate memory needs
