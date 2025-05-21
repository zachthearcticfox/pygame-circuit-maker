$tempdir = "$env:TEMP\pcm-installer"
$installdir = "$env:APPDATA\pygame-circuit-maker"

mkdir $tempdir -Force
mkdir $installdir -Force

Set-Location $tempdir

try {
    git clone "https://github.com/zachthearcticfox/pygame-circuit-maker"
}
catch {
    Write-Host "git is not installed, installing git."

    $downloadurl = "https://github.com/git-for-windows/git/releases/download/v2.49.0.windows.1/Git-2.49.0-64-bit.exe"
    $gitInstaller = "$tempdir\gitdl.exe"

    Invoke-WebRequest -Uri $downloadurl -OutFile $gitInstaller

    Start-Process -FilePath $gitInstaller -ArgumentList "/VERYSILENT", "/NORESTART", "/SP-" -Wait

    Write-Host "installed git."

    git clone "https://github.com/zachthearcticfox/pygame-circuit-maker"
}

$sourceDir = "$tempdir\pygame-circuit-maker"

if (Test-Path "$sourceDir\pygame-circuit-maker.exe") {
    Move-Item "$sourceDir\pygame-circuit-maker.exe" "$installdir\pygame-circuit-maker.exe"
}

if (Test-Path "$sourceDir\main.save") {
    Move-Item "$sourceDir\main.save" "$installdir\main.save"
}
