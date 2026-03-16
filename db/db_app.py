from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from db.base import Base



db = SQLAlchemy(model_class=Base)
