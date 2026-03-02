from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from db.db_app import db
from db.user import User
from seed import main_generate


app = Flask(__name__)

# SQLite configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Create tables
with app.app_context():
    db.create_all()


@app.route("/")
def hello():
    users = db.session.query(User).all()
    print(users)
    return {"status": "ok", "message": "Tables created successfully"}

@app.route("/generate")
def generate():
    main_generate()

    return {"status": "ok", "message": "generation completed"}


if __name__ == "__main__":
    app.run(debug=True)