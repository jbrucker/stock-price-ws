from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class StockPrice(BaseModel):
    date: str = Field(..., description="ISO date string (YYYY-MM-DD)")
    open: float
    high: float
    low: float
    close: float
    volume: int
    dividends: Optional[float] = None
    stock_splits: Optional[float] = None


class StockMetadata(BaseModel):
    name: Optional[str] = None
    currency: Optional[str] = None
    market_cap: Optional[int] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


class StockInfoSchema(BaseModel):
    """Schema representing the JSON payload produced by `StockInfo.as_json()`.

    Fields are aligned with the `StockInfo` class in `app/models/stock_info.py`:
      - `symbol`: uppercase ticker symbol
      - `retrieved_at`: ISO timestamp string
      - `prices`: list of `StockPrice` entries (one per day)
      - `metadata`: optional stock metadata
    """

    symbol: str
    retrieved_at: datetime
    prices: List[StockPrice]
    metadata: Optional[StockMetadata] = None

    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "retrieved_at": datetime.utcnow().isoformat(),
                "prices": [
                    {
                        "date": "2026-02-06",
                        "open": 150.12,
                        "high": 152.34,
                        "low": 149.77,
                        "close": 151.22,
                        "volume": 98765432,
                    }
                ],
                "metadata": {
                    "name": "Apple Inc.",
                    "currency": "USD",
                    "market_cap": 2500000000000,
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                },
            }
        }
