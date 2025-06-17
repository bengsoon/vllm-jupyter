#!/usr/bin/env python3
"""
Configuration validation script for vLLM + Jupyter Docker Compose project.
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Global variable to store the Docker Compose command that works
DOCKER_COMPOSE_CMD = None


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_status(message: str, status: str = "info"):
    """Print colored status messages."""
    if status == "success":
        print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.ENDC}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")
    else:
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")


def check_docker_installation() -> bool:
    """Check if Docker and Docker Compose are installed."""
    try:
        # Check Docker
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_status(f"Docker found: {result.stdout.strip()}", "success")
        else:
            print_status("Docker not found or not working", "error")
            return False
            
        # Check Docker Compose - try new syntax first (docker compose)
        compose_found = False
        compose_command = None
        
        # Try new Docker Compose (docker compose)
        try:
            result = subprocess.run(['docker', 'compose', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print_status(f"Docker Compose found (new syntax): {result.stdout.strip()}", "success")
                compose_found = True
                compose_command = "docker compose"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try legacy Docker Compose (docker-compose) if new syntax failed
        if not compose_found:
            try:
                result = subprocess.run(['docker-compose', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print_status(f"Docker Compose found (legacy syntax): {result.stdout.strip()}", "success")
                    compose_found = True
                    compose_command = "docker-compose"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        if not compose_found:
            print_status("Docker Compose not found - neither 'docker compose' nor 'docker-compose' work", "error")
            print_status("Please install Docker Compose or Docker Desktop", "error")
            return False
        
        # Store the working command for later use
        global DOCKER_COMPOSE_CMD
        DOCKER_COMPOSE_CMD = compose_command
        
        return True
        
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print_status(f"Error checking Docker installation: {e}", "error")
        return False


def check_nvidia_gpu() -> bool:
    """Check NVIDIA GPU availability."""
    try:
        result = subprocess.run(['nvidia-smi'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Extract GPU info
            lines = result.stdout.split('\n')
            gpu_lines = [line for line in lines if 'GeForce' in line or 'Tesla' in line or 'RTX' in line]
            if gpu_lines:
                print_status("NVIDIA GPU detected:", "success")
                for gpu_line in gpu_lines:
                    print(f"   {gpu_line.strip()}")
            else:
                print_status("NVIDIA drivers installed but no GPU info found", "warning")
            return True
        else:
            print_status("NVIDIA drivers not found - GPU acceleration unavailable", "warning")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_status("nvidia-smi not found - GPU acceleration unavailable", "warning")
        return False


def check_file_structure() -> List[str]:
    """Check if required files and directories exist."""
    required_files = [
        'docker-compose.yml',
        'jupyter/Dockerfile',
        'jupyter/requirements.txt',
        'README.md'
    ]
    
    required_dirs = [
        'jupyter',
        'notebooks',
        'models',
        'data'
    ]
    
    issues = []
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            print_status(f"Found: {file_path}", "success")
        else:
            print_status(f"Missing: {file_path}", "error")
            issues.append(f"Missing file: {file_path}")
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print_status(f"Found directory: {dir_path}", "success")
        else:
            print_status(f"Missing directory: {dir_path}", "error")
            issues.append(f"Missing directory: {dir_path}")
    
    return issues


def validate_docker_compose() -> List[str]:
    """Validate docker-compose.yml file."""
    issues = []
    
    try:
        with open('docker-compose.yml', 'r') as f:
            compose_data = yaml.safe_load(f)
        
        # Check required services
        services = compose_data.get('services', {})
        required_services = ['vllm-server', 'jupyter-lab']
        
        for service in required_services:
            if service in services:
                print_status(f"Service '{service}' found in compose file", "success")
            else:
                print_status(f"Service '{service}' missing from compose file", "error")
                issues.append(f"Missing service: {service}")
        
        # Check port mappings
        for service_name, service_config in services.items():
            ports = service_config.get('ports', [])
            if ports:
                print_status(f"Service '{service_name}' has port mappings: {ports}", "success")
            else:
                print_status(f"Service '{service_name}' has no port mappings", "warning")
        
        # Check networks
        if 'networks' in compose_data:
            print_status("Custom networks defined", "success")
        else:
            print_status("No custom networks defined - using default", "warning")
            
    except FileNotFoundError:
        issues.append("docker-compose.yml file not found")
        print_status("docker-compose.yml file not found", "error")
    except yaml.YAMLError as e:
        issues.append(f"Invalid YAML in docker-compose.yml: {e}")
        print_status(f"Invalid YAML in docker-compose.yml: {e}", "error")
    
    return issues


def check_environment_file() -> List[str]:
    """Check environment configuration."""
    issues = []
    
    if os.path.exists('.env'):
        print_status("Environment file (.env) found", "success")
        
        # Check for default/insecure values
        with open('.env', 'r') as f:
            env_content = f.read()
            
        insecure_values = [
            'your-api-key-here',
            'your-secure-token-here',
            'password123',
            'admin'
        ]
        
        for insecure_value in insecure_values:
            if insecure_value in env_content:
                print_status(f"Insecure default value found: {insecure_value}", "warning")
                issues.append(f"Change default value: {insecure_value}")
        
    else:
        if os.path.exists('.env.example'):
            print_status("No .env file found, but .env.example exists", "warning")
            issues.append("Copy .env.example to .env and configure your settings")
        else:
            print_status("No environment files found", "error")
            issues.append("Create .env file with your configuration")
    
    return issues


def check_system_resources() -> List[str]:
    """Check system resources."""
    issues = []
    
    try:
        # Check available memory
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        
        for line in meminfo.split('\n'):
            if line.startswith('MemTotal:'):
                mem_kb = int(line.split()[1])
                mem_gb = mem_kb / (1024 * 1024)
                
                if mem_gb >= 8:
                    print_status(f"System memory: {mem_gb:.1f} GB", "success")
                elif mem_gb >= 4:
                    print_status(f"System memory: {mem_gb:.1f} GB (low for large models)", "warning")
                    issues.append("Consider using smaller models or adding more RAM")
                else:
                    print_status(f"System memory: {mem_gb:.1f} GB (insufficient)", "error")
                    issues.append("Insufficient RAM - need at least 4GB, 8GB+ recommended")
                break
        
        # Check disk space
        disk_usage = subprocess.run(['df', '-h', '.'], 
                                  capture_output=True, text=True)
        if disk_usage.returncode == 0:
            lines = disk_usage.stdout.strip().split('\n')
            if len(lines) > 1:
                disk_info = lines[1].split()
                available = disk_info[3]
                print_status(f"Available disk space: {available}", "success")
        
    except Exception as e:
        print_status(f"Could not check system resources: {e}", "warning")
    
    return issues


def main():
    """Main validation function."""
    print(f"{Colors.BOLD}🔍 vLLM + Jupyter Docker Compose Configuration Validation{Colors.ENDC}")
    print("=" * 70)
    print()
    
    all_issues = []
    
    # Check Docker installation
    print(f"{Colors.BOLD}1. Docker Installation{Colors.ENDC}")
    print("-" * 30)
    if not check_docker_installation():
        print_status("Docker installation check failed", "error")
        return 1
    print()
    
    # Check NVIDIA GPU
    print(f"{Colors.BOLD}2. GPU Support{Colors.ENDC}")
    print("-" * 30)
    check_nvidia_gpu()
    print()
    
    # Check file structure
    print(f"{Colors.BOLD}3. File Structure{Colors.ENDC}")
    print("-" * 30)
    file_issues = check_file_structure()
    all_issues.extend(file_issues)
    print()
    
    # Validate docker-compose.yml
    print(f"{Colors.BOLD}4. Docker Compose Configuration{Colors.ENDC}")
    print("-" * 40)
    compose_issues = validate_docker_compose()
    all_issues.extend(compose_issues)
    print()
    
    # Check environment configuration
    print(f"{Colors.BOLD}5. Environment Configuration{Colors.ENDC}")
    print("-" * 40)
    env_issues = check_environment_file()
    all_issues.extend(env_issues)
    print()
    
    # Check system resources
    print(f"{Colors.BOLD}6. System Resources{Colors.ENDC}")
    print("-" * 30)
    resource_issues = check_system_resources()
    all_issues.extend(resource_issues)
    print()
    
    # Summary
    print(f"{Colors.BOLD}📋 Validation Summary{Colors.ENDC}")
    print("=" * 30)
    
    if not all_issues:
        print_status("All checks passed! Your configuration looks good.", "success")
        print()
        print("🚀 You can now start the services with:")
        print("   ./start.sh")
        print("   # or")
        print("   make up")
        return 0
    else:
        print_status(f"Found {len(all_issues)} issues that need attention:", "warning")
        print()
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        print()
        print("🔧 Please fix these issues before starting the services.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
