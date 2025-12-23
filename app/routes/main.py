from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["GET"])
def index():
	"""API root endpoint with a minimal welcome payload."""
	return jsonify({
		"message": "Navigant Backend API",
		"version": "v1",
	}), 200
