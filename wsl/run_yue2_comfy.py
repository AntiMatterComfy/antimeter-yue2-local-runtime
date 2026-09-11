#!/usr/bin/env python3
"""The small WSL-side runner used by Antimeter YuE2 Generate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from yue2 import YuE2Pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    audio_path = output_dir / "yue2.flac"

    with YuE2Pipeline.from_pretrained("m-a-p/YuE2-3B", vae=request["vae"], device="cuda") as pipe:
        song = pipe(
            style=request["style"],
            lyrics=request["lyrics"],
            cot=request["cot"],
            seed=int(request["seed"]),
        )
        song.save(str(audio_path))
        song.save_artifacts(str(artifacts_dir))

    score_path = artifacts_dir / "score.abc"
    (output_dir / "result.json").write_text(json.dumps({
        "audio_file": audio_path.name,
        "score_file": str(score_path.relative_to(output_dir)) if score_path.is_file() else "",
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
