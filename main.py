#!/usr/bin/env python3
import os
import subprocess
import sys
import tomllib
import argparse
from dataclasses import dataclass

@dataclass
class Colours:
    """This is a class to hold the ascii escape sequences for printing colours."""

    red: str = "\033[31m"
    endc: str = "\033[m"
    green: str = "\033[32m"
    yellow: str = "\033[33m"
    blue: str = "\033[34m"

def die(message: str) -> None:
    """This is a function to exit the program with a die message."""

    print(f"{Colours.red}[ERROR]{Colours.endc} {message}", file=sys.stderr)
    exit(1)

def parse_args():
    """This is a function to handle the parsing of command line args passed to the program."""

    parser = argparse.ArgumentParser(
        prog='Xenia Installer',
        description='Program to install Xenia Linux.'
    )
    parser.add_argument(
        '-a', '--automated',
        action='append',
        nargs=1,
        dest='config_name',
        help='Run the installer automated from a toml config file.'
    )

    args = parser.parse_args()

    if args.config_name is not None:
        if len(args.config_name) > 1:
            die("Mutiple config files provided - only 1 can be parsed.")
        config_file: string = args.config_name
        interactive: bool = True
    else:
        interactive: bool = False

    # print(args.config_name[0])

class VarChecker:
    """
    This is a class to ensure the validity of variables passed to the script.

    Attributes:
        var_type      (string): Contains the type of variable to check.
        check_var (string): Contains the contents of the variable to check.
    """

    def __init__(self, var_type: str, check_var: str) -> None:
        """
        The constructors for the VarChecker class.

        Parameters:
            var_type  (string): Contains the type of variable to check.
            check_var (string): Contains the contents of the variable to check.
        """

        self.var_type: str = var_type
        self.check_var: str = check_var

    def checker(self) -> bool:
        """The function to sort the type of variable to sort, and call the correct function."""

        match self.var_type:
            case "drive":
                return self.drive()
            case other:
                return False

    def drive(self) -> bool:
        """The function to validate the drive variable."""

        drives = get_drives()

        if self.check_var in drives:
            return True
        else:
            return False

def parse_config(config_file: str) -> dict:
    """
    The is the function to parse the toml config file.

    Parameters:
        config_file (string): Contains the path to the configuration file.
    """

    with open(config_file, "rb") as file:
        config_parsed = tomllib.load(file)

    required_varibles: list = ["drive"]

    for i in range(len(required_varibles)):
        if not required_varibles[i] in config_parsed.keys():
            user_input: str = input(f"{Colours.red}[ERROR]{Colours.endc} The specified configuration file {config_file} is missing the required key {required_varibles[i]}. Would you like to specify it now? (Y/n) ")
            match user_input.lower():
                case "" | "y" | "yes":
                    append_new_key: bool = True
                case "n" | "no":
                    append_new_key: bool = False
                case other:
                    die("Invalid input - exiting!")
            if append_new_key:
                user_input: str = input(f"Please enter the value you would like to use for {required_varibles[i]}: ")
                var_checker = VarChecker(required_varibles[i], user_input)

                if not var_checker.checker():
                    die(f"{user_input} is an invalid entry for the key {required_varibles[i]} - exiting!")

                append_data: str = f"{required_varibles[i]} = {user_input}\n"

                with open(config_file, "a") as file:
                    file.write(append_data)

                config_parsed[required_varibles[i]] = user_input
                print(config_parsed)
            else:
                die(f"Missing required variable {required_varibles[i]} - exiting!")

    exit(1) # Temporary - for development/debugging
    return config_parsed

def get_drives() -> list:
    """The function to get all possible drives for installation."""

    all_drives_array = next(os.walk('/sys/block'))[1]

    supported_types: list = ["sd", "nvme", "mmcblk"]

    drives: list = [i for i in all_drives_array if any(i.startswith(drivetype) for drivetype in supported_types)]

    return drives

def mount(drive: str, stage4_url: str) -> None:
    """
    The function to mount all required filesystems for the install.

    Parameters:
        drive      (string): Contains the drive to install too.
        stage4_url (string): Contains the link to the latest stage4 rootfs.
    """

    if not os.path.exists(r'/mnt/xenia'):
        os.makedirs(r'/mnt/xenia')

    folder_paths: list = [r'/mnt/xenia', r'/mnt/xenia/roots', r'/mnt/xenia/overlay', r'/mnt/xenia/root', r'/mnt/xenia/home']

    for i in range (len(folder_paths)):
        if not os.path.exists(folder_paths[i]):
            os.makedirs(folder_paths[i])

    subprocess.run(["mount", "--label", "ROOTS", "/mnt/roots"])
    subprocess.run(["mount", "--label", "OVERLAY", "/mnt/overlay"])
    subprocess.run(["mount", "--label", "HOME", "/mnt/home"])

    folder_paths: list = [r'/mnt/overlay/var',r'/mnt/overlay/varw',r'/mnt/overlay/etc',r'/mnt/overlay/etcw']
    
    for i in range (len(folder_paths)):
        if not os.path.exists(folder_paths[i]):
            os.makedirs(folder_paths[i])

    subprocess.run(["rm", "-f", "/mnt/xenia/roots/root.img"])
    subprocess.run(["wget", "-O", "/mnt/xenia/roots/root.img", stage4_url]) # TODO: use requests instead of shelling out

def main():
    """The main function."""

    install_drive = "" # Temporary - for development/debugging

    parse_args()
    parse_config("config.toml")

    mount(install_drive, "https://repo.xenialinux.com/releases/current/root.img")

if __name__ == '__main__':
    main()
