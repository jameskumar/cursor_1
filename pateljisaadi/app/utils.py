from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(view):
	@wraps(view)
	def wrapped_view(**kwargs):
		if session.get("user_id") is None:
			flash("Please log in to continue.", "warning")
			return redirect(url_for("auth.login", next=request.path))
		return view(**kwargs)

	return wrapped_view

