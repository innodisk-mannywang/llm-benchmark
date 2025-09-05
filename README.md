# llm-benchmark
### 🚀 Async & OpenAI-Compatible LLM Benchmark
A high-performance benchmarking tool for Large Language Models supporting async execution and OpenAI API format.
Easily measure latency, throughput, and token speed with concurrent requests and streaming response support. Perfect for evaluating both cloud and self-hosted models.

## ✨ Features
- **Real-time Resource Monitoring**: CPU, Memory, and GPU usage tracking
- **Enhanced Reporting**: CV-style console output with detailed metrics
- **Concurrent Testing**: Support for multiple concurrent connections
- **OpenAI Compatible**: Works with any OpenAI-compatible API endpoint
- **Docker Support**: Easy deployment with GPU acceleration support

## 🏋️ Pre-require
* Docker
    * [Docker 20.10+](https://docs.docker.com/engine/install/ubuntu/)
    * Setting docker to group
        ```bash
        sudo usermod -aG docker $USER
        ```
* NVIDIA GPU Support (Optional)
    * [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
    * Required for GPU resource monitoring
* Repository
    * clone the repository
      ```bash
      git clone https://github.com/TsoTing-Li/llm-benchmark.git
      ```
## 🛠️ Build environment in docker
```bash
docker build -f docker/Dockerfile -t llm-benchmark:latest .
```

## 🏁 Startup
```bash
./run-vllm-gptoss.sh --no-pull
docker run -it --rm --name llm-benchmark-tool --gpus all --network=host -v $(pwd):/workspace llm-benchmark bash
```

## ✨ Example
* chat example (CV 風格報告)
    ```bash
    python3 src/benchmark.py \
        --base_url http://localhost:8000 \
        --endpoint /v1/chat/completions \
        --model openai/gpt-oss-20b \
        --num_request 20 \
        --concurrency 8 \
        --prompt "how are you?" \
        --max_tokens 32 \
        --output_file report_llm_chat.json \
        --cv_style_output
    ```
* generate example (CV 風格報告)
    ```bash
    python3 src/benchmark.py \
        --base_url http://localhost:8000 \
        --endpoint /v1/completions \
        --model openai/gpt-oss-20b \
        --num_request 100 \
        --concurrency 16 \
        --dataset_path ShareGPT_tiny.json \
        --max_tokens 32 \
        --output_file report_llm_dataset.json \
        --cv_style_output
    ```
- **For more parameter details, please check** [params.md](docs/params.md)

## 📊 Report

### Console Output (CV Style)
```
================================================================================
🔍 增強版 LLM Benchmark 報告
================================================================================

📊 測試配置:
  • 模型: openai/gpt-oss-20b
  • 資料集/提示: ShareGPT_tiny.json
  • 總請求數: 100
  • 併發連線數: 16
  • 執行時間: 3 秒
  • Provider: Innodisk IPA Dept.

⚡ 性能指標:
  • 總請求速率: 18.51 req/s (requests per second)
  • 每連線速率: 1.16 req/s (requests per second per connection)
  • 平均延遲: 826.15 ms (milliseconds)
  • 延遲範圍: 340.67 - 1863.17 ms (milliseconds)
  • 總吞吐量: 18.51 req/s (requests per second)
  • 平均TTFT: 349.34 ms (Time To First Token, milliseconds)
  • TTFT範圍: 21.00 - 1401.59 ms (milliseconds)

💻 資源使用情況:
  • CPU使用率: 4.7% (最高: 7.2%) (percentage)
  • 記憶體使用率: 3.7% (最高: 3.8%) (percentage)
  • GPU使用率: 28.7% (最高: 45.0%) (percentage)

🎯 輸出統計:
  • 平均回應tokens: 36.00 (tokens per request)
  • 總請求數: 100 (total requests)
  • 成功請求數: 100 (successful requests)

================================================================================
```

### JSON Report
```json
{
  "timestamp": "2025-09-05T01:34:24.349284",
  "configuration": {
    "model": "openai/gpt-oss-20b",
    "dataset": "ShareGPT_tiny.json",
    "concurrency": 16,
    "seconds": 3,
    "provider": "Innodisk IPA Dept."
  },
  "summary": {
    "total_concurrency": 16,
    "total_requests": 100,
    "total_runtime": 3.2857659539949964
  },
  "performance_metrics": {
    "fps": {
      "average": 1.9021440015838442,
      "min": 1.9021440015838442,
      "max": 1.9021440015838442
    },
    "latency_ms": {
      "average": 484.0487191599095,
      "min": 345.65436000411864,
      "max": 510.41040000563953
    },
    "throughput": {
      "average": 1.9021440015838442,
      "total": 30.434304025341508
    }
  },
  "resource_usage": {
    "cpu_percent": {"average": 4.7, "max": 7.2},
    "memory_percent": {"average": 3.7, "max": 3.8},
    "gpu_percent": {"average": 28.7, "max": 45.0}
  },
  "ttft_ms": {
    "average": 349.34,
    "min": 21.00,
    "max": 1401.59
  }
}
```
- **For more report detail, please check** [report.md](docs/report.md)

## 📏 Units & Metrics

### Performance Metrics
- **req/s**: Requests per second (每秒請求數)
- **ms**: Milliseconds (毫秒)
- **TTFT**: Time To First Token (首Token延遲時間)
- **tok/s**: Tokens per second (每秒Token數)

### Resource Usage
- **%**: Percentage (百分比)
- **CPU使用率**: CPU utilization percentage
- **記憶體使用率**: Memory utilization percentage  
- **GPU使用率**: GPU utilization percentage

### Output Statistics
- **tokens**: Number of tokens generated per request
- **requests**: Total number of requests sent
- **successful requests**: Number of successfully completed requests