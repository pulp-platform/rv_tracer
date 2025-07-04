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

from src.domain.trace_processor_model import TraceState


def log_instruction(address, state: TraceState):

    # Get the instruction details
    mnemonic, op_str = state.instruction_map[address]
    # Log the instruction
    with open("execution_trace", "a") as f:
        f.write(f"{hex(address)} {mnemonic} {op_str}\n")
