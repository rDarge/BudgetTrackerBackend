from datetime import datetime
from typing import List
from sqlalchemy import (
    Boolean,
    ForeignKey,
    LargeBinary,
    String,
    DateTime,
    Float,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    pass


class TransactionFile(Base):
    __tablename__ = "transaction_file"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(200))
    data: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    transactions: Mapped[List["Transaction"]] = relationship("Transaction")


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="account")


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    init_date: Mapped[datetime | None] = mapped_column(DateTime)
    post_date: Mapped[datetime] = mapped_column(DateTime)
    description: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(Float)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", name="transaction_account_id")
    )
    account: Mapped[Account] = relationship(back_populates="transactions")

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("category.id", name="transaction_category_id")
    )
    category: Mapped["Category"] = relationship(back_populates="transactions")

    source_file_id: Mapped[int | None] = mapped_column(
        ForeignKey("transaction_file.id", name="transaction_file_id")
    )
    source_file: Mapped[TransactionFile] = relationship(back_populates="transactions")

    __table_args__ = (
        UniqueConstraint("post_date", "description", "amount", name="_transaction_uc"),
    )


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    transactions: Mapped[List[Transaction]] = relationship(back_populates="category")

    rules: Mapped[List["Rule"]] = relationship(back_populates="category")

    supercategory_id: Mapped[int] = mapped_column(ForeignKey("supercategory.id"))
    supercategory: Mapped["Supercategory"] = relationship(back_populates="categories")


class Supercategory(Base):
    __tablename__ = "supercategory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    categories: Mapped[List[Category]] = relationship()


class Rule(Base):
    __tablename__ = "rule"

    id: Mapped[int] = mapped_column(primary_key=True)

    contains: Mapped[str] = mapped_column(String(100))
    case_sensitive: Mapped[bool] = mapped_column(Boolean)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("category.id", name="rule_category_id")
    )
    category: Mapped["Category"] = relationship(back_populates="rules")
