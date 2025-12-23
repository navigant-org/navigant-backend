from flask import jsonify


def error_response(message, status_code=400, **extra):
	"""Return a standardized JSON error response.

	This is a small utility you can reuse across routes to
	keep error payloads consistent.
	"""

	payload = {"status": "error", "message": message}
	payload.update(extra)

	response = jsonify(payload)
	response.status_code = status_code
	return response
