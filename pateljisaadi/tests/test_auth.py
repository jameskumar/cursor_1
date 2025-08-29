from conftest import register, login


def test_register_login_logout_flow(client):
	# Register
	rv = register(client)
	assert b"Registration successful" in rv.data

	# Login
	rv = login(client)
	assert b"Dashboard" in rv.data or b"Find Matches" in rv.data

	# Logout
	rv = client.get("/auth/logout", follow_redirects=True)
	assert b"logged out" in rv.data.lower()

