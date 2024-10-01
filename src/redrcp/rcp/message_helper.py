from enum import Enum

from ..rcp.enums import MessageType, MessageCode, MessageConstants


def buildCommand(message_type: MessageType, message_code: MessageCode, *args) -> bytearray:
    command_buffer = bytearray()
    command_buffer.append(MessageConstants.PREAMBLE.value)
    command_buffer.append(message_type.value)
    command_buffer.append(message_code.value)
    command_buffer += int(0).to_bytes(2, 'big')

    arg_length = 0
    for arg in args:
        if isinstance(arg, list):
            for item in arg:
                command_buffer.append(item)
                arg_length += 1
        elif isinstance(arg, bytes):
            for item in arg:
                command_buffer.append(item)
                arg_length += 1
        elif isinstance(arg, bytearray):
            command_buffer += bytearray(arg)
            arg_length += len(arg)
        elif isinstance(arg, Enum):
            command_buffer.append(arg.value)
            arg_length += 1
        else:
            command_buffer.append(arg)
            arg_length += 1

    # Set real arg length
    command_buffer[3:5] = arg_length.to_bytes(2, 'big')

    command_buffer.append(MessageConstants.ENDMARK.value)

    # Get CRC16 without preamble
    crc16_buffer = crc16(command_buffer[1:])
    command_buffer += crc16_buffer
    return command_buffer


def crc16(buffer: bytearray):
    crc = 0xFFFF
    for byte in buffer:
        crc ^= byte << 8
        for j in range(8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    crc &= 0xFFFF
    return crc.to_bytes(2, 'big')
