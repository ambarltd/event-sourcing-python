from dataclasses import dataclass
from common.aggregate.aggregate import Aggregate

@dataclass
class AdministratorEmail(Aggregate):
    administrator_id: str
    lowercase_email: str


    def __init__(self, aggregate_id: str, aggregate_version: int, administrator_id: str, lowercase_email: str):
        super().__init__(aggregate_id, aggregate_version)
        self.administrator_id = administrator_id
        self.lowercase_email = lowercase_email