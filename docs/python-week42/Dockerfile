# syntax=docker/dockerfile:1
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE} AS builder
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv && /opt/venv/bin/python -m pip install --no-cache-dir -r requirements.txt

FROM ${PYTHON_IMAGE} AS runtime
ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 API_BIND=0.0.0.0 API_PORT=8002
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --create-home app
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY orm_api ./orm_api
COPY migrations ./migrations
COPY alembic.ini manage.py server.py healthcheck.py ./
RUN mkdir -p /app/instance && chown app:app /app/instance
USER 10001:10001
EXPOSE 8002
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 CMD ["python","healthcheck.py"]
CMD ["python","server.py"]
