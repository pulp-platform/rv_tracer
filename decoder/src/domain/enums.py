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
from enum import Enum

# This file contains all the enum type used in the domain.


# The enum representing the operating mode of the encoder
class Ioptions(Enum):
    DELTA_ADDRESS = 0
    FULL_ADDRESS = 1
    IMPLICIT_EXCEPTION = 2
    SIJUMP = 3
    IMPLICIT_RETURN = 4
    BRANCH_PREDICTION = 5
    JUMP_TARGET_CACHE = 6


# The enum representing the qual_status
class QualStatus(Enum):
    NO_CHANGE = 0
    ENDED_REP = 1
    TRACE_LOST = 2
    ENDED_NTR = 3


class Privilege(Enum):
    M = 3
    HS = 2
    S = 1
    U = 0
