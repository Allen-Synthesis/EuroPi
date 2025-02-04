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

from contrib.scope import Scope


@pytest.mark.parametrize(
    "a_voltage, expected_pos",
    [
        (0.0, 31),
        (0.1, 31),
        (0.5, 30),
        (1.0, 29),
        (1.5, 28),
        (3.0, 24),
        (4.0, 21),
        (6.0, 16),
        (8.0, 11),
        (10.0, 6),
        (12.0, 0),
    ],
)
def test_calc_y_pos(a_voltage, expected_pos):
    assert Scope.calc_y_pos(12, a_voltage) == expected_pos



@pytest.mark.parametrize(
    "max_disp_voltage, a_voltage, expected_pos",
    [
        (6.0, 0.0, 31),
        (6.0, 0.1, 31),
        (6.0, 0.5, 29),
        (6.0, 1.0, 26),
        (6.0, 1.5, 24),
        (6.0, 3.0, 16),
        (6.0, 4.0, 11),
        (6.0, 6.0, 0),
        (6.0, 8.0, -10),
        (6.0, 10.0, -20),
        (6.0, 12.0, -31),
    ],
)
def test_calc_y_pos_scale(max_disp_voltage, a_voltage, expected_pos):
    assert Scope.calc_y_pos(max_disp_voltage, a_voltage) == expected_pos
