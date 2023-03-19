import os
import json


def load_file(filename, mode: str = "r") -> any:
    try:
        with open(filename, mode) as file:
            return file.read()
    except OSError as e:
        return ""


def load_json_data(json_str):
    """Load previously saved json data as a dict.

    Check for a previously saved data. If it exists, return data as a
    dict. If no data is found, an empty dictionary will be returned.
    """
    if json_str == "":
        return {}
    try:
        return json.loads(json_str)
    except ValueError as e:
        print(f"Unable to decode {json_str}: {e}")
        return {}


def delete_file(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
