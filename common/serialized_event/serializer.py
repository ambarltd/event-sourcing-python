from datetime import datetime
import json
import pytz

from domain.administration.administrator.event.administrator_email_verification_sent import \
    AdministratorEmailVerificationSent
from domain.administration.administrator.event.administrator_email_verified import AdministratorEmailVerified
from domain.administration.administrator.event.administrator_signed_up import AdministratorSignedUp
from common.event.event import Event
from common.serialized_event.serialized_event import SerializedEvent

class Serializer:
    def serialize(self, event: Event) -> SerializedEvent:
        return SerializedEvent(
            event_id=event.event_id,
            aggregate_id=event.aggregate_id,
            aggregate_version=event.aggregate_version,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            recorded_on=self._format_datetime(event.recorded_on),
            event_name=self._determine_event_name(event),
            json_payload=self._create_json_payload(event),
            json_metadata='{}'
        )

    def _format_datetime(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        else:
            dt = dt.astimezone(pytz.UTC)
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')

    def _determine_event_name(self, event: Event) -> str:
        if isinstance(event, AdministratorSignedUp):
            return 'Administrator_AdministratorSignedUp'
        if isinstance(event, AdministratorEmailVerificationSent):
            return 'Administrator_AdministratorEmailVerificationSent'
        if isinstance(event, AdministratorEmailVerified):
            return 'Administrator_AdministratorEmailVerified'
        raise ValueError(f"Unknown event type: {event.__class__.__name__}")

    def _create_json_payload(self, event: Event) -> str:
        if isinstance(event, AdministratorSignedUp):
            payload = {
                'firstName': event.first_name,
                'lastName': event.last_name,
                'email': event.email,
                'hashedPassword': event.hashed_password
            }
        elif isinstance(event, AdministratorEmailVerificationSent):
            payload = {
                'code': event.code,
                'sentFrom': event.sent_from,
                'sentTo': event.sent_to,
                'emailContents': event.email_contents
            }
        elif isinstance(event, AdministratorEmailVerified):
            payload = {
                'withCode': event.with_code
            }
        else:
            raise ValueError(f"Unknown event type: {event.__class__.__name__}")

        return json.dumps(payload)