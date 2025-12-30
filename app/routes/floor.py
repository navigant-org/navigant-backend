from flask import Blueprint, request, jsonify
from app import db
from app.models import Floor

floor_bp = Blueprint("floor", __name__)

@floor_bp.route("/", methods=["POST"])
def create_floor():
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
def update_floor(floor_id):
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
def delete_floor(floor_id):
    floor = Floor.query.get(floor_id)
    if not floor:
        return jsonify({"error": "Floor not found"}), 404

    db.session.delete(floor)
    db.session.commit()

    return jsonify({"message": "Floor deleted successfully"}), 200
