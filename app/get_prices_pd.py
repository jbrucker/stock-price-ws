"""Get historical stock prices from Yahoo Finance.

Yahoo Finance can return historial prices in multiple formats.
Each day's price includes Open, High, Low, Close, and Volume.

Requires: yfinance and Pandas Python packages
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys


def get_stock_prices(symbol: str, howmany: int) -> pd.DataFrame:
    """
    Retrieve stock prices for a given symbol for the most recent trading days.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'META')
        howmany: Number of most recent trading days to retrieve

    Returns:
        pandas.DataFrame with historical price data including Open, High, Low, 
        Close, Volume columns indexed by date

    Raises:
        ValueError: If invalid symbol or no data available
        Exception: For network or API-related errors
    """
    try:
        # Create a Ticker object for the given symbol
        ticker = yf.Ticker(symbol)

        # Use period parameter to get the most recent data
        # Format: f"{howmany}d" for number of days
        period_str = f"{howmany}d"

        # Fetch historical data
        # The history() method returns OHLCV data by default[citation:2][citation:5]
        hist_data = ticker.history(period=period_str)

        # Check if we got any data
        if hist_data.empty:
            raise ValueError(f"No data available for symbol '{symbol}'. "
                           "Please check if the symbol is correct.")

        # Return the historical data
        return hist_data

    except Exception as e:
        # Re-raise the exception with additional context
        if isinstance(e, ValueError):
            raise e
        else:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")


# Alternative implementation using download() method
def get_stock_prices_alternative(symbol: str, howmany: int) -> pd.DataFrame:
    """
    Alternative implementation using yf.download() function.
    Some users prefer this approach for simpler syntax[citation:3][citation:7].
    """
    try:
        # Calculate start date based on howmany days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=howmany * 2)  # Buffer for non-trading days

        # Download data for the period
        data = yf.download(
            symbol, 
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False
        )

        # Get only the most recent 'howmany' days
        if not data.empty:
            return data.tail(howmany)
        else:
            raise ValueError(f"No data available for symbol '{symbol}'")

    except Exception as e:
        raise Exception(f"Error fetching data: {str(e)}")


# Example usage and demonstration
if __name__ == "__main__":
    # Example 1: Get last 10 days of Apple stock data
    print("Example 1: Getting last 10 days of Apple (AAPL) stock prices")
    print("-" * 60)
    try:
        apple_data = get_stock_prices("AAPL", 10)
        print(f"Retrieved {len(apple_data)} days of data for AAPL")
        print("\nLatest 5 rows of data:")
        print(apple_data.tail())

        # Show basic statistics
        print("\nSummary statistics for closing prices:")
        print(f"Latest Close: ${apple_data['Close'].iloc[-1]:.2f}")
        print(f"Recent High: ${apple_data['High'].max():.2f}")
        print(f"Recent Low: ${apple_data['Low'].min():.2f}")

    except Exception as e:
        print(f"Error: {e}")

    sys.exit(1)

    print("\n" + "=" * 60 + "\n")

    # Example 2: Get last 5 days of Tesla stock data
    print("Example 2: Getting last 5 days of Tesla (TSLA) stock prices")
    print("-" * 60)
    try:
        tesla_data = get_stock_prices("TSLA", 5)
        print(f"Retrieved {len(tesla_data)} days of data for TSLA")
        print("\nAll data:")
        print(tesla_data)

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60 + "\n")

    # Example 3: Handle error case
    print("Example 3: Testing error handling with invalid symbol")
    print("-" * 60)
    try:
        invalid_data = get_stock_prices("INVALID_SYMBOL", 5)
    except Exception as e:
        print(f"Expected error handled: {e}")
