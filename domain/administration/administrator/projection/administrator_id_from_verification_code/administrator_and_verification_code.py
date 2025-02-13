from dataclasses import dataclass

@dataclass
class AdministratorAndVerificationCode:
    _id: str  # This will be the administrator_id
    verification_code: str