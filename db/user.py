from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    is_group: Mapped[bool] = mapped_column(Boolean, default=False)