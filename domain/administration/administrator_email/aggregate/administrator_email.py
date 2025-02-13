from dataclasses import dataclass
from common.aggregate.aggregate import Aggregate


@dataclass
class AdministratorEmail(Aggregate):
    lowercase_email: str
    administrator_id: str


    def __init__(self, aggregate_id: str, aggregate_version: int, lowercase_email: str, administrator_id: str):
        super().__init__(aggregate_id, aggregate_version)
        self.lowercase_email = lowercase_email
        self.administrator_id = administrator_id
