import requests
import pandas as pd
import io
import math
import os
import json
from datetime import datetime, timedelta

CACHE_DURATION_HOURS = 24  # Cache data for 24 hours

def load_cached_data(cache_file):
    """Load data from cache if it exists and is not expired."""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=CACHE_DURATION_HOURS):
                print(f"Loading cached data from {cache_file}")
                return pd.DataFrame(cache_data['data'])
            else:
                print(f"Cache expired for {cache_file}, fetching fresh data")
        except Exception as e:
            print(f"Error loading cache {cache_file}: {e}")
    return None

def save_cached_data(cache_file, df):
    """Save data to cache with timestamp."""
    try:
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': df.to_dict('records')
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        print(f"Saved data to cache: {cache_file}")
    except Exception as e:
        print(f"Error saving cache {cache_file}: {e}")

def fetch_api_data(endpoint):
    """Helper function to fetch data from a specific CBN API endpoint."""
    base_url = "https://www.cbn.gov.ng/api/"
    url = f"{base_url}{endpoint}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # The APIs return a list, we want the first (and likely only) item
            if data and isinstance(data, list):
                return data[0]
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def number_with_commas(x):
    """Formats a number with commas, mimicking the JS function."""
    try:
        # Convert to float first in case it's a string
        num = float(x)
        # Use f-string formatting for commas
        return f"{num:,.2f}"
    except (ValueError, TypeError):
        return x # Return original value if conversion fails

def fetch_macro_indicators():
    """
    Fetches the Macro Economic Indicators from CBN's JSON APIs.
    Uses caching to avoid repeated API calls.
    
    Returns:
        pandas.DataFrame: A DataFrame containing the indicators.
                          Returns an empty DataFrame on failure.
    """
    cache_file = "data/cbn_indicators_cache.json"
    
    # Try to load from cache first
    cached_df = load_cached_data(cache_file)
    if cached_df is not None:
        return cached_df
    
    print("Fetching CBN macro indicators from APIs...")
    
    indicators_list = []
    
    # --- Fetch all data first ---
    money_credit_data = fetch_api_data("GetAllMoneyAndCreditStats")
    inflation_data = fetch_api_data("GetAllInflationRates")
    call_rate_data = fetch_api_data("GetTopInterbankCallRate")
    money_market_data = fetch_api_data("GetAllMoneyMarketIndicators")
    securities_data = fetch_api_data("GetSecurities_NTB_TOP")
    crude_oil_data = fetch_api_data("GetAllCrudeOilPrices")

    # --- 1. Money Supply (M3) ---
    if money_credit_data:
        indicators_list.append({
            "Economic Indicators": "Money Supply (M3)",
            "Value": f"=N={number_with_commas(money_credit_data.get('moneySupply_M3', 0))} million",
            "As at:": money_credit_data.get('period', 'N/A')
        })
        
    # --- 2. Credit to Other Sectors ---
        indicators_list.append({
            "Economic Indicators": "Credit to Other Sectors",
            "Value": f"=N={number_with_commas(money_credit_data.get('creditToPrivateSector', 0))} million",
            "As at:": money_credit_data.get('period', 'N/A')
        })
    
    # --- 3. Inflation Rate ---
    if inflation_data:
        indicators_list.append({
            "Economic Indicators": "Year-on-Year All Item Inflation Rate",
            "Value": f"{inflation_data.get('allItemsYearOn', 'N/A')}%",
            "As at:": inflation_data.get('period', 'N/A')
        })

    # --- 4. Inter-bank Call Rate ---
    if call_rate_data:
        indicators_list.append({
            "Economic Indicators": "Average Inter-bank Call Rate",
            "Value": f"{call_rate_data.get('weightedaverage', 'N/A')}%",
            "As at:": call_rate_data.get('ratedate', 'N/A')
        })

    # --- 5. Monetary Policy Rate ---
    if money_market_data:
        indicators_list.append({
            "Economic Indicators": "Monetary Policy Rate",
            "Value": f"{money_market_data.get('mpr', 'N/A')}%",
            "As at:": money_market_data.get('period', 'N/A')
        })

    # --- 6. Treasury Bill Rate 91-Day Tenor ---
    if securities_data:
        # Mimic the JS rounding: Math.round(rate * 100) / 100
        rate = securities_data.get('rate', 0)
        try:
            rounded_rate = round(float(rate) * 100) / 100
        except ValueError:
            rounded_rate = 'N/A'
            
        indicators_list.append({
            "Economic Indicators": "Treasury Bill Rate 91-Day Tenor",
            "Value": f"{rounded_rate}%",
            "As at:": securities_data.get('auctionDate', 'N/A')
        })

    # --- 7. 3-Month Tenor Deposit Rate ---
    if money_market_data: # Re-use this data
        indicators_list.append({
            "Economic Indicators": "3-Month Tenor Deposit Rate of Banks",
            "Value": f"{money_market_data.get('threeMonthsDeposit', 'N/A')}%",
            "As at:": money_market_data.get('period', 'N/A')
        })

    # --- 8. Prime Lending Rate ---
        indicators_list.append({
            "Economic Indicators": "Monthly Average Prime Lending Rate",
            "Value": f"{money_market_data.get('primeLending', 'N/A')}%",
            "As at:": money_market_data.get('period', 'N/A')
        })

    # --- 9. Crude Oil Price ---
    if crude_oil_data:
        indicators_list.append({
            "Economic Indicators": "Spot Price of Nigeria's Reference Crude Oil",
            "Value": f"US ${crude_oil_data.get('crudeOilPrice', 'N/A')}",
            "As at:": crude_oil_data.get('period', 'N/A')
        })

    # --- Convert list of dicts to DataFrame ---
    if not indicators_list:
        print("Warning: Failed to fetch any indicator data.")
        return pd.DataFrame(columns=["Economic Indicators", "Value", "As at:"])

    print("Successfully fetched indicators from APIs.")
    df = pd.DataFrame(indicators_list)
    
    # Save to cache
    save_cached_data(cache_file, df)
    
    return df

if __name__ == "__main__":
    # This allows you to test the script directly
    # Run: python fetch/cbn_indicators.py
    df = fetch_macro_indicators()
    if not df.empty:
        print("Data fetched successfully:")
        print(df)
    else:
        print("Failed to fetch data.")