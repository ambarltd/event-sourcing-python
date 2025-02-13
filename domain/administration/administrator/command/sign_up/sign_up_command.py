from dataclasses import dataclass
from common.command.command import Command

@dataclass
class SignUpCommand(Command):
    first_name: str
    last_name: str
    email: str
    password: str  # This is the raw password that will be hashed in the handler