from datetime import datetime
import bcrypt
from common.command.command_handler import CommandHandler
from common.event_store.aggregate_does_not_exist import AggregateDoesNotExist
from common.util.id_generator import IdGenerator
from domain.administration.administrator.command.sign_up_as_administrator.sign_up_as_administrator_command import SignUpAsAdministratorCommand
from domain.administration.administrator.event.administrator_signed_up import AdministratorSignedUp
import secrets
import string

from domain.administration.administrator_email.aggregate.administrator_email import AdministratorEmail


class SignUpAsAdministratorCommandHandler(CommandHandler):
    async def handle_command(self, command: SignUpAsAdministratorCommand) -> None:
        administrator_id = IdGenerator.generate_random_id()
        event_id = IdGenerator.generate_random_id()

        administrator_email_id = self._generate_administrator_email_id(command.email)
        try:
            await self._postgres_transactional_event_store.find_aggregate(administrator_email_id, AdministratorEmail)
            raise ValueError("Email is already registered")
        except AggregateDoesNotExist:
            pass

        hashed_password = bcrypt.hashpw(command.password.encode(), bcrypt.gensalt()).decode()
        verification_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(15))  # 14 alphanumeric characters ~= 2^90 possibilities

        admin_signed_up = AdministratorSignedUp(
            event_id=event_id,
            aggregate_id=administrator_id,
            aggregate_version=1,
            correlation_id=event_id,
            causation_id=event_id,
            recorded_on=datetime.utcnow(),
            first_name=command.first_name,
            last_name=command.last_name,
            email=command.email,
            hashed_password=hashed_password,
            verification_code=verification_code
        )

        await self._postgres_transactional_event_store.save_event(admin_signed_up)

    def _generate_administrator_email_id(self, email: str) -> str:
        lowercase_email = email.lower()
        return IdGenerator.generate_deterministic_id(f"Unique:Administration_Administrator_AdministratorEmail:{lowercase_email}")
