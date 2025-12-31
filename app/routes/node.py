from flask import Blueprint, request, jsonify
from app import db
from app.models import Node

node_bp = Blueprint("node", __name__)

@node_bp.route("/", methods=["POST"])
def create_node():
    data = request.get_json()
    if not data or 'name' not in data or 'floor_id' not in data or 'x_coordinate' not in data or 'y_coordinate' not in data or 'node_type' not in data:
        return {"error": "Please provide all required fields"}, 400

    new_node = Node(
        name=data['name'],
        floor_id=data['floor_id'],
        x_coordinate=data['x_coordinate'],
        y_coordinate=data['y_coordinate'],
        node_type=data['node_type']
    )
    
    db.session.add(new_node)
    db.session.commit()
    
    return jsonify({
        "message": "Node created successfully",
        "node": {
            "node_id": new_node.node_id,
            "name": new_node.name,
            "floor_id": new_node.floor_id,
            "x_coordinate": new_node.x_coordinate,
            "y_coordinate": new_node.y_coordinate,
            "node_type": new_node.node_type,
            "created_at": new_node.created_at.isoformat()
        }
    }), 201
    
@node_bp.route("/<int:node_id>", methods=["GET"])
def get_node(node_id):
    node = Node.query.get(node_id)
    if node:
        return jsonify({
            "node_id": node.node_id,
            "name": node.name,
            "floor_id": node.floor_id,
            "x_coordinate": node.x_coordinate,
            "y_coordinate": node.y_coordinate,
            "node_type": node.node_type,
            "created_at": node.created_at.isoformat()
        }), 200
    else:
        return jsonify({"error": "Node not found"}), 404

@node_bp.route("/<int:node_id>", methods=["PUT"])
def update_node(node_id):
    node = Node.query.get(node_id)
    if not node:
        return jsonify({"error": "Node not found"}), 404

    data = request.get_json()
    if 'name' in data:
        node.name = data['name']
    if 'floor_id' in data:
        node.floor_id = data['floor_id']
    if 'x_coordinate' in data:
        node.x_coordinate = data['x_coordinate']
    if 'y_coordinate' in data:
        node.y_coordinate = data['y_coordinate']
    if 'node_type' in data:
        node.node_type = data['node_type']

    db.session.commit()

    return jsonify({
        "message": "Node updated successfully",
        "node": {
            "node_id": node.node_id,
            "name": node.name,
            "floor_id": node.floor_id,
            "x_coordinate": node.x_coordinate,
            "y_coordinate": node.y_coordinate,
            "node_type": node.node_type,
            "created_at": node.created_at.isoformat()
        }
    }), 200
    
@node_bp.route("/<int:node_id>", methods=["DELETE"])
def delete_node(node_id):
    node = Node.query.get(node_id)
    if not node:
        return jsonify({"error": "Node not found"}), 404

    db.session.delete(node)
    db.session.commit()

    return jsonify({"message": "Node deleted successfully"}), 200

@node_bp.route("/<int:node_id>/fingerprints", methods=["GET"])
def get_node_fingerprints(node_id):
    node = Node.query.get(node_id)
    if not node:
        return jsonify({"error": "Node not found"}), 404

    from app.models import Mg_Fingerprint
    fingerprints = Mg_Fingerprint.query.filter_by(node_id=node_id).all()
    fingerprints_data = [{
        "fingerprint_id": fp.fingerprint_id,
        "mean_x": fp.mean_x,
        "mean_y": fp.mean_y,
        "mean_z": fp.mean_z,
        "std_x": fp.std_x,  
        "std_y": fp.std_y,
        "std_z": fp.std_z
    } for fp in fingerprints]
    
    return jsonify({
        "node_id": node.node_id,
        "fingerprints": fingerprints_data
    }), 200