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

# Authors: Umberto Laghi (umberto.laghi2@unibo.it), Samuele Righi (samuele.righi@studio.unibo.it)

# imports
import os
import sys

#
from os import path
from src.controller.trace_decoder import decoder

# this controller works as the main orchestrator of the whole system:
# 1. reads the path of both the compiled code and the one containg the packets from terminal
# 2. starts the process of creating a trace
# 3. outputs the result

# checks if exactly two args are provided
if len(sys.argv) != 3:
    print("Usage: python3 decoder.py <packets.bin> <compiled.riscv>")
    sys.exit(1)

# assigning file paths to vars
packets_path = sys.argv[1]
compiled_path = sys.argv[2]

# checks if the files exist
if not path.exists(packets_path):
    print(f"Error: the file {packets_path} does not exist.")
    sys.exit(1)
if not path.exists(compiled_path):
    print(f"Error: the file {compiled_path} does not exist.")
    sys.exit(1)

# checks if the file extensions are correct
if not packets_path.endswith(".bin"):
    print(f"Error: the file {packets_path} must be a binary file.")
    sys.exit(1)
if not compiled_path.endswith(".riscv"):
    print(f"Error: the file {compiled_path} must be RISC-V compiled file.")
    sys.exit(1)

# delete the output file if it exists
if path.exists("execution_trace"):
    os.remove("execution_trace")

decoder(packets_path, compiled_path)
