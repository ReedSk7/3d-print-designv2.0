# Project-only dependency setup. Run from any directory; activation is unnecessary.
# Example: .\scripts\setup.ps1 -PythonVersion 3.13
# Or: .\scripts\setup.ps1 -PythonExecutable 'C:\Tools\Python312\python.exe'
[CmdletBinding()]
param(
    [ValidateSet('3.12', '3.13')]
    [string]$PythonVersion = '3.12',
    [string]$PythonExecutable = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $RepoRoot '.venv'
$VenvPython = Join-Path $VenvPath 'Scripts\python.exe'
$LockPath = Join-Path $RepoRoot 'requirements-lock.txt'

function Invoke-CheckedNative {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed (exit $LASTEXITCODE): $Program $($Arguments -join ' ')"
    }
}

if (-not (Test-Path -LiteralPath $LockPath -PathType Leaf)) {
    throw "Missing dependency lock: $LockPath"
}

if (Test-Path -LiteralPath $VenvPath) {
    if (-not (Test-Path -LiteralPath (Join-Path $VenvPath 'pyvenv.cfg') -PathType Leaf) -or
        -not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
        throw 'Existing .venv is not a usable Windows virtual environment. Preserve it and select a new checkout or move it aside manually; setup will not overwrite it.'
    }
} else {
    $LauncherArgs = @()
    if ($PythonExecutable) {
        $Launcher = (Get-Command -Name $PythonExecutable -CommandType Application -ErrorAction Stop).Source
    } else {
        $Launcher = (Get-Command -Name 'py' -CommandType Application -ErrorAction Stop).Source
        $LauncherArgs = @("-$PythonVersion")
    }
    $VersionProbe = 'import sys; print(sys.executable); print(sys.version); sys.exit(0 if sys.version_info[:2] in ((3,12),(3,13)) else 1)'
    Invoke-CheckedNative -Program $Launcher -Arguments ($LauncherArgs + @('-c', $VersionProbe))
    Invoke-CheckedNative -Program $Launcher -Arguments ($LauncherArgs + @('-m', 'venv', $VenvPath))
}

# A folder named .venv is not sufficient: reject a global/misdirected interpreter.
$IsolationProbe = 'import pathlib,sys; expected=pathlib.Path(sys.argv[1]).resolve(); valid=sys.prefix!=sys.base_prefix and pathlib.Path(sys.prefix).resolve()==expected and sys.version_info[:2] in ((3,12),(3,13)); print("Project interpreter:",sys.executable); sys.exit(0 if valid else 1)'
Invoke-CheckedNative -Program $VenvPython -Arguments @('-c', $IsolationProbe, $VenvPath)
Invoke-CheckedNative -Program $VenvPython -Arguments @('-m', 'pip', '--isolated', '--require-virtualenv', 'install', '--prefix', $VenvPath, '-r', $LockPath)
Invoke-CheckedNative -Program $VenvPython -Arguments @('-m', 'pip', 'check')
Write-Host 'Project dependencies installed. OpenSCAD, Bambu Studio and Codex are separate installations; no printer settings were changed.'
Invoke-CheckedNative -Program $VenvPython -Arguments @((Join-Path $PSScriptRoot 'check_environment.py'))
