FROM --platform=$BUILDPLATFORM python:3.12-slim AS selection
ARG BUILDARCH
ADD --chmod=755 https://github.com/gpustack/gguf-parser-go/releases/download/v0.27.0/gguf-parser-linux-${BUILDARCH} /usr/local/bin/gguf-parser
WORKDIR /selector
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY select_model.py ./
ARG MODEL=bartowski/Qwen_Qwen3-30B-A3B-Instruct-2507-GGUF
ARG MODEL_ENDPOINT=https://huggingface.co
ARG TARGET_MEMORY_KIB
ARG CONTEXT_LENGTH=4096
RUN python select_model.py > /model-url.txt

FROM ghcr.io/ggml-org/llama.cpp:server@sha256:df320e983b2871d31fcb88165eedfcbd5156841d3d7dbd2b7ea3e85a1e1286a1

ARG CONTEXT_LENGTH=4096

ENV N_CTX=${CONTEXT_LENGTH}
ENV N_THREADS=8
ENV N_BATCH=512
ENV N_GPU_LAYERS=0

WORKDIR /app

COPY --from=selection /model-url.txt /app/model-url.txt

COPY --chmod=755 entrypoint.sh /usr/local/bin/topo-llama-entrypoint

HEALTHCHECK --interval=30s --timeout=5s --start-period=300s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/topo-llama-entrypoint"]
CMD []
