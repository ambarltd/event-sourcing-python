from flask import Response

from common.ambar.ambar_http_request import AmbarHttpRequest
from common.ambar.ambar_response_factory import AmbarResponseFactory
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.serialized_event.deserializer import Deserializer
from common.util.logger import log
from common.reaction.reaction_handler import ReactionHandler


class ReactionController:
    def __init__(
            self,
            postgres_transactional_event_store: PostgresTransactionalEventStore,
            mongo_transactional_projection_operator: MongoTransactionalProjectionOperator,
            deserializer: Deserializer
    ):
        self._postgres_transactional_event_store = postgres_transactional_event_store
        self._mongo_transactional_projection_operator = mongo_transactional_projection_operator
        self._deserializer = deserializer

    async def process_reaction_http_request(
            self,
            ambar_http_request: AmbarHttpRequest,
            reaction_handler: ReactionHandler
    ) -> tuple[Response, int]:
        try:
            log.debug(
                f"Starting to process reaction for event name: {ambar_http_request.payload.event_name} "
                f"using handler: {reaction_handler.__class__.__name__}"
            )

            await self._postgres_transactional_event_store.begin_transaction()
            await self._mongo_transactional_projection_operator.start_transaction()

            await reaction_handler.react(
                self._deserializer.deserialize(ambar_http_request.payload)
            )

            await self._postgres_transactional_event_store.commit_transaction()
            await self._mongo_transactional_projection_operator.commit_transaction()

            await self._postgres_transactional_event_store.abort_dangling_transactions_and_return_connection_to_pool()
            await self._mongo_transactional_projection_operator.abort_dangling_transactions_and_return_session_to_pool()

            log.debug(
                f"Reaction successfully processed for event name: {ambar_http_request.payload.event_name} "
                f"using handler: {reaction_handler.__class__.__name__}"
            )
            return Response(AmbarResponseFactory.success_response(), content_type='application/json'), 200

        except Exception as error:
            if isinstance(error, ValueError) and str(error).startswith('Unknown event type'):
                await self._postgres_transactional_event_store.abort_dangling_transactions_and_return_connection_to_pool()
                await self._mongo_transactional_projection_operator.abort_dangling_transactions_and_return_session_to_pool()

                log.debug(
                    f"Unknown event in reaction ignored for event name: {ambar_http_request.payload.event_name} "
                    f"using handler: {reaction_handler.__class__.__name__}"
                )
                return Response(AmbarResponseFactory.success_response(), content_type='application/json'), 200

            await self._postgres_transactional_event_store.abort_dangling_transactions_and_return_connection_to_pool()
            await self._mongo_transactional_projection_operator.abort_dangling_transactions_and_return_session_to_pool()

            log.error('Exception in ProcessReactionHttpRequest:', error=error)
            return Response(AmbarResponseFactory.retry_response(error), content_type='application/json'), 200
