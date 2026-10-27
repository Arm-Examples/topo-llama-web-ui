# Topo llama.cpp web UI

> This is a [Topo](https://github.com/arm/topo) Project and follows the [Topo Project Specification](https://github.com/arm/topo/tree/main/docs/project-specification).

Complete LLM chat application with Arm CPU inference provided by llama.cpp.

## Overview

This project demonstrates running large language models on CPU with inference provided by the llama.cpp server and a configurable GGUF model.

The upstream Linux Arm64 llama.cpp server image is built with architecture-specific CPU backend variants enabled. llama.cpp can then load a backend variant that matches the Arm CPU features available at runtime.

The stack includes:

- llama.cpp
- Qwen3-30B-A3B-Instruct-2507 with target-aware precision selection
- Built-in web chat interface
- No GPU required - pure CPU inference

## Arm CPU Optimizations

The prebuilt `ghcr.io/ggml-org/llama.cpp:server` image currently enables llama.cpp CPU backend variants for Linux Arm. This project pins the image digest so these exact variants remain stable.

The Linux Arm backend variants and feature combinations are defined in upstream [`ggml/src/CMakeLists.txt`](https://github.com/ggml-org/llama.cpp/blob/ac4cddeb0dbd778f650bf568f6f08344a06abe3a/ggml/src/CMakeLists.txt#L403-L415), and the CPU server image is built with `GGML_CPU_ALL_VARIANTS=ON` in upstream [`.devops/cpu.Dockerfile`](https://github.com/ggml-org/llama.cpp/blob/ac4cddeb0dbd778f650bf568f6f08344a06abe3a/.devops/cpu.Dockerfile#L15-L19).

| Backend variant | Arm features included                                                     |
| --------------- | ------------------------------------------------------------------------- |
| `armv8.0_1`     | Baseline Armv8.0                                                          |
| `armv8.2_1`     | Dot product                                                               |
| `armv8.2_2`     | Dot product, FP16 vector arithmetic                                       |
| `armv8.2_3`     | Dot product, FP16 vector arithmetic, SVE                                  |
| `armv8.6_1`     | Dot product, FP16 vector arithmetic, SVE, int8 matrix multiply            |
| `armv8.6_2`     | Dot product, FP16 vector arithmetic, SVE, int8 matrix multiply, SVE2      |
| `armv9.2_1`     | Dot product, FP16 vector arithmetic, SVE, int8 matrix multiply, SME       |
| `armv9.2_2`     | Dot product, FP16 vector arithmetic, SVE, int8 matrix multiply, SVE2, SME |

## Prerequisites

1. **Arm Hardware**: An Arm system (physical or virtual).
2. **Docker**: For container orchestration with Topo
3. **Topo**: An experimental build supporting `configure --target` and parameter fact bindings.

`topo configure --target` supplies target RAM to the build. [gguf-parser](https://github.com/gpustack/gguf-parser-go) estimates CPU memory from remote GGUF metadata, without downloading weights. The selector chooses the highest supported precision estimated to fit, from Q2_K through BF16/F16.

The default model is Qwen3-30B-A3B-Instruct-2507; other GGUF repositories with supported precisions can also be used. The model downloads at startup and is cached inside the container, including all shards when needed.

Selection uses total RAM minus an OS reserve, not currently available memory. Estimates are not a fit or performance guarantee; check available RAM before deploying. Estimates include resident weights, KV cache, and compute buffers at the configured context and batch size.

## Build-Time Parameters

| Parameter           | Description                                                         | Default                                           |
| ------------------- | ------------------------------------------------------------------- | ------------------------------------------------- |
| `MODEL`             | Hugging Face GGUF repository ID                                     | `bartowski/Qwen_Qwen3-30B-A3B-Instruct-2507-GGUF` |
| `MODEL_ENDPOINT`    | Hugging Face API-compatible endpoint for repository model downloads | `https://huggingface.co`                          |
| `TARGET_MEMORY_KIB` | Target RAM in KiB, populated by `configure --target`                | From target                                       |
| `CONTEXT_LENGTH`    | Context tokens for estimation and inference                         | `4096`                                            |

## Usage

The easiest way to deploy is using `topo`. Download and install `topo` from [here](https://github.com/arm/topo)

### Clone the project:

```bash
export TOPO_EXPERIMENTAL_FEATURES=1
topo clone https://github.com/Arm-Examples/topo-llama-web-ui.git --target <ip-address-of-target>
```

### Build and Deploy the project:

```bash
cd topo-llama-web-ui
topo deploy --target <ip-address-of-target>
```

### Common Model Selection Examples

Use a different model:

```bash
topo configure MODEL=bartowski/Qwen2.5-14B-Instruct-GGUF
```

### Access the Chat Interface

Open your browser to `http://<ip-address-of-target>:8080` to start chatting!
