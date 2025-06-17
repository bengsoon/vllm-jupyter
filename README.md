# vLLM + Jupyter Lab Docker Compose Project

This project provides a complete setup for running vLLM server for offline batched inference alongside Jupyter Lab for interactive development and experimentation.

## 🏗️ Architecture

- **vLLM Server**: Provides OpenAI-compatible API for fast language model inference
- **Jupyter Lab**: Interactive development environment with pre-configured packages
- **Shared Network**: Both containers can communicate with each other
- **External Access**: Both services are accessible from outside the Docker environment

## 📋 Prerequisites

- Docker and Docker Compose installed
- NVIDIA GPU with Docker GPU support (for vLLM server)
- At least 8GB of RAM (more recommended for larger models)

## 🚀 Quick Start

1. **Clone or create the project directory**:
   ```bash
   cd /home/bengsoon/Projects/vllm-jupyter-docker
   ```

2. **Configure your settings**:
   - Copy `.env.example` to `.env` and customize:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` to set:
     - `VLLM_API_KEY`: Your API authentication key
     - `VLLM_MODEL`: Model name to load
     - `JUPYTER_TOKEN`: Jupyter Lab access token
     - Model parameters (max length, tensor parallel size, etc.)
   - Or use the model switching script:
     ```bash
     ./switch_model.sh microsoft/DialoGPT-medium
     ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the services**:
   - **Jupyter Lab**: http://localhost:8888 (token: `your-secure-token-here`)
   - **vLLM API**: http://localhost:8000 (API key: `your-api-key-here`)

## 📁 Project Structure

```
vllm-jupyter-docker/
├── docker-compose.yml          # Main orchestration file
├── jupyter/
│   ├── Dockerfile             # Custom Jupyter container
│   └── requirements.txt       # Python dependencies
├── notebooks/
│   ├── vllm_batched_inference_example.ipynb  # Comprehensive batched inference demo
│   └── vllm_inference_remote.ipynb           # Simple remote API connection examples
├── models/                    # Directory for local models (optional)
├── data/                      # Shared data directory
├── .env                       # Environment variables (API keys, model config)
├── .env.example              # Template for environment variables
├── switch_model.sh           # Script for quick model switching
├── add_package.sh            # Script for fast package installation
├── MODEL_SWITCHING.md        # Detailed model switching guide
├── validate_config.py        # Configuration validation script
├── test_vllm_api.py         # API testing and health check script
└── README.md                 # This file
```

## ⚙️ Configuration

### vLLM Server Configuration

Edit the `docker-compose.yml` file to customize the vLLM server:

```yaml
command: >
  --model Qwen/Qwen2.5-3B-Instruct    # Model to load
  --host 0.0.0.0
  --port 8000
  --served-model-name chatbot          # API model name
  --max-model-len 2048                 # Context length
  --dtype auto                         # Data type (auto/float16/bfloat16)
  --api-key your-api-key-here         # API authentication
  --tensor-parallel-size 1            # GPU parallelism
```

### Model Options

You can use any models available on HuggingFace. For example:
- `microsoft/DialoGPT-medium`
- `Qwen/Qwen2.5-3B-Instruct`

### Jupyter Lab Configuration

The Jupyter container includes:
- Scientific computing packages (numpy, pandas, matplotlib)
- Machine learning libraries (scikit-learn, transformers)
- HTTP clients for API communication (requests, httpx)
- OpenAI client library (compatible with vLLM)
- **Lightning-fast package installation with uv** (10-100x faster than pip)

### 🚀 Quick Package Installation

Install new packages instantly with uv:
```bash
# Using the convenience script
./add_package.sh matplotlib seaborn plotly

# Or using make
make install-deps

# Or directly with Docker Compose
docker compose exec jupyter-lab uv pip install --system package_name
```

## � Jupyter Notebooks Guide

### `vllm_batched_inference_example.ipynb`
**Comprehensive Batched Inference Demonstration**

This notebook provides a complete example of using vLLM for batched inference:

**Features:**
- **Health Check**: Verifies vLLM server connectivity and status
- **Single Inference**: Basic single-prompt inference examples
- **Batched Processing**: Efficient processing of multiple prompts simultaneously
- **Performance Analysis**: Timing analysis and throughput measurements
- **Visualization**: Charts showing inference performance and response times
- **Error Handling**: Robust error handling and retry mechanisms
- **Data Export**: Save results to CSV for further analysis
- **Async Processing**: Examples of asynchronous inference for better performance

**Use Cases:**
- Large-scale text processing
- Performance benchmarking
- Batch evaluation of prompts
- Data analysis workflows

### `vllm_inference_remote.ipynb`
**Simple Remote API Connection Examples**

This notebook focuses on basic connectivity and quick testing:

**Features:**
- **Environment Setup**: Loading API keys and configuration from `.env`
- **Basic Connection**: Simple OpenAI-compatible API connection
- **Quick Testing**: Fast inference examples for debugging
- **Configuration Examples**: Different ways to configure the OpenAI client

**Use Cases:**
- Initial setup and testing
- Debugging connection issues
- Quick prototyping
- Learning the API basics

**Current Status**: *Note: This notebook contains some syntax errors in the API calls that need to be fixed for proper execution.*

## �🔧 Usage Examples

### 1. Basic API Call

```python
import requests

response = requests.post(
    "http://vllm-server:8000/v1/chat/completions",
    headers={"Authorization": "Bearer your-api-key-here"},
    json={
        "model": "chatbot",
        "messages": [{"role": "user", "content": "Hello!"}],
        "max_tokens": 100
    }
)
print(response.json())
```

### 2. Batched Inference

The included notebooks demonstrate different aspects of vLLM usage:

**`vllm_batched_inference_example.ipynb`** - Comprehensive demonstration including:
- Health checking the vLLM server
- Single inference requests
- Batched inference with multiple prompts
- Performance analysis and visualization
- Results export to CSV
- Error handling and retry logic

**`vllm_inference_remote.ipynb`** - Simple examples for:
- Basic OpenAI-compatible API connection
- Environment variable configuration
- Quick testing and debugging

### 3. Async Processing

```python
import asyncio
import httpx

async def batch_process(prompts):
    async with httpx.AsyncClient() as client:
        tasks = []
        for prompt in prompts:
            task = client.post(
                "http://vllm-server:8000/v1/chat/completions",
                headers={"Authorization": "Bearer your-api-key-here"},
                json={
                    "model": "chatbot",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100
                }
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

## 🔒 Security Considerations

1. **Change default tokens and API keys**:
   - Update `JUPYTER_TOKEN` in docker-compose.yml
   - Update `--api-key` for vLLM server

2. **Network security**:
   - Services use a dedicated Docker network
   - Consider using reverse proxy for production

3. **Resource limits**:
   - Configure appropriate memory and GPU limits
   - Monitor resource usage

## 🐛 Troubleshooting

### vLLM Server Issues

1. **GPU not detected**:
   ```bash
   # Check GPU availability
   docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
   ```

2. **Model loading errors**:
   - Ensure sufficient memory
   - Check model name and availability
   - Verify HuggingFace access for gated models

3. **Server not responding**:
   ```bash
   # Check container logs
   docker-compose logs vllm-server
   
   # Test connectivity
   curl http://localhost:8000/health
   ```

### Jupyter Lab Issues

1. **Can't access Jupyter**:
   - Verify the token in docker-compose.yml
   - Check port mapping (8888:8888)

2. **Package installation issues**:
   ```bash
   # Rebuild the Jupyter container
   docker-compose build jupyter-lab
   docker-compose up -d
   ```

## 📊 Performance Tips

1. **Model Selection**:
   - Start with smaller models for testing
   - Use quantized models (GPTQ, AWQ) for better memory efficiency

2. **Batch Processing**:
   - Process multiple requests concurrently
   - Use appropriate batch sizes (3-10 requests)
   - Implement proper error handling

3. **Resource Optimization**:
   - Monitor GPU memory usage
   - Adjust `max-model-len` based on your needs
   - Use `tensor-parallel-size` for multi-GPU setups

## 🛠️ Utility Scripts

### `switch_model.sh`
Quick model switching script:
```bash
# Switch to a new model
./switch_model.sh microsoft/DialoGPT-small

# Switch with custom parameters
./switch_model.sh Qwen/Qwen2.5-1.5B-Instruct 4096 1
```

### `add_package.sh`
Fast package installation using uv:
```bash
# Install packages quickly
./add_package.sh matplotlib seaborn plotly
```

### `validate_config.py`
Validate your configuration before starting:
```bash
python validate_config.py
```

### `test_vllm_api.py`
Test API connectivity and performance:
```bash
python test_vllm_api.py
```

## 🛠️ Advanced Configuration

### Using Local Models

1. Place your model files in the `./models` directory
2. Update the docker-compose.yml:
   ```yaml
   command: >
     --model /models/your-model-name
     # ... other parameters
   ```

### Custom Environment Variables

Add environment variables to pass configuration:

```yaml
environment:
  - VLLM_MODEL_NAME=your-model
  - VLLM_MAX_TOKENS=2048
  - JUPYTER_ENABLE_LAB=yes
```

### Production Deployment

For production use, consider:
- Using Docker secrets for sensitive data
- Implementing proper logging and monitoring
- Setting up reverse proxy (nginx/traefik)
- Configuring resource limits and health checks

## 📝 License

This project is provided as-is for educational and development purposes. Please ensure compliance with the licenses of the underlying components (vLLM, Jupyter, model licenses).

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
