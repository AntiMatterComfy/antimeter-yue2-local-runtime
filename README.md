# Antimeter YuE2 Local Runtime for ComfyUI

Run the official YuE2 music pipeline from ComfyUI on either:

- **Windows + WSL 2** — ComfyUI stays on Windows; YuE2 runs locally in Ubuntu/WSL.
- **Native Linux** — ComfyUI and YuE2 run on the same Linux machine.

This is not a converted ComfyUI checkpoint. YuE2 is loaded by its official Hugging Face pipeline, then the node returns its 48 kHz FLAC to ComfyUI as `AUDIO`. The release contains no model weights and never sends prompts or audio to a cloud API.

YuE2 model weights are **CC BY-NC 4.0**. Review that licence, and the rights in your inputs and outputs, before planning a commercial use.

## Automated installation

Extract the complete `ComfyUI-Antimeter-YuE2` folder into `ComfyUI/custom_nodes/` first.

### ComfyUI Manager installation

Once the Manager catalogue pull request is merged, search **Antimeter YuE2 Local Runtime** in ComfyUI Manager and install the node package. Restart ComfyUI, then run the matching Windows or Linux installer below. Manager installs the node code only; it deliberately does **not** install WSL, Linux packages, Python, or model weights automatically.

This separation is intentional: the YuE2 runtime needs a local NVIDIA/WSL/Linux environment and a multi-gigabyte Hugging Face download. The platform installers validate the GPU and show an actionable incompatibility warning before changing that environment.

### Windows 10/11 + WSL 2

Open PowerShell in the extracted node folder and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\installers\install_windows.ps1 -InstallWsl -PreloadModels
```

`-InstallWsl` is only needed when Ubuntu/WSL is not already installed. Windows may ask for a reboot and Ubuntu may ask you to create a Linux username; run the same command once more after that. Omit `-PreloadModels` to download the weights during the first ComfyUI render.

The installer checks GPU 0 on Windows, then checks the same GPU inside the selected WSL distribution before it installs Python, the official inference wheel, runtime scripts, and optionally the models. Use another apt-based distribution with `-Distro Debian`; otherwise it automatically selects your default installed WSL distribution.

### Native Linux

Open a terminal in the extracted node folder and run:

```bash
chmod +x installers/install_linux.sh
./installers/install_linux.sh --install-system-packages --preload-models
```

On non-apt Linux, install Python 3.12 with venv support yourself, then run `./installers/install_linux.sh --preload-models`. Omit `--preload-models` to delay the large model download until the first render. Use `--help` to select another runtime directory or Python executable.

Restart ComfyUI after a successful installation. Search for **Antimeter YuE2 Generate** and open `workflows/Antimeter_YuE2_Local_Starter.json`. Leave `runtime = auto`: it selects WSL on Windows and native execution on Linux.

## Automatic GPU compatibility policy

The installer and generation node inspect **NVIDIA GPU 0** with `nvidia-smi` before installing or rendering. They classify the machine as follows:

| Tier | Rule | Behaviour |
|---|---|---|
| Supported | NVIDIA CUDA GPU, compute capability **8.0+** (BF16), **24 GB-class VRAM** (at least 23,000 MiB reported) | Installation and generation are enabled. This is YuE2's published hardware target. |
| Experimental | NVIDIA CUDA GPU, compute capability **8.0+**, **16–23.9 GB-class VRAM** (15,000–22,999 MiB reported) | Installation and generation are allowed with a visible warning. An out-of-memory failure remains possible. |
| Incompatible | No NVIDIA CUDA GPU, compute capability below 8.0, or under the 16 GB-class threshold | Installation/generation stops with an actionable message. |

The official YuE2 release specifies Linux, CUDA/BF16, a 24 GB NVIDIA GPU, and 24 GB available host RAM. The model authors do not publish a ComfyUI certification matrix, so this pack cannot honestly guarantee every card by marketing name. It guarantees that cards in the **Supported** tier pass the pack's documented hardware gate; actual performance still depends on drivers, CUDA in WSL/Linux, free VRAM, system RAM, and other GPU jobs.

### Common GPUs in the Supported tier

These cards meet the published 24 GB + BF16 hardware rule when the NVIDIA driver and CUDA runtime are healthy:

- GeForce RTX 3090 and RTX 4090
- RTX A5000, RTX A5500, RTX A6000, and RTX 6000 Ada
- NVIDIA A10, A100, H100, and newer data-center cards with at least 24 GB VRAM

Examples such as RTX 3080 Ti 12 GB, RTX 4080 16 GB, RTX A4000 16 GB, and RTX 4000 Ada 20 GB are **not guaranteed**. A 16–23.9 GB Ampere-or-newer NVIDIA card can use the experimental path; cards below 16 GB and AMD/Intel GPUs are blocked because the released YuE2 runtime requires CUDA/BF16.

If your machine has multiple GPUs, make the intended YuE2 card GPU 0 before installing or set `CUDA_VISIBLE_DEVICES` so that the selected device becomes index 0. The current official pipeline uses `device="cuda"`.

## What the node saves

Every successful execution creates a separate folder in:

```text
ComfyUI/output/audio/YuE2/<job-id>/
```

It contains `yue2.flac`, `request.json`, `result.json`, and `artifacts/`. In full or melody planning modes, `artifacts/score.abc` is the editable composition. The node's `gpu_status` output reports whether the job used the supported or experimental hardware tier. **Antimeter YuE2 GPU Check** can run the same preflight without rendering a song.

## First workflow

1. Enter a compact **style** direction: language, genre, lead vocal, instruments, arrangement, and mix.
2. Add sectioned **lyrics**. Write `[Instrumental]` when you do not want singing.
3. Start with `cot = full`; it creates an editable melody-and-chord plan. Use `melody` for score-driven covers and `off` for direct generation without a symbolic plan.
4. Use the default **YuE2-Vae** for listening. Select **YuE2-Vae-legacy** only when you specifically need the benchmark decoder.
5. Connect `audio` to ComfyUI's **Save Audio (FLAC)** node. `score_path`, `artifacts_path`, and `gpu_status` remain available for inspection.

## Official downloads

YuE2 uses Hugging Face repository layouts, not `.safetensors` files placed into ComfyUI's normal `models/checkpoints` directory. The installers use the official inference wheel and store the full repository cache in `~/yue2-comfy/hf_cache`. Let the official pipeline download it automatically, or use the direct links below to inspect/download the artifacts.

| Item | Direct official download | Purpose |
|---|---|---|
| YuE2 inference wheel | [yue2_infer-0.1.5-py3-none-any.whl](https://huggingface.co/m-a-p/YuE2-3B/resolve/main/yue2_infer-0.1.5-py3-none-any.whl?download=true) | Installed by the automated installers |
| YuE2-3B weights | [model.safetensors](https://huggingface.co/m-a-p/YuE2-3B/resolve/main/model.safetensors?download=true) | Main song-generation model; its repository also needs config/tokenizer files |
| Default decoder | [YuE2-Vae model.safetensors](https://huggingface.co/m-a-p/YuE2-Vae/resolve/main/model.safetensors?download=true) | Recommended for perceptual audio quality |
| Benchmark decoder | [YuE2-Vae-legacy model.safetensors](https://huggingface.co/m-a-p/YuE2-Vae-legacy/resolve/main/model.safetensors?download=true) | Used for the reported benchmark protocol |

Official model pages: [YuE2-3B](https://huggingface.co/m-a-p/YuE2-3B) · [YuE2-Vae](https://huggingface.co/m-a-p/YuE2-Vae) · [YuE2-Vae-legacy](https://huggingface.co/m-a-p/YuE2-Vae-legacy).

## Sources and licence

- [YuE2 source and generation guide](https://github.com/multimodal-art-projection/YuE)
- [YuE2 demos](https://map-yue2.github.io/)
- [YuE2 model card, hardware notes, and benchmark details](https://huggingface.co/m-a-p/YuE2-3B)
- [CC BY-NC 4.0 model licence](https://huggingface.co/m-a-p/YuE2-3B/blob/main/LICENSE)

YuE2's source code is Apache-2.0, but its model weights are separately CC BY-NC 4.0. This is an independent community integration and is not affiliated with Multimodal Art Projection, Suno, Hugging Face, or ComfyUI.
