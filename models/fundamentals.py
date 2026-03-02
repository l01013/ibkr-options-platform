"""Fundamental data database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from models.base import Base


class FundamentalData(Base):
    __tablename__ = "fundamentals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, unique=True)
    company_name = Column(String(200))
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Float)            # in USD
    pe_ratio = Column(Float)
    forward_pe = Column(Float)
    eps = Column(Float)
    revenue = Column(Float)               # in USD
    revenue_growth = Column(Float)        # percentage
    profit_margin = Column(Float)         # percentage
    dividend_yield = Column(Float)        # percentage
    beta = Column(Float)
    week52_high = Column(Float)
    week52_low = Column(Float)
    avg_volume = Column(Integer)
    shares_outstanding = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_fundamentals_symbol", "symbol"),
    )
