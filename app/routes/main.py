from flask import Blueprint, jsonify, request
from app import db
from app.models import Mg_Fingerprint, Mg_Raw_Reading, Mg_session
from app.ml import windowed_statistics, KNNModel
import numpy as np
from collections import Counter
from app.utils import token_required

main_bp = Blueprint("main", __name__)

# Global variable to cache trained models per building
# { building_id: KNNModel }
model_cache = {}

def get_trained_model(building_id=None):
    global model_cache
    if building_id in model_cache:
        return model_cache[building_id]

    from app.models import Node, Floor

    query = Mg_Fingerprint.query
    if building_id:
        # Filter fingerprints by building
        query = query.join(Node, Mg_Fingerprint.node_id == Node.node_id)\
                     .join(Floor, Node.floor_id == Floor.floor_id)\
                     .filter(Floor.building_id == building_id)

    fingerprints = query.all()
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
    
    model_cache[building_id] = knn
    return knn


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
	global model_cache
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
			mean_x=float(win[0]),
			mean_y=float(win[1]),
			mean_z=float(win[2]),
			std_x=float(win[3]),
			std_y=float(win[4]),
			std_z=float(win[5]),
			sample_count=10
		)
		db.session.add(fingerprint)
	db.session.commit()

	# Invalidate relevant caches
	from app.models import Node, Floor
	node = Node.query.get(data['node_id'])
	if node:
		floor = Floor.query.get(node.floor_id)
		if floor:
			# Invalidate both specific building and global cache
			model_cache.pop(floor.building_id, None)
			model_cache.pop(None, None)
	else:
		model_cache.clear()

	return jsonify({"message": "Fingerprint created successfully"}), 201

@main_bp.route("/delete_all_fingerprints", methods=["DELETE"])
#@token_required
def delete_all_fingerprints():
	try:
		Mg_Raw_Reading.query.delete()
		Mg_session.query.delete()
		Mg_Fingerprint.query.delete()
		
		db.session.commit()
		
		return {"message": "All magnetometer data deleted successfully"}, 200
	
	except Exception as e:
		db.session.rollback()
		return {"error": str(e)}, 500

@main_bp.route("/localize", methods=["POST"])
def localize():
	data = request.get_json()
	if not data or 'readings' not in data:
		return {"error": "Readings data is required"}, 400
	readings = data['readings']

	if not isinstance(readings, list) or len(readings) == 0:
		return {"error": "Readings must be a non-empty list"}, 400

	# Convert readings to a format suitable for windowed_statistics (list of lists)
	readings_matrix = [[r['mag_x'], r['mag_y'], r['mag_z']] for r in readings]
	windowed_readings = windowed_statistics(readings_matrix, window_size=3)
	if windowed_readings.size == 0:
		return {"error": "Not enough data to form a complete window"}, 400

	# Get trained model (cached if available)
	building_id = data.get('building_id')
	knn = get_trained_model(building_id)
	if knn is None:
		return {"error": "No fingerprints available for localization"}, 400
	predictions = knn.predict(windowed_readings)
	predicted_node = int(Counter(predictions).most_common(1)[0][0])
 
	from app.models import Node
 
	node = Node.query.get(predicted_node)
	if not node:
		return {"error": "Predicted node not found in database"}, 400

	return jsonify({
		"predicted_node_id": node.node_id,
		"name": node.name,
		"x_coord": node.x_coordinate,
		"y_coord": node.y_coordinate,
		"floor_id": node.floor_id,
		"node_type": node.node_type
	}), 200
 
@main_bp.route("/path", methods=["GET"])
def get_path():
	data = request.get_json()
	if not data or 'start_node_id' not in data or 'end_node_id' not in data:
		return {"error": "start_node_id and end_node_id are required"}, 400

	from app.pathfinding import findpath, build_graph
	from app.models import Node, Floor
 
	building_id = data.get('building_id')
	if not building_id:
		start_node = Node.query.get(data['start_node_id'])
		if not start_node:
			return {"error": "Start node not found"}, 404
		floor = Floor.query.get(start_node.floor_id)
		if not floor:
			return {"error": "Floor not found for start node"}, 404
		building_id = floor.building_id

	try:
		graph = build_graph(building_id)
	except ValueError as e:
		return {"error": str(e)}, 400

	distance, path = findpath(data['start_node_id'], data['end_node_id'], graph)
 
	if distance == float('inf'):
		return jsonify({"message": "No path found between the specified nodes"}), 404

	# Optimize: fetch all nodes in path in one query
	nodes_in_path = Node.query.filter(Node.node_id.in_(path)).all()
	node_map = {n.node_id: n for n in nodes_in_path}
	
	path_details = [
		{
			"node_id": node_id,
			"name": node_map[node_id].name,
			"x_coordinate": node_map[node_id].x_coordinate,
			"y_coordinate": node_map[node_id].y_coordinate,
			"node_type": node_map[node_id].node_type,
			"floor_id": node_map[node_id].floor_id
		} for node_id in path if node_id in node_map
	]
 
	return jsonify({
		"total_distance": distance,
		"path": path,
		"path_details": path_details
	})
