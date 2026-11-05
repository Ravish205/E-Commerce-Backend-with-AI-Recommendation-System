import os
from backend.app import create_app
from backend.app.models.base import db

env = os.environ.get("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
