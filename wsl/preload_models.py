#!/usr/bin/env python3
"""Download and validate the official YuE2 model repositories without rendering."""

from yue2 import YuE2Pipeline


with YuE2Pipeline.from_pretrained("m-a-p/YuE2-3B", device="cuda"):
    print("YuE2-3B and the default YuE2-Vae are ready in the local Hugging Face cache.")
