from app.common.errors import AppError


class MessageRoleError(Exception):
    def __init__(self, role: str, reason: str):
        self.role = role
        self.reason = reason
        super().__init__(f"Message has invalid role '{role}': {reason}")


class UnsupportedMessageContentError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Message has unsupported content type: {reason}")


class BadMessageOrderError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Bas message order in chat: {reason}")


class ChatEmptyError(Exception):
    def __init__(self) -> None:
        super().__init__("cannot generate with an empty chat")