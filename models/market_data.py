"""Market data database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from models.base import Base


class HistoricalBar(Base):
    __tablename__ = "historical_bars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), default="SMART")
    bar_size = Column(String(20), nullable=False)  # e.g. "1 day", "1 hour"
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, default=0)
    bar_count = Column(Integer, default=0)
    average = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_bars_symbol_size_ts", "symbol", "bar_size", "timestamp", unique=True),
    )


class OptionsSnapshot(Base):
    __tablename__ = "options_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    underlying = Column(String(20), nullable=False)
    expiry = Column(String(8), nullable=False)      # YYYYMMDD
    strike = Column(Float, nullable=False)
    right = Column(String(1), nullable=False)        # C or P
    bid = Column(Float)
    ask = Column(Float)
    last = Column(Float)
    volume = Column(Integer, default=0)
    open_interest = Column(Integer, default=0)
    implied_vol = Column(Float)
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)
    snapshot_time = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_opt_underlying_expiry", "underlying", "expiry", "strike", "right"),
    )
