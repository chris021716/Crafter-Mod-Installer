import os
import json
import shutil
import platform
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog


APP_NAME = "Crafter"

LOADERS = [
    "Fabric",
    "Forge",
    "NeoForge",
    "Quilt"
]

LAUNCHERS = [
    "Minecraft Launcher",
    "Prism Launcher",
    "CurseForge",
    "Modrinth App"
]


def get_crafter_data_folder():
    system = platform.system()

    if system == "Windows":
        base = Path(
            os.environ.get(
                "LOCALAPPDATA",
                Path.home() / "AppData" / "Local"
            )
        )
        return base / "Crafter"

    if system == "Darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "Crafter"
        )

    return (
        Path.home()
        / ".local"
        / "share"
        / "Crafter"
    )


CRAFTER_DATA = get_crafter_data_folder()
CRAFTER_MODS = CRAFTER_DATA / "mods"
CRAFTER_LOGS = CRAFTER_DATA / "logs"
CRAFTER_CONFIG = CRAFTER_DATA / "config"

CRAFTER_MODS.mkdir(parents=True, exist_ok=True)
CRAFTER_LOGS.mkdir(parents=True, exist_ok=True)
CRAFTER_CONFIG.mkdir(parents=True, exist_ok=True)


def open_folder(path):
    path = Path(path)

    try:
        if platform.system() == "Windows":
            os.startfile(path)

        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])

        else:
            subprocess.Popen(["xdg-open", str(path)])

    except Exception as error:
        messagebox.showerror(
            "Crafter",
            f"Could not open folder:\n\n{error}"
        )


def guess_loader(text):
    text = text.lower()

    if "neoforge" in text:
        return "NeoForge"

    if "fabric" in text:
        return "Fabric"

    if "quilt" in text:
        return "Quilt"

    if "forge" in text:
        return "Forge"

    return None


class MinecraftProfile:
    def __init__(
        self,
        launcher,
        name,
        game_directory,
        loader=None
    ):
        self.launcher = launcher
        self.name = name
        self.game_directory = Path(game_directory)
        self.loader = loader

    @property
    def mods_folder(self):
        return self.game_directory / "mods"

    def display_name(self):
        if self.loader:
            return f"{self.name} [{self.loader}]"

        return self.name


def minecraft_folder():
    home = Path.home()

    if platform.system() == "Windows":
        appdata = Path(
            os.environ.get(
                "APPDATA",
                home / "AppData" / "Roaming"
            )
        )

        return appdata / ".minecraft"

    if platform.system() == "Darwin":
        return (
            home
            / "Library"
            / "Application Support"
            / "minecraft"
        )

    return home / ".minecraft"


def scan_minecraft_launcher():
    profiles = []

    root = minecraft_folder()

    if not root.exists():
        return profiles

    launcher_profiles = root / "launcher_profiles.json"

    if launcher_profiles.exists():

        try:
            with launcher_profiles.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            profile_data = data.get(
                "profiles",
                {}
            )

            for profile_id, profile in profile_data.items():

                name = profile.get(
                    "name",
                    profile_id
                )

                version = profile.get(
                    "lastVersionId",
                    ""
                )

                game_directory = profile.get(
                    "gameDir",
                    str(root)
                )

                profiles.append(
                    MinecraftProfile(
                        "Minecraft Launcher",
                        name,
                        game_directory,
                        guess_loader(version)
                    )
                )

        except Exception:
            pass

    if not profiles:

        profiles.append(
            MinecraftProfile(
                "Minecraft Launcher",
                "Default Minecraft",
                root,
                None
            )
        )

    return profiles


def prism_locations():
    home = Path.home()

    locations = []

    if platform.system() == "Windows":

        appdata = Path(
            os.environ.get(
                "APPDATA",
                home / "AppData" / "Roaming"
            )
        )

        locations.append(
            appdata / "PrismLauncher"
        )

    elif platform.system() == "Darwin":

        locations.append(
            home
            / "Library"
            / "Application Support"
            / "PrismLauncher"
        )

    else:

        locations.append(
            home
            / ".local"
            / "share"
            / "PrismLauncher"
        )

        locations.append(
            home
            / ".var"
            / "app"
            / "org.prismlauncher.PrismLauncher"
            / "data"
            / "PrismLauncher"
        )

    return locations


def scan_prism_launcher():
    profiles = []

    for root in prism_locations():

        instances = root / "instances"

        if not instances.exists():
            continue

        for instance in instances.iterdir():

            if not instance.is_dir():
                continue

            minecraft_dir = (
                instance
                / ".minecraft"
            )

            if not minecraft_dir.exists():

                minecraft_dir = (
                    instance
                    / "minecraft"
                )

            if not minecraft_dir.exists():
                continue

            combined_text = ""

            config_files = [
                instance / "instance.cfg",
                instance / "mmc-pack.json"
            ]

            for config in config_files:

                if config.exists():

                    try:
                        combined_text += (
                            config.read_text(
                                encoding="utf-8",
                                errors="ignore"
                            )
                        )

                    except Exception:
                        pass

            profiles.append(
                MinecraftProfile(
                    "Prism Launcher",
                    instance.name,
                    minecraft_dir,
                    guess_loader(
                        combined_text
                    )
                )
            )

    return profiles


def curseforge_locations():
    home = Path.home()

    locations = []

    if platform.system() == "Windows":

        locations.extend([
            home
            / "curseforge"
            / "minecraft"
            / "Instances",

            home
            / "Documents"
            / "Curse"
            / "Minecraft"
            / "Instances",

            Path(
                os.environ.get(
                    "APPDATA",
                    home / "AppData" / "Roaming"
                )
            )
            / "CurseForge"
            / "minecraft"
            / "Instances"
        ])

    elif platform.system() == "Darwin":

        locations.extend([
            home
            / "Documents"
            / "Curse"
            / "Minecraft"
            / "Instances",

            home
            / "Library"
            / "Application Support"
            / "CurseForge"
            / "minecraft"
            / "Instances"
        ])

    else:

        locations.extend([
            home
            / "curseforge"
            / "minecraft"
            / "Instances",

            home
            / ".local"
            / "share"
            / "CurseForge"
            / "minecraft"
            / "Instances"
        ])

    return locations


def scan_curseforge():
    profiles = []

    for root in curseforge_locations():

        if not root.exists():
            continue

        for instance in root.iterdir():

            if not instance.is_dir():
                continue

            combined_text = instance.name

            manifest = (
                instance
                / "manifest.json"
            )

            if manifest.exists():

                try:
                    combined_text += (
                        manifest.read_text(
                            encoding="utf-8",
                            errors="ignore"
                        )
                    )

                except Exception:
                    pass

            profiles.append(
                MinecraftProfile(
                    "CurseForge",
                    instance.name,
                    instance,
                    guess_loader(
                        combined_text
                    )
                )
            )

    return profiles


def modrinth_locations():
    home = Path.home()

    locations = []

    if platform.system() == "Windows":

        appdata = Path(
            os.environ.get(
                "APPDATA",
                home / "AppData" / "Roaming"
            )
        )

        locations.extend([
            appdata
            / "com.modrinth.theseus"
            / "profiles",

            appdata
            / "ModrinthApp"
            / "profiles"
        ])

    elif platform.system() == "Darwin":

        locations.extend([
            home
            / "Library"
            / "Application Support"
            / "com.modrinth.theseus"
            / "profiles",

            home
            / "Library"
            / "Application Support"
            / "ModrinthApp"
            / "profiles"
        ])

    else:

        locations.extend([
            home
            / ".local"
            / "share"
            / "com.modrinth.theseus"
            / "profiles",

            home
            / ".var"
            / "app"
            / "com.modrinth.ModrinthApp"
            / "data"
            / "com.modrinth.theseus"
            / "profiles"
        ])

    return locations


def scan_modrinth():
    profiles = []

    for root in modrinth_locations():

        if not root.exists():
            continue

        for instance in root.iterdir():

            if not instance.is_dir():
                continue

            combined_text = instance.name

            metadata_files = [
                instance / "profile.json",
                instance / "profile.toml",
                instance / "instance.json"
            ]

            for metadata in metadata_files:

                if metadata.exists():

                    try:
                        combined_text += (
                            metadata.read_text(
                                encoding="utf-8",
                                errors="ignore"
                            )
                        )

                    except Exception:
                        pass

            profiles.append(
                MinecraftProfile(
                    "Modrinth App",
                    instance.name,
                    instance,
                    guess_loader(
                        combined_text
                    )
                )
            )

    return profiles


def scan_launcher(launcher):

    if launcher == "Minecraft Launcher":
        return scan_minecraft_launcher()

    if launcher == "Prism Launcher":
        return scan_prism_launcher()

    if launcher == "CurseForge":
        return scan_curseforge()

    if launcher == "Modrinth App":
        return scan_modrinth()

    return []


class Crafter(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(
            "Crafter"
        )

        self.geometry(
            "850x680"
        )

        self.minsize(
            760,
            580
        )

        self.loader = tk.StringVar(
            value="Fabric"
        )

        self.launcher = tk.StringVar(
            value="Minecraft Launcher"
        )

        self.profile = tk.StringVar()

        self.profiles = []
        self.filtered_profiles = []
        self.mod_files = []

        self.create_interface()

        self.refresh_mods()

        self.scan_profiles()


    def create_interface(self):

        container = ttk.Frame(
            self,
            padding=20
        )

        container.pack(
            fill="both",
            expand=True
        )

        title = ttk.Label(
            container,
            text="CRAFTER",
            font=(
                "Segoe UI",
                24,
                "bold"
            )
        )

        title.pack(
            anchor="w"
        )

        subtitle = ttk.Label(
            container,
            text=(
                "Minecraft Mod Installer"
            )
        )

        subtitle.pack(
            anchor="w",
            pady=(0, 20)
        )

        target = ttk.LabelFrame(
            container,
            text="Install Target",
            padding=15
        )

        target.pack(
            fill="x"
        )

        ttk.Label(
            target,
            text="1. Mod Loader"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        loader_box = ttk.Combobox(
            target,
            textvariable=self.loader,
            values=LOADERS,
            state="readonly"
        )

        loader_box.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(0, 10),
            pady=(5, 15)
        )

        loader_box.bind(
            "<<ComboboxSelected>>",
            lambda event:
            self.filter_profiles()
        )

        ttk.Label(
            target,
            text="2. Launcher"
        ).grid(
            row=0,
            column=1,
            sticky="w"
        )

        launcher_box = ttk.Combobox(
            target,
            textvariable=self.launcher,
            values=LAUNCHERS,
            state="readonly"
        )

        launcher_box.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=(5, 15)
        )

        launcher_box.bind(
            "<<ComboboxSelected>>",
            lambda event:
            self.scan_profiles()
        )

        ttk.Button(
            target,
            text="Scan",
            command=self.scan_profiles
        ).grid(
            row=1,
            column=2,
            pady=(5, 15)
        )

        ttk.Label(
            target,
            text="3. Instance / Profile"
        ).grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="w"
        )

        self.profile_box = ttk.Combobox(
            target,
            textvariable=self.profile,
            state="readonly"
        )

        self.profile_box.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(5, 0)
        )

        target.columnconfigure(
            0,
            weight=1
        )

        target.columnconfigure(
            1,
            weight=1
        )

        mod_frame = ttk.LabelFrame(
            container,
            text="Crafter Mods",
            padding=15
        )

        mod_frame.pack(
            fill="both",
            expand=True,
            pady=15
        )

        button_row = ttk.Frame(
            mod_frame
        )

        button_row.pack(
            fill="x"
        )

        self.folder_label = ttk.Label(
            button_row,
            text=str(
                CRAFTER_MODS
            )
        )

        self.folder_label.pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Button(
            button_row,
            text="Open Mods Folder",
            command=lambda:
            open_folder(CRAFTER_MODS)
        ).pack(
            side="right",
            padx=(10, 0)
        )

        ttk.Button(
            button_row,
            text="Refresh",
            command=self.refresh_mods
        ).pack(
            side="right"
        )

        self.mod_list = tk.Listbox(
            mod_frame,
            height=12
        )

        self.mod_list.pack(
            fill="both",
            expand=True,
            pady=(10, 0)
        )

        bottom = ttk.Frame(
            container
        )

        bottom.pack(
            fill="x"
        )

        ttk.Button(
            bottom,
            text="Add Mod Files",
            command=self.add_mods
        ).pack(
            side="left"
        )

        ttk.Button(
            bottom,
            text="Open Crafter Data",
            command=lambda:
            open_folder(CRAFTER_DATA)
        ).pack(
            side="left",
            padx=(10, 0)
        )

        ttk.Button(
            bottom,
            text="Install Mods",
            command=self.install_mods
        ).pack(
            side="right"
        )


    def refresh_mods(self):

        self.mod_files = sorted(
            CRAFTER_MODS.glob(
                "*.jar"
            )
        )

        if not hasattr(
            self,
            "mod_list"
        ):
            return

        self.mod_list.delete(
            0,
            tk.END
        )

        if not self.mod_files:

            self.mod_list.insert(
                tk.END,
                "No mods found."
            )

            return

        for mod in self.mod_files:

            self.mod_list.insert(
                tk.END,
                mod.name
            )


    def add_mods(self):

        files = filedialog.askopenfilenames(
            title="Select Minecraft Mods",
            filetypes=[
                (
                    "Minecraft Mods",
                    "*.jar"
                )
            ]
        )

        for file in files:

            source = Path(file)

            destination = (
                CRAFTER_MODS
                / source.name
            )

            try:

                shutil.copy2(
                    source,
                    destination
                )

            except Exception as error:

                messagebox.showerror(
                    "Crafter",
                    (
                        f"Could not add:\n"
                        f"{source.name}\n\n"
                        f"{error}"
                    )
                )

        self.refresh_mods()


    def scan_profiles(self):

        launcher = (
            self.launcher.get()
        )

        self.profiles = (
            scan_launcher(
                launcher
            )
        )

        self.filter_profiles()


    def filter_profiles(self):

        selected_loader = (
            self.loader.get()
        )

        compatible = []

        for profile in self.profiles:

            if not profile.loader:

                compatible.append(
                    profile
                )

            elif (
                profile.loader.lower()
                ==
                selected_loader.lower()
            ):

                compatible.append(
                    profile
                )

        if compatible:

            self.filtered_profiles = (
                compatible
            )

        else:

            self.filtered_profiles = (
                self.profiles
            )

        names = [
            profile.display_name()
            for profile
            in self.filtered_profiles
        ]

        self.profile_box[
            "values"
        ] = names

        if names:

            self.profile.set(
                names[0]
            )

        else:

            self.profile.set(
                ""
            )


    def get_selected_profile(self):

        selected = (
            self.profile.get()
        )

        for profile in self.filtered_profiles:

            if (
                profile.display_name()
                ==
                selected
            ):

                return profile

        return None


    def install_mods(self):

        self.refresh_mods()

        if not self.mod_files:

            messagebox.showwarning(
                "Crafter",
                (
                    "There are no mods "
                    "in the Crafter mods folder."
                )
            )

            return

        profile = (
            self.get_selected_profile()
        )

        if not profile:

            messagebox.showwarning(
                "Crafter",
                (
                    "No Minecraft profile "
                    "is selected."
                )
            )

            return

        destination = (
            profile.mods_folder
        )

        confirmation = (
            f"Install {len(self.mod_files)} mod(s)?\n\n"
            f"Launcher:\n"
            f"{profile.launcher}\n\n"
            f"Profile:\n"
            f"{profile.name}\n\n"
            f"Loader:\n"
            f"{self.loader.get()}\n\n"
            f"Destination:\n"
            f"{destination}\n\n"
            f"Crafter will copy the files."
        )

        if not messagebox.askyesno(
            "Crafter",
            confirmation
        ):

            return

        try:

            destination.mkdir(
                parents=True,
                exist_ok=True
            )

            installed = 0

            for mod in self.mod_files:

                target = (
                    destination
                    / mod.name
                )

                shutil.copy2(
                    mod,
                    target
                )

                installed += 1

            messagebox.showinfo(
                "Crafter",
                (
                    f"Installed "
                    f"{installed} mod(s) successfully!\n\n"
                    f"{destination}"
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Crafter",
                (
                    "Installation failed.\n\n"
                    f"{error}"
                )
            )


if __name__ == "__main__":

    app = Crafter()

    app.mainloop()