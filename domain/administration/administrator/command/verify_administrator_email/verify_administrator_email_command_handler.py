from datetime import datetime
from common.command.command_handler import CommandHandler
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.util.id_generator import IdGenerator
from domain.administration.administrator.aggregate.administrator import Administrator
from domain.administration.administrator.command.verify_administrator_email.verify_administrator_email_command import VerifyAdministratorEmailCommand
from domain.administration.administrator.event.administrator_email_verified import AdministratorEmailVerified
from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_id_from_verification_code import \
    AdministratorIdFromVerificationCode


class VerifyAdministratorEmailCommandHandler(CommandHandler):
    def __init__(
        self,
        postgres_transactional_event_store: PostgresTransactionalEventStore,
        mongo_transactional_projection_operator: MongoTransactionalProjectionOperator,
        administrator_id_from_verification_code: AdministratorIdFromVerificationCode
    ):
        super().__init__(postgres_transactional_event_store, mongo_transactional_projection_operator)
        self._administrator_id_from_verification_code = administrator_id_from_verification_code

    async def handle_command(self, command: VerifyAdministratorEmailCommand) -> None:
        administrator_id = await self._administrator_id_from_verification_code.administrator_id_from_verification_code(command.verification_code)
        if not isinstance(administrator_id, str):
            raise ValueError("Invalid code")

        aggregate_data = await self._postgres_transactional_event_store.find_aggregate(administrator_id)
        administrator = aggregate_data.aggregate

        if not isinstance(administrator, Administrator):
            raise ValueError("Administrator not found")

        if administrator.is_email_verified:
            raise ValueError("Administrator email already verified")

        event_id = IdGenerator.generate_random_id()

        admin_email_verified = AdministratorEmailVerified(
            event_id=event_id,
            aggregate_id=administrator.aggregate_id,
            aggregate_version=administrator.aggregate_version + 1,
            correlation_id=aggregate_data.correlation_id_of_last_event,
            causation_id=aggregate_data.event_id_of_last_event,
            recorded_on=datetime.utcnow(),
            with_code=command.verification_code
        )

        await self._postgres_transactional_event_store.save_event(admin_email_verified)