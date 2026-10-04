param([string]$PythonPath,[int]$Port=8765,[switch]$NoBrowser)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
if (-not $PythonPath) { $PythonPath=Join-Path $projectRoot '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) { throw 'Select the project Python environment with -PythonPath. No dependencies will be installed automatically.' }
$localDirectory=Join-Path $projectRoot 'owner-validation\local\workshop'
New-Item -ItemType Directory -Path $localDirectory -Force | Out-Null
$serverScript=Join-Path $PSScriptRoot 'serve_workshop.py'
$readinessText=& $PythonPath -B $serverScript --check-only
if ($LASTEXITCODE -ne 0) { Write-Output $readinessText; throw 'Workshop readiness failed. Correct the reported Python/dependency/OpenSCAD/assets issue; nothing was installed.' }
Write-Output 'Python, dependencies, OpenSCAD and local app assets are ready.'
$instanceId=[guid]::NewGuid().ToString('N')
$process=Start-Process -FilePath $PythonPath -ArgumentList @('-B',('"'+$serverScript+'"'),'--port',$Port,'--instance-id',$instanceId) -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $localDirectory 'startup.log') -RedirectStandardError (Join-Path $localDirectory 'startup-error.log')
$ready=$false
for ($attempt=0;$attempt -lt 40;$attempt++) {
    if ($process.HasExited) { throw ('Workshop startup failed. Read '+(Join-Path $localDirectory 'startup-error.log')) }
    try { $session=Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/session"; if ($session.instance_id -eq $instanceId) { $ready=$true; break } } catch { }
    Start-Sleep -Milliseconds 250
}
if (-not $ready) { Stop-Process -Id $process.Id; throw 'Workshop readiness timed out. Check startup logs.' }
Write-Output "Print Workshop: http://127.0.0.1:$Port. Use Stop workshop in the app when finished."
if (-not $NoBrowser) { Start-Process "http://127.0.0.1:$Port" }
