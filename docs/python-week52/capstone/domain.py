"""Public session validation, shared by the HTTP adapter and repository examples."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


def canonical_day(value: str) -> str:
    """Require a real calendar day in exactly YYYY-MM-DD form."""
    if date.fromisoformat(value).isoformat() != value:
        raise ValueError("day must use YYYY-MM-DD")
    return value


class SessionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: str = Field(strict=True)
    subject: str = Field(strict=True, min_length=1, max_length=80)
    minutes: int = Field(strict=True, ge=1, le=1440)
    note: str = Field(default="", strict=True, max_length=1000)

    @field_validator("day")
    @classmethod
    def validate_day(cls, value: str) -> str:
        return canonical_day(value)

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:
        value = value.strip()
        if not value or any(ord(character) < 32 for character in value):
            raise ValueError("subject must be nonblank and contain no control characters")
        return value

    @field_validator("note")
    @classmethod
    def validate_note(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("note must not contain NUL")
        return value


class SessionEdit(SessionInput):
    version: int = Field(strict=True, ge=1)
