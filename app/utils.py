from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.models import User
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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            # Support "Bearer <token>"
            parts = request.headers['Authorization'].split()
            if len(parts) == 2:
                token = parts[1]
            else:
                token = request.headers['Authorization']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token. User not found.'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
