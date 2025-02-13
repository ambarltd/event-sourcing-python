from typing import Optional

from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_and_verification_code_repository import \
    AdministratorAndVerificationCodeRepository


class AdministratorIdFromVerificationCode:
    def __init__(self, administrator_and_verification_code_repository: AdministratorAndVerificationCodeRepository):
        self._administrator_and_verification_code_repository = administrator_and_verification_code_repository

    async def administrator_id_from_verification_code(self, verification_code: str) -> Optional[str]:
        administrator_and_verification_code = await self._administrator_and_verification_code_repository.find_one_by_verification_code(verification_code=verification_code)

        if isinstance(administrator_and_verification_code, AdministratorIdFromVerificationCode):
            return administrator_and_verification_code._id

        return None