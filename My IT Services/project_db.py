from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import (
    create_engine,
    ForeignKey,
    String,
    Boolean,
    Integer,
    DateTime,
    inspect,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)


DATABASE_URL = "sqlite:///project.db"


class Base(DeclarativeBase):
    pass


class User(UserMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False,
    )

    requests: Mapped[list["Request"]] = relationship(
        back_populates="user"
    )

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="user"
    )


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    price: Mapped[float] = mapped_column(
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    requests: Mapped[list["Request"]] = relationship(
        back_populates="service"
    )


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped[User] = relationship(
        back_populates="requests"
    )

    service: Mapped[Service] = relationship(
        back_populates="requests"
    )

    review: Mapped["Review | None"] = relationship(
        back_populates="request",
        uselist=False,
    )

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    request_id: Mapped[int] = mapped_column(
        ForeignKey("requests.id"),
        unique=True,
        nullable=False,
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    comment: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="reviews"
    )

    request: Mapped["Request"] = relationship(
        back_populates="review"
    )


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    # Создаём отсутствующие таблицы.
    Base.metadata.create_all(engine)

    # Добавляем дату к существующим заявкам,
    # если в старой базе такого столбца ещё нет.
    request_columns = {
        column["name"]
        for column in inspect(engine).get_columns("requests")
    }

    if "created_at" not in request_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE requests "
                    "ADD COLUMN created_at DATETIME"
                )
            )

            connection.execute(
                text(
                    "UPDATE requests "
                    "SET created_at = CURRENT_TIMESTAMP "
                    "WHERE created_at IS NULL"
                )
            )


if __name__ == "__main__":
    print("База даних успішно створена!")