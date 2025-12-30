from flask import Blueprint, request, jsonify
from app import db
from app.models import Building, Floor

building_bp = Blueprint("building", __name__)

@building_bp.route("/", methods=["GET"])
def get_buildings():
    buildings = Building.query.all()
    if buildings:
        buildings_list = [
            {
                "building_id": b.building_id,
                "name": b.name,
                "description": b.description,
                "created_at": b.created_at.isoformat()
            } for b in buildings
        ]
        return jsonify({"buildings": buildings_list, "count": len(buildings_list)}), 200
    else:
        return jsonify({"message": "No buildings found"}), 404
    
@building_bp.route("/", methods=["POST"])
def create_building():
    data = request.get_json()
    if not data or 'name' not in data or 'description' not in data:
        return {"error": "Name and description are required"}, 400

    new_building = Building(
        name=data['name'],
        description=data['description']
    )

    db.session.add(new_building)
    db.session.commit()

    return jsonify({
        "message": "Building created successfully",
        "building": {
            "building_id": new_building.building_id,
            "name": new_building.name,
            "description": new_building.description,
            "created_at": new_building.created_at.isoformat()
        }
    }), 201

@building_bp.route("/<int:building_id>", methods=["GET"])
def get_building(building_id):
    building = Building.query.get(building_id)
    if building:
        return jsonify({
            "building_id": building.building_id,
            "name": building.name,
            "description": building.description,
            "created_at": building.created_at.isoformat()
        }), 200
    else:
        return jsonify({"error": "Building not found"}), 404
    
@building_bp.route("/<int:building_id>", methods=["PUT"])
def update_building(building_id):
    building = Building.query.get(building_id)
    if not building:
        return jsonify({"error": "Building not found"}), 404

    data = request.get_json()
    if 'name' in data:
        building.name = data['name']
    if 'description' in data:
        building.description = data['description']

    db.session.commit()

    return jsonify({
        "message": "Building updated successfully",
        "building": {
            "building_id": building.building_id,
            "name": building.name,
            "description": building.description,
            "created_at": building.created_at.isoformat()
        }
    }), 200

@building_bp.route("/<int:building_id>", methods=["DELETE"])
def delete_building(building_id):
    building = Building.query.get(building_id)
    if not building:
        return jsonify({"error": "Building not found"}), 404

    db.session.delete(building)
    db.session.commit()

    return jsonify({"message": "Building deleted successfully"}), 200

@building_bp.route("/<int:building_id>/floors", methods=["GET"])
def get_building_floors(building_id):
    building = Building.query.get(building_id)
    if not building:
        return jsonify({"error": "Building not found"}), 404

    floors = Floor.query.filter_by(building_id=building_id).all()
    if floors:
        floors_list = [
            {
                "floor_id": f.floor_id,
                "building_id": f.building_id,
                "floor_number": f.floor_number,
                "map_img_url": f.map_img_url,
                "scale": f.scale,
                "origin_x": f.origin_x,
                "origin_y": f.origin_y,
                "created_at": f.created_at.isoformat()
            } for f in floors
        ]
        return jsonify({"floors": floors_list, "count": len(floors_list)}), 200
    else:
        return jsonify({"message": "No floors found for this building"}), 404