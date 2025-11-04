# 🔐 SSH Key Setup - Remove Password Prompts

## Problem

Every SSH command asks for password, which is annoying for automation.

## Solution: SSH Key Authentication

### Quick Setup (5 minutes)

#### Step 1: Generate SSH Key (if you don't have one)

```powershell
# Check if you already have a key
if (Test-Path "$env:USERPROFILE\.ssh\id_rsa.pub") {
    Write-Host "SSH key already exists!" -ForegroundColor Green
    cat "$env:USERPROFILE\.ssh\id_rsa.pub"
} else {
    Write-Host "Generating new SSH key..." -ForegroundColor Yellow
    ssh-keygen -t rsa -b 4096 -N '""' -f "$env:USERPROFILE\.ssh\id_rsa"
}
```

#### Step 2: Copy Key to Raspberry Pi

```powershell
# Replace with your Pi's IP
$PiIP = "192.168.0.182"

# Copy the key (you'll need to enter password ONE last time)
type "$env:USERPROFILE\.ssh\id_rsa.pub" | ssh pi@$PiIP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

#### Step 3: Test Password-Free Login

```powershell
ssh pi@192.168.0.182 "echo 'Success! No password needed!'"
```

If it works without asking for password, you're done! ✅

---

## Alternative: Use Existing Key

If you have a key from PuTTY or another tool:

### From PuTTY Key

```powershell
# Convert PuTTY key to OpenSSH format
puttygen your_key.ppk -O private-openssh -o "$env:USERPROFILE\.ssh\id_rsa"

# Copy to Pi (enter password once)
type "$env:USERPROFILE\.ssh\id_rsa.pub" | ssh pi@192.168.0.182 "cat >> ~/.ssh/authorized_keys"
```

---

## After Setup

Once SSH keys are configured:

- ✅ No more password prompts
- ✅ Auto-connection works smoothly
- ✅ Faster connection times
- ✅ More secure than passwords

---

## Quick Setup Script

Run this to set up automatically:

```powershell
# Quick SSH Key Setup
$PiIP = "192.168.0.182"
$PiUser = "pi"

Write-Host "Setting up password-free SSH..." -ForegroundColor Cyan

# Generate key if needed
if (-not (Test-Path "$env:USERPROFILE\.ssh\id_rsa")) {
    Write-Host "Generating SSH key..." -ForegroundColor Yellow
    ssh-keygen -t rsa -b 4096 -N '""' -f "$env:USERPROFILE\.ssh\id_rsa"
}

# Copy to Pi
Write-Host "Copying key to Pi (enter password ONE last time)..." -ForegroundColor Yellow
type "$env:USERPROFILE\.ssh\id_rsa.pub" | ssh "$PiUser@$PiIP" "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"

# Test
Write-Host "`nTesting..." -ForegroundColor Cyan
$result = ssh "$PiUser@$PiIP" "echo OK" 2>$null

if ($result -eq "OK") {
    Write-Host "SUCCESS! Password-free SSH is working!" -ForegroundColor Green
} else {
    Write-Host "Something went wrong. Try again or check Pi settings." -ForegroundColor Red
}
```

Save as `setup_ssh_keys.ps1` and run once.

---

## Without SSH Keys (Alternative)

If you can't set up SSH keys, the system still works but will ask for passwords. The auto-connect handles this gracefully.
