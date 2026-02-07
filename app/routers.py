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
import json

from fastapi import APIRouter, HTTPException, Query, Response, Request
from .services import StockInfo
from .schemas import StockInfoSchema

router = APIRouter()


@router.get("/stock/{symbol}",
            response_model=StockInfoSchema,
            responses={ 200: {"description": "Success"},
                        404: {"description": "Stock symbol not found"},
                        500: {"description": "Internal server error"},
                        501: {"description": "Protobuf support not available"}}
            )
def get_stock_prices(symbol: str, request: Request,
                     limit: int = Query(100, ge=1,
                                    description="Number of most recent daily prices to return")
                     ):
    """Return {limit} days of stock price data, using content negotiation.

    The client's `Accept` header determines the response format. If the
    header contains a Protobuf MIME type, then return price data
    in  Protobuf-serialized format.  Otherwise JSON is returned.
    """
    accept = (request.headers.get("accept") or "").lower()

    # accept either MIME type name
    protobuf_types = ("application/protobuf", "application/x-protobuf")

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
            info = StockInfo(symbol).get_prices(limit)
            price_list = info.as_list()
            message = as_protobuf(symbol, stock_pb2, price_list)

            return Response(content=message.SerializeToString(),
                            media_type="application/protobuf"
                            )

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:  # pragma: no cover - surface errors to client
            raise HTTPException(status_code=500, detail=str(e))

    # Default to JSON format
    try:
        info = StockInfo(symbol).get_prices(limit)
        data = json.loads(info.as_json())
        # Validate and coerce types with Pydantic before returning
        schema = StockInfoSchema.model_validate(data)
        return schema
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
