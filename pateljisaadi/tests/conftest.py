import os
import sys
import tempfile
import pytest

# Ensure project root is on sys.path for `import app`
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.db import init_db, get_db


@pytest.fixture()
def app():
	fd, db_path = tempfile.mkstemp()
	os.close(fd)

	app = create_app(
		{
			"TESTING": True,
			"SECRET_KEY": "test",
			"DATABASE": db_path,
		}
	)

	with app.app_context():
		init_db()

	yield app

	os.remove(db_path)


@pytest.fixture()
def client(app):
	return app.test_client()


@pytest.fixture()
def runner(app):
	return app.test_cli_runner()


def register(client, email="user@example.com", name="Test User", password="secret"):
	return client.post(
		"/auth/register",
		data={"email": email, "full_name": name, "password": password},
		follow_redirects=True,
	)


def login(client, email="user@example.com", password="secret"):
	return client.post(
		"/auth/login",
		data={"email": email, "password": password},
		follow_redirects=True,
	)

