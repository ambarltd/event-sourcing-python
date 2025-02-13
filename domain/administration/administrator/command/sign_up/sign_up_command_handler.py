from datetime import datetime
import hashlib
import bcrypt
from common.command.command_handler import CommandHandler
from common.util.id_generator import IdGenerator
from domain.administration.administrator.command.sign_up.sign_up_command import SignUpCommand
from domain.administration.administrator.event.administrator_signed_up import AdministratorSignedUp

def _generate_administrator_email_id(email: str) -> str:
    normalized_email = email.lower()
    return IdGenerator.generate_deterministic_id(f"administrator_email:{normalized_email}")


class SignUpCommandHandler(CommandHandler):
    async def handle_command(self, command: SignUpCommand) -> None:
        administrator_id = IdGenerator.generate_random_id()
        event_id = IdGenerator.generate_random_id()

        administrator_email_id = _generate_administrator_email_id(command.email)
        try:
            await self._postgres_transactional_event_store.find_aggregate(administrator_email_id)
            raise ValueError("Email is already registered")
        except RuntimeError:
            pass

        hashed_password = bcrypt.hashpw(command.password.encode(), bcrypt.gensalt()).decode()

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
            hashed_password=hashed_password
        )

        await self._postgres_transactional_event_store.save_event(admin_signed_up)

