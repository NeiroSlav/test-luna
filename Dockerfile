FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

ADD pyproject.toml uv.lock /app/
RUN uv sync

ADD src /app

EXPOSE 8080:8080

CMD ["uv", "run", "uvicorn", "main:app", "--host=0.0.0.0", "--port=8080"]