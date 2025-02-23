# Copyright 2024 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import errno
import os
import json

from europi_log import *


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
        log_warning(f"Unable to read {filename}: {e}", "file_utils")
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
        log_warning(f"Unable to parse JSON data from {filename}: {e}", "file_utils")
        return {}
    except OSError as e:
        if e.errno == errno.ENOENT:
            log_info(f"/{filename} does not exist. Using default settings", "file_utils")
        else:
            log_warning(f"Unable to open {filename}: {e}", "file_utils")
        return {}


def delete_file(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
