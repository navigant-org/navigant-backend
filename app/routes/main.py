from flask import Blueprint, jsonify, request
from app import db
from app.models import Mg_Fingerprint, Mg_Raw_Reading, Mg_session
from app.ml import windowed_statistics, KNNModel
import numpy as np
from collections import Counter
from app.utils import token_required

main_bp = Blueprint("main", __name__)

# Global variable to cache the trained model
cached_knn = None

def get_trained_model():
    global cached_knn
    if cached_knn is not None:
        return cached_knn

    # Load fingerprints from DB
    fingerprints = Mg_Fingerprint.query.all()
    if not fingerprints:
        return None

    X_train = []
    y_train = []
    for fp in fingerprints:
        features = [fp.mean_x, fp.mean_y, fp.mean_z, fp.std_x, fp.std_y, fp.std_z]
        X_train.append(features)
        y_train.append(fp.node_id)
    
    X_train = np.array(X_train)
    y_train = np.array(y_train)
 
    # Train KNN model
    knn = KNNModel(k=3)
    knn.fit(X_train, y_train)
    
    cached_knn = knn
    return cached_knn


@main_bp.route("/", methods=["GET"])
def index():
	"""API root endpoint with a minimal welcome payload."""
	return jsonify({
		"message": "Navigant Backend API",
		"version": "v1",
	}), 200


@main_bp.route("/fingerprint", methods=["POST"])
# @token_required
def create_fingerprint():
	global cached_knn
	data = request.get_json()
	if not data or 'readings' not in data or 'node_id' not in data:
		return {"error": "Readings data and node_id are required"}, 400

	readings = data['readings']
	if not isinstance(readings, list) or len(readings) == 0:
		return {"error": "Readings must be a non-empty list"}, 400

	# Store raw readings into Mg_Raw_Reading table

	# Create a new session
	import uuid

	session = Mg_session(
		session_id=str(uuid.uuid4()),
		node_id=data.get('node_id', 0),
	)
	db.session.add(session)
	db.session.commit()

	for reading in readings:
		mg_reading = Mg_Raw_Reading(
			session_id=session.session_id,
			mag_x=reading['mag_x'],
			mag_y=reading['mag_y'],
			mag_z=reading['mag_z']
		)
		db.session.add(mg_reading)

	db.session.commit()

	# Convert readings to a format suitable for windowed_statistics (list of lists)
	readings_matrix = [[r['mag_x'], r['mag_y'], r['mag_z']] for r in readings]
	windowed_readings = windowed_statistics(readings_matrix, window_size=10)
	if windowed_readings.size == 0:
		return {"error": "Not enough data to form a complete window"}, 400
	for win in windowed_readings:
		fingerprint = Mg_Fingerprint(
			node_id=data['node_id'],
			mean_x=win[0],
			mean_y=win[1],
			mean_z=win[2],
			std_x=win[3],
			std_y=win[4],
			std_z=win[5],
			sample_count=10
		)
		db.session.add(fingerprint)
	db.session.commit()

	# Invalidate the cache since we added new data
	cached_knn = None

	return jsonify({"message": "Fingerprint created successfully"}), 201


@main_bp.route("/localize", methods=["POST"])
def localize():
	data = request.get_json()
	if not data or 'readings' not in data:
		return {"error": "Readings data is required"}, 400
	readings = data['readings']

	if not isinstance(readings, list) or len(readings) == 0:
		return {"error": "Readings must be a non-empty list"}, 400

	windowed_readings = windowed_statistics(readings, window_size=3)
	if windowed_readings.size == 0:
		return {"error": "Not enough data to form a complete window"}, 400

	# Get trained model (cached if available)
	knn = get_trained_model()
	if knn is None:
		return {"error": "No fingerprints available for localization"}, 400
	predictions = knn.predict(windowed_readings)
	predicted_node = Counter(predictions).most_common(1)[0][0]
 
	return jsonify({"predicted_node_id": predicted_node}), 200