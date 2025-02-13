from typing import Optional

from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_and_verification_code import \
    AdministratorAndVerificationCode


class AdministratorAndVerificationCodeRepository:
    COLLECTION_NAME = 'Administration_Administrator_AdministratorAndVerificationCode'

    def __init__(self, mongo_operator: MongoTransactionalProjectionOperator):
        self._mongo_operator = mongo_operator

    async def save(self, administrator_and_verification_code: AdministratorAndVerificationCode) -> None:
        await self._mongo_operator.replace_one(
            self.COLLECTION_NAME,
            {'_id': administrator_and_verification_code._id},
            {
                '_id': administrator_and_verification_code._id,
                'verification_code': administrator_and_verification_code.verification_code
            },
            {'upsert': True}
        )

    async def find_one_by_verification_code(self, verification_code: str) -> Optional[AdministratorAndVerificationCode]:
        results = await self._mongo_operator.find(
            self.COLLECTION_NAME,
            {'verification_code': verification_code}
        )
        if not results:
            return None

        doc = results[0]
        return AdministratorAndVerificationCode(
            _id=doc['_id'],
            verification_code=doc['verification_code']
        )

    async def delete_by_id(self, _id: str) -> None:
        await self._mongo_operator.replace_one(
            self.COLLECTION_NAME,
            {'_id': _id},
            {},
            {'upsert': False}
        )