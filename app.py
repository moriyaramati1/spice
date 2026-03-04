from authzed.api.v1 import InsecureClient, WriteSchemaRequest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from db.db_app import db
from db.user import User
from db.project import Project
from db.resource_pool_group import ResourcePoolGroup
from redis_client import redis_client
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
      relation parent: resource_pool_group
      relation owner: user | usergroup#member
    
      permission edit = parent->edit + owner      
    }


    definition project {
      relation resource_pool_group: resource_pool_group
      relation responsible_team: usergroup
      relation owner: user | usergroup#member
    
      permission edit = owner + responsible_team->member + resource_pool_group->edit
      permission create_deployment = owner + responsible_team->member
      permission resources_editor = resource_pool_group->member 
    }

"""


spicedb_client.init_spicedb_client()

spicedb_client.client.WriteSchema(WriteSchemaRequest(schema=schema))

for event in spicedb_client.client.watch_relationships():
    print("New change detected")

    for update in event.updates:
        relation = update.relationship
        redis_client.sadd(f"{relation.subject.object.object_id}:{relation.relation}", relation.resource.object_id)
        redis_client.sadd(f"{relation.resource.object_id}:{relation.relation}_users", relation.subject.object.object_id)

        # print(
        #     f"Resource: {relation.resource.object_type}:{relation.resource.object_id} | "
        #     f"Relation: {relation.relation} | "
        #     f"Subject: {relation.subject.object.object_type}:{relation.subject.object.object_id}"
        # )



# Create tables
with app.app_context():
    db.create_all()


@app.route("/")
def hello():
    projects = db.session.query(ResourcePoolGroup).all()
    print(len(projects), " sum projects")
    return {"status": "ok", "message": "Tables created successfully"}
#
@app.route("/generate")
def generate():
    main_generate()

    return {"status": "ok", "message": "generation completed"}


if __name__ == "__main__":
    app.run(debug=True)