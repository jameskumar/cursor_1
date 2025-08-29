from conftest import register, login
from app.db import get_db


def test_profile_create_and_update(app, client):
	register(client)
	login(client)
	# Create profile
	rv = client.post(
		"/profile/me",
		data={
			"gender": "female",
			"age": 28,
			"religion": "Hindu",
			"caste": "Patel",
			"gotra": "—",
			"location": "Ahmedabad",
			"occupation": "Engineer",
			"bio": "Hello there",
		},
		follow_redirects=True,
	)
	assert b"Profile saved" in rv.data

	with app.app_context():
		db = get_db()
		row = db.execute("SELECT * FROM profiles").fetchone()
		assert row is not None
		assert row["caste"] == "Patel"

	# Update profile
	rv = client.post(
		"/profile/me",
		data={
			"gender": "female",
			"age": 29,
			"location": "Surat",
			"bio": "Updated",
		},
		follow_redirects=True,
	)
	assert b"Profile saved" in rv.data

	with app.app_context():
		db = get_db()
		row = db.execute("SELECT * FROM profiles").fetchone()
		assert row["age"] == 29
		assert row["location"] == "Surat"

