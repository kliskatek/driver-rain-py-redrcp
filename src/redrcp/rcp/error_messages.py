from .enums import MessageCode, ErrorCode


class ErrorMessage:
    def __init__(self, command_code: MessageCode, error_code: ErrorCode):
        if not isinstance(command_code, MessageCode):
            raise ValueError('command_code is not of type MessageCode')
        if not isinstance(error_code, ErrorCode):
            raise ValueError('error_code is not of type ErrorCode')
        self.command_code = command_code
        self.error_code = error_code

    def __str__(self):
        return "Error code " + self.error_code.name + " to command code " + self.command_code.name
