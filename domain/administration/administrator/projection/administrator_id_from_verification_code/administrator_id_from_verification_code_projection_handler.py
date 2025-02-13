from common.projection.projection_handler import ProjectionHandler
from common.event.event import Event
from domain.administration.administrator.event.administrator_signed_up import AdministratorSignedUp
from domain.administration.administrator.event.administrator_email_verified import AdministratorEmailVerified
from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_and_verification_code import \
    AdministratorAndVerificationCode
from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_and_verification_code_repository import \
    AdministratorAndVerificationCodeRepository


class AdministratorIdFromVerificationCodeProjectionHandler(ProjectionHandler):
    def __init__(self, verification_code_repository: AdministratorAndVerificationCodeRepository):
        self._verification_code_repository = verification_code_repository

    async def project(self, event: Event) -> None:
        if isinstance(event, AdministratorSignedUp):
            await self._handle_administrator_signed_up(event)
        elif isinstance(event, AdministratorEmailVerified):
            await self._handle_administrator_email_verified(event)

    async def _handle_administrator_signed_up(self, event: AdministratorSignedUp) -> None:
        await self._verification_code_repository.save(
            AdministratorAndVerificationCode(
                _id=event.aggregate_id,
                verification_code=event.verification_code
            )
        )

    async def _handle_administrator_email_verified(self, event: AdministratorEmailVerified) -> None:
        await self._verification_code_repository.delete_by_id(event.aggregate_id)