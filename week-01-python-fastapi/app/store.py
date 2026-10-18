"""In-memory repository. Protocol = C# interface, but structural: any class with these methods fits."""

import asyncio
from typing import Protocol
from uuid import UUID

from .models import Prompt, PromptCreate


class PromptStore(Protocol):
    async def add(self, data: PromptCreate) -> Prompt: ...
    async def get(self, prompt_id: UUID) -> Prompt | None: ...
    async def list(self, tag: str | None = None) -> list[Prompt]: ...
    async def delete(self, prompt_id: UUID) -> bool: ...


class InMemoryPromptStore:
    """Thread-safe-ish store. asyncio.Lock ~ SemaphoreSlim(1,1) in C#."""

    def __init__(self) -> None:
        self._items: dict[UUID, Prompt] = {}
        self._lock = asyncio.Lock()

    async def add(self, data: PromptCreate) -> Prompt:
        prompt = Prompt(**data.model_dump(exclude={"variables"}))
        async with self._lock:  # ~ `await sem.WaitAsync(); try {...} finally {sem.Release();}`
            self._items[prompt.id] = prompt
        return prompt

    async def get(self, prompt_id: UUID) -> Prompt | None:
        return self._items.get(prompt_id)

    async def list(self, tag: str | None = None) -> list[Prompt]:
        # List comprehension ~ LINQ: _items.Values.Where(p => ...).OrderBy(p => p.CreatedAt).ToList()
        items = [p for p in self._items.values() if tag is None or tag in p.tags]
        return sorted(items, key=lambda p: p.created_at)

    async def delete(self, prompt_id: UUID) -> bool:
        async with self._lock:
            return self._items.pop(prompt_id, None) is not None
