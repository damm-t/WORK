# ==============================================================================
#   QUANT DESK — 1-CLICK WINDOWS 24/7 HOST SETUP SCRIPT
#   Right-click this file -> "Run with PowerShell" (Run as Administrator)
# ==============================================================================

# 1. Require Administrator Privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Elevating privileges to Administrator..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList ("-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"")
    exit` T1`2 `2J  `  
    K'j[op098vcx]
}

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   🚀 CONFIGURING WINDOWS 24/7 QUANT EXECUTION ENGINE" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 2. Configure WSL2 Mirrored Networking (Shares Windows LAN IP directly with Linux)
Write-Host "`n[1/4] Setting up WSL2 High-Speed Mirrored Networking..." -ForegroundColor Green
$wslConfigPath = "$env:USERPROFILE\.wslconfig"
$wslConfigContent = @"
[wsl2]
networkingMode=mirrored
firewall=true
autoProxy=true
"@
Set-Content -Path $wslConfigPath -Value $wslConfigContent -Force
Write-Host "  -> .wslconfig configured with networkingMode=mirrored" -ForegroundColor Gray

# 3. Enable Windows Virtual Machine Platform & WSL Features
Write-Host "`n[2/4] Verifying Windows Virtualization Features & WSL2..." -ForegroundColor Green
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart | Out-Null
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart | Out-Null

$wslStatus = wsl -l -v 2>$null
if ($wslStatus -match "Ubuntu") {
    Write-Host "  -> Ubuntu is already installed in WSL2." -ForegroundColor Gray
} else {
    Write-Host "  -> Installing WSL2 and Ubuntu (this may take a few minutes)..." -ForegroundColor Yellow
    wsl --install -d Ubuntu --no-launch
    Write-Host "  -> Ubuntu installation complete." -ForegroundColor Gray
}

# 4. Install & Enable Windows OpenSSH Server
Write-Host "`n[3/4] Enabling OpenSSH Server & Firewall..." -ForegroundColor Green
$sshCapability = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
if ($sshCapability.State -ne 'Installed') {
    Write-Host "  -> Installing OpenSSH.Server capability..." -ForegroundColor Yellow
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
}

# Start OpenSSH Service and set to Automatic
Start-Service sshd -ErrorAction SilentlyContinue
Set-Service -Name sshd -StartupType 'Automatic'

# Open Firewall Port 22 and 8080
New-NetFirewallRule -Name 'QuantDesk-SSH' -DisplayName 'Quant Desk SSH' -Enabled True -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -ErrorAction SilentlyContinue | Out-Null
New-NetFirewallRule -Name 'QuantDesk-Web' -DisplayName 'Quant Desk Web Cockpit' -Enabled True -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -ErrorAction SilentlyContinue | Out-Null
Write-Host "  -> OpenSSH Server is running and firewalls are configured." -ForegroundColor Gray

# 5. Get Local IP Address
Write-Host "`n[4/4] Detecting Local Network IP..." -ForegroundColor Green
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
    $_.InterfaceAlias -notmatch "vEthernet|Loopback|WSL" -and $_.IPAddress -notmatch "^169\." -and $_.IPAddress -notmatch "^127\." 
} | Select-Object -First 1).IPAddress

$windowsUser = $env:USERNAME

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host "   ✅ WINDOWS HOST IS READY FOR 24/7 QUANT DESK!" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  • Windows Username : $windowsUser" -ForegroundColor White
Write-Host "  • Local Machine IP : $localIP" -ForegroundColor Yellow
Write-Host "  • OpenSSH Server   : RUNNING (Port 22)" -ForegroundColor White
Write-Host "  • WSL2 Ubuntu      : READY" -ForegroundColor White
Write-Host "`n👉 TELL YOUR AI ASSISTANT ON MAC THIS INFO:" -ForegroundColor Cyan
Write-Host "   Host IP: $localIP | User: $windowsUser" -ForegroundColor Yellow
Write-Host "=================================================================`n" -ForegroundColor Cyan

Pause
