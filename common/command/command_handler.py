from abc import ABC, abstractmethod
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.command.command import Command
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator


class CommandHandler(ABC):
    def __init__(self, postgres_transactional_event_store: PostgresTransactionalEventStore, mongo_transactional_projection_operator: MongoTransactionalProjectionOperator):
        self._postgres_transactional_event_store = postgres_transactional_event_store
        self._mongo_transactional_projection_operator = mongo_transactional_projection_operator

    @abstractmethod
    async def handle_command(self, command: Command) -> None:
        pass