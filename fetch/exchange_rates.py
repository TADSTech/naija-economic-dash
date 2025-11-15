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
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Return the full data - could be a list or single object
            return data
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
        return f"{num:,.4f}"
    except (ValueError, TypeError):
        return x # Return original value if conversion fails

def fetch_exchange_rates():
    """
    Fetches exchange rates from CBN's JSON APIs.
    Attempts to get as many records as possible by trying different endpoints.
    Uses caching to avoid repeated API calls.

    Returns:
        pandas.DataFrame: A DataFrame containing exchange rates.
                          Returns an empty DataFrame on failure.
    """
    cache_file = "data/exchange_rates_cache.json"
    
    # Try to load from cache first
    cached_df = load_cached_data(cache_file)
    if cached_df is not None:
        return cached_df

    # Try multiple endpoints to get comprehensive exchange rate data
    endpoints_to_try = [
        "GetAllExchangeRates",  # Main exchange rates endpoint
        "GetExchangeRates",     # Alternative endpoint
        "GetAllRates",          # Another possible endpoint
    ]

    all_data = []

    for endpoint in endpoints_to_try:
        print(f"Trying endpoint: {endpoint}")
        data = fetch_api_data(endpoint)

        if data:
            print(f"Successfully fetched data from {endpoint}")
            # Handle both single object and list responses
            if isinstance(data, list):
                if len(data) > 0:
                    all_data.extend(data)
                    print(f"Added {len(data)} records from {endpoint}")
                else:
                    print(f"Empty list from {endpoint}")
            else:
                # Single object, add to list
                all_data.append(data)
                print(f"Added 1 record from {endpoint}")
        else:
            print(f"No data from {endpoint}")

    if not all_data:
        print("Warning: Failed to fetch exchange rate data from all endpoints.")
        return pd.DataFrame(columns=["Currency", "Date", "Buying Rate", "Central Rate", "Selling Rate"])

    # Convert to DataFrame
    try:
        df = pd.DataFrame(all_data)

        # Remove unwanted columns if they exist
        columns_to_remove = ['id', 'noOfDeals', 'created_at', 'updated_at']
        df = df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors='ignore')

        # Rename columns to match expected format
        column_mapping = {
            'currency': 'Currency',
            'ratedate': 'Date',
            'buyingrate': 'Buying Rate',
            'centralrate': 'Central Rate',
            'sellingrate': 'Selling Rate',
            'currencyname': 'Currency',
            'rate_date': 'Date',
            'buying_rate': 'Buying Rate',
            'central_rate': 'Central Rate',
            'selling_rate': 'Selling Rate'
        }

        df = df.rename(columns=column_mapping)

        # Convert date column if it exists
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')

        # Format numeric columns with commas
        numeric_columns = ['Buying Rate', 'Central Rate', 'Selling Rate']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(number_with_commas)

        # Remove duplicates based on Currency and Date
        if 'Currency' in df.columns and 'Date' in df.columns:
            df = df.drop_duplicates(subset=['Currency', 'Date'], keep='first')

        # Sort by date descending (most recent first), then by currency
        if 'Date' in df.columns:
            df = df.sort_values(['Date', 'Currency'], ascending=[False, True])

        # Select only the columns we want to display
        display_columns = ["Currency", "Date", "Buying Rate", "Central Rate", "Selling Rate"]
        available_columns = [col for col in display_columns if col in df.columns]
        df = df[available_columns]

        print(f"Successfully processed exchange rates. Total records: {len(df)}")
        # Save to cache
        save_cached_data(cache_file, df)
        return df

    except Exception as e:
        print(f"Error processing exchange rate data: {e}")
        return pd.DataFrame(columns=["Currency", "Date", "Buying Rate", "Central Rate", "Selling Rate"])

if __name__ == "__main__":
    # This allows you to test the script directly
    # Run: python fetch/exchange_rates.py
    df = fetch_exchange_rates()
    if not df.empty:
        print("Data fetched successfully:")
        print(df.head(15))  # Show first 15 rows
        print(f"\nTotal records: {len(df)}")
        print(f"Unique currencies: {df['Currency'].nunique() if 'Currency' in df.columns else 'N/A'}")
    else:
        print("Failed to fetch data.")