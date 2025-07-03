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

# Author: Umberto Laghi (umberto.laghi2@unibo.it)

# imports
from .enums import *

from abc import ABC
from tabulate import tabulate


# Abstract class that represent a packet
class Packet(ABC):
    # constructor
    def __init__(self, format: int):
        self.format = format

    def getFormat(self):
        return self.format


# Class that represents a Format 1 packet
class Format1(Packet):
    # constructor
    def __init__(self):
        # calling the constructor from the super class
        super().__init__(1)
        # initialize the other attributes
        self.branches = 0
        self.branch_map = ""
        self.address = 0
        self.notify = 0
        self.updiscon = 0
        self.irreport = 0
        self.irdepth = ""

    # print override
    def __str__(self):
        data = [
            ("format", f"{self.getFormat()}"),
            ("branches", f"{self.getBranches()}"),
            ("branch_map", f"{self.getBranchMap()}"),
            ("address", f"{self.getAddressHex()}"),
            ("notify", f"{self.getNotify()}"),
            ("updiscon", f"{self.getUpdiscon()}"),
            ("irreport", f"{self.getIrreport()}"),
            ("irdepth", f"{self.getIrdepth()}"),
        ]
        return tabulate(data, headers=["Field name", "Value"], tablefmt="grid")

    # getters
    def getBranches(self):
        return self.branches

    def getBranchMap(self):
        return self.branch_map

    def getAddressHex(self):  # returns as hex
        return hex(self.address)

    def getAddressDec(self):  # returns as decimal
        return self.address

    def getNotify(self):
        return self.notify

    def getUpdiscon(self):
        return self.updiscon

    def getIrreport(self):
        return self.irreport

    def getIrdepth(self):
        return self.irdepth

    # setters
    def setBranches(self, branches: int):
        self.branches = branches

    def setBranchMap(self, branch_map: str):
        self.branch_map = branch_map

    def setAddress(self, address: int):
        self.address = address

    def setNotify(self, notify: int):
        self.notify = notify

    def setUpdiscon(self, updiscon: int):
        self.updiscon = updiscon

    def setIrreport(self, irreport: int):
        self.irreport = irreport

    def setIrdepth(self, irdepth: str):
        self.irdepth = irdepth


# Class that represents a Format 2 packet
class Format2(Packet):
    # constructor
    def __init__(self):
        # calling the constructor from the super class
        super().__init__(2)
        # initialize the other attributes
        self.address = 0
        self.notify = 0
        self.updiscon = 0
        self.irreport = 0
        self.irdepth = ""

    # print override
    def __str__(self):
        data = [
            ("format", f"{self.getFormat()}"),
            ("address", f"{self.getAddressHex()}"),
            ("notify", f"{self.getNotify()}"),
            ("updiscon", f"{self.getUpdiscon()}"),
            ("irreport", f"{self.getIrreport()}"),
            ("irdepth", f"{self.getIrdepth()}"),
        ]
        return tabulate(data, headers=["Field name", "Value"], tablefmt="grid")

    # getters
    def getAddressHex(self):  # returns as hex
        return hex(self.address)

    def getAddressDec(self):  # returns as decimal
        return self.address

    def getNotify(self):
        return self.notify

    def getUpdiscon(self):
        return self.updiscon

    def getIrreport(self):
        return self.irreport

    def getIrdepth(self):
        return self.irdepth

    # setters
    def setAddress(self, address: int):
        self.address = address

    def setNotify(self, notify: int):
        self.notify = notify

    def setUpdiscon(self, updiscon: int):
        self.updiscon = updiscon

    def setIrreport(self, irreport: int):
        self.irreport = irreport

    def setIrdepth(self, irdepth: str):
        self.irdepth = irdepth


# Abstract class that represent a Format 3 packet
class Format3(Packet):
    # constructor
    def __init__(self, subformat: int):
        super().__init__(3)
        self.subformat = subformat

    def getSubformat(self):
        return self.subformat


# Abstract class that represent a Format 3 Subformat 0 packet
class Format3Subformat0(Format3):
    # constructor
    def __init__(self):
        super().__init__(0)
        self.branch = 0
        self.privilege = Privilege.U
        self.time = ""
        self.context = ""
        self.address = 0  # hex are int but with a different representation

    # print override
    def __str__(self):
        data = [
            ("format", f"{self.getFormat()}"),
            ("subformat", f"{self.getSubformat()}"),
            ("branch", f"{self.getBranch()}"),
            ("privilege", f"{self.getPrivilege()}"),
            ("time", f"{self.getTime()}"),
            ("context", f"{self.getContext()}"),
            ("address", f"{self.getAddressHex()}"),
        ]
        return tabulate(data, headers=["Field name", "Value"], tablefmt="grid")

    # getters
    def getBranch(self):
        return self.branch

    def getPrivilege(self):
        return self.privilege.name

    def getTime(self):
        return self.time

    def getContext(self):
        return self.context

    def getAddressHex(self):  # returns as hex
        return hex(self.address)

    def getAddressDec(self):  # returns as decimal
        return self.address

    # setters
    def setBranch(self, branch: int):
        self.branch = branch

    def setPrivilege(self, privilege: Privilege):
        self.privilege = privilege

    def setTime(self, time: str):
        self.time = time

    def setContext(self, context: str):
        self.context = context

    def setAddress(self, address: int):
        self.address = address


# Abstract class that represent a Format 3 Subformat 1 packet
class Format3Subformat1(Format3):
    # constructor
    def __init__(self):
        super().__init__(1)
        self.branch = 0
        self.privilege = Privilege.U
        self.time = ""
        self.context = ""
        self.ecause = 0
        self.interrupt = 0
        self.thaddr = 0
        self.address = 0
        self.tval = 0

    # print override
    def __str__(self):
        data = [
            ("format", f"{self.getFormat()}"),
            ("subformat", f"{self.getSubformat()}"),
            ("branch", f"{self.getBranch()}"),
            ("privilege", f"{self.getPrivilege()}"),
            ("time", f"{self.getTime()}"),
            ("context", f"{self.getContext()}"),
            ("ecause", f"{self.getEcause()}"),
            ("interrupt", f"{self.getInterrupt()}"),
            ("thaddr", f"{self.getThaddr()}"),
            ("address", f"{self.getAddressHex()}"),
            ("tval", f"{self.getTval()}"),
        ]
        return tabulate(data, headers=["Field name", "Value"], tablefmt="grid")

    # getters
    def getBranch(self):
        return self.branch

    def getPrivilege(self):
        return self.privilege.name

    def getTime(self):
        return self.time

    def getContext(self):
        return self.context

    def getEcause(self):
        return hex(self.ecause)

    def getInterrupt(self):
        return self.interrupt

    def getThaddr(self):
        return self.thaddr

    def getAddressHex(self):  # returns as hex
        return hex(self.address)

    def getAddressDec(self):  # returns as decimal
        return self.address

    def getTval(self):
        return hex(self.tval)

    # setters
    def setBranch(self, branch: int):
        self.branch = branch

    def setPrivilege(self, privilege: Privilege):
        self.privilege = privilege

    def setTime(self, time: str):
        self.time = time

    def setContext(self, context: str):
        self.context = context

    def setEcause(self, ecause: int):
        self.ecause = ecause

    def setInterrupt(self, interrupt: int):
        self.interrupt = interrupt

    def setThaddr(self, thaddr: int):
        self.thaddr = thaddr

    def setAddress(self, address: int):
        self.address = address

    def setTval(self, tval: int):
        self.tval = tval


# Abstract class that represent a Format 3 Subformat 2 packet
class Format3Subformat2(Format3):
    # constructor
    def __init__(self):
        super().__init__(2)
        self.privilege = Privilege.U
        self.time = ""
        self.context = ""

    # print override
    def __str__(self):
        data = [
            ("format", f"{self.getFormat()}"),
            ("subformat", f"{self.getSubformat()}"),
            ("privilege", f"{self.getPrivilege()}"),
            ("time", f"{self.getTime()}"),
            ("context", f"{self.getContext()}"),
        ]
        return tabulate(data, headers=["Field name", "Value"], tablefmt="grid")

    # getters
    def getPrivilege(self):
        return self.privilege.name

    def getTime(self):
        return self.time

    def getContext(self):
        return self.context

    # setters
    def setPrivilege(self, privilege: Privilege):
        self.privilege = privilege

    def setTime(self, time: str):
        self.time = time

    def setContext(self, context: str):
        self.context = context


# Abstract class that represent a Format 3 Subformat 3 packet
class Format3Subformat3(Format3):
    # constructor
    def __init__(self):
        super().__init__(3)
        self.ienable = 0
        self.encoder_mode = 0  # 0 for instruction trace
        self.qual_status = QualStatus.NO_CHANGE  # enum
        self.ioptions = {
            Ioptions.DELTA_ADDRESS: True,
            Ioptions.FULL_ADDRESS: False,
            Ioptions.IMPLICIT_EXCEPTION: False,
            Ioptions.SIJUMP: False,
            Ioptions.IMPLICIT_RETURN: False,
            Ioptions.BRANCH_PREDICTION: False,
            Ioptions.JUMP_TARGET_CACHE: False,
        }
        """
        The following fields are not used because 
        the data trace is not supported yet:
        self.denable = ""
        self.dloss = ""
        self.options = ""
        """

    # print override
    def __str__(self):
        data = [
            ("format", f"{self.getFormat()}"),
            ("subformat", f"{self.getSubformat()}"),
            ("ienable", f"{self.getIenable()}"),
            ("encoder_mode", f"{self.getEncoderMode()}"),
            ("qual_status", f"{self.getQualStatus()}"),
            ("ioptions", f"{self.printIoptions()}"),
        ]
        return tabulate(data, headers=["Field name", "Value"], tablefmt="grid")

    # getters
    def getIenable(self):
        return self.ienable

    def getEncoderMode(self):
        return self.encoder_mode

    def getQualStatus(self):
        return self.qual_status.name

    def getIoptions(self):
        return self.ioptions

    # setters
    def setIenable(self, ienable: int):
        self.ienable = ienable

    def setEncoderMode(self, encoder_mode: int):
        self.encoder_mode = encoder_mode

    def setQualStatus(self, qual_status: QualStatus):
        self.qual_status = qual_status

    def setIoptions(self, ioptions: dict):
        self.ioptions = ioptions

    # print
    def printIoptions(self):
        result = ""
        for el in self.ioptions:
            result += f"{el.name} : {self.ioptions[el]}\n"
        return result
