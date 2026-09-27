param(
    [Parameter(Mandatory = $true)][string]$Dataset,
    [Parameter(Mandatory = $true)][string]$Configuration,
    [Parameter(Mandatory = $true)][string]$Fold,
    [Parameter(Mandatory = $true)][string]$Trainer,
    [string]$Plans,
    [string]$Device = "cuda",
    [string]$NnUNetTrainExe = "nnUNetv2_train",
    [string]$RunManifestOut,
    [string]$ManifestPython = "python",
    [int]$DeclaredSeed,
    [int]$Seed
)

$ErrorActionPreference = "Stop"

if ($PSBoundParameters.ContainsKey("DeclaredSeed") -and $PSBoundParameters.ContainsKey("Seed")) {
    throw "Use either -DeclaredSeed or the deprecated -Seed alias, not both."
}
if ($PSBoundParameters.ContainsKey("Seed")) {
    Write-Warning "-Seed is deprecated; it records a declared seed only and does not control nnUNet trainer randomness. Use -DeclaredSeed."
    $DeclaredSeed = $Seed
}

foreach ($name in @("nnUNet_raw", "nnUNet_preprocessed", "nnUNet_results")) {
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name))) {
        throw "Required environment variable $name is not set."
    }
}

$env:nnUNet_n_proc_DA = if ($env:nnUNet_n_proc_DA) { $env:nnUNet_n_proc_DA } else { "1" }
$env:OMP_NUM_THREADS = if ($env:OMP_NUM_THREADS) { $env:OMP_NUM_THREADS } else { "1" }
$env:MKL_NUM_THREADS = if ($env:MKL_NUM_THREADS) { $env:MKL_NUM_THREADS } else { "1" }
$env:OPENBLAS_NUM_THREADS = if ($env:OPENBLAS_NUM_THREADS) { $env:OPENBLAS_NUM_THREADS } else { "1" }

$cmd = @($Dataset, $Configuration, $Fold, "-tr", $Trainer, "-device", $Device)
if (-not [string]::IsNullOrWhiteSpace($Plans)) {
    $cmd += @("-p", $Plans)
}

Write-Host "nnUNet_n_proc_DA=$env:nnUNet_n_proc_DA"
Write-Host "OMP_NUM_THREADS=$env:OMP_NUM_THREADS"
Write-Host "MKL_NUM_THREADS=$env:MKL_NUM_THREADS"
Write-Host "OPENBLAS_NUM_THREADS=$env:OPENBLAS_NUM_THREADS"
Write-Host "COMMAND: $NnUNetTrainExe $($cmd -join ' ')"

$trainerLaunchStatus = "STARTED"
try {
    & $NnUNetTrainExe @cmd
    $exitStatus = $LASTEXITCODE
    if ($null -eq $exitStatus) { $exitStatus = 0 }
}
catch {
    $trainerLaunchStatus = "LAUNCH_FAILED"
    $exitStatus = 127
    Write-Error "Trainer launch failed: $($_.Exception.Message)" -ErrorAction Continue
}

if ($RunManifestOut) {
    $manifestScript = Join-Path $PSScriptRoot "create_run_manifest.py"
    $repoRoot = Split-Path $PSScriptRoot -Parent
    $manifestCmd = @($manifestScript, "--repo-root", $repoRoot, "--output", $RunManifestOut, "--exit-status", "$exitStatus", "--notes", "nnUNet training wrapper; trainer_launch_status=$trainerLaunchStatus")
    if ($PSBoundParameters.ContainsKey("DeclaredSeed") -or $PSBoundParameters.ContainsKey("Seed")) {
        $manifestCmd += @("--declared-seed", "$DeclaredSeed", "--seed-verification-status", "UNVERIFIED_DECLARATION_ONLY")
    }
    $manifestCmd += @("--", $NnUNetTrainExe) + $cmd
    Write-Host "RUN_MANIFEST_COMMAND: $ManifestPython $($manifestCmd -join ' ')"
    try {
        & $ManifestPython @manifestCmd
        $manifestExitStatus = $LASTEXITCODE
        if ($null -eq $manifestExitStatus) { $manifestExitStatus = 0 }
    }
    catch {
        $manifestExitStatus = 70
        Write-Error "Run manifest launch failed: $($_.Exception.Message)" -ErrorAction Continue
    }
    if ($manifestExitStatus -ne 0 -and $exitStatus -eq 0) {
        exit 70
    }
}

exit $exitStatus
