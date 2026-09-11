#!/usr/bin/env bash
set -euo pipefail

NODE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
RUNTIME_DIR="$HOME/yue2-comfy"
PYTHON_BIN=""
INSTALL_SYSTEM_PACKAGES=0
PRELOAD_MODELS=0

usage() {
    cat <<'EOF'
Usage: install_linux.sh [--install-system-packages] [--preload-models] [--runtime-dir PATH] [--python PATH]

--install-system-packages  Use apt to install Python 3.12 and its venv package when needed.
--preload-models           Download and load YuE2 once after installation.
--runtime-dir PATH         Runtime location; default: ~/yue2-comfy.
--python PATH              Python executable; default: python3.12, then python3.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --install-system-packages) INSTALL_SYSTEM_PACKAGES=1 ;;
        --preload-models) PRELOAD_MODELS=1 ;;
        --runtime-dir)
            RUNTIME_DIR="$2"
            shift
            ;;
        --python)
            PYTHON_BIN="$2"
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "INCOMPATIBLE: YuE2 needs an NVIDIA CUDA driver visible to Linux (nvidia-smi was not found)." >&2
    exit 3
fi

GPU_LINE=$(nvidia-smi -i 0 --query-gpu=name,memory.total,compute_cap --format=csv,noheader,nounits | head -n 1)
IFS=',' read -r GPU_NAME GPU_MEMORY GPU_CAPABILITY <<< "$GPU_LINE"
GPU_MEMORY=${GPU_MEMORY//[!0-9]/}
GPU_CAPABILITY=${GPU_CAPABILITY//[!0-9.]/}
if [[ -z "$GPU_NAME" || -z "$GPU_MEMORY" || -z "$GPU_CAPABILITY" ]]; then
    echo "INCOMPATIBLE: could not read NVIDIA GPU 0 VRAM and compute capability." >&2
    exit 3
fi

GPU_GIB=$(awk "BEGIN { printf \"%.1f\", $GPU_MEMORY / 1024 }")
if ! awk "BEGIN { exit !($GPU_CAPABILITY >= 8.0) }"; then
    echo "INCOMPATIBLE: $GPU_NAME has compute capability $GPU_CAPABILITY. YuE2 requires NVIDIA BF16 support (8.0+)." >&2
    exit 3
fi
if (( GPU_MEMORY < 15000 )); then
    echo "INCOMPATIBLE: $GPU_NAME has ${GPU_GIB} GiB VRAM. This pack blocks cards below 16 GiB; upstream recommends 24 GiB." >&2
    exit 3
fi
if (( GPU_MEMORY < 23000 )); then
    echo "EXPERIMENTAL: $GPU_NAME has ${GPU_GIB} GiB VRAM. It is BF16-capable but below the official 24 GiB recommendation; generation can run out of memory." >&2
else
    echo "SUPPORTED: $GPU_NAME has ${GPU_GIB} GiB VRAM and compute capability $GPU_CAPABILITY."
fi

if [[ -z "$PYTHON_BIN" ]]; then
    if command -v python3.12 >/dev/null 2>&1; then
        PYTHON_BIN=python3.12
    else
        PYTHON_BIN=python3
    fi
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1 || ! "$PYTHON_BIN" -m venv --help >/dev/null 2>&1; then
    if (( INSTALL_SYSTEM_PACKAGES == 0 )); then
        echo "Python with venv support is missing. Re-run with --install-system-packages or install Python 3.12 + venv yourself." >&2
        exit 4
    fi
    if ! command -v apt-get >/dev/null 2>&1; then
        echo "Automatic system-package installation is only available on apt-based Linux. Install Python 3.12 and venv manually." >&2
        exit 4
    fi
    sudo apt-get update
    sudo apt-get install -y python3.12 python3.12-venv
    PYTHON_BIN=python3.12
fi

PYTHON_VERSION=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if ! awk "BEGIN { exit !($PYTHON_VERSION >= 3.10) }"; then
    echo "YuE2 requires Python 3.10 or newer; found $PYTHON_VERSION." >&2
    exit 4
fi

mkdir -p "$RUNTIME_DIR"
install -m 755 "$NODE_DIR/wsl/run_yue2_comfy" "$RUNTIME_DIR/run_yue2_comfy"
install -m 755 "$NODE_DIR/wsl/install_yue2.sh" "$RUNTIME_DIR/install_yue2.sh"
install -m 644 "$NODE_DIR/wsl/run_yue2_comfy.py" "$RUNTIME_DIR/run_yue2_comfy.py"
install -m 644 "$NODE_DIR/wsl/preload_models.py" "$RUNTIME_DIR/preload_models.py"
PYTHON="$PYTHON_BIN" "$RUNTIME_DIR/install_yue2.sh"

if (( PRELOAD_MODELS == 1 )); then
    YUE2_HF_HOME="$RUNTIME_DIR/hf_cache" "$RUNTIME_DIR/.venv/bin/python" "$RUNTIME_DIR/preload_models.py"
fi

echo "YuE2 local runtime installed at $RUNTIME_DIR. Restart ComfyUI, then use Antimeter YuE2 Generate with runtime = local_linux."
