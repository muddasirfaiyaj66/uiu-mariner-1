# 📑 UIU MARINER - Documentation Index

Welcome to the UIU MARINER ROV Control System documentation!

---

## 🚀 Quick Start

**New users start here:**

1. **[WINDOWS_GUIDE.md](WINDOWS_GUIDE.md)** - Complete Windows installation walkthrough

   - Step-by-step setup
   - First-time usage
   - Screenshots and commands

2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Field operations cheat sheet
   - Control layout
   - Connection strings
   - Emergency procedures
   - Pre-flight checklist

---

## 📚 Complete Documentation

### Setup & Installation

- **[README.md](README.md)** - Main documentation

  - System overview
  - Architecture diagram
  - Installation (all platforms)
  - Configuration guide
  - Safety features

- **[requirements.txt](requirements.txt)** - Python dependencies

  - pymavlink, pygame, PyQt6, pyserial

- **[config.json](config.json)** - Connection settings
  - MAVLink connection string
  - Joystick configuration
  - Update rates

### Technical Documentation

- **[ARCHITECTURE.txt](ARCHITECTURE.txt)** - System design diagrams

  - Component architecture
  - Data flow
  - Control loop timing
  - Safety chain

- **[SUMMARY.md](SUMMARY.md)** - Build summary
  - What was built
  - File structure
  - Quality checklist
  - Performance specs

### User Guides

- **[WINDOWS_GUIDE.md](WINDOWS_GUIDE.md)** - Windows-specific guide

  - Installation steps
  - Troubleshooting
  - Daily operations
  - Advanced config

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference card

  - Joystick controls
  - Connection examples
  - Startup sequence
  - Emergency procedures

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem solving
  - Common errors
  - Diagnostic steps
  - Debug mode
  - System diagnostics

### Code Structure

```
src/
├── connections/
│   └── mavlinkConnection.py    # MAVLink communication with Pixhawk
├── controllers/
│   └── joystickController.py   # Joystick input processing
└── ui/
    └── rovControlApp.py        # Main PyQt6 GUI application
```

**[test_system.py](test_system.py)** - Offline testing suite

---

## 🎯 Documentation by Task

### I want to...

**...install the software**
→ Start with [WINDOWS_GUIDE.md](WINDOWS_GUIDE.md) Section 1-9

**...understand how it works**
→ Read [ARCHITECTURE.txt](ARCHITECTURE.txt) and [SUMMARY.md](SUMMARY.md)

**...connect to my Pixhawk**
→ See [README.md](README.md) "Configuration" + [config.json](config.json)

**...learn the controls**
→ Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) "Joystick Controls"

**...fix a problem**
→ Open [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**...run a test without hardware**
→ Execute `python test_system.py`

**...modify the code**
→ Read [ARCHITECTURE.txt](ARCHITECTURE.txt) then explore `src/`

**...prepare for operations**
→ Follow [QUICK_REFERENCE.md](QUICK_REFERENCE.md) "Pre-Flight Checklist"

---

## 📁 File Reference

### Configuration Files

| File          | Purpose                               |
| ------------- | ------------------------------------- |
| `config.json` | MAVLink connection, joystick settings |
| `.gitignore`  | Git ignore patterns                   |

### Launcher Scripts

| File         | Purpose                     |
| ------------ | --------------------------- |
| `launch.ps1` | Windows PowerShell launcher |
| `launch.sh`  | Linux/macOS bash launcher   |

### Documentation Files

| File                 | Purpose                         |
| -------------------- | ------------------------------- |
| `README.md`          | Main documentation (400+ lines) |
| `SUMMARY.md`         | Build summary and specs         |
| `ARCHITECTURE.txt`   | System diagrams (ASCII art)     |
| `QUICK_REFERENCE.md` | Field operations guide          |
| `WINDOWS_GUIDE.md`   | Windows installation guide      |
| `TROUBLESHOOTING.md` | Problem solving guide           |
| `INDEX.md`           | This file                       |

### Source Code

| File                                    | Lines | Purpose                  |
| --------------------------------------- | ----- | ------------------------ |
| `src/connections/mavlinkConnection.py`  | 181   | MAVLink protocol handler |
| `src/controllers/joystickController.py` | 271   | Joystick input processor |
| `src/ui/rovControlApp.py`               | 396   | Main GUI application     |
| `test_system.py`                        | 180   | Offline test suite       |

### Dependencies

| File               | Purpose             |
| ------------------ | ------------------- |
| `requirements.txt` | Python package list |

---

## 📊 Documentation Statistics

- **Total Documentation**: 7 files, ~4,000 lines
- **Source Code**: 3 modules, ~850 lines
- **Test Code**: 1 file, 180 lines
- **Configuration**: 2 files (JSON, gitignore)
- **Launchers**: 2 scripts (Windows, Linux)

---

## 🔍 Quick Search

**Keywords:**

- **Joystick**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md), [joystickController.py](src/controllers/joystickController.py)
- **MAVLink**: [mavlinkConnection.py](src/connections/mavlinkConnection.py), [ARCHITECTURE.txt](ARCHITECTURE.txt)
- **Pixhawk**: [README.md](README.md), [config.json](config.json)
- **Thrusters**: [ARCHITECTURE.txt](ARCHITECTURE.txt), [joystickController.py](src/controllers/joystickController.py)
- **Installation**: [WINDOWS_GUIDE.md](WINDOWS_GUIDE.md), [README.md](README.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Emergency**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md), [rovControlApp.py](src/ui/rovControlApp.py)
- **Configuration**: [config.json](config.json), [README.md](README.md)
- **Testing**: [test_system.py](test_system.py)
- **Safety**: [README.md](README.md), [ARCHITECTURE.txt](ARCHITECTURE.txt)

---

## 🎓 Learning Path

### Beginner

1. Read [README.md](README.md) overview
2. Follow [WINDOWS_GUIDE.md](WINDOWS_GUIDE.md) installation
3. Print [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. Run `python test_system.py`

### Intermediate

1. Study [ARCHITECTURE.txt](ARCHITECTURE.txt)
2. Read source code comments
3. Modify [config.json](config.json) settings
4. Test different flight modes

### Advanced

1. Read [SUMMARY.md](SUMMARY.md) for design decisions
2. Study `src/` modules in detail
3. Modify thruster mappings
4. Add custom features
5. Integrate sensors/cameras

---

## 📝 Documentation Versions

**Current Version**: 1.0  
**Last Updated**: November 4, 2025  
**Status**: Production Ready

### Changelog

**v1.0 (Nov 2025)**

- Initial release
- Complete ROV control system
- All documentation created
- Tested on Windows 10/11

---

## 🤝 Contributing

To improve documentation:

1. Identify gap or error
2. Edit relevant .md file
3. Test changes
4. Update INDEX.md if adding new file

**Documentation Standards:**

- Use Markdown formatting
- Include code examples
- Add troubleshooting sections
- Keep language clear and concise

---

## 📞 Support Resources

### In This Repository

- 📖 Full docs in 7 files
- 🧪 Test suite (`test_system.py`)
- 🎮 Example config (`config.json`)
- 🚀 Ready-to-run code (`src/`)

### External Resources

- **ArduSub**: https://ardusub.com/
- **MAVLink**: https://mavlink.io/
- **PyQt6**: https://riverbankcomputing.com/
- **Pygame**: https://pygame.org/
- **QGroundControl**: https://qgroundcontrol.com/

---

## ✅ Documentation Checklist

Before first operation, ensure you've read:

- [ ] [README.md](README.md) - System overview
- [ ] [WINDOWS_GUIDE.md](WINDOWS_GUIDE.md) - Installation
- [ ] [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Controls
- [ ] [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [ ] [config.json](config.json) - Your settings are correct
- [ ] Safety sections in all docs

---

## 🎉 Ready to Start?

**Recommended reading order:**

1. **README.md** (15 min) - Overview
2. **WINDOWS_GUIDE.md** (30 min) - Setup
3. **QUICK_REFERENCE.md** (10 min) - Operations
4. **ARCHITECTURE.txt** (20 min) - How it works

**Total time**: ~1 hour to full understanding

Then dive in! 🌊

---

**UIU MARINER Team**  
**November 2025**

_"Documentation is code's best friend."_
