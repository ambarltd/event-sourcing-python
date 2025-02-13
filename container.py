import os
from common.util.postgres_connection_pool import PostgresConnectionPool
from common.util.mongo_session_pool import MongoSessionPool
from common.serialized_event.deserializer import Deserializer
from common.serialized_event.serializer import Serializer
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.util.mongo_initializer import MongoInitializer
from common.util.postgres_initializer import PostgresInitializer
from domain.administration.administrator.command.sign_up.sign_up_command_controller import SignUpCommandController
from domain.administration.administrator.command.sign_up.sign_up_command_handler import SignUpCommandHandler


class SharedContainer:
    def __init__(self):
        # Connection strings
        postgres_connection_string = f"postgresql://{os.getenv('EVENT_STORE_USER')}:{os.getenv('EVENT_STORE_PASSWORD')}@{os.getenv('EVENT_STORE_HOST')}:{os.getenv('EVENT_STORE_PORT')}/{os.getenv('EVENT_STORE_DATABASE_NAME')}"
        mongo_connection_string = f"mongodb://{os.getenv('MONGODB_PROJECTION_DATABASE_USERNAME')}:{os.getenv('MONGODB_PROJECTION_DATABASE_PASSWORD')}@{os.getenv('MONGODB_PROJECTION_HOST')}:{os.getenv('MONGODB_PROJECTION_PORT')}/{os.getenv('MONGODB_PROJECTION_DATABASE_NAME')}?authSource=admin"

        # Core services
        self.postgres_connection_pool = PostgresConnectionPool(
            connection_string=postgres_connection_string
        )
        self.mongo_session_pool = MongoSessionPool(
            connection_string=mongo_connection_string
        )
        self.serializer = Serializer()
        self.deserializer = Deserializer()

        # Initializers
        self.postgres_initializer = PostgresInitializer(
            connection_pool=self.postgres_connection_pool,
            event_store_database_name=os.getenv('EVENT_STORE_DATABASE_NAME'),
            event_store_table=os.getenv('EVENT_STORE_CREATE_TABLE_WITH_NAME'),
            replication_username=os.getenv('EVENT_STORE_CREATE_REPLICATION_USER_WITH_USERNAME'),
            replication_password=os.getenv('EVENT_STORE_CREATE_REPLICATION_USER_WITH_PASSWORD'),
            replication_publication=os.getenv('EVENT_STORE_CREATE_REPLICATION_PUBLICATION')
        )
        self.mongo_initializer = MongoInitializer(
            session_pool=self.mongo_session_pool,
            database_name=os.getenv('MONGODB_PROJECTION_DATABASE_NAME')
        )


class RequestContainer:
    def __init__(self, shared_container: SharedContainer):
        self.shared_container = shared_container

        self._postgres_transactional_event_store = PostgresTransactionalEventStore(
            connection_pool=self.shared_container.postgres_connection_pool,
            serializer=self.shared_container.serializer,
            deserializer=self.shared_container.deserializer,
            event_store_table=os.getenv('EVENT_STORE_CREATE_TABLE_WITH_NAME')
        )

        self._mongo_transactional_projection_operator = MongoTransactionalProjectionOperator(
            session_pool=self.shared_container.mongo_session_pool,
            database_name=os.getenv('MONGODB_PROJECTION_DATABASE_NAME')
        )

    def administrator_sign_up_command_controller(self):
        return SignUpCommandController(
            event_store=self._postgres_transactional_event_store,
            mongo_operator=self._mongo_transactional_projection_operator,
            sign_up_command_handler=SignUpCommandHandler(
                postgres_transactional_event_store=self._postgres_transactional_event_store
            )
        )