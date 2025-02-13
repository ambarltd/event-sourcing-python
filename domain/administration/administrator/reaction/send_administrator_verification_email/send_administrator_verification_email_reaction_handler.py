from datetime import datetime

from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.reaction.reaction_handler import ReactionHandler
from common.event.event import Event
from common.util.id_generator import IdGenerator
from common.util.email_sender import EmailSender
from domain.administration.administrator.aggregate.administrator import Administrator
from domain.administration.administrator.event.administrator_signed_up import AdministratorSignedUp
from domain.administration.administrator.event.administrator_email_verification_sent import AdministratorEmailVerificationSent


class SendAdministratorVerificationEmailReactionHandler(ReactionHandler):
    def __init__(
        self,
        postgres_transactional_event_store: PostgresTransactionalEventStore,
        mongo_transactional_projection_operator: MongoTransactionalProjectionOperator,
        email_sender: EmailSender,
    ):
        super().__init__(postgres_transactional_event_store, mongo_transactional_projection_operator)
        self._email_sender = email_sender

    async def react(self, event: Event) -> None:
        if not isinstance(event, AdministratorSignedUp):
            return

        reaction_event_id = IdGenerator.generate_deterministic_id(
            f"UniqueReaction:Administration_Administrator_SendAdministratorVerificationEmail:{event.aggregate_id}"
        )
        if await self._postgres_transactional_event_store.does_event_already_exist(reaction_event_id):
            return

        aggregate_data = await self._postgres_transactional_event_store.find_aggregate(event.aggregate_id, Administrator)
        verification_code = aggregate_data.aggregate.verification_code

        if not isinstance(verification_code, str):
            raise RuntimeError("No verification code found for administrator")

        html_content = f"""
        <h2>Welcome to Our Platform!</h2>
        <p>Hello {event.first_name},</p>
        <p>Thank you for signing up. Please verify your email address by entering the following code:</p>
        <h3 style="font-size: 24px; letter-spacing: 5px; background-color: #f5f5f5; padding: 10px; text-align: center;">
            {verification_code}
        </h3>
        <p>If you didn't request this verification, please ignore this email.</p>
        <br>
        <p>Best regards,<br>Your Platform Team</p>
        """

        sent_from = await self._email_sender.send_email_to_administrator_and_return_sent_from(
            to_email=event.email,
            subject="Verify Your Email Address",
            html_content=html_content
        )

        sent_event = AdministratorEmailVerificationSent(
            event_id=reaction_event_id,
            aggregate_id=event.aggregate_id,
            aggregate_version=event.aggregate_version + 1,
            correlation_id=event.correlation_id,
            causation_id=event.event_id,
            recorded_on=datetime.utcnow(),
            code=verification_code,
            sent_from=sent_from,
            sent_to=event.email,
            email_contents=html_content
        )

        await self._postgres_transactional_event_store.save_event(sent_event)