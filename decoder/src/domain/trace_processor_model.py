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


class DiscoveryResponse:
    # hardcoded encoder parameters
    def __init__(self):
        self.iaddress_lsb = 0
        self.call_counter_size = 0
        self.return_stack_size = 0


class Instruction:
    # represents a decoded RISC-V instruction

    def __init__(self, opcode, rd=None, rs1=None, rs2=None, imm=None):
        self.opcode = opcode
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm

    def __repr__(self):
        return f"Instr(opcode='{self.opcode}', rd='{self.rd}', rs1='{self.rs1}', imm='{self.imm}')"


class TraceState:
    # represents the state of the trace processor
    def __init__(self):
        self.te_inst_list = []
        self.instruction_map = []

        self.pc = 0
        self.last_pc = 0
        self.branches = 0
        self.branch_map = 0
        self.stop_at_last_branch = False
        self.inferred_address = False
        self.start_of_trace = True
        self.address = 0
        self.privilege = 0
        self.options = None
        self.return_stack = []
        self.irstack_depth = 0

    def set_instruction_map(self, m):
        self.instruction_map = m

    def set_te_inst_list(self, l):
        self.te_inst_list = l
