from datetime import datetime
from common.event.transformation_event import TransformationEvent
from domain.administration.administrator.aggregate.administrator import Administrator

class AdministratorEmailVerified(TransformationEvent[Administrator]):
    def __init__(
        self,
        event_id: str,
        aggregate_id: str,
        aggregate_version: int,
        correlation_id: str,
        causation_id: str,
        recorded_on: datetime,
        with_code: str
    ):
        super().__init__(
            event_id=event_id,
            aggregate_version=aggregate_version,
            aggregate_id=aggregate_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            recorded_on=recorded_on
        )
        self.with_code = with_code

    def transform_aggregate(self, aggregate: Administrator) -> Administrator:
        return Administrator(
            aggregate_id=self.aggregate_id,
            aggregate_version=self.aggregate_version,
            first_name=aggregate.first_name,
            last_name=aggregate.last_name,
            email=aggregate.email,
            is_email_verified=True,
            hashed_password=aggregate.hashed_password
        )