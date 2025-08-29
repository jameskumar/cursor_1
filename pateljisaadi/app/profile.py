import os
from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from .db import get_db
from .utils import login_required


bp = Blueprint("profile", __name__, url_prefix="/profile")


def _save_photo(file_storage) -> str | None:
	if not file_storage or file_storage.filename == "":
		return None
	allowed = {".jpg", ".jpeg", ".png", ".webp"}
	name, ext = os.path.splitext(file_storage.filename.lower())
	if ext not in allowed:
		return None
	filename = f"{uuid4().hex}{ext}"
	file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
	file_storage.save(file_path)
	return filename


@bp.route("/me", methods=["GET", "POST"])
@login_required
def edit_me():
	db = get_db()
	user_id = session.get("user_id")
	profile = db.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()

	if request.method == "POST":
		gender = request.form.get("gender") or None
		age = request.form.get("age") or None
		religion = request.form.get("religion") or None
		caste = request.form.get("caste") or None
		gotra = request.form.get("gotra") or None
		location = request.form.get("location") or None
		occupation = request.form.get("occupation") or None
		bio = request.form.get("bio") or None
		photo = _save_photo(request.files.get("photo"))

		if profile is None:
			db.execute(
				"""
				INSERT INTO profiles (user_id, gender, age, religion, caste, gotra, location, occupation, bio, photo_filename)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				""",
				(user_id, gender, age, religion, caste, gotra, location, occupation, bio, photo),
			)
		else:
			update_fields = [
				("gender", gender),
				("age", age),
				("religion", religion),
				("caste", caste),
				("gotra", gotra),
				("location", location),
				("occupation", occupation),
				("bio", bio),
			]
			if photo:
				update_fields.append(("photo_filename", photo))
			set_clause = ", ".join([f"{k} = ?" for k, _ in update_fields])
			params = [v for _, v in update_fields]
			params.append(user_id)
			db.execute(f"UPDATE profiles SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", params)

		db.commit()
		flash("Profile saved.", "success")
		return redirect(url_for("profile.edit_me"))

	return render_template("profile_edit.html", profile=profile)


@bp.route("/view/<int:user_id>")
def view_profile(user_id: int):
	db = get_db()
	user = db.execute("SELECT id, full_name FROM users WHERE id = ?", (user_id,)).fetchone()
	profile = db.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
	return render_template("profile_view.html", user=user, profile=profile)

