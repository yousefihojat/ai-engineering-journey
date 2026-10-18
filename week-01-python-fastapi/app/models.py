"""Pydantic models = C# DTOs/records with built-in validation (like DataAnnotations, but enforced)."""

import string
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field


class PromptCreate(BaseModel):
    """Request body. ~ C# `record PromptCreate(...)` with [Required]/[StringLength]."""

    name: str = Field(min_length=1, max_length=100)
    template: str = Field(min_length=1, description="Text with {placeholders}")
    tags: list[str] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def variables(self) -> list[str]:
        """Placeholder names found in the template, e.g. 'Hi {name}' -> ['name']."""
        names = [field for _, field, _, _ in string.Formatter().parse(self.template) if field]
        return sorted(set(names))


class Prompt(PromptCreate):
    """Stored prompt. Inheritance works like C# class inheritance."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RenderRequest(BaseModel):
    values: dict[str, str]


class RenderResponse(BaseModel):
    prompt_id: UUID
    text: str
