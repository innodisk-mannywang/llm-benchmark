#!/usr/bin/env bash

set -euo pipefail

# Defaults
IMAGE_NAME="vllm/vllm-openai:latest"
CONTAINER_NAME="vllm-model-server"
MODEL_NAME="openai/gpt-oss-20b"
PORT=8000
MAX_MODEL_LEN=8192
GPUS="all"
HF_TOKEN_DEFAULT=""
PULL_IMAGE=true

print_usage() {
  cat <<EOF
Usage: $(basename "$0") [options] [-- server_args...]

Options:
  --model_name <repo_or_path>   Model repo id or local path (default: ${MODEL_NAME})
  --hf_token <token>            HuggingFace token (default: built-in token)
  --port <port>                 API port (default: ${PORT})
  --max_model_len <len>         Max model length (default: ${MAX_MODEL_LEN})
  --name <container_name>       Container name (default: ${CONTAINER_NAME})
  --gpus <gpus>                 GPUs for Docker --gpus (default: ${GPUS})
  --no-pull                     Skip docker pull
  -h, --help                    Show this help

Notes:
  - Uses --network=host and mounts ~/.cache/huggingface.
EOF
}

SERVER_ARGS=()
HF_TOKEN="${HF_TOKEN_DEFAULT}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model_name)
      MODEL_NAME="$2"; shift 2 ;;
    --hf_token)
      HF_TOKEN="$2"; shift 2 ;;
    --port)
      PORT="$2"; shift 2 ;;
    --max_model_len)
      MAX_MODEL_LEN="$2"; shift 2 ;;
    --name)
      CONTAINER_NAME="$2"; shift 2 ;;
    --gpus)
      GPUS="$2"; shift 2 ;;
    --no-pull)
      PULL_IMAGE=false; shift 1 ;;
    -h|--help)
      print_usage; exit 0 ;;
    --)
      shift; SERVER_ARGS=("$@"); break ;;
    *)
      echo "Unknown option: $1" >&2; print_usage; exit 1 ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker not found in PATH" >&2
  exit 1
fi

if [[ "${PULL_IMAGE}" == "true" ]]; then
  echo "Pulling image ${IMAGE_NAME} ..."
  docker pull "${IMAGE_NAME}" | cat
fi

# Remove existing container if name conflicts
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Removing existing container ${CONTAINER_NAME} ..."
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
fi

set -x
docker run -d \
  --name "${CONTAINER_NAME}" \
  --runtime nvidia --gpus "${GPUS}" \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --ipc=host \
  --network=host \
  -p "${PORT}" \
  --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}" \
  "${IMAGE_NAME}" \
  --model "${MODEL_NAME}" \
  --port "${PORT}" \
  --max_model_len "${MAX_MODEL_LEN}" \
  "${SERVER_ARGS[@]}"
set +x

echo "Started vLLM container '${CONTAINER_NAME}'."
echo "Health check: curl -s http://localhost:${PORT}/v1/models | jq ."

# 等待服務就緒並顯示狀態
echo "⏳ 等待 vLLM 服務啟動..."
i=0
until curl -sf http://localhost:${PORT}/v1/models >/dev/null 2>&1; do
  echo "   等待中... ($((i*3)) 秒)"
  sleep 3
  i=$((i+1))
  if [ $i -ge 60 ]; then
    echo "❌ 服務啟動超時 (3分鐘)"
    echo "請檢查容器日誌: docker logs ${CONTAINER_NAME}"
    exit 1
  fi
done

echo "✅ vLLM 服務已就緒！"
echo "📊 模型資訊:"
curl -s http://localhost:${PORT}/v1/models | jq '.data[0] | {id, object, max_model_len}'