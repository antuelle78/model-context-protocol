import requests
from app.schemas import GetStockPriceArgs
from app.config import settings

def get_stock_price(args: GetStockPriceArgs):
    """
    Fetches the current stock price for a given ticker symbol using Alpha Vantage.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={args.ticker}&apikey={settings.ALPHAVANTAGE_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price = data["Global Quote"]["05. price"]
            return f"The current stock price of {args.ticker} is {price}"
        else:
            return f"Could not find stock price for {args.ticker}. Response: {data}"
    except Exception as e:
        return f"An error occurred: {e}"
