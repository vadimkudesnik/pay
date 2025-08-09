from typing import List

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    full_name = Column(String)
    is_admin = Column(Boolean, default=False)
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="user")
    accounts = relationship("Account", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    account_id = Column(
        Integer,
        Sequence("account_seq", start=1, increment=1),
        unique=False,
        autoincrement=True,
        nullable=False,
    )
    user_id = Column(Integer, ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    balance: Mapped[float] = mapped_column(Float, default=0.0)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True)
    account_id = Column(Integer, unique=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float)
    user: Mapped["User"] = relationship("User", back_populates="payments")
