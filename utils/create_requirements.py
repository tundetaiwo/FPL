""" Script to create requirements for both windows and unix based systems"""
# %%
import io
import os
import platform
import sys
from subprocess import PIPE, Popen
from typing import List


def create_requirements(folder: str, write_names: List[str] = None) -> None:
    """
    Function to write requirements file for both windows and unix based system

    Parameters
    ----------
    `str` folder: locationn of directory to write requirements files
    `List[str]` write_names: TODO

    Returns
    -------
    `None`

    """
    if not os.path.isdir(folder):
        raise ValueError(f"folder argument: '{folder}' is not a directory.")

    if write_names is None:
        write_names = ["win", "unix"]
    os_type = platform.system().lower()
    if os_type in ["linux", "darwin"]:
        message = "python3 -m pip freeze"
    elif os_type == "windows":
        message = "python -m pip freeze"
    else:
        raise ValueError("Only Windows, Mac and Linux based systems are supported.")

    process = Popen(message, stdout=PIPE, stderr=PIPE, shell=True)
    out, _ = (output.decode("utf-8") for output in process.communicate())

    package_list = out.split("\n")
    if os_type == "windows":
        requirements_file_win = "\n".join(package_list)
        pywin_pos = package_list.index("pywin32==304")
        package_list.pop(pywin_pos)
        requirements_file_unix = "\n".join(package_list)
    else:
        requirements_file_unix = "\n".join(package_list)
        package_list.append("pywin32==304")
        package_list.sort()
        requirements_file_win = "\n".join(package_list)

    for os_type, requirements_file in zip(
        write_names, [requirements_file_win, requirements_file_unix]
    ):
        with open(f"{folder}/requirements_{os_type}.txt", "w") as file:
            print(f"{folder}/requirements_{os_type}")
            file.write(requirements_file)
