from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, field_validator

from empire.server.core.db import models


class BadRequestResponse(BaseModel):
    detail: str


class NotFoundResponse(BaseModel):
    detail: str


class ValueType(str, Enum):
    string = "STRING"
    float = "FLOAT"
    integer = "INTEGER"
    boolean = "BOOLEAN"
    file = "FILE"


class CustomOptionSchema(BaseModel):
    description: str
    required: bool
    value: str
    suggested_values: list[str]
    strict: bool
    value_type: ValueType

    # Ensure the functionality of pydantic v1 coercing values to strings
    # https://github.com/pydantic/pydantic/issues/5606
    @field_validator("value", mode="plain")
    @classmethod
    def check_value(cls, v):
        return str(v)

    @field_validator("suggested_values", mode="plain")
    @classmethod
    def check_suggested_values(cls, v):
        return [str(value) for value in v]


class OrderDirection(str, Enum):
    asc = "asc"
    desc = "desc"


class DownloadDescription(BaseModel):
    id: int
    filename: str
    link: str
    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str | None = None
    handle: str | None = None
    link: str | None = None


def domain_to_dto_download_description(download: models.Download):
    if download.filename:
        filename = download.filename
    else:
        filename = download.location.split("/")[-1]

    return DownloadDescription(
        id=download.id,
        filename=filename,
        link=f"/api/v2/downloads/{download.id}/download",
    )


def to_value_type(value: Any, type: str = "") -> ValueType:
    type = type or ""
    if type.lower() == "file":
        return ValueType.file
    elif type.lower() in ["string", "str"] or isinstance(value, str):
        return ValueType.string
    elif type.lower() in ["boolean", "bool"] or isinstance(value, bool):
        return ValueType.boolean
    elif type.lower() == "float" or isinstance(value, float):
        return ValueType.float
    elif type.lower() in ["integer", "int"] or isinstance(value, int):
        return ValueType.integer
    else:
        return ValueType.string


def to_string(value):
    return str(value)


# This is sort of an undocumented behavior for the Empire API. The openapi spec says
#   the values should be strings, but it has allowed other types.
# The behavior in pydantic v1 was to just coerce values to strings, but in v2
#   this behavior was changed to raise a validation error. Using this custom
#   type with a BeforeValidator allows us to coerce the value to a string before
#   validation.
# This could be removed in Empire 6 as a breaking change.
coerced_dict = dict[str, Annotated[str, BeforeValidator(to_string)]]


# Set proxy IDs
PROXY_NAME = {
    "SOCKS4": 1,
    "SOCKS5": 2,
    "HTTP": 3,
    "SSL": 4,
    "SSL_WEAK": 5,
    "SSL_ANON": 6,
    "TOR": 7,
    "HTTPS": 8,
    "HTTP_CONNECT": 9,
    "HTTPS_CONNECT": 10,
}

# inverse of PROXY_NAME
PROXY_ID = {v: k for k, v in PROXY_NAME.items()}
