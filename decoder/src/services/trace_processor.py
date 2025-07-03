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
from .trace_processor_utils import *

from src.domain.enums import Ioptions, QualStatus
from src.domain.trace_processor_model import (
    DiscoveryResponse,
    TraceState,
)

discovery_response = DiscoveryResponse()


def process_te_inst(
    te_inst, state: TraceState
):  # called for every te_inst packet
    if te_inst.format == 3:
        if te_inst.subformat == 3:  # support packet
            process_support(te_inst, state)
            return
        """
        NOT IMPLEMENTED
        if te_inst.subformat == 2: # context packet
            return 
        """
        if te_inst.subformat == 1:  # trap packet
            report_trap(te_inst, state)
            if not te_inst.interrupt:  # exception
                report_epc(exception_address(te_inst))
            if not te_inst.thaddr:  # trap only - nothing retired
                return

        state.inferred_address = False  # flag reset
        state.address = te_inst.address << discovery_response.iaddress_lsb
        if te_inst.subformat == 1 or state.start_of_trace == True:
            state.branches = 0
            state.branch_map = 0
        if is_branch(
            get_instr(state.address, state)
        ):  # if instruction is a branch this is 1 unprocessed branch
            state.branch_map |= (
                int(str(te_inst.branch), 2) << state.branches
            )  # update branchmap
            state.branches += 1
        if te_inst.subformat == 0 and not state.start_of_trace:
            follow_execution_path(te_inst, state)
        else:
            state.pc = state.address
            report_pc(state.pc, state)
            state.last_pc = (
                state.pc
            )  # previous pc not known but ensures correct, operation for is_sequential_jump()
            state.privilege = te_inst.privilege
            state.start_of_trace = False
            state.irstack_depth = 0

    else:
        if state.start_of_trace:  # this should not be possible
            raise Exception("ERROR: Expecting trace to start whit format 3")

        if te_inst.format == 2 or te_inst.branches != 0:
            state.stop_at_last_branch = False
            if state.options[Ioptions.FULL_ADDRESS]:
                state.address = (
                    te_inst.address << discovery_response.iaddress_lsb
                )
            else:
                state.address += (
                    te_inst.address << discovery_response.iaddress_lsb
                )

        if te_inst.format == 1:
            state.stop_at_last_branch = (
                te_inst.branches == 0
            )  # 0 if current instruction is not a brach
            state.branch_map |= (
                int(str(te_inst.branch_map), 2) << state.branches
            )  # update branchmap
            if te_inst.branches == 0:
                state.branches += 31
            else:
                state.branches += te_inst.branches
        follow_execution_path(te_inst, state)


def follow_execution_path(
    te_inst, state: TraceState
):  # follow execution path to reported address
    # local variables
    previous_address = state.pc
    stop_here = False

    while True:
        if (
            state.inferred_address
        ):  # iterate again from previously reported address to find second occurrence
            stop_here = next_pc(previous_address, te_inst)
            report_pc(state.pc)
            if stop_here:
                state.inferred_address = False
        else:
            stop_here = next_pc(te_inst, state)
            report_pc(state.pc, state)

            if (
                state.branches == 1
                and is_branch(get_instr(state.pc, state))
                and state.stop_at_last_branch
            ):
                # reached final branch, stop here
                # (do not follow to next instruction as we do not yet know whether it retires)
                state.stop_at_last_branch = False
                return

            if stop_here:
                # reached reported address following an uninferable discontinuity, stop here
                if unprocessed_branches(state.pc, state):
                    raise Exception("ERROR: Unprocessed state.branches")
                return

            if (
                te_inst.format != 3
                and state.pc == state.address
                and not state.stop_at_last_branch
                and te_inst.notify
                != get_preceding_bit(te_inst, "notify", state)
                and not unprocessed_branches(state.pc, state)
            ):
                # all state.branches processed, and reached reported address due to notification, 
                # not as an uninferable jump target
                return

            if (
                te_inst.format != 3
                and state.pc == state.address
                and not state.stop_at_last_branch
                and not is_uninferable_discon(get_instr(state.last_pc, state))
                and te_inst.updiscon
                == get_preceding_bit(te_inst, "updiscon", state)
                and not unprocessed_branches(
                    state.pc, state
                )  # in the docs this call has no parameters (probably an error?)
                and (
                    te_inst.irreport
                    == get_preceding_bit(te_inst, "irreport", state)
                    or te_inst.irdepth == state.irstack_depth
                )
            ):
                # all state.branches processed, and reached reported address, but not as an 
                # uniferrable jump target stop here for now, though flag indicates this may
                # not be final retired instruction
                state.inferred_address = True
                return

            if (
                te_inst.format == 3
                and state.pc == state.address
                and not unprocessed_branches(state.pc, state)
                and (
                    te_inst.privilege == state.privilege
                    or is_return_from_trap(get_instr(state.last_pc))
                )
            ):
                # all state.branches processed, and reached reported address
                return


def next_pc(te_inst, state: TraceState):  # compute next pc
    # local variables
    instr = get_instr(state.pc, state)
    this_pc = state.pc
    stop_here = False

    if is_inferable_jump(instr):
        state.pc += int(instr.imm, 0)
    elif is_sequential_jump(
        instr, state.last_pc, state
    ):  # lui/auipc followed by jump using the same register
        state.pc = sequential_jump_target(state.pc, state.last_pc)
    elif is_implicit_return(instr, te_inst, state):
        state.pc = pop_return_stack()
    elif is_uninferable_discon(instr):
        if state.stop_at_last_branch:
            raise Exception("ERROR: Unexpected uninferable discontinuity")
        else:
            state.pc = state.address
            stop_here = True
    elif is_taken_branch(instr, state):
        if is_compressed_branch(instr) or is_pseudo_branch(instr):
            state.pc += int(instr.rs1, 0)
        else:
            state.pc += int(instr.imm, 0)
    else:
        state.pc += instruction_size(instr)

    if is_call(instr):
        push_return_stack(this_pc)

    state.last_pc = this_pc
    return stop_here


def process_support(te_inst, state: TraceState):
    # local variables
    stop_here = False
    state.options = te_inst.ioptions
    if te_inst.qual_status != QualStatus.NO_CHANGE:
        state.start_of_trace = True  # trace ended, so get ready to start again
    if te_inst.qual_status == QualStatus.ENDED_NTR and state.inferred_address:
        previous_address = state.pc  # local
        state.inferred_address = False
        while True:
            stop_here = next_pc(previous_address, te_inst)
            report_pc(state.pc)
            if stop_here:
                return
    return


def unprocessed_branches(
    address, state: TraceState
):  # check all state.branches processed (except 1 if this instruction is a branch)
    return state.branches != (1 if is_branch(get_instr(address, state)) else 0)


def push_return_stack(state: TraceState):
    if (
        state.options[Ioptions.IMPLICIT_RETURN] == False
    ):  # implicit return mode disabled
        return

    # local variables
    if discovery_response.return_stack_size:
        state.irstack_depth_max = 2**discovery_response.return_stack_size
    else:
        state.irstack_depth_max = 2**discovery_response.call_counter_size

    instr = get_instr(state.address)
    link = state.address
    if state.irstack_depth == state.irstack_depth_max:
        # delete oldest entry from stack to make room for new entry added below
        state.irstack_depth -= 1
        for i in range(state.irstack_depth):
            state.return_stack[i] = state.return_stack[i + 1]
    link += instruction_size(instr)
    state.return_stack[state.irstack_depth] = link
    state.irstack_depth += 1
    return


def pop_return_stack(state: TraceState):  # pop address from return stack
    # function not called if state.irstack_depth is 0, so no need to check for underflow
    state.irstack_depth -= 1  
    link = state.return_stack[state.irstack_depth]
    return link


def exception_address(te_inst, state: TraceState):
    # local variable
    instr = get_instr(state.pc)
    if is_uninferable_discon(instr) and not te_inst.thaddr:
        return te_inst.address
    if instr.opcode in ["ecall", "ebreak", "c.ebreak"]:
        return state.pc
    return next_pc(state.pc, te_inst)


def sequential_jump_target(
    address, prev_address
):  # find the target of a sequentially inferable jump
    # local variables
    instr = get_instr(address)
    prev_instr = get_instr(prev_address)
    target = 0

    if prev_instr.opcode == "auipc":
        target = prev_address
    target += prev_instr.imm
    if instr.opcode == "jalr":
        target += instr.imm
    return target
