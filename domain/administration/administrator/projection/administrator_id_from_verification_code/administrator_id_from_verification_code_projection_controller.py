from flask import Request, Response
from common.projection.projection_controller import ProjectionController
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.serialized_event.deserializer import Deserializer
from common.ambar.ambar_http_request import AmbarHttpRequest
from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_id_from_verification_code_projection_handler import AdministratorIdFromVerificationCodeProjectionHandler

class AdministratorIdFromVerificationCodeProjectionController(ProjectionController):
    def __init__(
        self,
        mongo_operator: MongoTransactionalProjectionOperator,
        deserializer: Deserializer,
        administrator_id_from_verification_code_projection_handler: AdministratorIdFromVerificationCodeProjectionHandler,
    ):
        super().__init__(mongo_operator, deserializer)
        self._administrator_id_from_verification_code_projection_handler = administrator_id_from_verification_code_projection_handler

    async def handle_projection_request(self, request: Request) -> tuple[Response, int]:
        return await self.process_projection_http_request(
            AmbarHttpRequest.model_validate(request.get_json()),
            self._administrator_id_from_verification_code_projection_handler,
            'Administration_Administrator_AdministratorIdFromVerificationCode'
        )