from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from .db import get_db
from .utils import login_required


bp = Blueprint("views", __name__)


@bp.route("/")
def index():
	return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
	db = get_db()
	user_id = session.get("user_id")
	my_profile = db.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
	return render_template("dashboard.html", my_profile=my_profile)


@bp.route("/search")
def search():
	query_gender = request.args.get("gender")
	query_caste = request.args.get("caste")
	query_location = request.args.get("location")

	conditions = []
	params = []
	if query_gender:
		conditions.append("gender = ?")
		params.append(query_gender)
	if query_caste:
		conditions.append("caste LIKE ?")
		params.append(f"%{query_caste}%")
	if query_location:
		conditions.append("location LIKE ?")
		params.append(f"%{query_location}%")

	where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
	db = get_db()
	rows = db.execute(
		f"""
		SELECT users.id as user_id, users.full_name, profiles.*
		FROM users JOIN profiles ON users.id = profiles.user_id
		{where_clause}
		ORDER BY profiles.updated_at DESC
		LIMIT 50
		""",
		params,
	).fetchall()
	return render_template("search.html", results=rows)


@bp.route("/interest/<int:to_user_id>", methods=["POST"])
@login_required
def express_interest(to_user_id: int):
	if to_user_id == session.get("user_id"):
		flash("You cannot express interest in yourself.", "warning")
		return redirect(url_for("views.search"))
	db = get_db()
	message = (request.form.get("message") or "Interested in connecting").strip()
	try:
		db.execute(
			"INSERT OR IGNORE INTO interests (from_user_id, to_user_id, message) VALUES (?, ?, ?)",
			(session.get("user_id"), to_user_id, message),
		)
		db.commit()
		flash("Interest sent!", "success")
	except Exception:
		flash("Could not send interest.", "danger")
	return redirect(url_for("profile.view_profile", user_id=to_user_id))

