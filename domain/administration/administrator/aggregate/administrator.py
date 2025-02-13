from dataclasses import dataclass
from typing import Optional

from common.aggregate.aggregate import Aggregate

@dataclass
class Administrator(Aggregate):
    first_name: str
    last_name: str
    email: str
    is_email_verified: bool
    hashed_password: str
    verification_code: Optional[str]


    def __init__(self, aggregate_id: str, aggregate_version: int, first_name: str, last_name: str, email: str, is_email_verified: bool, hashed_password: str, verification_code: Optional[str]):
        super().__init__(aggregate_id, aggregate_version)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_email_verified = is_email_verified
        self.hashed_password = hashed_password
        self.verification_code = verification_code