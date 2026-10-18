# Week 1–2 · Python & FastAPI for .NET Developers

**Goal:** be productive in modern, typed, async Python — the language of the AI ecosystem.
**Mini-project:** *Prompt Library API* — store prompt templates with `{placeholders}` and render them.
This service is reused in later weeks (prompt engineering, evals).

## Run

```bash
uv sync                                   # restore packages (~ dotnet restore)
uv run uvicorn app.main:app --reload      # run (~ dotnet watch run) → http://localhost:8000/docs
uv run pytest -q                          # test  (~ dotnet test)
uv run ruff check . && uv run mypy app    # lint + strict type check (~ analyzers + nullable)
```

## C# → Python cheat sheet

| C# / .NET | Python | See |
|---|---|---|
| `dotnet` CLI + NuGet + `.csproj` | `uv` + `pyproject.toml` | `pyproject.toml` |
| `record` / DTO + DataAnnotations | Pydantic `BaseModel` + `Field(...)` | `app/models.py` |
| `interface IStore` | `typing.Protocol` (structural) | `app/store.py` |
| `string?` | `str \| None` | everywhere |
| LINQ `Where/Select/OrderBy` | list comprehension + `sorted(key=...)` | `store.list` |
| `async Task<T>` / `await` | `async def ... -> T` / `await` | everywhere |
| `SemaphoreSlim(1,1)` | `asyncio.Lock()` + `async with` | `store.add` |
| Minimal API `app.MapGet` | `@app.get(...)` | `app/main.py` |
| DI `AddSingleton` + injection | `Depends(...)` + `Annotated` | `Store` alias |
| xUnit + `WebApplicationFactory` | pytest fixture + `TestClient` | `tests/` |
| `using` / `IDisposable` | `with` / context manager | `async with` |
| Swagger (Swashbuckle) | built-in at `/docs` | — |

## Exercises (do these yourself — write a test first for each)

1. **Update:** add `PUT /prompts/{id}` that replaces name/template/tags and keeps `id` + `created_at`.
2. **Versioning:** each update creates a new version; `GET /prompts/{id}/versions` lists them.
   *(Prompt versioning is a real AI-Engineering concern.)*
3. **Persistence:** add `SqlitePromptStore` implementing the same `Protocol` (use `aiosqlite`),
   select the store via an env var with `pydantic-settings` (~ `IOptions<T>`).
4. **Middleware:** log method, path, status and duration for every request (~ ASP.NET middleware).
5. **Async practice:** `POST /prompts/render-batch` that renders many prompts concurrently
   with `asyncio.gather` (~ `Task.WhenAll`).

Done when: all tests pass, `ruff` and `mypy --strict` are clean.

## Reading (~2 h)

- FastAPI tutorial — sections *First Steps* to *Dependencies*: <https://fastapi.tiangolo.com/tutorial/>
- Pydantic concepts — *Models* and *Fields*: <https://docs.pydantic.dev/latest/concepts/models/>
- Python `asyncio` basics: <https://docs.python.org/3/library/asyncio-task.html>
