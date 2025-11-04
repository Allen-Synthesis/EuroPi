#!/usr/bin/env python3
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

# Local imports - automata implementations
from contrib.cellarium_docs.automata.life import Life
from contrib.cellarium_docs.automata.brians_brain import BriansBrain
from contrib.cellarium_docs.automata.droplets import Droplets
from contrib.cellarium_docs.automata.langtons_ant import LangtonsAnt
from contrib.cellarium_docs.automata.rule30 import Rule30
from contrib.cellarium_docs.automata.rule90 import Rule90
from contrib.cellarium_docs.automata.seeds import Seeds

# Order of list determines order of automata in selection menus
automata_list = [
    Life,
    BriansBrain,
    Droplets,
    Seeds,
    LangtonsAnt,
    Rule30,
    Rule90
    # Add more automata classes here
]

# Dictionary for easy lookup by name
automata_dict = {}

def get_automata_by_index(index):
    """Get automaton class by index"""
    if 0 <= index < len(automata_list):
        return automata_list[index]
    return automata_list[0]  # Default to first automaton

def get_automata_names():
    """Get list of automaton names"""
    names = []
    for automaton in automata_list:
        if hasattr(automaton, 'name'):
            names.append(automaton.name)
        else:
            names.append(automaton.__name__)
    return names

def initialize_registry():
    """Initialize the automata dictionary"""
    global automata_dict
    for automaton in automata_list:
        name = automaton.name if hasattr(automaton, 'name') else automaton.__name__
        automata_dict[name] = automaton

# Initialize on import
initialize_registry()