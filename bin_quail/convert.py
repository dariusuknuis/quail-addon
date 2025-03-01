import bpy
import sys
import os
import stat
import subprocess

def convert(src, dst):
    suffix = ""
    cmd = bpy.utils.user_resource('SCRIPTS') + "/addons/quail-addon/quail"
    if sys.platform == "win32":
        suffix = ".exe"
    if sys.platform == "linux":
        suffix = "-linux"
    if sys.platform == "darwin":
        suffix = "-darwin"

    cmd += suffix

    mode = os.stat(cmd).st_mode
    if mode != 33261:
        os.chmod(cmd, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print("quail%s convert %s %s" % (suffix, src, dst))

    args = [cmd, "convert", src, dst]
    process = subprocess.run(
        args, capture_output=True, text=True)
    print(process.stdout)
    if process.returncode == 0:
        return ""
    lines = process.stdout.splitlines()
    if len(lines) > 0:
        return lines[-1]
    return process.stdout