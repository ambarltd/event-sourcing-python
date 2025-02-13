from dataclasses import dataclass
from common.command.command import Command

@dataclass
class VerifyAdministratorEmailCommand(Command):
    verification_code: str