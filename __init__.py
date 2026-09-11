"""YuE2 generation through a user-installed local runtime."""

from __future__ import annotations

import json
from pathlib import Path
import platform
import re
import shlex
import subprocess
from uuid import uuid4

import folder_paths
from comfy_extras.nodes_audio import load as load_audio


_WSL_DISTRO = re.compile(r"^[A-Za-z0-9_.-]+$")
_OUTPUT_NAME = re.compile(r"[^A-Za-z0-9_-]+")
_GPU_MEMORY = re.compile(r"(\d+)")
_COMPUTE_CAPABILITY = re.compile(r"\d+(?:\.\d+)?")
_EXPERIMENTAL_MIN_VRAM_MIB = 15_000
_SUPPORTED_MIN_VRAM_MIB = 23_000


def _to_wsl_path(path: Path) -> str:
    """Translate a local Windows path to its normal WSL /mnt mount."""
    resolved = path.resolve()
    drive = resolved.drive
    if len(drive) != 2 or drive[1] != ":":
        raise ValueError("The YuE2 WSL bridge needs ComfyUI on a local Windows drive.")
    tail = str(resolved)[2:].replace("\\", "/").lstrip("/")
    return f"/mnt/{drive[0].lower()}/{tail}"


def _wsl_runner_expression(runner_path: str) -> str:
    """Quote a POSIX runner path while allowing the useful ~/ shorthand."""
    value = runner_path.strip()
    if not value:
        raise ValueError("Set the WSL YuE2 runner path.")
    if value == "~":
        return '"$HOME"'
    if value.startswith("~/"):
        return '"$HOME"/' + shlex.quote(value[2:])
    return shlex.quote(value)


def _safe_output_folder(value: str) -> str:
    name = _OUTPUT_NAME.sub("_", value.strip()).strip("_.-")
    return name or "YuE2"


def _job_file(job_dir: Path, relative_name: str) -> Path:
    candidate = (job_dir / relative_name).resolve()
    try:
        candidate.relative_to(job_dir.resolve())
    except ValueError as exc:
        raise RuntimeError("YuE2 returned a file path outside its ComfyUI job folder.") from exc
    return candidate


def _last_output(result: subprocess.CompletedProcess[str]) -> str:
    text = (result.stderr or result.stdout or "The WSL runtime returned no diagnostic output.").strip()
    return text[-4000:]


def _select_runtime(value: str) -> str:
    if value == "auto":
        if platform.system() == "Windows":
            return "windows_wsl"
        if platform.system() == "Linux":
            return "local_linux"
        raise RuntimeError("YuE2 supports Windows through WSL 2 or a native Linux ComfyUI installation.")
    if value == "windows_wsl" and platform.system() != "Windows":
        raise RuntimeError("The Windows WSL runtime can only be selected from Windows.")
    if value == "local_linux" and platform.system() != "Linux":
        raise RuntimeError("The local Linux runtime can only be selected from Linux.")
    return value


def _gpu_details(runtime: str, wsl_distro: str) -> tuple[str, int, float]:
    query = ["nvidia-smi", "-i", "0", "--query-gpu=name,memory.total,compute_cap", "--format=csv,noheader,nounits"]
    if runtime == "windows_wsl":
        if not _WSL_DISTRO.fullmatch(wsl_distro):
            raise ValueError("The WSL distribution name may contain only letters, digits, dots, underscores, and hyphens.")
        command = ["wsl.exe", "-d", wsl_distro, "--", *query]
    else:
        command = query
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=15)
    except FileNotFoundError as exc:
        target = "WSL" if runtime == "windows_wsl" else "Linux"
        raise RuntimeError(f"YuE2 needs an NVIDIA CUDA driver visible to {target}; nvidia-smi was not found.") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("YuE2 GPU detection timed out. Check the NVIDIA driver, then try again.") from exc
    if completed.returncode != 0 or not completed.stdout.strip():
        raise RuntimeError(f"YuE2 could not access NVIDIA GPU 0:\n{_last_output(completed)}")

    fields = [item.strip() for item in completed.stdout.splitlines()[0].split(",")]
    if len(fields) != 3:
        raise RuntimeError("YuE2 could not read the NVIDIA GPU name, memory, and compute capability.")
    memory = _GPU_MEMORY.search(fields[1])
    capability = _COMPUTE_CAPABILITY.search(fields[2])
    if memory is None or capability is None:
        raise RuntimeError("YuE2 could not confirm GPU VRAM or BF16-capable compute capability.")
    return fields[0], int(memory.group(1)), float(capability.group(0))


def _gpu_status(name: str, memory_mib: int, capability: float) -> str:
    memory_gib = memory_mib / 1024
    if capability < 8.0:
        raise RuntimeError(
            f"YuE2 cannot run on {name} (compute capability {capability:g}). "
            "The official runtime needs an NVIDIA GPU with BF16 support (compute capability 8.0 or newer)."
        )
    if memory_mib < _EXPERIMENTAL_MIN_VRAM_MIB:
        raise RuntimeError(
            f"YuE2 cannot run reliably on {name} ({memory_gib:.1f} GiB VRAM). "
            "This bridge blocks cards below 16 GiB; the upstream recommendation is 24 GiB."
        )
    if memory_mib < _SUPPORTED_MIN_VRAM_MIB:
        return (
            f"EXPERIMENTAL — {name}, {memory_gib:.1f} GiB VRAM, compute capability {capability:g}. "
            "The GPU is BF16-capable but below YuE2's official 24 GiB recommendation; a render can run out of memory."
        )
    return f"SUPPORTED — {name}, {memory_gib:.1f} GiB VRAM, compute capability {capability:g}."


def _preflight_gpu(runtime: str, wsl_distro: str) -> str:
    return _gpu_status(*_gpu_details(runtime, wsl_distro))


def _run_runtime(runtime: str, wsl_distro: str, runner_path: str, request_path: Path, job_dir: Path, timeout_minutes: int):
    if runtime == "windows_wsl":
        command = " ".join([
            "exec",
            _wsl_runner_expression(runner_path),
            "--request",
            shlex.quote(_to_wsl_path(request_path)),
            "--output",
            shlex.quote(_to_wsl_path(job_dir)),
        ])
        args = ["wsl.exe", "-d", wsl_distro, "--", "sh", "-lc", command]
    else:
        runner = Path(runner_path).expanduser()
        if not runner.is_file():
            raise RuntimeError(f"YuE2 runner not found: {runner}. Run installers/install_linux.sh first.")
        args = [str(runner), "--request", str(request_path), "--output", str(job_dir)]
    try:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=int(timeout_minutes) * 60,
            check=False,
        )
    except FileNotFoundError as exc:
        if runtime == "windows_wsl":
            raise RuntimeError("WSL is not installed or wsl.exe is unavailable. Run installers/install_windows.ps1.") from exc
        raise RuntimeError("YuE2's local Linux runner could not start. Run installers/install_linux.sh first.") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"YuE2 exceeded the {timeout_minutes}-minute limit. Increase the node timeout after confirming GPU activity.") from exc


class AntimeterYuE2Generate:
    """Run the official YuE2 pipeline from Windows WSL or native Linux."""

    CATEGORY = "audio/YuE2"
    RETURN_TYPES = ("AUDIO", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("audio", "score_path", "artifacts_path", "gpu_status")
    FUNCTION = "generate"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "style": ("STRING", {
                    "multiline": True,
                    "default": "English alt-pop, intimate female vocal, warm analogue synths, clean electric guitar, punchy drums, wide modern mix",
                }),
                "lyrics": ("STRING", {
                    "multiline": True,
                    "default": "[Verse]\nCity lights are turning blue\nI keep a little fire for you\n\n[Chorus]\nWe are brighter than the rain\nRunning wild through neon lanes",
                }),
                "cot": (["full", "melody", "off"], {"default": "full"}),
                "seed": ("INT", {"default": 42, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "control_after_generate": True}),
                "decoder": (["m-a-p/YuE2-Vae", "m-a-p/YuE2-Vae-legacy"], {"default": "m-a-p/YuE2-Vae"}),
                "wsl_distro": ("STRING", {"default": "Ubuntu"}),
                "runner_path": ("STRING", {"default": "~/yue2-comfy/run_yue2_comfy"}),
                "timeout_minutes": ("INT", {"default": 20, "min": 1, "max": 120}),
                "output_folder": ("STRING", {"default": "YuE2"}),
                "runtime": (["auto", "windows_wsl", "local_linux"], {"default": "auto"}),
            },
        }

    def generate(
        self,
        style: str,
        lyrics: str,
        cot: str,
        seed: int,
        decoder: str,
        wsl_distro: str,
        runner_path: str,
        timeout_minutes: int,
        output_folder: str,
        runtime: str = "auto",
    ):
        if not style.strip():
            raise ValueError("YuE2 needs a style prompt.")
        if not lyrics.strip():
            raise ValueError("YuE2 needs lyrics. Use [Instrumental] for an instrumental request.")
        selected_runtime = _select_runtime(runtime)
        gpu_status = _preflight_gpu(selected_runtime, wsl_distro)
        print(f"YuE2 GPU preflight: {gpu_status}")

        job_dir = Path(folder_paths.get_output_directory()) / "audio" / _safe_output_folder(output_folder) / uuid4().hex
        job_dir.mkdir(parents=True, exist_ok=False)
        request_path = job_dir / "request.json"
        request_path.write_text(json.dumps({
            "style": style,
            "lyrics": lyrics,
            "cot": cot,
            "seed": int(seed),
            "vae": decoder,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        completed = _run_runtime(selected_runtime, wsl_distro, runner_path, request_path, job_dir, timeout_minutes)

        if completed.returncode != 0:
            raise RuntimeError(f"YuE2 job failed (exit {completed.returncode}):\n{_last_output(completed)}")

        result_path = job_dir / "result.json"
        if not result_path.is_file():
            raise RuntimeError("YuE2 completed without result.json. Check the WSL command and runner installation.")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        audio_path = _job_file(job_dir, str(result.get("audio_file", "")))
        if not audio_path.is_file():
            raise RuntimeError("YuE2 completed without the expected FLAC output.")

        waveform, sample_rate = load_audio(str(audio_path))
        audio = {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}
        score_path = _job_file(job_dir, str(result.get("score_file", "")))
        return (audio, str(score_path) if score_path.is_file() else "", str(job_dir), gpu_status)


class AntimeterYuE2GPUCheck:
    """Show the YuE2 hardware tier without starting a music render."""

    CATEGORY = "audio/YuE2"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("gpu_status", "vram_mib")
    FUNCTION = "check"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "runtime": (["auto", "windows_wsl", "local_linux"], {"default": "auto"}),
                "wsl_distro": ("STRING", {"default": "Ubuntu"}),
            },
        }

    def check(self, runtime: str, wsl_distro: str):
        selected_runtime = _select_runtime(runtime)
        name, memory_mib, capability = _gpu_details(selected_runtime, wsl_distro)
        return (_gpu_status(name, memory_mib, capability), memory_mib)


NODE_CLASS_MAPPINGS = {
    "AntimeterYuE2Generate": AntimeterYuE2Generate,
    "AntimeterYuE2GPUCheck": AntimeterYuE2GPUCheck,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AntimeterYuE2Generate": "Antimeter YuE2 Generate",
    "AntimeterYuE2GPUCheck": "Antimeter YuE2 GPU Check",
}
