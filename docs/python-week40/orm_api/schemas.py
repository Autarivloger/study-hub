"""JSON contracts. Ownership and password hashes are never writable/public fields."""
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class UserCreate(Input):
    username: Annotated[str, Field(min_length=3, max_length=32)]
    password: Annotated[SecretStr, Field(min_length=12, max_length=128)]

    @field_validator("username")
    @classmethod
    def canonical_username(cls, value):
        value = value.strip().lower()
        if not 3 <= len(value) <= 32 or not all(c in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in value):
            raise ValueError("Use 3–32 ASCII letters, digits or underscores")
        return value


class UserRead(BaseModel):
    id: int
    username: str


class NoteCreate(Input):
    title: Annotated[str, Field(min_length=1, max_length=100)]
    body: Annotated[str, Field(min_length=1, max_length=2000)]
    completed: bool = False

    @field_validator("title", "body")
    @classmethod
    def meaningful_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Text must contain a non-space character")
        return value


class NoteReplace(NoteCreate):
    completed: bool


class NotePatch(Input):
    title: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    body: Annotated[str | None, Field(min_length=1, max_length=2000)] = None
    completed: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def nonempty_nonnull(cls, value):
        if isinstance(value, dict) and (not value or any(v is None for v in value.values())):
            raise ValueError("Supply at least one field; explicit null is not supported")
        return value

    @field_validator("title", "body")
    @classmethod
    def meaningful_text(cls, value):
        return NoteCreate.meaningful_text(value)


class NoteRead(BaseModel):
    id: int
    title: str
    body: str
    completed: bool
    created_at: str


class NotePage(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[NoteRead]


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class TagSelection(Input):
    names: Annotated[list[str], Field(max_length=3)]

    @field_validator("names")
    @classmethod
    def known_unique_names(cls, value):
        if len(value) != len(set(value)) or any(name not in {"python", "api", "database"} for name in value):
            raise ValueError("Choose unique known tag names")
        return value
