from flask import Request, Response, jsonify
from pydantic import BaseModel, Field, EmailStr
from common.command.command_controller import CommandController
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from domain.administration.administrator.command.sign_up_as_administrator.sign_up_as_administrator_command import SignUpAsAdministratorCommand
from domain.administration.administrator.command.sign_up_as_administrator.sign_up_command_handler import SignUpAsAdministratorCommandHandler

class SignUpAsAdministratorRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class SignUpAsAdministratorCommandController(CommandController):
    def __init__(
        self,
        event_store: PostgresTransactionalEventStore,
        mongo_operator: MongoTransactionalProjectionOperator,
        sign_up_as_administrator_command_handler: SignUpAsAdministratorCommandHandler
    ):
        super().__init__(event_store, mongo_operator)
        self._sign_up_as_administrator_command_handler = sign_up_as_administrator_command_handler

    async def handle_sign_up(self, request: Request) -> tuple[Response, int]:
        request_data = SignUpAsAdministratorRequest(**request.get_json())

        command = SignUpAsAdministratorCommand(
            first_name=request_data.first_name,
            last_name=request_data.last_name,
            email=str(request_data.email),
            password=request_data.password
        )

        await self.process_command(command, self._sign_up_as_administrator_command_handler)
        return jsonify({"message": "Administrator signup successful"}), 201