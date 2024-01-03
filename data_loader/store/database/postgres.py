"""Database..."""

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, Tuple, Type, TypeVar, Union

from base.base_accessor import BaseAccessor
from core.settings import PostgresSettings
from sqlalchemy import (
    DATETIME,
    TIMESTAMP,
    Delete,
    MetaData,
    Result,
    Select,
    UpdateBase,
    ValuesBase,
    delete,
    func,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept, MappedAsDataclass

Query = Union[ValuesBase, Select, UpdateBase, Delete]
Model = TypeVar("Model", bound=DeclarativeAttributeIntercept)
Field_table = Tuple[str, int]
Field_names = str
Sorted_direction = Literal["ASC", "DESC"]
Sorted_order = Dict[Field_names, Sorted_direction]


@dataclass
class Base(MappedAsDataclass, DeclarativeBase):
    """Setting up metadata.

    In particular, we specify a schema for storing tables.
    """

    metadata = MetaData(
        schema=PostgresSettings().postgres_schema,
        quote_schema=True,
    )
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    created: Mapped[DATETIME] = mapped_column(
        TIMESTAMP,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    modified: Mapped[DATETIME] = mapped_column(
        TIMESTAMP,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        init=False,
    )
    ic(metadata.schema)

    def __repr__(self):
        """Redefinition.

        Returns:
            object: new instance name
        """
        return "{class_name}(id={id})".format(
            id=self.id,
            class_name=self.__class__.__name__,
        )

    __str__ = __repr__


class Postgres(BaseAccessor):
    """Description of the rules for connecting.

    PostgresSQL to the Fast-Api application.
    """

    _engine: Optional[AsyncEngine] = None
    _db: Optional[Type[DeclarativeBase]] = None
    session: Optional[AsyncSession] = None
    settings: Optional[PostgresSettings] = None

    async def connect(self):
        """Configuring the connection to the database."""
        self.settings = PostgresSettings()
        self._db = Base
        self._engine = create_async_engine(
            self.settings.dsn(True),
            echo=False,
            future=True,
        )
        self.session = AsyncSession(self._engine, expire_on_commit=False)
        self.logger.info("Connected to Postgres, {dsn}".format(dsn=self.settings.dsn()))

    async def disconnect(self):
        """Closing the connection to the database."""
        if self._engine:
            await self._engine.dispose()
        self.logger.info("Disconnected from Postgres")

    @staticmethod
    def get_query_insert(model: Model, **insert_data) -> Query:
        """Get query inserted.

        Args:
            model: Table model
            insert_data: fields for insert dict[name, value]

        Returns:
        object: query
        """
        return insert(model).values(**insert_data)

    @staticmethod
    def get_query_update_by_field(
        model: Model, field_name: str, field_value: Any, **update_data
    ) -> Query:
        """Get query update records by field.

        Args:
            model: Table model
            field_name: Field names in the model
            field_value: Field values in the model
            update_data: fields for update dict[name, value]
        Returns:
            object: Query object
        """
        return (
            update(model)
            .values(**update_data)
            .where(text(f"{field_name} = '{field_value}'"))
        )

    @staticmethod
    def get_query_delete_by_field(
        model: Model, field_name: str, field_value: Any
    ) -> Delete:
        """Get query delete records in Table.

        Args:
            model: Table model
            field_name: Field names in the model
            field_value: Field values in the model

        Returns:
            object: Query object
        """
        return delete(model).where(text(f"{field_name} = '{field_value}'"))

    @staticmethod
    def get_query_select_by_field(
        model: Model, field_name: str, field_value: Any
    ) -> Query:
        """Get a query by field name.

        Args:
            model: Table model
            field_name: Field names in the model
            field_value: Field values in the model

        Returns:
            object: Query object
        """
        return select(model).where(
            text(f"{model.__tablename__}.{field_name} = '{field_value}'")
        )

    async def query_execute(self, query: Query) -> Result[Any]:
        """Query execute.

        Args:
            query: CRUD query for Database

        Returns:
              Any: result of query
        """
        async with self.app.postgres.session.begin().session as session:
            result = await session.execute(query)
            await session.commit()
            return result

    async def query_executes(self, *query: Query) -> list[Result[Any]]:
        """Query executes.

        Args:
            query: CRUD query for Database

        Returns:
              Any: result of query
        """
        async with self.app.postgres.session as session:
            result = [await session.execute(q) for q in query]
            await session.commit()
            return result

    @staticmethod
    def get_query_filter(
        model: Model, page: int = 0, size: int = 10, sort_params: Sorted_order = None
    ) -> Query:
        """Get query filter by sorted parameters.

        Args:
            model: Model table
            page: number of page
            size: page size
            sort_params: sort parameters

        Returns:
            query: Query object
        """
        query = select(model).limit(size).offset(page * size)
        query_sort = ", ".join(
            [f"{name} {value}" for name, value in sort_params.items()]
        )
        return query.order_by(text(query_sort))

    async def get_random(self, model: Model, count: int = 1) -> Result[Any]:
        """Get query filter by sorted parameters.

         Args:
             model: Model table
             count: count returned from get_random
        Returns:
               Any: result of query
        """
        return await self.query_execute(
            select(model).order_by(func.random()).limit(count)
        )
