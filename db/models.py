from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, BigInteger, DateTime, DECIMAL, ForeignKey
from typing import Optional
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

class Record(Base):
    __tablename__ = "records"
    record_id: Mapped[str] = mapped_column(String(36), primary_key=True) 
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    occurred_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False) 
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
