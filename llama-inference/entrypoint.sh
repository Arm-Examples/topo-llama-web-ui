#!/bin/sh
set -eu

model_ref=$(cat /app/model-url.txt)

set -- \
  --host 0.0.0.0 \
  --port 8080 \
  --ctx-size "${N_CTX}" \
  --parallel 1 \
  --threads "${N_THREADS}" \
  --batch-size "${N_BATCH}" \
  --n-gpu-layers "${N_GPU_LAYERS}" \
  --model-url "$model_ref" \
  "$@"

exec /app/llama-server "$@"
