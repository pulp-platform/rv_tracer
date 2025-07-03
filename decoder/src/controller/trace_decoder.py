# Copyright (C) 2025 ETH Zurich and University of Bologna

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Author: Samuele Righi (samuele.righi@studio.unibo.it)

# imports
from src.services.packet_parser import parse_packets
from src.services.trace_processor import process_te_inst
from src.services.elf_disassembler import get_instruction_map

from src.domain import *


def decoder(packets_path, compiled_path):
    # reads the binary file and creating packets
    packets = parse_packets(packets_path)
    # creates the trace
    instruction_map = get_instruction_map(compiled_path)

    # creates the trace state
    state = TraceState()
    state.set_instruction_map(instruction_map)
    state.set_te_inst_list(packets)

    # processes the packets
    for packet in packets:
        process_te_inst(packet, state)
