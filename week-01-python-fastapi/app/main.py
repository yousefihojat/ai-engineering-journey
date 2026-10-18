"""FastAPI app. Compare with ASP.NET Core Minimal APIs: app.MapGet(...) <-> @app.get(...)."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status

from .models import Prompt, PromptCreate, RenderRequest, RenderResponse
from .store import InMemoryPromptStore, PromptStore

app = FastAPI(title="Prompt Library API", version="0.1.0")

# Singleton, like builder.Services.AddSingleton<IPromptStore, InMemoryPromptStore>()
_store = InMemoryPromptStore()


def get_store() -> PromptStore:
    return _store


# Annotated + Depends ~ constructor/parameter injection in ASP.NET Core
Store = Annotated[PromptStore, Depends(get_store)]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/prompts", status_code=status.HTTP_201_CREATED)
async def create_prompt(body: PromptCreate, store: Store) -> Prompt:
    return await store.add(body)


@app.get("/prompts")
async def list_prompts(store: Store, tag: str | None = None) -> list[Prompt]:
    return await store.list(tag)


@app.get("/prompts/{prompt_id}")
async def get_prompt(prompt_id: UUID, store: Store) -> Prompt:
    prompt = await store.get(prompt_id)
    if prompt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Prompt not found")
    return prompt


@app.delete("/prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: UUID, store: Store) -> None:
    if not await store.delete(prompt_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Prompt not found")


@app.post("/prompts/{prompt_id}/render")
async def render_prompt(prompt_id: UUID, body: RenderRequest, store: Store) -> RenderResponse:
    prompt = await get_prompt(prompt_id, store)
    missing = [v for v in prompt.variables if v not in body.values]
    if missing:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, f"Missing values: {', '.join(missing)}")
    return RenderResponse(prompt_id=prompt.id, text=prompt.template.format_map(body.values))
