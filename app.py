import time

from authzed.api.v1 import InsecureClient, WriteSchemaRequest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from query_example import get_projects
from db.db_app import db
from db.project import Project

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
    projects = db.session.query(Project).all()
    print(len(projects), " sum projects")
    return {"status": "ok", "message": "Tables created successfully"}
#
@app.route("/generate")
def generate():
    main_generate()

    return {"status": "ok", "message": "generation completed"}


def execute_example():
    start = time.perf_counter()
    get_projects(db.session, 149, 'project', 'owner',0,'m')
    end = time.perf_counter()
    print("total",end - start)

if __name__ == "__main__":
    #user_id 149
    app.run(debug=False)