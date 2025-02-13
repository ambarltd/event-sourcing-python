from flask import Request, Response, jsonify
from pydantic import BaseModel, Field
from common.command.command_controller import CommandController
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from domain.administration.administrator.command.verify_administrator_email.verify_administrator_email_command import \
    VerifyAdministratorEmailCommand
from domain.administration.administrator.command.verify_administrator_email.verify_administrator_email_command_handler import \
    VerifyAdministratorEmailCommandHandler


class VerifyAdministratorEmailRequest(BaseModel):
    verification_code: str = Field(..., min_length=10, max_length=30)


class VerifyAdministratorEmailCommandController(CommandController):
    def __init__(
            self,
            event_store: PostgresTransactionalEventStore,
            mongo_operator: MongoTransactionalProjectionOperator,
            verify_administrator_email_command_handler: VerifyAdministratorEmailCommandHandler
    ):
        super().__init__(event_store, mongo_operator)
        self._verify_administrator_email_command_handler = verify_administrator_email_command_handler

    async def handle_verify_email(self, request: Request) -> tuple[Response, int]:
        request_data = VerifyAdministratorEmailRequest(**request.get_json())

        command = VerifyAdministratorEmailCommand(
            verification_code=request_data.verification_code
        )

        await self.process_command(command, self._verify_administrator_email_command_handler)
        return jsonify({"message": "Email verification successful"}), 200