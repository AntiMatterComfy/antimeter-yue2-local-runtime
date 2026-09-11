# YuE2 is here: open music generation has reached the Suno-class conversation

**Free YuE2 + ComfyUI Local Runtime Starter Pack**

There is a new open-weight music model worth hearing: **YuE2** from Multimodal Art Projection.

It turns lyrics and a style prompt into complete songs with vocals and accompaniment—but the interesting part is what happens before the audio renders. YuE2 can write an editable melody-and-chord score, so a song is no longer only a lucky audio result. You can inspect the composition, revise the harmony, change a melody, then render a new performance.

That is a serious creative difference. It makes YuE2 feel less like a one-shot “make me a song” button and more like a music-generation instrument.

The authors' 192-prompt WildSongBench reports a **6.9632 SongBench average for YuE2 best-of-8**, versus **6.8721 for Suno v5**. The normal YuE2 setting scored 6.7316. Those are the authors' automatic benchmark results, not proof that one model wins every genre or that YuE2 is a literal Suno V6 replacement—but they absolutely put this open release into the same quality conversation. Listen to the demos before judging: [YuE2 demo gallery](https://map-yue2.github.io/).

## What YuE2 can do

- Write a complete vocal song from lyrics plus a style direction.
- Generate a readable **ABC score** with melody and chords before rendering.
- Re-render an edited score with a new arrangement or revised lyrics.
- Create score-conditioned reinterpretations when you have the right to use the source music.
- Produce 48 kHz stereo audio locally on a capable NVIDIA GPU.

## What is included in this free starter pack

- **Antimeter YuE2 Generate** — a real local-runtime ComfyUI node, not a fake “YuE2-style” workflow.
- Automated installers for **Windows + WSL 2** and **native Linux**, including NVIDIA GPU/VRAM preflight checks.
- A ready-to-import ComfyUI starter workflow.
- An English setup guide with direct official links to the YuE2 model, default VAE, benchmark VAE, and inference wheel.
- Copy-ready prompt examples for pop, synthwave, J-pop, instrumental Afro-house, jazz-funk, and metalcore.
- Saved generation artifacts: the FLAC, request JSON, score, and intermediate assets stay together in your ComfyUI output folder.

## Read this before installing

YuE2 is not currently a standard ComfyUI `.safetensors` checkpoint. The official runtime needs **Linux, CUDA/BF16, and a 24 GB NVIDIA GPU**. The pack runs natively on Linux or uses **WSL 2** from Windows, while keeping each generation inside the normal ComfyUI workflow. It runs fully locally—no cloud music API and no prompt upload.

The installer enables the official 24 GB BF16 tier, allows 16–23.9 GB BF16 NVIDIA cards as an explicitly marked experimental path, and stops unsupported systems with an actionable warning. It cannot make AMD/Intel GPUs or low-VRAM cards compatible with YuE2's released CUDA runtime.

The model weights are released under **CC BY-NC 4.0**. This is a free, non-commercial starter pack; review the upstream licence yourself before using the weights, sharing them, or making commercial plans around them.

## Start here

1. Install the included custom node in `ComfyUI/custom_nodes/`.
2. Run the one-command Windows or Linux installer in the included README.
3. Open `workflows/Antimeter_YuE2_Local_Starter.json`.
4. Write a style direction, add original lyrics, and click **Queue Prompt**.

For your first render, leave `cot = full` and the default **YuE2-Vae** selected. After the job completes, open the saved `score.abc` if you want to make the next version more intentional.

Official links: [YuE2 source](https://github.com/multimodal-art-projection/YuE) · [YuE2-3B model](https://huggingface.co/m-a-p/YuE2-3B) · [YuE2-Vae](https://huggingface.co/m-a-p/YuE2-Vae) · [model licence](https://huggingface.co/m-a-p/YuE2-3B/blob/main/LICENSE).

If you make something with it, share a short clip, your style prompt, the lyrics format, and whether you used `full`, `melody`, or `off`. I want to hear where this model is strong—and where it still needs work.

— AntiMatter Comfy
