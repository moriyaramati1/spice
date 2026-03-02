from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import String, ForeignKey
import uuid
class Base(DeclarativeBase):
    pass
def uuid4_str():
    return str(uuid.uuid4())