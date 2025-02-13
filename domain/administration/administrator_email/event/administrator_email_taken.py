from datetime import datetime
from common.event.creation_event import CreationEvent
from common.util.id_generator import IdGenerator
from domain.administration.administrator_email.aggregate.administrator_email import AdministratorEmail


class AdministratorEmailTaken(CreationEvent[AdministratorEmail]):
    def __init__(
        self,
        event_id: str,
        aggregate_id: str,
        aggregate_version: int,
        correlation_id: str,
        causation_id: str,
        recorded_on: datetime,
        lowercase_email: str,
        administrator_id: str
    ):
        super().__init__(
            event_id=event_id,
            aggregate_id=aggregate_id,
            aggregate_version=aggregate_version,
            correlation_id=correlation_id,
            causation_id=causation_id,
            recorded_on=recorded_on
        )
        self.lowercase_email = lowercase_email.lower()
        self.administrator_id = administrator_id

    def create_aggregate(self) -> AdministratorEmail:
        return AdministratorEmail(
            aggregate_id=self.aggregate_id,
            aggregate_version=self.aggregate_version,
            lowercase_email=self.lowercase_email,
            administrator_id=self.administrator_id,
        )


def administrator_email_aggregate_id_from_email(email: str) -> str:
    lowercase_email = email.lower()
    return IdGenerator.generate_deterministic_id(
        f"UniqueAggregate:Administration_Administrator_AdministratorEmail:{lowercase_email}")