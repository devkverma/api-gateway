from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

class API(Base):
    __tablename__ = "apis"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    base_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
    )