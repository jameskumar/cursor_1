import os
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .db import get_db


bp = Blueprint("auth", __name__, url_prefix="/auth")


def _hash_password(password: str) -> str:
	# Simple salted hash for demo; replace with Argon2/Bcrypt in production
	salt = os.environ.get("PASSWORD_SALT", "static-demo-salt").encode()
	return hashlib.sha256(salt + password.encode()).hexdigest()


@bp.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		email = request.form.get("email", "").strip().lower()
		full_name = request.form.get("full_name", "").strip()
		password = request.form.get("password", "")

		error = None
		if not email or not full_name or not password:
			error = "All fields are required."

		if error is None:
			db = get_db()
			try:
				db.execute(
					"INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)",
					(email, _hash_password(password), full_name),
				)
				db.commit()
				flash("Registration successful. Please log in.", "success")
				return redirect(url_for("auth.login"))
			except Exception:
				error = "Account with this email may already exist."

		flash(error, "danger")

	return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")
		db = get_db()
		user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
		if user and user["password_hash"] == _hash_password(password):
			session.clear()
			session["user_id"] = user["id"]
			session["user_name"] = user["full_name"]
			next_url = request.args.get("next")
			return redirect(next_url or url_for("views.dashboard"))
		flash("Invalid credentials.", "danger")
	return render_template("login.html")


@bp.route("/logout")
def logout():
	session.clear()
	flash("You have been logged out.", "info")
	return redirect(url_for("views.index"))

