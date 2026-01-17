import bpy
import sys
import os
import stat
import subprocess


def _addon_root_dir() -> str:
    # .../quail_addon/bin_quail/convert.py -> .../quail_addon
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _quail_exe_path() -> str:
    suffix = ""
    if sys.platform == "win32":
        suffix = ".exe"
    elif sys.platform.startswith("linux"):
        suffix = "-linux"
    elif sys.platform == "darwin":
        suffix = "-darwin"

    # your packaged files are: quail.exe, quail-linux, quail-darwin at addon root
    base = os.path.join(_addon_root_dir(), "quail")
    return base + suffix


def convert(src, dst):
    cmd = _quail_exe_path()

    if not os.path.exists(cmd):
        # Helpful error that tells you exactly where it looked
        raise FileNotFoundError(
            f"quail binary not found: {cmd}\n"
            f"addon root: {_addon_root_dir()}\n"
            f"platform: {sys.platform}"
        )

    # Ensure executable bit (mostly relevant for linux/mac; harmless on windows)
    mode = os.stat(cmd).st_mode
    if (mode & stat.S_IXUSR) == 0:
        os.chmod(cmd, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"{os.path.basename(cmd)} convert {src} {dst}")

    args = [cmd, "convert", src, dst]
    process = subprocess.run(args, capture_output=True, text=True)

    print(process.stdout)
    if process.returncode == 0:
        return ""

    # prefer stderr if present
    if process.stderr:
        return process.stderr.strip()

    lines = process.stdout.splitlines()
    if lines:
        return lines[-1]
    return process.stdout