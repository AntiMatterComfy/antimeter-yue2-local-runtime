[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z0-9_.-]+$')]
    [string]$Distro = 'auto',
    [switch]$InstallWsl,
    [switch]$PreloadModels
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertTo-PosixSingleQuoted([string]$Value) {
    return "'" + $Value.Replace("'", "'`"'`"'") + "'"
}

function Get-NvidiaProfile {
    $gpuLines = & nvidia-smi.exe -i 0 --query-gpu=name,memory.total,compute_cap --format=csv,noheader,nounits 2>$null
    $nvidiaExit = $LASTEXITCODE
    $line = $gpuLines | Select-Object -First 1
    if ($nvidiaExit -ne 0 -or [string]::IsNullOrWhiteSpace($line)) {
        throw 'INCOMPATIBLE: nvidia-smi could not find NVIDIA GPU 0. YuE2 needs an NVIDIA CUDA GPU.'
    }
    $parts = $line.Split(',').ForEach({ $_.Trim() })
    if ($parts.Count -ne 3) {
        throw 'INCOMPATIBLE: nvidia-smi did not return GPU name, VRAM, and compute capability.'
    }
    $memoryMatch = [regex]::Match($parts[1], '\d+')
    $capabilityMatch = [regex]::Match($parts[2], '\d+(\.\d+)?')
    if (-not $memoryMatch.Success -or -not $capabilityMatch.Success) {
        throw 'INCOMPATIBLE: the NVIDIA driver did not expose VRAM or compute capability.'
    }
    $memoryMiB = [int]$memoryMatch.Value
    $capability = [double]$capabilityMatch.Value
    $memoryGiB = $memoryMiB / 1024
    if ($capability -lt 8.0) {
        throw "INCOMPATIBLE: $($parts[0]) has compute capability $capability. YuE2 requires NVIDIA BF16 support (8.0 or newer)."
    }
    if ($memoryMiB -lt 15000) {
        throw "INCOMPATIBLE: $($parts[0]) has $([math]::Round($memoryGiB, 1)) GiB VRAM. This pack blocks cards below 16 GiB; upstream recommends 24 GiB."
    }
    $tier = if ($memoryMiB -lt 23000) { 'EXPERIMENTAL' } else { 'SUPPORTED' }
    return [pscustomobject]@{
        Name = $parts[0]
        MemoryMiB = $memoryMiB
        MemoryGiB = [math]::Round($memoryGiB, 1)
        ComputeCapability = $capability
        Tier = $tier
    }
}

if (-not $IsWindows) {
    throw 'Run install_linux.sh on Linux.'
}

$gpu = Get-NvidiaProfile
Write-Host "$($gpu.Tier): $($gpu.Name), $($gpu.MemoryGiB) GiB VRAM, compute capability $($gpu.ComputeCapability)."
if ($gpu.Tier -eq 'EXPERIMENTAL') {
    Write-Warning 'This BF16-capable GPU is below YuE2''s official 24 GiB recommendation. Installation can continue, but generation can run out of memory.'
}

$ramGiB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
if ($ramGiB -lt 24) {
    Write-Warning "Only $ramGiB GiB system RAM detected. The upstream recommendation is 24 GiB available host RAM."
}

try {
    $distros = @(& wsl.exe --list --quiet 2>$null | ForEach-Object { $_.Trim([char]0, [char]0xFEFF, ' ') } | Where-Object { $_ })
    $hasWsl = $LASTEXITCODE -eq 0
} catch {
    $hasWsl = $false
    $distros = @()
}

if ($Distro -eq 'auto') {
    $Distro = if ($hasWsl -and $distros.Count -gt 0) { $distros[0] } else { 'Ubuntu' }
    Write-Host "Using WSL distribution '$Distro'."
}

if (-not $hasWsl -or -not ($distros -contains $Distro)) {
    if (-not $InstallWsl) {
        throw "WSL distribution '$Distro' is not ready. Re-run with -InstallWsl, reboot if Windows asks, then run this installer again."
    }
    Write-Host "Installing WSL distribution '$Distro'. A Windows restart or first-run Linux account setup may be required."
    & wsl.exe --install -d $Distro
    if ($LASTEXITCODE -ne 0) {
        throw "WSL installation returned exit code $LASTEXITCODE. Finish WSL setup, then run this installer again."
    }
    Write-Host 'WSL installation was started. Complete any Windows/Ubuntu setup prompts, then run this installer again.'
    exit 0
}

$wslGpu = & wsl.exe -d $Distro -- nvidia-smi -i 0 --query-gpu=name,memory.total,compute_cap --format=csv,noheader,nounits 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($wslGpu | Select-Object -First 1))) {
    throw "WSL '$Distro' cannot access the NVIDIA GPU. Update the Windows NVIDIA driver and WSL, then verify 'wsl -d $Distro -- nvidia-smi'."
}

$nodeRoot = Split-Path -Parent $PSScriptRoot
$wslSourceLines = & wsl.exe -d $Distro -- wslpath -a (Join-Path $nodeRoot 'wsl')
$wslSourceExit = $LASTEXITCODE
$wslSource = ($wslSourceLines | Select-Object -First 1).Trim()
if ($wslSourceExit -ne 0 -or [string]::IsNullOrWhiteSpace($wslSource)) {
    throw 'Could not translate the extracted node folder into a WSL path.'
}

$preloadCommand = if ($PreloadModels) {
    'YUE2_HF_HOME="$HOME/yue2-comfy/hf_cache" "$HOME/yue2-comfy/.venv/bin/python" "$HOME/yue2-comfy/preload_models.py"'
} else {
    ':'
}
$bootstrap = @'
set -eu
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv
mkdir -p "$HOME/yue2-comfy"
cp -a __SOURCE__/. "$HOME/yue2-comfy/"
chmod +x "$HOME/yue2-comfy/install_yue2.sh" "$HOME/yue2-comfy/run_yue2_comfy"
cd "$HOME/yue2-comfy"
./install_yue2.sh
__PRELOAD__
'@
$bootstrap = $bootstrap.Replace('__SOURCE__', (ConvertTo-PosixSingleQuoted $wslSource)).Replace('__PRELOAD__', $preloadCommand)

& wsl.exe -d $Distro -- sh -lc $bootstrap
if ($LASTEXITCODE -ne 0) {
    throw "WSL YuE2 installation failed with exit code $LASTEXITCODE."
}

Write-Host 'YuE2 is installed. Restart ComfyUI, load the workflow, and keep runtime = auto.'
