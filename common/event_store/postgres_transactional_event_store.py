from typing import TypeVar, Optional, List, Type

from common.event_store.aggregate_does_not_exist import AggregateDoesNotExist
from common.util.postgres_connection_pool import PostgresConnectionPool
from common.serialized_event.serializer import Serializer
from common.serialized_event.deserializer import Deserializer
from common.serialized_event.serialized_event import SerializedEvent
from common.event.event import Event
from common.event.creation_event import CreationEvent
from common.event.transformation_event import TransformationEvent
from common.aggregate.aggregate import Aggregate
from common.util.logger import log
from common.event_store.aggregate_and_event_ids_in_last_event import AggregateAndEventIdsInLastEvent

T = TypeVar('T', bound=Aggregate)

class PostgresTransactionalEventStore:
    def __init__(
        self,
        connection_pool: PostgresConnectionPool,
        serializer: Serializer,
        deserializer: Deserializer,
        event_store_table: str
    ):
        self._connection_pool = connection_pool
        self._serializer = serializer
        self._deserializer = deserializer
        self._event_store_table = event_store_table
        self._connection = None
        self._active_transaction = False

    async def begin_transaction(self) -> None:
        if self._connection or self._active_transaction:
            raise RuntimeError('Connection or transaction already active!')

        try:
            self._connection = await self._connection_pool.open_connection()
            self._connection.cursor().execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            self._active_transaction = True
        except Exception as error:
            max_len = 500
            error_message = str(error)
            raise RuntimeError(
                'Failed to start transaction with ' +
                (error_message[:max_len] if len(error_message) > max_len else error_message)
            )

    async def find_aggregate(self, aggregate_id: str, aggregate_type: Type[T]) -> AggregateAndEventIdsInLastEvent[T]:
        if not self._active_transaction:
            raise RuntimeError('Transaction must be active to perform find aggregate operations!')

        serialized_events = await self._find_all_serialized_events_by_aggregate_id(aggregate_id)
        events = [self._deserializer.deserialize(e) for e in serialized_events]

        if not events:
            raise AggregateDoesNotExist()

        creation_event = events[0]
        transformation_events = events[1:]

        if not isinstance(creation_event, CreationEvent):
            raise RuntimeError('First event is not a creation event')

        aggregate = creation_event.create_aggregate()
        event_id_of_last_event = creation_event.event_id
        correlation_id_of_last_event = creation_event.correlation_id

        if not isinstance(aggregate, aggregate_type):
            raise RuntimeError('Created aggregate type does not match expected type')

        for transformation_event in transformation_events:
            if not isinstance(transformation_event, TransformationEvent):
                raise RuntimeError('Event is not a transformation event')
            aggregate = transformation_event.transform_aggregate(aggregate)
            event_id_of_last_event = transformation_event.event_id
            correlation_id_of_last_event = transformation_event.correlation_id

            if not isinstance(aggregate, aggregate_type):
                raise RuntimeError('Transformed aggregate type does not match expected type')

        return AggregateAndEventIdsInLastEvent(
            aggregate=aggregate,
            event_id_of_last_event=event_id_of_last_event,
            correlation_id_of_last_event=correlation_id_of_last_event
        )

    async def save_event(self, event: Event) -> None:
        if not self._active_transaction:
            raise RuntimeError('Transaction must be active to perform save operations!')

        await self._save_serialized_event(self._serializer.serialize(event))

    async def does_event_already_exist(self, event_id: str) -> bool:
        if not self._active_transaction:
            raise RuntimeError('Transaction must be active to perform find event operations!')

        event = await self._find_serialized_event_by_event_id(event_id)
        return event is not None

    async def commit_transaction(self) -> None:
        if not self._active_transaction:
            raise RuntimeError('Transaction must be active to commit!')

        try:
            if self._connection:
                self._connection.commit()
            self._active_transaction = False
        except Exception as error:
            raise RuntimeError(f"Failed to commit transaction: {error}")

    async def abort_dangling_transactions_and_return_connection_to_pool(self) -> None:
        if self._active_transaction:
            try:
                if self._connection:
                    self._connection.rollback()
                self._active_transaction = False
            except Exception as error:
                log.error('Failed to rollback PG transaction', error=error)

        if self._connection:
            try:
                await self._connection_pool.return_connection(self._connection)
                self._connection = None
            except Exception as error:
                log.error('Failed to release PG connection', error=error)

    async def _find_all_serialized_events_by_aggregate_id(self, aggregate_id: str) -> List[SerializedEvent]:
        if not self._connection:
            raise RuntimeError('No active connection')

        sql = f"""
            SELECT id, event_id, aggregate_id, causation_id, correlation_id,
                   aggregate_version, json_payload, json_metadata, recorded_on, event_name
            FROM {self._event_store_table}
            WHERE aggregate_id = %s
            ORDER BY aggregate_version ASC
        """

        try:
            cursor = self._connection.cursor()
            cursor.execute(sql, (aggregate_id,))
            rows = cursor.fetchall()
            return [self._map_row_to_serialized_event(row) for row in rows]
        except Exception as error:
            raise RuntimeError(f"Failed to fetch events for aggregate: {aggregate_id}: {error}")

    async def _save_serialized_event(self, serialized_event: SerializedEvent) -> None:
        if not self._connection:
            raise RuntimeError('No active connection')

        sql = f"""
            INSERT INTO {self._event_store_table} (
                event_id, aggregate_id, causation_id, correlation_id,
                aggregate_version, json_payload, json_metadata, recorded_on, event_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            serialized_event.event_id,
            serialized_event.aggregate_id,
            serialized_event.causation_id,
            serialized_event.correlation_id,
            serialized_event.aggregate_version,
            serialized_event.json_payload,
            serialized_event.json_metadata,
            serialized_event.recorded_on,
            serialized_event.event_name
        )

        try:
            cursor = self._connection.cursor()
            cursor.execute(sql, values)
        except Exception as error:
            raise RuntimeError(f"Failed to save event: {serialized_event.event_id}: {error}")

    async def _find_serialized_event_by_event_id(self, event_id: str) -> Optional[SerializedEvent]:
        if not self._connection:
            raise RuntimeError('No active connection')

        sql = f"""
            SELECT id, event_id, aggregate_id, causation_id, correlation_id,
                   aggregate_version, json_payload, json_metadata, recorded_on, event_name
            FROM {self._event_store_table}
            WHERE event_id = %s
        """

        try:
            cursor = self._connection.cursor()
            cursor.execute(sql, (event_id,))
            row = cursor.fetchone()
            return self._map_row_to_serialized_event(row) if row else None
        except Exception as error:
            raise RuntimeError(f"Failed to fetch event: {event_id}: {error}")

    def _map_row_to_serialized_event(self, row) -> SerializedEvent:
        return SerializedEvent(
            id=row[0],
            event_id=row[1],
            aggregate_id=row[2],
            causation_id=row[3],
            correlation_id=row[4],
            aggregate_version=row[5],
            json_payload=row[6],
            json_metadata=row[7],
            recorded_on=row[8],
            event_name=row[9]
        )