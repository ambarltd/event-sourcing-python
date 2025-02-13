import os

from common.util.email_sender import EmailSender
from common.util.postgres_connection_pool import PostgresConnectionPool
from common.util.mongo_session_pool import MongoSessionPool
from common.serialized_event.deserializer import Deserializer
from common.serialized_event.serializer import Serializer
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.util.mongo_initializer import MongoInitializer
from common.util.postgres_initializer import PostgresInitializer
from domain.administration.administrator.command.sign_up_as_administrator.sign_up_as_administrator_command_controller import SignUpAsAdministratorCommandController
from domain.administration.administrator.command.sign_up_as_administrator.sign_up_as_administrator_command_handler import SignUpAsAdministratorCommandHandler
from domain.administration.administrator.command.verify_administrator_email.verify_administrator_email_command_controller import \
    VerifyAdministratorEmailCommandController
from domain.administration.administrator.command.verify_administrator_email.verify_administrator_email_command_handler import \
    VerifyAdministratorEmailCommandHandler
from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_and_verification_code_repository import \
    AdministratorAndVerificationCodeRepository
from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_id_from_verification_code import \
    AdministratorIdFromVerificationCode
from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_id_from_verification_code_projection_controller import \
    AdministratorIdFromVerificationCodeProjectionController
from domain.administration.administrator.projection.administrator_id_from_verification_code.administrator_id_from_verification_code_projection_handler import \
    AdministratorIdFromVerificationCodeProjectionHandler
from domain.administration.administrator.reaction.send_administrator_verification_email.send_administrator_verification_email_reaction_controller import \
    SendAdministratorVerificationEmailReactionController
from domain.administration.administrator.reaction.send_administrator_verification_email.send_administrator_verification_email_reaction_handler import \
    SendAdministratorVerificationEmailReactionHandler


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
        self.email_sender = EmailSender(
            smtp_host=os.getenv('SMTP_HOST'),
            smtp_port=int(os.getenv('SMTP_PORT')),
            smtp_username=os.getenv('SMTP_USERNAME'),
            smtp_password=os.getenv('SMTP_PASSWORD'),
            smtp_from_email_for_administrators=os.getenv('SMTP_FROM_EMAIL_FOR_ADMINISTRATORS')
        );

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


    def administration_administrator_command_administrator_sign_up_as_administrator_command_controller(self):
        return SignUpAsAdministratorCommandController(
            event_store=self._postgres_transactional_event_store,
            mongo_operator=self._mongo_transactional_projection_operator,
            sign_up_as_administrator_command_handler=SignUpAsAdministratorCommandHandler(
                postgres_transactional_event_store=self._postgres_transactional_event_store,
                mongo_transactional_projection_operator=self._mongo_transactional_projection_operator
            )
        )


    def administration_administrator_command_verify_administrator_email_command_controller(self):
        return VerifyAdministratorEmailCommandController(
            event_store=self._postgres_transactional_event_store,
            mongo_operator=self._mongo_transactional_projection_operator,
            verify_administrator_email_command_handler=VerifyAdministratorEmailCommandHandler(
                postgres_transactional_event_store=self._postgres_transactional_event_store,
                mongo_transactional_projection_operator=self._mongo_transactional_projection_operator,
                administrator_id_from_verification_code=AdministratorIdFromVerificationCode(
                    AdministratorAndVerificationCodeRepository(
                        mongo_operator=self._mongo_transactional_projection_operator
                    )
                )

            )
        )


    def administration_administrator_projection_administrator_id_from_verification_code_projection_controller(self):
        return AdministratorIdFromVerificationCodeProjectionController(
            mongo_operator=self._mongo_transactional_projection_operator,
            deserializer=self.shared_container.deserializer,
            administrator_id_from_verification_code_projection_handler=AdministratorIdFromVerificationCodeProjectionHandler(
                verification_code_repository=AdministratorAndVerificationCodeRepository(
                    self._mongo_transactional_projection_operator
                )
            )
        )



    def administration_administrator_reaction_send_administrator_verification_email_controller(self):
        return SendAdministratorVerificationEmailReactionController(
            event_store=self._postgres_transactional_event_store,
            mongo_operator=self._mongo_transactional_projection_operator,
            deserializer=self.shared_container.deserializer,
            send_administrator_verification_email_reaction_handler=SendAdministratorVerificationEmailReactionHandler(
                postgres_transactional_event_store=self._postgres_transactional_event_store,
                mongo_transactional_projection_operator=self._mongo_transactional_projection_operator,
                email_sender=self.shared_container.email_sender
            )
        )
