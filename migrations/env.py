import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app
from sqlalchemy import engine_from_config, pool

config = context.config
config_file = config.config_file_name
assert config_file is not None
fileConfig(config_file)
logger = logging.getLogger("alembic.env")

db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI")
assert db_url is not None
config.set_main_option("sqlalchemy.url", db_url)
target_metadata = current_app.extensions["migrate"].db.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section)
    assert section is not None
    engine = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        **current_app.extensions["migrate"].configure_args,
    )
    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
