from db.db_app import app, db
from db.user import User

#
# @app.route("/")
# def hello():
#     users = db.session.query(User).all()
#     print(users)
#     return {"status": "ok", "message": "Tables created successfully"}