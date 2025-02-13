import json
from datetime import datetime

from domain.administration.administrator.event.administrator_email_verification_sent import \
    AdministratorEmailVerificationSent
from domain.administration.administrator.event.administrator_email_verified import AdministratorEmailVerified
from domain.administration.administrator.event.administrator_signed_up import AdministratorSignedUp
from common.event.event import Event
from common.serialized_event.serialized_event import SerializedEvent

class Deserializer:
    def __init__(self):
        self._event_types = {
            'Administrator_AdministratorSignedUp': AdministratorSignedUp,
            'Administrator_AdministratorEmailVerificationSent': AdministratorEmailVerificationSent,
            'Administrator_AdministratorEmailVerified': AdministratorEmailVerified,
        }

    def deserialize(self, serialized_event: SerializedEvent) -> Event:
        event_class = self._event_types.get(serialized_event.event_name)
        if not event_class:
            raise ValueError(f"Unknown event type: {serialized_event.event_name}")

        recorded_on = self._parse_datetime(serialized_event.recorded_on)
        payload = json.loads(serialized_event.json_payload)

        if event_class == AdministratorSignedUp:
            return AdministratorSignedUp(
                event_id=serialized_event.event_id,
                aggregate_id=serialized_event.aggregate_id,
                aggregate_version=serialized_event.aggregate_version,
                correlation_id=serialized_event.correlation_id,
                causation_id=serialized_event.causation_id,
                recorded_on=recorded_on,
                first_name=payload['firstName'],
                last_name=payload['lastName'],
                email=payload['email'],
                hashed_password=payload['hashedPassword']
            )
        elif event_class == AdministratorEmailVerificationSent:
            return AdministratorEmailVerificationSent(
                event_id=serialized_event.event_id,
                aggregate_id=serialized_event.aggregate_id,
                aggregate_version=serialized_event.aggregate_version,
                correlation_id=serialized_event.correlation_id,
                causation_id=serialized_event.causation_id,
                recorded_on=recorded_on,
                code=payload['code'],
                sent_from=payload['sentFrom'],
                sent_to=payload['sentTo'],
                email_contents=payload['emailContents']
            )
        elif event_class == AdministratorEmailVerified:
            return AdministratorEmailVerified(
                event_id=serialized_event.event_id,
                aggregate_id=serialized_event.aggregate_id,
                aggregate_version=serialized_event.aggregate_version,
                correlation_id=serialized_event.correlation_id,
                causation_id=serialized_event.causation_id,
                recorded_on=recorded_on,
                with_code=payload['withCode']
            )
        else:
            raise ValueError(f"Unknown event type: {serialized_event.event_name}")

    def _parse_datetime(self, date_str: str) -> datetime:
        if not date_str.endswith(' UTC'):
            raise ValueError(f"Invalid date format: {date_str}")
        return datetime.strptime(date_str[:-4], '%Y-%m-%d %H:%M:%S')