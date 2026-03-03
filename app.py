from authzed.api.v1 import InsecureClient, WriteSchemaRequest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from db.db_app import db
from db.user import User
from db.project import Project
from db.resource_pool_group import ResourcePoolGroup
from spicedb_test.client import spicedb_client

from seed import main_generate


app = Flask(__name__)

# SQLite configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

schema = """
    definition user {}
    definition usergroup {
        relation direct_member: user

        permission member = direct_member
    }

    definition resource_pool_group {
        relation owner: user
        relation can_edit: user

        permission direct_permission = owner
        permission can_edit_permission = owner + can_edit
    }

    definition project {
        relation resource_pool_group: resource_pool_group
        relation owner: user
        relation editor: user 

        // Logical link (not used for lookup)

        // Runtime permission
        permission edit = owner + editor
    }

"""


spicedb_client.init_spicedb_client()

spicedb_client.client.WriteSchema(WriteSchemaRequest(schema=schema))


# Create tables
with app.app_context():
    db.create_all()


@app.route("/")
def hello():
    users = db.session.query(User).all()
    print(users)
    return {"status": "ok", "message": "Tables created successfully"}
#
@app.route("/generate")
def generate():
    main_generate()

    return {"status": "ok", "message": "generation completed"}


if __name__ == "__main__":
    app.run(debug=True)