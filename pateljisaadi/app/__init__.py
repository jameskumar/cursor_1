import os
from flask import Flask
from dotenv import load_dotenv


def create_app(test_config: dict | None = None) -> Flask:
	app = Flask(__name__, instance_relative_config=True)

	# Load .env if present
	load_dotenv()

	# Default configuration
	app.config.from_mapping(
		SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-me"),
		DATABASE=os.path.join(app.instance_path, "pateljisaadi.sqlite"),
		UPLOAD_FOLDER=os.path.join(app.root_path, "static", "img", "uploads"),
		MAX_CONTENT_LENGTH=8 * 1024 * 1024,
	)

	if test_config is not None:
		app.config.update(test_config)
	else:
		# Load instance config, if it exists
		app.config.from_pyfile("config.py", silent=True)

	# Ensure instance and upload folders exist
	os.makedirs(app.instance_path, exist_ok=True)
	os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

	# Register DB
	from . import db
	db.init_app(app)

	# Blueprints
	from .auth import bp as auth_bp
	app.register_blueprint(auth_bp)

	from .profile import bp as profile_bp
	app.register_blueprint(profile_bp)

	from .views import bp as views_bp
	app.register_blueprint(views_bp)

	return app

