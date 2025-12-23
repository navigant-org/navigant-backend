# navigant-backend

Minimal Flask backend with SQLAlchemy, Flask-Migrate, and CORS.

## Setup

```bash
python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Running the app

```bash
flask run
```

The API root is available at `GET /api/`

## Database migrations

```bash
export FLASK_APP=run.py
flask db init      # first time only
flask db migrate   # generate migration
flask db upgrade   # apply migration
```

Models live in `app/models.py` and Flask extensions are initialized in
`app/__init__.py` via the application factory `create_app`.
