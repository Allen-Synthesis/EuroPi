import errno
import os
import json


def load_file(filename, mode: str = "r") -> any:
    """Load a file and return its contents

    @param filename  The name of the file to load
    @param mode      The mode to open the file in. Should be "r" for text files or "rb" for binary files

    @return  The file's contents, either as a string or bytes, depending on mode.
    """
    try:
        with open(filename, mode) as file:
            return file.read()
    except OSError as e:
        print(f"Unable to read {filename}: {e}")
        if "b" in mode:
            return b""
        else:
            return ""


def load_json_file(filename, mode="r") -> dict:
    """Load a file and return its contents

    @param filename  The name of the file to load
    @param mode      The mode to open the file in. Should be "r" except in very unique circumstances

    @return  The file's contents as a dict
    """
    try:
        with open(filename, mode) as file:
            return json.load(file)
    except ValueError as e:
        print(f"Unable to parse JSON data from {filename}: {e}")
        return {}
    except OSError as e:
        if e.errno == errno.ENOENT:
            print(f"/{filename} does not exist. Using default settings")
        else:
            print(f"Unable to open {filename}: {e}")
        return {}


def delete_file(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
