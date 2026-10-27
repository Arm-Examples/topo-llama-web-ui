"""Select the highest supported GGUF precision estimated to fit target RAM."""

import json
import os
import re
import subprocess

from huggingface_hub import HfApi, hf_hub_url

QUANTS = ("BF16", "F16", "Q8_0", "Q6_K", "Q5_K_M", "Q4_K_M", "Q3_K_M", "Q2_K")
FILENAME = re.compile(
    rf"(?:^|[.-])({'|'.join(QUANTS)})(?:-00001-of-\d{{5}})?\.gguf$", re.I
)


def main():
    memory = os.getenv("TARGET_MEMORY_KIB")
    context = int(os.environ["CONTEXT_LENGTH"])
    if context <= 0 or (memory and int(memory) <= 0):
        raise ValueError("TARGET_MEMORY_KIB and CONTEXT_LENGTH must be positive")
    repo, endpoint = os.environ["MODEL"], os.environ["MODEL_ENDPOINT"]
    info = HfApi(endpoint=endpoint).model_info(repo)
    candidates = []
    for file in info.siblings or []:
        match = FILENAME.search(file.rfilename)
        if match and "mmproj" not in file.rfilename.lower():
            quant = match[1].upper()
            url = hf_hub_url(repo, file.rfilename, revision=info.sha, endpoint=endpoint)
            candidates.append((QUANTS.index(quant), url))
    candidates.sort()
    if not memory:
        for quality, url in candidates:
            if QUANTS[quality] == "Q4_K_M":
                print(url)
                return
        raise ValueError("Q4_K_M is unavailable")

    total = int(memory) * 1024
    # Reserve RAM for the OS and background processes.
    budget = total - max(4 * 1024**3, min(int(total * 0.15), 32 * 1024**3))
    for _, url in candidates:
        result = subprocess.run([
            "gguf-parser", "--url", url, "--json", "--gpu-layers", "0",
            "--ctx-size", str(context), "--batch-size", "512",
            "--ubatch-size", "512", "--parallel-size", "1", "--no-mmap",
        ], check=True, stdout=subprocess.PIPE, text=True)
        report = json.loads(result.stdout)
        if context > report["architecture"]["maximumContextLength"]:
            raise ValueError("requested context exceeds model limit")
        # Include resident weights even though llama.cpp can memory-map them.
        required = report["estimate"]["items"][0]["ram"]["nonuma"]
        if required <= budget:
            print(url)
            return
    raise ValueError("no supported quantization fits; use a smaller model or context")


if __name__ == "__main__":
    main()
