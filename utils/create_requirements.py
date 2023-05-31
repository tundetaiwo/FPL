""" Script to create requirements for both windows and unix based systems"""
# %%
import io
import os
import platform
import sys
from subprocess import PIPE, Popen
from typing import List


def create_requirements(folder: str, os_names: List[str] = None) -> None:
    """
    Function to write requirements file for both windows and unix based system

    Parameters
    ----------
    `str` folder: location of directory to write requirements files
    `List[str]` os_names: names of operating systems, if None then set to ["win", "unix"]

    Returns
    -------
    `None`

    """
    if not os.path.isdir(folder):
        raise ValueError(f"folder argument: '{folder}' is not a directory.")

    if os_names is None:
        os_names = ["win", "unix"]
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
        package_list.sort(key=str.casefold)
        requirements_file_win = "\n".join(package_list)

    for os_type, requirements_file in zip(
        os_names, [requirements_file_win, requirements_file_unix]
    ):
        with open(f"{folder}/requirements_{os_type}.txt", "w") as file:
            print(f"{folder}/requirements_{os_type}")
            file.write(requirements_file)
