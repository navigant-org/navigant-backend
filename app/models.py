from app import db
from datetime import datetime

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Node(db.Model):
    node_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    x_coordinate = db.Column(db.Float, nullable=False)
    y_coordinate = db.Column(db.Float, nullable=False)
    node_type = db.Column(db.String(50), nullable=False)
    floor_id = db.Column(db.Integer, db.ForeignKey('floor.floor_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Edge(db.Model):
    edge_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_node_id = db.Column(db.Integer, db.ForeignKey('node.node_id'), nullable=False)
    end_node_id = db.Column(db.Integer, db.ForeignKey('node.node_id'), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    floor_id = db.Column(db.Integer, db.ForeignKey('floor.floor_id'), nullable=False)
    is_walkable = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Floor(db.Model):
    floor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.building_id'), nullable=False)
    floor_number = db.Column(db.Integer, nullable=False)
    map_img_url = db.Column(db.String(500), nullable=True)
    scale = db.Column(db.Float, nullable=False, default=1.0)
    origin_x = db.Column(db.Float, nullable=False, default=0.0)
    origin_y = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Building(db.Model):
    building_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Mg_Raw_Reading(db.Model):
    reading_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(100), db.ForeignKey('mg_session.session_id'), nullable=False)
    mag_x = db.Column(db.Float, nullable=False)
    mag_y = db.Column(db.Float, nullable=False)
    mag_z = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class Mg_session(db.Model):
    session_id = db.Column(db.String(100), primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('node.node_id'), nullable=False)
    # device_id = db.Column(db.String(100), nullable=False)
    # started_at = db.Column(db.DateTime, default=datetime.utcnow)
    # ended_at = db.Column(db.DateTime, nullable=True)
    
class Mg_Fingerprint(db.Model):
    fingerprint_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    node_id = db.Column(db.Integer, db.ForeignKey('node.node_id'), nullable=False)
    mean_x = db.Column(db.Float, nullable=False)
    mean_y = db.Column(db.Float, nullable=False)
    mean_z = db.Column(db.Float, nullable=False)
    std_x = db.Column(db.Float, nullable=False)
    std_y = db.Column(db.Float, nullable=False)
    std_z = db.Column(db.Float, nullable=False)
    sample_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class ML_model(db.Model):
    model_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_type = db.Column(db.String(100), nullable=False)
    window_size = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Localization_log(db.Model):
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_model.model_id'), nullable=False)
    predicted_node_id = db.Column(db.Integer, db.ForeignKey('node.node_id'), nullable=False)
    actual_node_id = db.Column(db.Integer, db.ForeignKey('node.node_id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)