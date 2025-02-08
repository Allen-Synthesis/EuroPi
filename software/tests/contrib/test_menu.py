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
import inspect
import sys
import pytest
import utime
from contrib.menu import EUROPI_SCRIPTS
from bootloader import BootloaderMenu


@pytest.fixture
def mock_time_module(monkeypatch):
    """the time module isn't as easily mocked as the utime module is,
    but we can just swap it out for our mock for this test"""
    monkeypatch.setitem(sys.modules, "time", utime)


def test_menu_imports(mock_time_module):
    """User the bootloader code to test that every script declared in EUROPI_SCRIPTS can be imported."""
    bootloader = BootloaderMenu(EUROPI_SCRIPTS)
    for display_name in EUROPI_SCRIPTS.keys():
        class_name = EUROPI_SCRIPTS[display_name]
        clazz = bootloader.get_class_for_name(class_name)
        assert inspect.isclass(clazz), f"{class_name} does not resolve to a class"
        assert bootloader._is_europi_script(clazz), f"{class_name} is not a EuroPiScript"
