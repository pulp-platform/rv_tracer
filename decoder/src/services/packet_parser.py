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
from src.domain.packet_format import *

from src.domain.enums import *
from src.domain.const import *

current_ioptions = Ioptions.DELTA_ADDRESS  # default start value


# utils functions
def _convert_line(chunk: bytes) -> str:
    """converts line from bytes to characters"""
    packet_bits = ""
    for byte in chunk:
        bits = f"{byte:08b}"  # converts the byte into a bit sequence
        packet_bits += bits
    return packet_bits


def _extract_payload(packet_bits: str) -> str:
    """extracts the payload from the encapsulated packet"""
    # splits the packet_bits string into the sections
    header = packet_bits[312:]
    timestamp = packet_bits[248:312]
    packet_len = int(header[-5:], 2)  # from header extracts the payload length
    return packet_bits[
        248 - packet_len * 8 : 248
    ]  # packet_len is multiplied by 8 to get the bits


def _find_address_len(
    payload_len: int, known_fields_len: int
) -> tuple[int, int]:
    """determines the length of address within a packet"""
    # this operation is required beacause the address gets compressed encoder side
    # and the number of bits kept is not known

    # corner case: address has length 0
    # this means is all padding
    if payload_len - known_fields_len < 9:
        return 0, payload_len - known_fields_len

    # general case
    address_len = (
        (payload_len - known_fields_len) // 8
    ) * 8 + 1  # finds the highest multiple of 8 + 1
    padding_len = payload_len - known_fields_len - address_len
    return address_len, padding_len


def _round_up(n: int) -> int:
    """rounds to the upper multiple of 8"""
    return ((n + 7) // 8) * 8


def _find_branch_map_len(branches: int) -> int:
    """determines the branch map length"""
    match branches:
        case _ if branches == 0:
            return 31
        case _ if branches == 1:
            return branches
        case _ if 2 <= branches <= 3:
            return 3
        case _ if 4 <= branches <= 7:
            return 7
        case _ if 8 <= branches <= 15:
            return 15
        case _ if 16 <= branches <= 31:
            return 31


def _twos_complement(bit_string: str) -> int:
    """computes the 2's complement of int value val"""
    if not bit_string:  # checks if the sequence is null
        return 0

    if bit_string[0] == "1":  # first bit 1: negative value
        # computes 2's complement to get absolute value
        value = int(bit_string, 2) - (1 << len(bit_string))
    else:  # first bit 0: positive value
        value = int(bit_string, 2)

    return value


def _extend_with_sign(bit_string: str, target_length: int) -> str:
    """extends with sign a bit string"""
    current_length = len(bit_string)

    if current_length == target_length:  # checks if already full length
        return bit_string

    msb = bit_string[0]  # selects MSB
    extension = msb * (target_length - current_length)  # extends with sign
    return extension + bit_string


def _parse_modes(bit_string: str) -> dict:
    # init
    ioptions = {
        Ioptions.DELTA_ADDRESS: True,
        Ioptions.FULL_ADDRESS: False,
        Ioptions.IMPLICIT_EXCEPTION: False,
        Ioptions.SIJUMP: False,
        Ioptions.IMPLICIT_RETURN: False,
        Ioptions.BRANCH_PREDICTION: False,
        Ioptions.JUMP_TARGET_CACHE: False,
    }
    # delta address
    if int(bit_string[0], 2):
        ioptions[Ioptions.DELTA_ADDRESS] = True
    else:
        ioptions[Ioptions.DELTA_ADDRESS] = False
    # full address
    if int(bit_string[1], 2):
        ioptions[Ioptions.FULL_ADDRESS] = True
    else:
        ioptions[Ioptions.FULL_ADDRESS] = False
    # implicit exception
    if int(bit_string[2], 2):
        ioptions[Ioptions.IMPLICIT_EXCEPTION] = True
    else:
        ioptions[Ioptions.IMPLICIT_EXCEPTION] = False
    # sijump
    if int(bit_string[3], 2):
        ioptions[Ioptions.SIJUMP] = True
    else:
        ioptions[Ioptions.SIJUMP] = False
    # implicit return
    if int(bit_string[4], 2):
        ioptions[Ioptions.IMPLICIT_RETURN] = True
    else:
        ioptions[Ioptions.IMPLICIT_RETURN] = False
    # branch prediction
    if int(bit_string[5], 2):
        ioptions[Ioptions.BRANCH_PREDICTION] = True
    else:
        ioptions[Ioptions.BRANCH_PREDICTION] = False
    # jump target cache
    if int(bit_string[6], 2):
        ioptions[Ioptions.JUMP_TARGET_CACHE] = True
    else:
        ioptions[Ioptions.JUMP_TARGET_CACHE] = False

    return ioptions


# parsing functions
def _parse_format3_subformat3(payload: str) -> Packet:
    """parses a string into a format 3 subformat 3 packet"""

    # fields to parse:
    # format          2
    # subformat       2
    # ienable         1
    # encoder_mode    1
    # qual_status     2
    # ioptions        3
    # following not supported
    # denable     ??
    # dloss       ??
    # doptions    ??

    current_index = 4
    packet = Format3Subformat3()

    # sets attributes
    packet.setIenable(int(payload[-(current_index + 1) : -current_index], 2))
    # print(payload[-(current_index+1):-current_index])
    current_index += 1
    packet.setEncoderMode(
        int(payload[-(current_index + 1) : -current_index], 2)
    )
    current_index += 1
    packet.setQualStatus(
        QualStatus(
            int(
                payload[-(QUAL_STATUS_LEN + current_index) : -current_index], 2
            )
        )
    )
    current_index += QUAL_STATUS_LEN
    packet.setIoptions(
        _parse_modes(payload[-(current_index + IOPTIONS_LEN) : -current_index])
    )

    # sets the ioptions as the one just read
    current_ioptions = packet.getIoptions()

    return packet


def _parse_format3_subformat2(payload: str) -> Packet:
    """parses a string into a format 3 subformat 2 packet"""

    # fields to parse:
    # format      2
    # subformat   2
    # priv        PRIV_LEN
    # time        ??
    # context     ??

    current_index = 4
    packet = Format3Subformat2()

    # sets attributes
    packet.setPrivilege(
        Privilege(
            int(payload[-(current_index + PRIV_LEN) : -current_index], 2)
        )
    )
    # TODO: setTime(), setContext

    return packet


def _parse_format3_subformat1(payload: str) -> Packet:
    """parses a string into a format 3 subformat 1 packet"""

    # fields to parse:
    # format      2
    # subformat   2
    # branch      1
    # priv        PRIV_LEN
    # time        ??
    # context     ??
    # ecause      XLEN
    # interrupt   1
    # thaddr      1
    # address     compressed
    # tval        XLEN

    # computes the compressed address length
    payload_len = len(payload)
    known_fields_len = 7 + PRIV_LEN + 2 * XLEN
    # adds time and/or context length
    if NO_TIME == 0:
        # TODO:
        # increase known_fields_length of time len
        pass
    if NO_CONTEXT == 0:
        # TODO:
        # increase known_fields_length of context len
        pass
    address_len, padding_len = _find_address_len(payload_len, known_fields_len)

    current_index = 4
    packet = Format3Subformat1()

    # sets attributes
    packet.setBranch(int(payload[-(current_index + 1) : -current_index], 2))
    current_index += 1
    packet.setPrivilege(
        Privilege(
            int(payload[-(current_index + PRIV_LEN) : -current_index], 2)
        )
    )
    # checks if time and context are enabled and save them
    current_index += PRIV_LEN
    if NO_TIME == 0:
        # TODO:
        # read and set time
        # update current_index
        pass
    if NO_CONTEXT == 0:
        # TODO:
        # read and set context
        # update current_index
        pass
    ecause = payload[-(current_index + XLEN) : -(current_index)]
    packet.setEcause(int(ecause, 2))
    current_index += XLEN
    packet.setInterrupt(int(payload[-(current_index + 1) : -current_index]))
    current_index += 1
    packet.setThaddr(int(payload[-(current_index + 1) : -current_index], 2))
    current_index += 1
    packet.setAddress(
        int(payload[-(current_index + address_len) : -current_index], 2)
    )
    current_index += address_len
    packet.setTval(
        int(payload[-(current_index + XLEN - padding_len) : -current_index], 2)
    )

    return packet


def _parse_format3_subformat0(payload: str) -> Packet:
    """parses a string into a format 3 subformat 0 packet"""

    # fields to parse:
    # format      2
    # subformat   2
    # branch      1
    # priv        PRIV_LEN
    # time        64
    # context     ??
    # address     compressed

    # the first field starts from the last char
    # format and subformat have been extracted

    # computing the compressed address length
    payload_len = len(payload)
    known_fields_len = 5 + PRIV_LEN
    # adds time and/or context length
    if NO_TIME == 0:
        # TODO
        # increases known_fields_length
        pass
    if NO_CONTEXT == 0:
        # TODO
        # increases known_fields_length
        pass
    address_len, padding_len = _find_address_len(payload_len, known_fields_len)

    current_index = 4  # starts from 4 because the format and subformat are
    packet = Format3Subformat0()

    # sets attributes
    packet.setBranch(int(payload[-(current_index + 1) : -current_index], 2))
    current_index += 1  # update current_index
    packet.setPrivilege(
        Privilege(
            int(payload[-(current_index + PRIV_LEN) : -current_index], 2)
        )
    )
    current_index += PRIV_LEN
    # checks if time and context are enabled and save them
    if NO_TIME == 0:
        # TODO:
        # read and set time
        # update current_index
        pass
    if NO_CONTEXT == 0:
        # TODO:
        # read and set context
        # update current_index
        pass
    packet.setAddress(
        int(payload[-(current_index + address_len) : -(current_index)], 2)
    )

    return packet


def _parse_format2(payload: str):
    """parses a string into a format 2 packet"""

    # fields to parse:
    # format      2
    # address     compressed
    # notify      1
    # updiscon    1
    # irreport    1
    # irdepth     2**CALL_COUNTER_SIZE

    current_index = 2
    packet = Format2()

    # sets attributes
    # checks if delta address is enabled
    if current_ioptions == Ioptions.DELTA_ADDRESS:
        # computing the compressed address length
        payload_len = len(payload)
        known_fields_len = 5 + 2**CALL_COUNTER_SIZE
        # adds time and/or context length
        if NO_TIME == 0:
            # TODO
            # increases known_fields_length
            pass
        if NO_CONTEXT == 0:
            # TODO
            # increases known_fields_length
            pass
        address_len, padding_len = _find_address_len(
            payload_len, known_fields_len
        )

        extendedAddr = _extend_with_sign(
            payload[-(current_index + address_len) : -current_index], XLEN + 1
        )
        twoCompAddr = _twos_complement(extendedAddr)
        packet.setAddress(twoCompAddr)
        current_index += address_len
    else:
        packet.setAddress(
            int(payload[-(current_index + XLEN) : -current_index], 2)
        )
        current_index += XLEN

    packet.setNotify(int(payload[-(current_index + 1) : -(current_index)], 2))
    current_index += 1
    packet.setUpdiscon(int(payload[-(current_index + 1) : -current_index], 2))
    current_index += 1
    packet.setIrreport(int(payload[-(current_index + 1) : -current_index], 2))
    current_index += 1
    packet.setIrdepth(
        int(
            payload[-(current_index + 2**CALL_COUNTER_SIZE) : -current_index],
            2,
        )
    )

    return packet


def _parse_format1(payload: str):
    """parses a string into a format 2 packet"""

    # fields to parse:
    # 1st type payload:
    # format
    # branches
    # branch_map
    # address
    # notify
    # updiscon
    # irreport
    # iredepth

    # 2nd type payload:
    # format
    # branches
    # branch_map

    # how to determine the payload type
    # it parses format and branches, from that we compute the length the packet should have if it is the 2nd
    # type payload. If it corresponds it is the 2nd type payload, otherwise it is the 1st one.

    # example:
    # value of branches is 10
    # the packet should have a total length of 2+10+17=29 -> rounded becomes 32/8=4 bytes

    # in summary: we compute the totale length based on branches fields,
    # round it to the upper closest multiple of eight
    # divided it by 8 and check if it corresponds to the packet length

    current_index = 2
    packet = Format1()

    branches = int(payload[-(current_index + 5) : -current_index], 2)
    packet.setBranches(branches)
    current_index += 5
    # compute the part of branch_map put inside payload
    branch_map_len = _find_branch_map_len(branches)
    packet.setBranchMap(
        payload[-(current_index + branch_map_len) : -current_index]
    )
    current_index += branch_map_len

    # computes total packet length in bytes
    total_len = _round_up(7 + branch_map_len) / 8

    # checks out if the computed length corresponds to the one of the payload
    if total_len != len(payload) / 8:  # 1st payload type
        # checks if delta address mode is enabled
        if current_ioptions == Ioptions.DELTA_ADDRESS:
            # computing the compressed address length
            payload_len = len(payload)
            known_fields_len = 10 + branch_map_len + 2**CALL_COUNTER_SIZE
            # adds time and/or context length
            if NO_TIME == 0:
                # TODO
                # increases known_fields_length
                pass
            if NO_CONTEXT == 0:
                # TODO
                # increases known_fields_length
                pass
            address_len, padding_len = _find_address_len(
                payload_len, known_fields_len
            )

            extendedAddr = _extend_with_sign(
                payload[-(current_index + address_len) : -current_index],
                XLEN + 1,
            )
            twoCompAddr = _twos_complement(extendedAddr)
            packet.setAddress(twoCompAddr)
            current_index += address_len
        else:
            packet.setAddress(
                int(payload[-(current_index + XLEN) : -current_index], 2)
            )
            current_index += XLEN

        packet.setNotify(
            int(payload[-(current_index + 1) : -current_index], 2)
        )
        current_index += 1
        packet.setUpdiscon(
            int(payload[-(current_index + 1) : -current_index], 2)
        )
        current_index += 1
        packet.setIrreport(
            int(payload[-(current_index + 1) : -current_index], 2)
        )
        current_index += 1
        packet.setIrdepth(
            int(
                payload[
                    -(current_index + 2**CALL_COUNTER_SIZE) : -current_index
                ],
                2,
            )
        )
    return packet


def parse_packet(payload: str) -> Packet:
    """selects the right function to parse a packet"""
    format = int(payload[-2:], 2)  # extracts packet format
    # match case to select the different packet types
    match format:
        case 3:
            subformat = int(payload[-4:-2], 2)  # extracts subformat
            # selects the right subformat
            match subformat:
                case 0:
                    return _parse_format3_subformat0(payload)
                case 1:
                    return _parse_format3_subformat1(payload)
                case 2:
                    return _parse_format3_subformat2(payload)
                case 3:
                    return _parse_format3_subformat3(payload)
                case _:
                    print("Error: wrong subformat")
        case 2:
            return _parse_format2(payload)
        case 1:
            return _parse_format1(payload)
        case 0:
            # TODO
            pass
        case _:
            print("Error: not valid packet type")


def parse_packets(path: str) -> list[Packet]:
    """processes the binary file to extract the packets"""
    packets: list[Packet] = []  # packets obtained are stored in a list

    # loads the binary file and reads one chunk at a time
    with open(path, "rb") as file:  # opens file in read mode as binary
        while chunk := file.read(CHUNK_SIZE):  # reads file chunk by chunk
            # each chunk is converted to text
            packet_bits = _convert_line(chunk)
            # from each packet is extracted the payload
            payload = _extract_payload(packet_bits)
            # processes the payload to create the packet
            packet = parse_packet(payload)
            # stores packet into a list
            packets.append(packet)

    # outputs the packets list as result
    return packets
