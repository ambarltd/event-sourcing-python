from flask import Request, Response, jsonify
from pydantic import BaseModel, Field, EmailStr
from common.command.command_controller import CommandController
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from domain.administration.administrator.command.sign_up.sign_up_command import SignUpCommand
from domain.administration.administrator.command.sign_up.sign_up_command_handler import SignUpCommandHandler

class SignUpRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class SignUpCommandController(CommandController):
    def __init__(
        self,
        event_store: PostgresTransactionalEventStore,
        mongo_operator: MongoTransactionalProjectionOperator,
        sign_up_command_handler: SignUpCommandHandler
    ):
        super().__init__(event_store, mongo_operator)
        self._sign_up_command_handler = sign_up_command_handler

    async def handle_sign_up(self, request: Request) -> tuple[Response, int]:
        request_data = SignUpRequest(**request.get_json())

        command = SignUpCommand(
            first_name=request_data.first_name,
            last_name=request_data.last_name,
            email=str(request_data.email),
            password=request_data.password
        )

        await self.process_command(command, self._sign_up_command_handler)
        return jsonify({"message": "Administrator signup successful"}), 201