# Free Patreon publishing checklist

- [ ] Attach a ZIP containing the complete `ComfyUI-Antimeter-YuE2` folder, not only the workflow JSON.
- [ ] Publish `posts/01_FREE_PATREON_POST_EN.md` as the free post body.
- [ ] Attach or link `PROMPT_EXAMPLES.md` as the prompt sheet.
- [ ] Paste the official YuE2 demo, model, source, and CC BY-NC 4.0 licence links from the post.
- [ ] Do not say the pack includes YuE2 weights; it does not.
- [ ] Do not call YuE2 “Suno V6” or claim it is a replacement. The release benchmark compares against Suno v5; use “Suno-class conversation” or “Suno-level ambition” instead.
- [ ] Keep the native Linux/Windows WSL, 24 GB VRAM supported-tier, experimental 16–23.9 GB tier, and non-commercial licence warnings visible above the download link.
- [ ] Test the ZIP on a clean ComfyUI + WSL setup and a clean native Linux ComfyUI setup before publishing. Confirm that the installer rejects an incompatible GPU and that a supported render writes a FLAC, `request.json`, `result.json`, and `artifacts/score.abc`.

## Repository and Manager release checklist

- [ ] Publish the tagged GitHub release and attach the matching starter-pack ZIP.
- [ ] In GitHub Actions, add `REGISTRY_ACCESS_TOKEN` before manually running the **Publish to Comfy Registry** workflow. The token is a Comfy Registry publisher API key, not a GitHub token.
- [ ] Keep the Manager catalogue PR limited to the node package metadata. The Manager install must not run the Windows/WSL or Linux system installer automatically.
- [ ] After a catalogue or Registry approval, verify the entry in a clean ComfyUI Manager installation and repeat the GPU preflight before a first render.
