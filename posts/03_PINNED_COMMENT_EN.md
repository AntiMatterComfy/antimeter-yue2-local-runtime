# Pinned comment / installation note

**Important:** this is a local runtime for the official YuE2 pipeline: Windows uses WSL 2 and Linux runs natively. It is not a normal drag-and-drop ComfyUI checkpoint and it does not use a Suno API.

The included installers check your NVIDIA GPU before proceeding. The supported tier is BF16-capable NVIDIA with 24 GB VRAM; 16–23.9 GB is experimental, and AMD/Intel, pre-BF16 NVIDIA, and sub-16 GB GPUs are stopped with a clear warning. Follow the README from top to bottom before opening the workflow. The first generation downloads the official YuE2-3B and VAE files.

Model weights are CC BY-NC 4.0: [read the licence](https://huggingface.co/m-a-p/YuE2-3B/blob/main/LICENSE). Use original lyrics and do not use a reference song unless you have the rights to make an adaptation.
