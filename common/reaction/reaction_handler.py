from abc import ABC, abstractmethod
from common.event.event import Event
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator


class ReactionHandler(ABC):
    def __init__(self, postgres_transactional_event_store: PostgresTransactionalEventStore, mongo_transactional_projection_operator: MongoTransactionalProjectionOperator):
        self._postgres_transactional_event_store = postgres_transactional_event_store
        self._mongo_transactional_projection_operator = mongo_transactional_projection_operator

    @abstractmethod
    async def react(self, event: Event) -> None:
        pass