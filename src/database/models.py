from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date
from datetime import date


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(25))
    last_name: Mapped[str] = mapped_column(String(25))
    email: Mapped[str] = mapped_column(String(75))
    phone_number: Mapped[int] = mapped_column(String(15))
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
