# fastapi-langfuse-example

FastAPI service that calls OpenAI through LangChain. Traces go to **self-hosted Langfuse**, not LangSmith.

## Ports

Existing host ports are left alone (`3000`, `5432`, …).

| Service | URL |
| --- | --- |
| FastAPI | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Langfuse UI | http://localhost:3100 |
| MinIO (Langfuse media) | http://localhost:9090 |

Postgres, Redis, ClickHouse, and the Langfuse worker stay on the Compose network only.

## Setup

```powershell
cd app
copy .env.example .env
```

Set `OPENAI_API_KEY` in `.env`, then:

```powershell
docker compose up --build
```

```bash
cp .env.example .env
```

Langfuse login (from init env): `admin@localhost.local` / `changeme123`  
Project: `fastapi-openai`

## API

`GET /health`

`POST /v1/chat`

```json
{
  "messages": [
    { "role": "system", "content": "Reply briefly." },
    { "role": "user", "content": "Hello" }
  ],
  "user_id": "local-dev",
  "session_id": "demo-1"
}
```

Optional fields: `model`, `temperature`, `tags`.

Demo error traces (tagged `error` in Langfuse):

- `model`: `force-error` — simulated app failure
- `model`: `force-timeout` — forced OpenAI timeout
- unknown model name or `temperature` outside `0–2` — provider errors

## Env

| Variable | Role |
| --- | --- |
| `LANGFUSE_BASE_URL` | SDK ingest. Compose sets `http://langfuse-web:3000` in Docker. |
| `LANGFUSE_PUBLIC_URL` | Browser/trace links (`http://localhost:3100`). |
| `LANGCHAIN_TRACING_V2` / `LANGSMITH_TRACING` | Keep `false`. |

See `.env.example` for the full list.

## Layout

```
app/
  main.py              # FastAPI app, lifespan, 422 handler
  core/                # Settings
  controllers/         # HTTP (health, chat)
  services/            # Chat, LLM, Langfuse
  schemas/chat.py
  docker-compose.yml
```


## License

See [LICENSE](LICENSE) for details.