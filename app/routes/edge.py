from flask import Blueprint, request, jsonify
from app import db
from app.models import Edge

edge_bp = Blueprint("edge", __name__)

@edge_bp.route("/", methods=["POST"])
def create_edge():
    data = request.get_json()
    if not data or 'start_node_id' not in data or 'end_node_id' not in data or 'distance' not in data or 'floor_id' not in data:
        return {"error": "Please provide all required fields"}, 400
    
    new_edge = Edge(
        start_node_id=data['start_node_id'],
        end_node_id=data['end_node_id'],
        distance=data['distance'],
        floor_id=data['floor_id']
    )
    
    db.session.add(new_edge)
    db.session.commit()
    return jsonify({
        "message": "Edge created successfully",
        "edge": {
            "edge_id": new_edge.edge_id,
            "start_node_id": new_edge.start_node_id,
            "end_node_id": new_edge.end_node_id,
            "distance": new_edge.distance,
            "floor_id": new_edge.floor_id,
            "created_at": new_edge.created_at.isoformat()
        }
    }), 201

@edge_bp.route("/<int:edge_id>", methods=["GET"])
def get_edge(edge_id):
    edge = Edge.query.get(edge_id)
    if edge:
        return jsonify({
            "edge_id": edge.edge_id,
            "start_node_id": edge.start_node_id,
            "end_node_id": edge.end_node_id,
            "distance": edge.distance,
            "floor_id": edge.floor_id,
            "created_at": edge.created_at.isoformat()
        }), 200
    else:
        return jsonify({"error": "Edge not found"}), 404
    
@edge_bp.route("/<int:edge_id>", methods=["PUT"])
def update_edge(edge_id):
    edge = Edge.query.get(edge_id)
    if not edge:
        return jsonify({"error": "Edge not found"}), 404

    data = request.get_json()
    if 'start_node_id' in data:
        edge.start_node_id = data['start_node_id']
    if 'end_node_id' in data:
        edge.end_node_id = data['end_node_id']
    if 'distance' in data:
        edge.distance = data['distance']
    if 'floor_id' in data:
        edge.floor_id = data['floor_id']

    db.session.commit()

    return jsonify({
        "message": "Edge updated successfully",
        "edge": {
            "edge_id": edge.edge_id,
            "start_node_id": edge.start_node_id,
            "end_node_id": edge.end_node_id,
            "distance": edge.distance,
            "floor_id": edge.floor_id,
            "created_at": edge.created_at.isoformat()
        }
    }), 200
    
@edge_bp.route("/<int:edge_id>", methods=["DELETE"])
def delete_edge(edge_id):
    edge = Edge.query.get(edge_id)
    if not edge:
        return jsonify({"error": "Edge not found"}), 404

    db.session.delete(edge)
    db.session.commit()

    return jsonify({"message": "Edge deleted successfully"}), 200