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
from .instruction_logger import log_instruction

from src.domain.trace_processor_model import TraceState, Instruction
from src.domain.enums import Ioptions
from src.domain.const import COMPRESSED_INSTRUCTION_SIZE, INSTRUCTION_SIZE


def is_taken_branch(instr, state: TraceState):  
    # determine if instruction is a branch and adjust branch count/map, 
    # return taken status local variables
    taken = False
    if not is_branch(instr):
        return False
    if state.branches == 0:
        raise Exception("ERROR: Cannot resolve branch")
    else:
        taken = (state.branch_map & 1) == 0  # taken=!branch[0]
        state.branches -= 1
        state.branch_map = (
            state.branch_map >> 1
        )  # shift branch map to next branch
    return taken


def is_branch(instr):  
    # determine if instruction is a branch
    if instr.opcode in [
        "beq",
        "bne",
        "blt",
        "bge",
        "bltu",
        "bgeu",
        "c.beqz",
        "c.bnez",
        "beqz",
        "bnez",
        "blez",
        "bgez",
        "bltz",
        "bgtz",
    ]:
        return True
    return False


def is_pseudo_branch(instr):
    if instr.opcode in ["beqz", "bnez", "blez", "bgez", "bltz", "bgtz"]:
        return True
    return False


def is_compressed_branch(instr):
    # determine if instruction is a compressed branch
    if instr.opcode in ["c.beqz", "c.bnez"]:
        return True
    return False


def is_inferable_jump(instr):  
    # determine if instruction is an inferable jump
    if instr.opcode in ["jal", "c.j", "c.jal"] or (
        instr.opcode == "jalr" and instr.rs1 == 0
    ):
        return True
    return False


def is_uninferable_jump(instr):  
    # determine if instruction is an uninferable jump
    if instr.opcode in ["c.jr", "c.jalr"] or (
        instr.opcode == "jalr" and instr.rs1 != 0
    ):
        return True
    return False


def is_return_from_trap(instr):  
    # determine if instruction is a return from trap
    if instr.opcode in ["uret", "sret", "mret", "dret"]:
        return True
    return False


def is_uninferable_discon(instr): 
    # determine if an instruction is an uninferable discontinuity
    if (
        is_uninferable_jump(instr)
        or is_return_from_trap(instr)
        or instr.opcode in ["ecall", "ebreak", "c.ebreak"]
    ):
        return True
    return False


def is_sequential_jump(instr, prev_addr, state: TraceState):  
    # determine if an instruction is a sequentially inferable jump
    if not (is_uninferable_jump(instr) and state.options[Ioptions.SIJUMP]):
        return False

    prev_instr = get_instr(prev_addr, state)  # local

    if prev_instr in ["auipc", "lui", "c.lui"]:
        return instr.rs1 == prev_instr.rd  # TODO: check if correct
    return False


def is_call(instr):  
    # determine if instruction is a call - excludes tail call as they do 
    # not push an address onto the return stack
    if instr.opcode in ["c.jal", "c.jalr"] or (
        instr.opcode in ["jalr", "jal"] and instr.rd == 1
    ):
        return True
    return False


def is_implicit_return(instr, te_inst, state: TraceState):  
    # determine if instruction return address can be implicitly inferred
    if state.options[Ioptions.IMPLICIT_RETURN] == False:
        return False
    if (instr.opcode == "jalr" and instr.rs1 == 1 and instr.rd == 0) or (
        instr.opcode == "c.jr" and instr.rs1 == 1
    ):
        if (
            te_inst.irreport != get_preceding_bit(te_inst, "irreport")
            and te_inst.irdepth == state.irstack_depth
        ):
            return False
        return state.irstack_depth > 0
    return True


def instruction_size(instr):
    if "c." in instr.opcode:
        return COMPRESSED_INSTRUCTION_SIZE
    return INSTRUCTION_SIZE


def report_pc(address, state: TraceState):
    log_instruction(address, state)
    return


def get_preceding_bit(te_inst, field_name, state: TraceState):
    # returns the value of the specified bit `field_name` from the te_inst packet
    # that precedes the given `te_inst` in the history

    try:
        # find the index of the given te_inst in history
        index = state.te_inst_list.index(te_inst)

        # ensure there is a preceding packet
        if index == 0:
            return None  # no preceding value available

        # return the value of the requested field from the preceding packet
        return getattr(state.te_inst_list[index - 1], field_name, None)

    except ValueError:
        # te_inst is not found in history
        raise Exception("ERROR: te_inst not found in te_inst_history")


def get_instr(address, state: TraceState):
    # retrieves an instruction object from the instruction map given an address
    # only considers instructions present in the discontinuities map

    if address not in state.instruction_map:
        raise Exception(f"ERROR: Address {hex(address)} is not an instruction")

    # get the instruction mnemonic and operands
    mnemonic, op_str = state.instruction_map[address]

    # convert mnemonic to lowercase for consistency
    opcode = mnemonic.lower()

    # split operands (handling cases like imm(rs1) -> imm, rs1)
    operands = op_str.replace("(", ",").replace(")", "").split(", ")

    # init
    imm, rs1, rs2, rd = None, None, None, None

    if opcode == "jalr":
        rd, rs1, imm = operands
    elif opcode in {"jal", "c.j", "c.jal", "c.jr", "c.jalr"}:
        imm = operands[0]
        if imm == "0": # end of trace recursive jump
            exit()

    elif opcode in {"beq", "bne", "blt", "bge", "bltu", "bgeu"}:
        rs1, rs2, imm = operands
    elif opcode in {
        "c.beqz",
        "c.bnez",
        "beqz",
        "bnez",
        "blez",
        "bgez",
        "bltz",
        "bgtz",
    }:
        rd, rs1 = operands

    return Instruction(opcode, rd, rs1, rs2, imm)


# NOT IMPLEMENTED
def report_trap(te_inst):
    # report ecause and tval
    raise NotImplementedError("report_trap() not implemented")


def report_epc(address):
    # report exception program counter value
    raise NotImplementedError("report_epc() not implemented")
