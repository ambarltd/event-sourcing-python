from datetime import datetime
from common.event.creation_event import CreationEvent
from domain.administration.administrator.aggregate.administrator import Administrator

class AdministratorSignedUp(CreationEvent[Administrator]):
    def __init__(
        self,
        event_id: str,
        aggregate_id: str,
        aggregate_version: int,
        correlation_id: str,
        causation_id: str,
        recorded_on: datetime,
        first_name: str,
        last_name: str,
        email: str,
        hashed_password: str,
        verification_code: str
    ):
        super().__init__(
            event_id=event_id,
            aggregate_id=aggregate_id,
            aggregate_version=aggregate_version,
            correlation_id=correlation_id,
            causation_id=causation_id,
            recorded_on=recorded_on
        )
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hashed_password = hashed_password
        self.verification_code = verification_code

    def create_aggregate(self) -> Administrator:
        return Administrator(
            aggregate_id=self.aggregate_id,
            aggregate_version=self.aggregate_version,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            is_email_verified=False,
            hashed_password=self.hashed_password,
            verification_code=self.verification_code
        )