import typing as t
from enum import Enum

from pydantic import GetCoreSchemaHandler
from pydantic_core import (
    CoreSchema,
    core_schema,
)


class ByName:
    """Annotated marker: (de)serialize an Enum by member name, as marshmallow did by default."""

    def __get_pydantic_core_schema__(self, source_type: type[Enum], handler: GetCoreSchemaHandler) -> CoreSchema:
        members = source_type.__members__

        def validate(value: t.Any) -> Enum:
            if isinstance(value, source_type):
                return value
            if isinstance(value, str) and value in members:
                return members[value]
            raise ValueError(f"Must be one of: {', '.join(members)}.")

        return core_schema.no_info_plain_validator_function(
            validate,
            json_schema_input_schema=core_schema.literal_schema(list(members)),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda member: member.name, return_schema=core_schema.literal_schema(list(members))
            ),
        )
