import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config


# Initialize Extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL missing - refusing to start with SQLite")

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize Plugins
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS (Allow React Admin & Unity App to talk to us)
    CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]) 

    # Import models so Flask-Migrate can detect them
    from app import models

    # Register Blueprints (Routes)
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.building import building_bp
    from app.routes.floor import floor_bp
    from app.routes.node import node_bp
    from app.routes.edge import edge_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(building_bp, url_prefix='/api/buildings')
    app.register_blueprint(floor_bp, url_prefix='/api/floors')
    app.register_blueprint(node_bp, url_prefix='/api/nodes')
    app.register_blueprint(edge_bp, url_prefix='/api/edges')

    return app