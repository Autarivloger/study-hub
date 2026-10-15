"""Alembic uses the explicitly supplied owned connection; no implicit production URL."""
from alembic import context
from orm_api.models import Base

connection = context.config.attributes.get("connection")
if connection is None:
    raise RuntimeError("Use manage.py or migration_config with an explicitly owned connection")
context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True, render_as_batch=True)
with context.begin_transaction():
    context.run_migrations()
