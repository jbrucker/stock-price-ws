"""Utility functions for working with the stock price data"""


import json
from typing import Any, Dict


def analyze_stock_prices(json_data: str) -> Dict[str, Any]:
    """
    Analyze stock price data from JSON string.

    Args:
        json_data: JSON string containing stock price data

    Returns:
        Dictionary with analysis results
    """
    data = json.loads(json_data)

    if not data:
        return {"error": "No data available"}

    closes = [day['close'] for day in data]
    volumes = [day['volume'] for day in data]

    analysis = {
        'period': {
            'start': data[0]['date'],
            'end': data[-1]['date'],
            'days': len(data)
        },
        'prices': {
            'current': closes[-1],
            'average': sum(closes) / len(closes),
            'high': max(closes),
            'low': min(closes),
            'change': closes[-1] - closes[0],
            'change_percent': (closes[-1] - closes[0]) / closes[0] * 100
        },
        'volume': {
            'average': sum(volumes) / len(volumes),
            'max': max(volumes),
            'min': min(volumes)
        }
    }

    return analysis
