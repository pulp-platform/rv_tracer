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

# file that store constants

# constants as defined in the TE
PRIV_LEN = 2
XLEN = 64
IOPTIONS_LEN = 7
QUAL_STATUS_LEN = 2
CALL_COUNTER_SIZE = 0  # it is an exponent
# time and context settings
NO_TIME = 1
NO_CONTEXT = 1
# decoder constants
CHUNK_SIZE = 40  # bytes == 320 bits
# instruction size
INSTRUCTION_SIZE = 4  # bytes == 32 bits
COMPRESSED_INSTRUCTION_SIZE = 2  # bytes == 16 bits
