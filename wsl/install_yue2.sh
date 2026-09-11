#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3.12}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Python 3.12 was not found. Install python3.12 and python3.12-venv, then run this script again." >&2
    exit 1
fi

"$PYTHON" -m venv "$SCRIPT_DIR/.venv"
"$SCRIPT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$SCRIPT_DIR/.venv/bin/python" -m pip install huggingface-hub==0.36.2
"$SCRIPT_DIR/.venv/bin/hf" download m-a-p/YuE2-3B yue2_infer-0.1.5-py3-none-any.whl --local-dir "$SCRIPT_DIR"
"$SCRIPT_DIR/.venv/bin/python" -m pip install "$SCRIPT_DIR/yue2_infer-0.1.5-py3-none-any.whl"

echo "YuE2 WSL runtime is installed. The first generation downloads the official YuE2-3B and YuE2-Vae weights."
