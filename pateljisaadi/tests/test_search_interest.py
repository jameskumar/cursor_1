from conftest import register, login
from app.db import get_db


def test_search_filters_and_interest_flow(app, client):
	# User A
	register(client, email="a@example.com", name="User A")
	login(client, email="a@example.com")
	client.post(
		"/profile/me",
		data={"gender": "male", "age": 30, "caste": "Patel", "location": "Ahmedabad"},
		follow_redirects=True,
	)
	client.get("/auth/logout", follow_redirects=True)

	# User B
	register(client, email="b@example.com", name="User B")
	login(client, email="b@example.com")
	client.post(
		"/profile/me",
		data={"gender": "female", "age": 27, "caste": "Patel", "location": "Surat"},
		follow_redirects=True,
	)

	# Search by caste
	rv = client.get("/search?caste=Patel")
	assert b"User A" in rv.data and b"User B" in rv.data

	# Search by gender
	rv = client.get("/search?gender=female")
	assert b"User B" in rv.data and b"User A" not in rv.data

	# View User B and express interest from B to A should not be visible here; switch
	client.get("/auth/logout", follow_redirects=True)
	login(client, email="a@example.com")

	# Express interest from A to B
	with app.app_context():
		db = get_db()
		user_b = db.execute("SELECT id FROM users WHERE email = ?", ("b@example.com",)).fetchone()
		b_id = user_b["id"]
	
	rv = client.post(f"/interest/{b_id}", data={"message": "Hi"}, follow_redirects=True)
	assert b"Interest sent" in rv.data

	with app.app_context():
		db = get_db()
		row = db.execute("SELECT * FROM interests").fetchone()
		assert row is not None