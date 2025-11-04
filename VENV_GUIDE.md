# Virtual Environment Setup Guide 🐍

## Why Use a Virtual Environment?

Virtual environments keep your Python packages isolated and organized:

✅ **No conflicts** - Dependencies don't interfere with other projects  
✅ **Clean system** - System Python stays untouched  
✅ **Reproducible** - Same versions for everyone  
✅ **Easy cleanup** - Delete `venv` folder to remove everything

---

## Quick Setup (Recommended Method)

### Option 1: PowerShell (Modern Windows)

```powershell
# Run the setup script
.\setup.ps1
```

### Option 2: Command Prompt (Classic Windows)

```cmd
# Run the setup script
setup.bat
```

That's it! The script will:

1. ✅ Check Python version (needs 3.8+)
2. ✅ Create virtual environment
3. ✅ Activate it automatically
4. ✅ Install all dependencies from requirements.txt

---

## Manual Setup (Step-by-Step)

If you prefer to do it manually or the scripts don't work:

### Step 1: Create Virtual Environment

```powershell
# PowerShell
python -m venv venv
```

```cmd
# Command Prompt
python -m venv venv
```

This creates a `venv` folder with isolated Python installation.

### Step 2: Activate Virtual Environment

**PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt:**

```cmd
venv\Scripts\activate.bat
```

**You'll see `(venv)` in your prompt when active:**

```
(venv) PS E:\UIU MARINER\mariner-software-1.0>
```

### Step 3: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:

- PyQt6 (GUI framework)
- pymavlink (MAVLink communication)
- pygame (Joystick support)
- opencv-python (Camera processing)
- numpy (Math operations)
- pyserial (Serial communication)
- python-dotenv (Configuration)

---

## Using Virtual Environment

### Activate (Every Time You Open Terminal)

**PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt:**

```cmd
venv\Scripts\activate.bat
```

### Check if Active

Look for `(venv)` at start of prompt:

```
(venv) PS E:\UIU MARINER\mariner-software-1.0>  ✅ Active
PS E:\UIU MARINER\mariner-software-1.0>         ❌ Not active
```

Or check Python location:

```powershell
Get-Command python | Select-Object Source
```

Should show:

```
E:\UIU MARINER\mariner-software-1.0\venv\Scripts\python.exe
```

### Run Application (When Active)

```powershell
# With virtual environment active
python launch_mariner.py

# OR directly
python src\ui\marinerApp.py
```

### Deactivate

```powershell
deactivate
```

---

## Troubleshooting

### "cannot be loaded because running scripts is disabled"

**PowerShell Error:**

```
.\venv\Scripts\Activate.ps1 : File cannot be loaded because running scripts is disabled on this system.
```

**Solution:**

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\venv\Scripts\Activate.ps1
```

### "Python not found"

**Error:** `python : The term 'python' is not recognized`

**Solution:**

1. Install Python from https://python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart terminal
4. Test: `python --version`

### "venv module not found"

**Error:** `No module named venv`

**Solution:**

```powershell
# Install venv module
python -m pip install virtualenv

# Then create with
python -m virtualenv venv
```

### Virtual environment not activating

**Try Command Prompt instead:**

```cmd
venv\Scripts\activate.bat
```

This always works (no execution policy issues).

### "pip install fails"

**Error:** Various package installation errors

**Solutions:**

```powershell
# 1. Upgrade pip
python -m pip install --upgrade pip

# 2. Install packages one by one
pip install PyQt6
pip install pymavlink
pip install pygame
pip install opencv-python
pip install numpy

# 3. Clear cache and retry
pip cache purge
pip install -r requirements.txt
```

### Virtual environment too large

The `venv` folder will be ~500MB-1GB. This is normal!

To save space:

```powershell
# Delete and recreate when needed
Remove-Item -Recurse -Force venv
python -m venv venv
```

---

## Project Structure with Virtual Environment

```
mariner-software-1.0/
├── venv/                       ← Virtual environment (DON'T commit to git)
│   ├── Scripts/
│   │   ├── activate.bat        ← CMD activation
│   │   ├── Activate.ps1        ← PowerShell activation
│   │   ├── python.exe          ← Isolated Python
│   │   └── pip.exe             ← Isolated pip
│   └── Lib/
│       └── site-packages/      ← All installed packages
│
├── setup.ps1                   ← Setup script (PowerShell)
├── setup.bat                   ← Setup script (CMD)
├── launch_mariner.py           ← Launcher (checks venv)
├── requirements.txt            ← Dependencies list
├── config.json                 ← Your settings
└── src/
    └── ...                     ← Application code
```

---

## Best Practices

### ✅ DO:

- Activate venv before running application
- Keep venv folder in project directory
- Update requirements.txt when adding packages
- Use `pip freeze > requirements.txt` to save current packages

### ❌ DON'T:

- Commit venv folder to git (add to .gitignore)
- Install packages globally when working on project
- Share venv folder between computers (recreate instead)
- Modify files inside venv folder manually

---

## Common Commands Reference

### Virtual Environment Management

```powershell
# Create
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (CMD)
venv\Scripts\activate.bat

# Deactivate
deactivate

# Delete
Remove-Item -Recurse -Force venv
```

### Package Management

```powershell
# Install from requirements.txt
pip install -r requirements.txt

# Install single package
pip install package-name

# Upgrade package
pip install --upgrade package-name

# List installed packages
pip list

# Save current packages
pip freeze > requirements.txt

# Uninstall package
pip uninstall package-name
```

### Checking Status

```powershell
# Check Python location
Get-Command python | Select-Object Source

# Check if venv active
$env:VIRTUAL_ENV

# Python version
python --version

# pip version
pip --version

# List packages
pip list
```

---

## Quick Start Workflow

### First Time Setup:

```powershell
# 1. Run setup script
.\setup.ps1

# 2. Script creates venv, activates, and installs everything
# You'll see (venv) in prompt when done
```

### Every Time After:

```powershell
# 1. Navigate to project
cd "E:\UIU MARINER\mariner-software-1.0"

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Run application
python launch_mariner.py

# 4. When done, deactivate
deactivate
```

---

## Updating Dependencies

### Add New Package:

```powershell
# Activate venv first
.\venv\Scripts\Activate.ps1

# Install new package
pip install new-package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Update All Packages:

```powershell
# List outdated
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update pip itself
python -m pip install --upgrade pip
```

---

## Removing Virtual Environment

### Complete Removal:

```powershell
# 1. Deactivate if active
deactivate

# 2. Delete folder
Remove-Item -Recurse -Force venv

# 3. Recreate fresh
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Integration with Launch Script

The `launch_mariner.py` script now checks for virtual environment:

```powershell
python launch_mariner.py
```

**If venv active:**

```
✅ Running in virtual environment
✅ All dependencies installed
🚀 Starting application...
```

**If venv NOT active:**

```
⚠️  Not running in virtual environment
💡 Virtual environment exists but not activated

Activate it with:
  PowerShell: .\venv\Scripts\Activate.ps1
  CMD:        venv\Scripts\activate.bat
```

---

## .gitignore for Virtual Environment

Add to `.gitignore` (if using git):

```
# Virtual environment
venv/
env/
ENV/
*.pyc
__pycache__/
```

---

## Summary

### Setup Once:

```powershell
.\setup.ps1
```

### Use Every Time:

```powershell
# 1. Activate
.\venv\Scripts\Activate.ps1

# 2. Run
python launch_mariner.py

# 3. Deactivate when done
deactivate
```

**That's it! Virtual environment keeps everything clean and organized! 🎉**

---

_Virtual Environment Guide v1.0_  
_UIU MARINER ROV Control System_
