# Crafter Source Code

This archive contains the source code for **Crafter**, a Minecraft mod installer developed by **Chris Inc**.

Crafter is written in **Python** and can be packaged into a standalone application using **PyInstaller**. Windows installer builds use **Inno Setup**.

## Supported Launchers

* Minecraft Launcher
* Prism Launcher
* CurseForge
* Modrinth App

## Supported Mod Loaders

* Fabric
* Forge
* NeoForge
* Quilt

## Source Files

### `crafter.py`

The main Python source code for Crafter.

It contains the graphical interface, launcher/profile scanning, Crafter data-folder management, and mod installation functionality.

### `CrafterInstaller.iss`

The Inno Setup script used to create the Windows `CrafterSetup.exe` installer.

### `LICENSE`

Crafter is released under the MIT License.

## Running From Source

Python is required only when running or developing Crafter from source.

Run:

```powershell
py crafter.py
```

## Building Crafter

Install PyInstaller:

```powershell
py -m pip install pyinstaller
```

Build the standalone Windows executable:

```powershell
py -m PyInstaller --onefile --windowed --name Crafter crafter.py
```

The compiled application will be created at:

```text
dist\Crafter.exe
```

Users running the compiled version do **not** need Python installed.

## Building CrafterSetup.exe

Install **Inno Setup 6** and open:

```text
CrafterInstaller.iss
```

Compile the script using:

```text
Build → Compile
```

This creates the distributable Windows setup application:

```text
CrafterSetup.exe
```

## Crafter Data

On Windows, Crafter stores its application data under:

```text
%LOCALAPPDATA%\Crafter\
```

This includes the mod staging folder:

```text
%LOCALAPPDATA%\Crafter\mods\
```

Mods placed there can be copied by Crafter into the selected Minecraft profile's `mods` directory.

## Platform Support

Crafter is intended for:

* Windows
* macOS
* Linux

PyInstaller builds must be created separately on each operating system.

The current setup installer uses Inno Setup and is specifically for Windows.

## Contributing

Crafter is open source. You may modify, improve, fork, or redistribute the project according to the MIT License.

Bug fixes, launcher compatibility improvements, and new features are welcome.

## License

MIT License

**Copyright (c) 2026 Chris Inc**

See the included `LICENSE` file for the complete license.
