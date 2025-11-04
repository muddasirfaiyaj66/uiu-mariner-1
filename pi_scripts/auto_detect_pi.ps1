# Auto-detect Raspberry Pi IP address on network
# Searches common IP ranges for Pi with SSH open

param(
    [string]$PiUser = "pi",
    [int]$Timeout = 1
)

Write-Host "Searching for Raspberry Pi on network..." -ForegroundColor Cyan

# Get local network info
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -and $_.PrefixOrigin -eq "Dhcp"})[0].IPAddress

if (-not $localIP) {
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"})[0].IPAddress
}

if (-not $localIP) {
    Write-Host "Could not detect local network" -ForegroundColor Red
    exit 1
}

$subnet = $localIP.Substring(0, $localIP.LastIndexOf('.'))
Write-Host "Scanning subnet: $subnet.0/24" -ForegroundColor Yellow

# Common Pi IP addresses to try first
$priorityIPs = @("$subnet.182", "$subnet.100", "$subnet.101", "$subnet.150")

foreach ($ip in $priorityIPs) {
    Write-Host "Trying $ip... " -NoNewline
    $result = Test-NetConnection -ComputerName $ip -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($result) {
        Write-Host "FOUND!" -ForegroundColor Green
        Write-Output $ip
        exit 0
    }
    Write-Host "No" -ForegroundColor Gray
}

# Scan full subnet if not found in priority list
Write-Host "Scanning full subnet (this may take a moment)..." -ForegroundColor Yellow
$jobs = @()

for ($i = 1; $i -le 254; $i++) {
    $ip = "$subnet.$i"
    if ($priorityIPs -notcontains $ip) {
        $jobs += Start-Job -ScriptBlock {
            param($testIP)
            if (Test-NetConnection -ComputerName $testIP -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue) {
                return $testIP
            }
        } -ArgumentList $ip
    }
}

# Wait for jobs with timeout
$foundIP = $null
$maxWait = 10
$waited = 0

while ($waited -lt $maxWait -and -not $foundIP) {
    Start-Sleep -Milliseconds 500
    $waited += 0.5
    
    foreach ($job in $jobs) {
        if ($job.State -eq "Completed") {
            $result = Receive-Job -Job $job
            if ($result) {
                $foundIP = $result
                break
            }
        }
    }
}

# Cleanup jobs
$jobs | Stop-Job | Remove-Job

if ($foundIP) {
    Write-Host "Found Raspberry Pi at: $foundIP" -ForegroundColor Green
    Write-Output $foundIP
    exit 0
} else {
    Write-Host "Raspberry Pi not found on network" -ForegroundColor Red
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "  1. Pi is powered on" -ForegroundColor Gray
    Write-Host "  2. Ethernet cable is connected" -ForegroundColor Gray
    Write-Host "  3. SSH is enabled on Pi" -ForegroundColor Gray
    exit 1
}
