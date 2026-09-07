FROM python:3.12-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANGCHAIN_TRACING_V2=false \
    LANGSMITH_TRACING=false \
    PYTHONPATH=/code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY core ./core/
COPY services ./services/
COPY controllers ./controllers/
COPY schemas ./schemas/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
