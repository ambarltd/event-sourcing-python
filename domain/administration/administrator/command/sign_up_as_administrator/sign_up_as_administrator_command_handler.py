from datetime import datetime
import bcrypt
from common.command.command_handler import CommandHandler
from common.util.id_generator import IdGenerator
from domain.administration.administrator.command.sign_up_as_administrator.sign_up_as_administrator_command import SignUpAsAdministratorCommand
from domain.administration.administrator.event.administrator_signed_up import AdministratorSignedUp
import secrets
import string


class SignUpAsAdministratorCommandHandler(CommandHandler):
    async def handle_command(self, command: SignUpAsAdministratorCommand) -> None:
        administrator_id = IdGenerator.generate_random_id()
        event_id = IdGenerator.generate_random_id()

        hashed_password = bcrypt.hashpw(command.password.encode(), bcrypt.gensalt()).decode()
        verification_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(15))  # 15 alphanumeric characters ~= 2^90 possibilities

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