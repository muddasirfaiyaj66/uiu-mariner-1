param(
    [string]$PiHost = "raspberrypi.local",
    [string]$User = "pi",
    [string]$RemotePath = "/home/pi",
    [string]$KeyPath = "",
    [switch]$EnableService
)

Write-Host "Deploying pi_scripts to ${User}@${PiHost}:${RemotePath}"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$piScripts = Join-Path $scriptDir "pi_scripts"

if (-not (Test-Path $piScripts)) {
    Write-Error "pi_scripts directory not found at $piScripts. Run this script from the repository root where pi_scripts/ exists."
    exit 1
}

$archive = Join-Path $scriptDir "pi_scripts.tar.gz"
if (Test-Path $archive) { Remove-Item $archive -Force }

Write-Host "Creating archive $archive ..."
# Use system tar (Windows has bsdtar bundled as tar on recent Windows builds)
$tarCmd = "tar -czf `"$archive`" -C `"$scriptDir`" pi_scripts"
Write-Host "Running: $tarCmd"
$tarResult = & tar -czf "$archive" -C "$scriptDir" "pi_scripts" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "tar failed: $tarResult"
    exit 1
}

# Build scp/ssh options
$scpArgs = @()
$sshArgs = @()
if ($KeyPath -ne "") {
    if (-not (Test-Path $KeyPath)) { Write-Error "Key file not found: $KeyPath"; exit 1 }
    $scpArgs += '-i'
    $scpArgs += $KeyPath
    $sshArgs += '-i'
    $sshArgs += $KeyPath
}

$remoteArchivePath = "$RemotePath/pi_scripts.tar.gz"

Write-Host "Copying archive to ${User}@${PiHost}:${RemotePath} ..."
$scpArgs += "$archive"
$scpArgs += "${User}@${PiHost}:${RemotePath}/"
$scpProcess = Start-Process -FilePath "scp" -ArgumentList $scpArgs -NoNewWindow -Wait -PassThru
if ($scpProcess.ExitCode -ne 0) { 
    Write-Error "scp failed with exit code $($scpProcess.ExitCode)"
    Remove-Item $archive -Force
    exit 1 
}

Write-Host "Extracting archive on remote host and setting permissions..."
$remoteCommands = @(
    "mkdir -p $RemotePath/mariner",
    "tar -xzf $remoteArchivePath -C $RemotePath/mariner",
    "rm -f $remoteArchivePath",
    "find $RemotePath/mariner/pi_scripts -type f \( -name '*.sh' -o -name '*.py' \) -exec chmod +x {} \;",
    "ls -lh $RemotePath/mariner/pi_scripts | head -20"
)

if ($EnableService) {
    $remoteCommands += @(
        "sudo cp $RemotePath/mariner/pi_scripts/mariner_autostart.service /etc/systemd/system/",
        "sudo systemctl daemon-reload",
        "sudo systemctl enable mariner_autostart.service"
    )
}

$joined = $remoteCommands -join " && "
$sshArgs += "${User}@${PiHost}"
$sshArgs += $joined

Write-Host "Running remote commands over SSH..."
$sshProcess = Start-Process -FilePath "ssh" -ArgumentList $sshArgs -NoNewWindow -Wait -PassThru
if ($sshProcess.ExitCode -ne 0) { 
    Write-Error "ssh failed with exit code $($sshProcess.ExitCode)"
    Remove-Item $archive -Force
    exit 1 
}

Write-Host "Cleaning up local archive"
Remove-Item $archive -Force

Write-Host ""
Write-Host "==================================="
Write-Host "Deployment complete!"
Write-Host "==================================="
Write-Host "Files are at: ${RemotePath}/mariner/pi_scripts on ${PiHost}"
if (-not $EnableService) { 
    Write-Host ""
    Write-Host "Note: systemd service not enabled."
    Write-Host "To enable autostart on boot, run with -EnableService flag."
}

exit 0
