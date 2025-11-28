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

from collections import OrderedDict
from europi_log import log_warning

"""Registry system for cellular automata implementations in Cellarium.

Provides a central registration and lookup system for all available
cellular automata simulations. Supports:
- Indexing by automaton name or numeric ID
- Dynamic registration of new automaton types
- Name list generation for menus
- Default automaton fallback

@author Grybbit (https://github.com/Bearwynn)
@year 2025
"""

# Dictionary mapping display names to fully qualified class paths
CELLARIUM_AUTOMATA = OrderedDict([
    ["Life",              "contrib.cellarium_docs.automata.life.Life"],
    ["Brian's Brain",     "contrib.cellarium_docs.automata.brians_brain.BriansBrain"],
    ["Droplets",          "contrib.cellarium_docs.automata.droplets.Droplets"],
    ["Seeds",             "contrib.cellarium_docs.automata.seeds.Seeds"],
    ["Langton's Ant",     "contrib.cellarium_docs.automata.langtons_ant.LangtonsAnt"],
    ["Rule 30",           "contrib.cellarium_docs.automata.rule30.Rule30"],
    ["Rule 90",           "contrib.cellarium_docs.automata.rule90.Rule90"],
])

def get_class_for_name(automaton_class_name: str) -> type:
    """Get the automaton class by its fully qualified name.
    
    Args:
        automaton_class_name: Fully qualified class name (e.g. "contrib.cellarium_docs.automata.life.Life")
    
    Returns:
        The automaton class if found and valid, None otherwise
    """
    try:
        module, clazz = automaton_class_name.rsplit(".", 1)
        return getattr(__import__(module, None, None, [None]), clazz)
    except Exception as e:
        log_warning(f"Warning: Invalid automaton class name: {automaton_class_name}\n  caused by: {e}", "cellarium")
        return None

def get_automata_by_index(index):
    """Get automaton class by index"""
    if 0 <= index < len(CELLARIUM_AUTOMATA):
        class_path = list(CELLARIUM_AUTOMATA.values())[index]
        return get_class_for_name(class_path)
    return get_class_for_name(list(CELLARIUM_AUTOMATA.values())[0])  # Default to first automaton

def get_automata_names():
    """Get list of automaton display names"""
    return list(CELLARIUM_AUTOMATA.keys())