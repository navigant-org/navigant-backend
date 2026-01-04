from flask import Blueprint, request, jsonify
from app import db
from app.models import Floor
from app.utils import token_required

floor_bp = Blueprint("floor", __name__)

@floor_bp.route("/", methods=["POST"])
@token_required
def create_floor(current_user):
    data = request.get_json()
    if not data or 'building_id' not in data or 'floor_number' not in data or 'map_img_url' not in data:
        return {"error": "Building ID, floor number, and map image URL are required"}, 400

    new_floor = Floor(
        building_id=data['building_id'],
        floor_number=data.get('floor_number', 0),
        map_img_url=data.get('map_img_url', ''),
        scale=data.get('scale', 1.0),
        origin_x=data.get('origin_x', 0.0),
        origin_y=data.get('origin_y', 0.0)
    )

    db.session.add(new_floor)
    db.session.commit()

    return jsonify({
        "message": "Floor created successfully",
        "floor": {
            "floor_id": new_floor.floor_id,
            "building_id": new_floor.building_id,
            "floor_number": new_floor.floor_number,
            "map_img_url": new_floor.map_img_url,
            "scale": new_floor.scale,
            "origin_x": new_floor.origin_x,
            "origin_y": new_floor.origin_y,
            "created_at": new_floor.created_at.isoformat()
        }
    }), 201

@floor_bp.route("/<int:floor_id>", methods=["GET"])
def get_floor(floor_id):
    floor = Floor.query.get(floor_id)
    if floor:
        return jsonify({
            "floor_id": floor.floor_id,
            "building_id": floor.building_id,
            "floor_number": floor.floor_number,
            "map_img_url": floor.map_img_url,
            "scale": floor.scale,
            "origin_x": floor.origin_x,
            "origin_y": floor.origin_y,
            "created_at": floor.created_at.isoformat()
        }), 200
    else:
        return jsonify({"error": "Floor not found"}), 404

@floor_bp.route("/<int:floor_id>", methods=["PUT"])
@token_required
def update_floor(current_user, floor_id):
    floor = Floor.query.get(floor_id)
    if not floor:
        return jsonify({"error": "Floor not found"}), 404

    data = request.get_json()
    if 'building_id' in data:
        floor.building_id = data['building_id']
    if 'floor_number' in data:
        floor.floor_number = data['floor_number']
    if 'map_img_url' in data:
        floor.map_img_url = data['map_img_url']
    if 'scale' in data:
        floor.scale = data['scale']
    if 'origin_x' in data:
        floor.origin_x = data['origin_x']
    if 'origin_y' in data:
        floor.origin_y = data['origin_y']

    db.session.commit()

    return jsonify({
        "message": "Floor updated successfully",
        "floor": {
            "floor_id": floor.floor_id,
            "building_id": floor.building_id,
            "floor_number": floor.floor_number,
            "map_img_url": floor.map_img_url,
            "scale": floor.scale,
            "origin_x": floor.origin_x,
            "origin_y": floor.origin_y,
            "created_at": floor.created_at.isoformat()
        }
    }), 200
    
@floor_bp.route("/<int:floor_id>", methods=["DELETE"])
@token_required
def delete_floor(current_user, floor_id):
    floor = Floor.query.get(floor_id)
    if not floor:
        return jsonify({"error": "Floor not found"}), 404

    db.session.delete(floor)
    db.session.commit()

    return jsonify({"message": "Floor deleted successfully"}), 200

@floor_bp.route("/<int:floor_id>/nodes", methods=["GET"])
def get_floor_nodes(floor_id):
    floor = Floor.query.get(floor_id)
    if not floor:
        return jsonify({"error": "Floor not found"}), 404

    from app.models import Node  # Import here to avoid circular imports
    nodes = Node.query.filter_by(floor_id=floor_id).all()
    if nodes:
        nodes_list = [
            {
                "node_id": n.node_id,
                "name": n.name,
                "x_coordinate": n.x_coordinate,
                "y_coordinate": n.y_coordinate,
                "node_type": n.node_type,
                "floor_id": n.floor_id,
                "created_at": n.created_at.isoformat()
            } for n in nodes
        ]
        return jsonify({"nodes": nodes_list, "count": len(nodes_list)}), 200
    else:
        return jsonify({"message": "No nodes found for this floor"}), 404
    
@floor_bp.route("/<int:floor_id>/edges", methods=["GET"])
def get_floor_edges(floor_id):
    floor = Floor.query.get(floor_id)
    if not floor:
        return jsonify({"error": "Floor not found"}), 404

    from app.models import Edge  # Import here to avoid circular imports
    edges = Edge.query.filter_by(floor_id=floor_id).all()
    if edges:
        edges_list = [
            {
                "edge_id": e.edge_id,
                "start_node_id": e.start_node_id,
                "end_node_id": e.end_node_id,
                "distance": e.distance,
                "is_walkable": e.is_walkable,
                "floor_id": e.floor_id,
                "created_at": e.created_at.isoformat()
            } for e in edges
        ]
        return jsonify({"edges": edges_list, "count": len(edges_list)}), 200
    else:
        return jsonify({"message": "No edges found for this floor"}), 404

@floor_bp.route("/<int:floor_id>/graph", methods=["GET"])
def get_floor_graph(floor_id):
    floor = Floor.query.get(floor_id)
    if not floor:
        return jsonify({"error": "Floor not found"}), 404

    from app.models import Node, Edge  # Import here to avoid circular imports
    nodes = Node.query.filter_by(floor_id=floor_id).all()
    edges = Edge.query.filter_by(floor_id=floor_id).all()

    nodes_list = [
        {
            "node_id": n.node_id,
            "name": n.name,
            "x_coordinate": n.x_coordinate,
            "y_coordinate": n.y_coordinate,
            "node_type": n.node_type,
            "floor_id": n.floor_id,
            "created_at": n.created_at.isoformat()
        } for n in nodes
    ]

    edges_list = [
        {
            "edge_id": e.edge_id,
            "start_node_id": e.start_node_id,
            "end_node_id": e.end_node_id,
            "distance": e.distance,
            "is_walkable": e.is_walkable,
            "floor_id": e.floor_id,
            "created_at": e.created_at.isoformat()
        } for e in edges
    ]

    return jsonify({
        "nodes": nodes_list,
        "edges": edges_list,
        "node_count": len(nodes_list),
        "edge_count": len(edges_list),
        "scale": floor.scale,
    }), 200