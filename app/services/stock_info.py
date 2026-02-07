"""Module to get historical stock price data from YFinance.

StockInfo class has methods:
get_prices(howmany: int)
- get historical stock price data from YFinance
as_list()
- return the data as a Python list (1 element per day) of dicts containing the price data
as_json(include_metadata=True|False)
- return the data as a JSON string, with optional metadata

YFinance is an open-source project that retrieves and reformats data from Yahoo Finance.
YFinance is *not* part of Yahoo Finance. YFinance *scrapes* data from Yahoo Finance web pages.
"""

from __future__ import annotations
from functools import lru_cache
import logging
import yfinance as yf
import json
from datetime import datetime
from typing import Any
import pandas as pd

# Round float prices to 2 decimal places? This removes noise in price data scraped by YFinance.
# If DECIMAL_PLACES > 0 then round prices to that many decimal places
DECIMAL_PLACES = 2


class StockInfo:
    """Get historial stock price data for one stock symbol.

    Data can be returned as JSON string, Python list of dicts, or Pandas Dataframe.

    Attributes:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'MSFT')
        prices: DataFrame of historical price data (from YFinance, cached by get_prices())
        ticker: yfinance Ticker object for symbol
    Usage:
        apple = StockInfo("AAPL")
    
    :params symbol: Stock ticker symbol, such as 'AAPL', 'MSFT', "BYDDF", "GOOG"
    """

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.prices = pd.DataFrame()
        try:
            self.ticker = yf.Ticker(symbol)
        except Exception as e:
            logging.error(f"Error creating Ticker for symbol {symbol}: {str(e)}")
            if isinstance(e, ValueError):
                raise e
            else:
                raise Exception(f"Error fetching data for {symbol}: {str(e)}")

    # cache the most recent 64 calls
    @lru_cache(maxsize=64)
    def get_prices(self, howmany: int) -> StockInfo:
        """
        Retrieve stock prices for a given symbol for the most recent trading days.

        :param howmany: Number of most recent trading days to retrieve
        :returns: reference to self with prices attribute populated
        :raises ValueError: If invalid parameter or no data available
        :raises Exception: For network or API-related errors
        """
        try:
            # Use period parameter to get the most recent data
            period_str = f"{howmany}d"

            # Fetch historical data
            self.prices = self.ticker.history(period=period_str)

            # Check if we got any data
            if self.prices.empty:
                raise ValueError(f"No data available for symbol '{self.symbol}'. "
                                 "Please check if the symbol is correct.")
            # Remove noise by rounding prices,
            # but don't round dividends or stock splits.
            price_columns = ['Open', 'High', 'Low', 'Close']
            if DECIMAL_PLACES > 0:
                self.prices[price_columns] = self.prices[price_columns].round(DECIMAL_PLACES)
        except Exception as e:
            # Re-raise the exception with additional context
            raise Exception(f"Error fetching data for {self.symbol}: {str(e)}")
        return self

    def as_list(self) -> list[dict[str, Any]]:
        """
        Convert the stock price data (DataFrame) to a list of Dicts.

        :returns: list containing stock price data. One element per day.
        :raises Error: If no price data

        Example:
        >>> apple = StockPriceData("AAPL").get_prices(50)
        >>> price_list = apple.as_list()
        """
        if self.prices is None or self.prices.empty:
            raise ValueError("No price data cached. Please call get_prices(n) first.")

        price_list = []

        for date, row in self.prices.iterrows():
            # Convert date to string format
            date_str = date.strftime('%Y-%m-%d')

            # Create a dictionary for this day's data
            price_data = {
                'date': date_str,
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            }

            # Add additional fields if they exist
            # row['Dividends'] > 0 returns np.False, so cast to bool.
            if 'Dividends' in row and row['Dividends'] and float(row['Dividends']) > 0:
                price_data['dividends'] = float(row['Dividends'])

            if 'Stock Splits' in row and row['Stock Splits'] and float(row['Stock Splits']) > 0:
                price_data['stock_splits'] = float(row['Stock Splits'])

            price_list.append(price_data)

        return price_list

    def as_json(self, include_metadata: bool = False) -> str:
        """
        Convert the previously retreived stock prices (DataFrame) to a JSON string.

        :param metadata: Whether to include stock metadata in the response
        :returns: string containing stock price data in JSON format.
        :raises ValueError: If no data is cached

        Example:
        >>> apple = StockPriceData("AAPL").get_prices(50)
        >>> json_data = apple.as_json()
        # print the price data
        >>> print(json_data["prices"])
        """
        price_list = self.as_list()
        response = {
            'symbol': self.symbol.upper(),
            'retrieved_at': datetime.now().isoformat(),
            'prices': price_list,
            # 'count': len(price_list),
        }
        # Add metadata if requested
        if include_metadata:
            response['metadata'] = self.get_metadata()
        return json.dumps(response, indent=2)

    def get_metadata(self) -> dict[str, Any]:
        """Return stock info metadata, such as company name, market cap, and industry.

        :returns: dict of metadata regarding the stock
        """
        info = self.ticker.info
        metadata = {
                'name': info.get('longName', ''),
                'currency': info.get('currency', 'USD'),
                'market_cap': info.get('marketCap'),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', '')
                }
        return metadata

    def as_dataframe(self) -> pd.DataFrame:
        """
        Return the cached stock prices as a Pandas DataFrame.

        :returns: DataFrame containing stock price data
        :raises ValueError: If no data is cached
        """
        if self.prices is None or self.prices.empty:
            raise ValueError("No price data cached. Please call get_prices(n) first.")
        return self.prices


# Example usage
if __name__ == "__main__":
    draw_line = lambda: print("-" * 64)  # noqa: E731 Do not assign a lambda expression
    # Example 1: Get last 5 days of Apple stock data as JSON
    NUM_DAYS = 5
    print(f"Example 1: Getting last 5 days of Apple (AAPL) stock prices as JSON")
    draw_line()
    try:
        apple = StockInfo("AAPL").get_prices(NUM_DAYS)
        print("JSON Response:")
        print(apple.as_json())

        print()
        print("As Python list of dict")
        print(apple.as_list())

    except Exception as e:
        print(f"Error: {e}")

    print()

    # Example 2: Get data as Python list
    print("Example 2: Getting last 3 days of Microsoft data as Python list")
    draw_line()
    try:
        msft = StockInfo("MSFT").get_prices(3)
        msft_list = msft.as_list()
        print(f"Type of response: {type(msft_list)}")
        print(f"Number of days: {len(msft_list)}")
        print("\nList structure:")
        for i, day_data in enumerate(msft_list):
            print(f"[{i}]: {day_data}")

    except Exception as e:
        print(f"Error: {e}")
