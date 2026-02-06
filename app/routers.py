"""Web service endpoints to get historical stock price data.

This module exposes a FastAPI `APIRouter` with endpoint:

GET /stock/{symbol} return price data in JSON or Protobuf format

The Protobuf endpoint attempts to import a generated `app.protos.stock_pb2`
module (created from `app/protos/stock.proto`). If the generated module or
the `protobuf` runtime is not available, the endpoint returns HTTP 501 with
instructions to enable Protobuf support.
"""

from __future__ import annotations
import datetime

from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from typing import Any
import json

from .models import StockInfo

router = APIRouter()


@router.get("/stock/{symbol}")
def get_stock_prices(symbol: str, request: Request) -> Any:
    """Return 100 days of stock price data, using content negotiation.

    The client's `Accept` header determines the response format. If the
    header contains a Protobuf MIME type (e.g. `application/x-protobuf` or
    `application/protobuf`), the endpoint returns a serialized
    `StockPrices` Protobuf message with `application/x-protobuf` media type.
    Otherwise JSON is returned.
    """
    accept = (request.headers.get("accept") or "").lower()

    protobuf_types = (
        "application/x-protobuf",
        "application/protobuf",
        "application/vnd.google.protobuf",
    )

    wants_protobuf = any(t in accept for t in protobuf_types)

    # If client prefers Protobuf, try to return Protobuf
    if wants_protobuf:
        try:
            from app.protos import stock_pb2  # type: ignore
        except Exception:
            raise HTTPException(
                status_code=501,
                detail=(
                    "Protobuf support not available. Generate app/protos/stock_pb2 "
                    "from app/protos/stock.proto and install 'protobuf' package."
                ),
            )

        try:
            info = StockInfo(symbol).get_prices(100)
            price_list = info.as_list()
            message = as_protobuf(symbol, stock_pb2, price_list)

            return Response(content=message.SerializeToString(),
                            media_type="application/x-protobuf"
                            )

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:  # pragma: no cover - surface errors to client
            raise HTTPException(status_code=500, detail=str(e))

    # Default to JSON format
    try:
        info = StockInfo(symbol).get_prices(100)
        data = json.loads(info.as_json())
        return JSONResponse(content=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:  # pragma: no cover - surface errors to client
        raise HTTPException(status_code=500, detail=str(e))


def as_protobuf(symbol, stock_pb2, price_list):
    """Write stock price data to a Protobuf StockPrices message."""
    msg = stock_pb2.StockPrices()
    msg.symbol = symbol.upper()
    if hasattr(msg, "retrieved_at"):
        msg.retrieved_at = datetime.datetime.now().isoformat()

    for p in price_list:
        item = msg.prices.add()
        item.date = p.get("date", "")
        item.open = float(p.get("open", 0.0))
        item.high = float(p.get("high", 0.0))
        item.low = float(p.get("low", 0.0))
        item.close = float(p.get("close", 0.0))
        item.volume = int(p.get("volume", 0))
        if "dividends" in p:
            item.dividends = float(p["dividends"])
        if "stock_splits" in p:
            item.stock_splits = float(p["stock_splits"])
    return msg
