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
import pytest

from bootloader import BootloaderMenu
from europi_script import EuroPiScript


class GoodTestScript1(EuroPiScript):
    pass


class GoodTestScript2(EuroPiScript):
    pass


class BadTestScript:
    pass


@pytest.mark.parametrize(
    "cls, expected",
    [
        (GoodTestScript1, True),
        (GoodTestScript2, True),
        (BadTestScript, False),
    ],
)
def test_is_europi_script(cls, expected):
    assert BootloaderMenu._is_europi_script(cls) == expected
