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
import yaml
#
from capstone import *
from elftools.elf.elffile import ELFFile


def load_riscv_instructions(filename, sections):
    # create a dictionary {PC: istruzione}
    with open(filename, "rb") as f:
        # create empty instruction map
        instruction_map = {}

        elf = ELFFile(f)

        # capstone riscv init
        md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV64 | CS_MODE_RISCVC)
        # for 32 bit sistems
        # md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)

        for sec in sections['disassemble']['sections']:
            instruction_map = extract_section(elf, md, instruction_map, sec)
        return instruction_map


def extract_section(elf, md, instruction_map, section_name):
    # extract bytecode and base address from section
    text_section = elf.get_section_by_name(section_name)
    if not text_section:
        raise ValueError("Section not found: " + section_name)
    code = text_section.data()
    base_addr = text_section["sh_addr"]

    # disassemble and populate map
    for ins in md.disasm(code, base_addr):
        """
        ins.address -> instruction address
        ins.mnemonic -> instruction name
        ins.op_str -> instruction operands
        """
        instruction_map[ins.address] = (ins.mnemonic, ins.op_str)

    return instruction_map


def get_sections():
    with open("disassembler_config.yaml") as stream:
        try:
            sections = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise Exception("Error while loading YAML file: "+exc) 
    return sections


def get_instruction_map(filename):
    return load_riscv_instructions(filename, get_sections())

