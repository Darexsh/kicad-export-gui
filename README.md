* * *

<div align="center">

🧰 KiCad Export Studio
======================

**A focused desktop GUI for rendering KiCad PCB images via `kicad-cli pcb render` with repeatable settings**  
🖼️🧩⚙️

![Projekt-Status](https://img.shields.io/badge/Status-Aktiv-brightgreen) ![License](https://img.shields.io/badge/License-NonCommercial-blue) ![Version](https://img.shields.io/badge/Version-1.0-orange)

</div>

* * *

✨ Authors
---------

| Name | GitHub | Role | Contact | Contributions |
| --- | --- | --- | --- | --- |
| **[Darexsh by Daniel Sichler](https://github.com/Darexsh)** | [Link](https://github.com/Darexsh?tab=repositories) | GUI + KiCad Render Workflow | 📧 [E-Mail](mailto:sichler.daniel@gmail.com) | UI Layout, Render Automation, Preset Wiring |


* * *

🚀 About the Project
--------------------

A lightweight GUI for **KiCad 9+** that helps export consistent board renders without retyping long CLI commands. Select a `.kicad_pcb`, choose resolution and render options, and output top/bottom images quickly.

* * *

⚡ Quick Install
---------------

1. Clone or [download this repo](#).
    
2. Install **KiCad 9+** so `kicad-cli` is available.
    
3. Run the app:
    
```bash
python kicad_export_gui.py
```

* * *

📥 Detailed Installation
------------------------

1. **Install prerequisites**
    
    * Python 3.x
        
    * KiCad 9+ (for `kicad-cli`)
        
2. **Configure KiCad command path (Windows)**
    
    * Update `KICAD_CMD_DEFAULT` in `ui_constants.py` if your KiCad install path differs
        
3. **Launch the app**
    
    * Run `python kicad_export_gui.py`
        
    * Select a `.kicad_pcb` board file and output folder
        
    * Click **Render Image**
        

* * *

⚙️ Features
-----------

* **Resolution presets:** 720p, 1080p, 2k, 4k, with editable width/height
    
* **Render sides:** top, bottom, left, right, front, back, or top + bottom
    
* **Backgrounds:** default, transparent, opaque
    
* **Quality presets:** basic, high, user
    
* **Advanced controls:**
    
    * Floor and perspective toggles
        
    * Presets: follow PCB editor / plot settings / legacy
        
    * Zoom, pan, pivot, and rotate inputs
        
    * Lighting controls (top, bottom, side, camera, side elevation)
        
* **Progress + log output** during rendering

* * *

📝 Notes
--------

* On Windows, the app uses `cmd.exe` to run `kicad-cli` via the `kicad-cmd.bat` path
    
* Output files are named by side, e.g. `top.png` and `bottom.png`
    
* Works best on the latest KiCad 9+ builds

* **Commercial use is not permitted**. You may use, modify, and distribute this project only for non-commercial purposes.
    

* * *

📜 License
----------

This project is licensed under the **Non-Commercial Software License (MIT-style) v1.0** and was developed as an educational project. You are free to use, modify, and distribute the code for **non-commercial purposes only**, and must credit the author:

**Copyright (c) 2025 Darexsh by Daniel Sichler**

Please include the following notice with any use or distribution:

> Developed by Daniel Sichler aka Darexsh. Licensed under the Non-Commercial Software License (MIT-style) v1.0. See `LICENSE` for details.

The full license is available in the [LICENSE](LICENSE) file.

* * *

<div align="center"> <sub>Created with ❤️ by Daniel Sichler</sub> </div>
