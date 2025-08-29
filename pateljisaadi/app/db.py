import sqlite3
from typing import Any
from flask import current_app, g
import click


def get_db() -> sqlite3.Connection:
	if "db" not in g:
		g.db = sqlite3.connect(
			current_app.config["DATABASE"],
			detect_types=sqlite3.PARSE_DECLTYPES,
		)
		g.db.row_factory = sqlite3.Row
	return g.db


def close_db(e: Exception | None = None) -> None:  # noqa: ARG001
	db = g.pop("db", None)
	if db is not None:
		db.close()


def init_db() -> None:
	db = get_db()
	with current_app.open_resource("schema.sql") as f:
		db.executescript(f.read().decode("utf-8"))
	db.commit()


def init_app(app: Any) -> None:
	app.teardown_appcontext(close_db)

	@app.cli.command("init-db")
	def init_db_command() -> None:
		"""Clear existing data and create new tables."""
		init_db()
		click.echo("Initialized the database.")

