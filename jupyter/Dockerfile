FROM jupyter/scipy-notebook:latest

USER root

# Install system dependencies and uv (install uv system-wide)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sh

# Verify uv is installed correctly
RUN which uv && uv --version

USER jovyan

# Create necessary directories
RUN mkdir -p /home/jovyan/.local /home/jovyan/.cache

# Copy requirements file
COPY requirements.txt /tmp/requirements.txt

# Install Python packages using uv (much faster than pip)
# Use --system flag to install to system Python since we're in a container
RUN uv pip install --system -r /tmp/requirements.txt

# Create directories for notebooks and data
RUN mkdir -p /home/jovyan/work /home/jovyan/data

# Set working directory
WORKDIR /home/jovyan/work

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter Lab
# Use shell form to allow environment variable expansion
CMD jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --ServerApp.token="${JUPYTER_TOKEN}" \
    --ServerApp.password="${JUPYTER_PASSWORD}" \
    --ServerApp.disable_check_xsrf=True
