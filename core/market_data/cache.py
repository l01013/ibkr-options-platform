"""Thread-safe in-memory data cache with TTL expiration."""

import time
import threading
from dataclasses import dataclass, field
from typing import Any
from config.settings import settings


@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    ttl: float

    @property
    def expired(self) -> bool:
        return (time.time() - self.timestamp) > self.ttl


class DataCache:
    """Thread-safe cache with separate namespaces for different data types."""

    def __init__(self):
        self._lock = threading.RLock()
        self._quotes: dict[str, CacheEntry] = {}       # symbol -> real-time quote
        self._bars: dict[str, CacheEntry] = {}          # "symbol:bar_size" -> historical bars
        self._options: dict[str, CacheEntry] = {}       # "symbol:expiry" -> options chain
        self._fundamentals: dict[str, CacheEntry] = {}  # symbol -> fundamental data
        self._misc: dict[str, CacheEntry] = {}          # generic key-value

    # ------------------------------------------------------------------
    # Quotes (real-time)
    # ------------------------------------------------------------------

    def set_quote(self, symbol: str, data: dict):
        with self._lock:
            self._quotes[symbol] = CacheEntry(
                value=data, timestamp=time.time(), ttl=settings.REALTIME_CACHE_TTL
            )

    def get_quote(self, symbol: str) -> dict | None:
        with self._lock:
            entry = self._quotes.get(symbol)
            if entry and not entry.expired:
                return entry.value
            return None

    def get_all_quotes(self) -> dict[str, dict]:
        with self._lock:
            return {
                sym: e.value
                for sym, e in self._quotes.items()
                if not e.expired
            }

    # ------------------------------------------------------------------
    # Historical Bars
    # ------------------------------------------------------------------

    def set_bars(self, symbol: str, bar_size: str, data: list):
        key = f"{symbol}:{bar_size}"
        with self._lock:
            self._bars[key] = CacheEntry(
                value=data, timestamp=time.time(), ttl=settings.HISTORICAL_CACHE_TTL
            )

    def get_bars(self, symbol: str, bar_size: str) -> list | None:
        key = f"{symbol}:{bar_size}"
        with self._lock:
            entry = self._bars.get(key)
            if entry and not entry.expired:
                return entry.value
            return None

    # ------------------------------------------------------------------
    # Options Chain
    # ------------------------------------------------------------------

    def set_options(self, symbol: str, expiry: str, data: list):
        key = f"{symbol}:{expiry}"
        with self._lock:
            self._options[key] = CacheEntry(
                value=data, timestamp=time.time(), ttl=settings.HISTORICAL_CACHE_TTL
            )

    def get_options(self, symbol: str, expiry: str) -> list | None:
        key = f"{symbol}:{expiry}"
        with self._lock:
            entry = self._options.get(key)
            if entry and not entry.expired:
                return entry.value
            return None

    # ------------------------------------------------------------------
    # Fundamentals
    # ------------------------------------------------------------------

    def set_fundamentals(self, symbol: str, data: dict):
        with self._lock:
            self._fundamentals[symbol] = CacheEntry(
                value=data, timestamp=time.time(), ttl=settings.FUNDAMENTALS_CACHE_TTL
            )

    def get_fundamentals(self, symbol: str) -> dict | None:
        with self._lock:
            entry = self._fundamentals.get(symbol)
            if entry and not entry.expired:
                return entry.value
            return None

    # ------------------------------------------------------------------
    # Misc / Generic
    # ------------------------------------------------------------------

    def set(self, key: str, value: Any, ttl: float = 60.0):
        with self._lock:
            self._misc[key] = CacheEntry(value=value, timestamp=time.time(), ttl=ttl)

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._misc.get(key)
            if entry and not entry.expired:
                return entry.value
            return None

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def clear_expired(self):
        """Remove all expired entries."""
        with self._lock:
            for store in (self._quotes, self._bars, self._options, self._fundamentals, self._misc):
                expired_keys = [k for k, v in store.items() if v.expired]
                for k in expired_keys:
                    del store[k]

    def clear_all(self):
        """Clear all caches."""
        with self._lock:
            self._quotes.clear()
            self._bars.clear()
            self._options.clear()
            self._fundamentals.clear()
            self._misc.clear()
