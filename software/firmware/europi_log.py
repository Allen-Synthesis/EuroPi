# Copyright 2025 Allen Synthesis
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
"""
Assorted functions to make text-based logging easier

We define 4 levels of log:
- info -- general status information, high-level execution flow
- warning -- warnings that something's unusual, but not necessarily broken
- error -- a critical error that means our module has stopped working
- debug -- developer-oriented debugging information

Each log item has a level and a tag associated with it. The tag should be
unique to each module to make tracing the source of warnings easier
"""

import os


def log_info(message, tag=None):
    if tag:
        write_log_entry(f"[INFO] [{tag}] {message}")
    else:
        write_log_entry(f"[INFO] {message}")


def log_warning(message, tag=None):
    if tag:
        write_log_entry(f"[WARN] [{tag}] {message}")
    else:
        write_log_entry(f"[WARN] {message}")


def log_error(message, tag=None):
    if tag:
        write_log_entry(f"[ERR ] [{tag}] {message}")
    else:
        write_log_entry(f"[ERR ] {message}")


def log_debug(message, tag=None):
    if tag:
        write_log_entry(f"[DBUG] [{tag}] {message}")
    else:
        write_log_entry(f"[DBUG] {message}")


def write_log_entry(log_entry: str):
    print(log_entry)
    try:
        with open("/europi_log.txt", "a") as log_out:
            log_out.write(log_entry)
            log_out.write("\n")
    except Exception:
        pass


def init_log():
    try:
        os.remove("/europi_log.txt")
    except Exception:
        pass
