import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# Cache file path
CACHE_FILE = 'data/real_gdp_cache.json'
CACHE_DURATION = timedelta(hours=24)

def fetch_real_gdp():
    """
    Fetch Real GDP data from CBN APIs with caching
    Returns a DataFrame with Real GDP by sector and component
    """

    # Check cache first
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time < CACHE_DURATION:
                    print("Loading cached data from", CACHE_FILE)
                    return pd.DataFrame(cache_data['data'])
        except (json.JSONDecodeError, KeyError):
            pass

    print("Fetching fresh Real GDP data...")

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # API endpoints to try
    endpoints = [
        "GetRealGDPGRAPH",
        "GetLatestRealGDP",
        "GetAllRealGDP"
    ]

    all_data = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for endpoint in endpoints:
        try:
            url = f"https://www.cbn.gov.ng/api/{endpoint}"
            print(f"Trying endpoint: {endpoint}")

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                print(f"Successfully fetched data from {endpoint}")
                print(f"Added {len(data)} records from {endpoint}")

                # Process the data
                if endpoint == "GetRealGDPGRAPH":
                    # This is likely chart data with time series
                    for item in data:
                        if isinstance(item, dict):
                            all_data.append(item)
                else:
                    # This is likely detailed sector data
                    for item in data:
                        if isinstance(item, dict):
                            all_data.append(item)

        except Exception as e:
            print(f"Error fetching from {endpoint}: {e}")
            continue

    if not all_data:
        print("No data fetched from any endpoint, using sample data")
        # Sample data structure based on the HTML
        sample_data = [
            {
                'Year': 2024,
                'Quarter': 'Q1',
                'Agriculture': 3851.89,
                'Crop Production': 3516.32,
                'Livestock': 169.62,
                'Forestry': 45.90,
                'Fishing': 120.04,
                'Industry': 3817.77,
                'Mining and Quarrying': 1181.94,
                'Manufacturing': 1824.14,
                'Electricity Gas Steam': 733.71,
                'Water Supply': 10.00,
                'Construction': 57.98,
                'Services': 10608.55,
                'Trade': 2870.16,
                'Accommodation Food': 184.67,
                'Transportation Storage': 216.34,
                'Information Communication': 173.32,
                'Financial Insurance': 3269.60,
                'Real Estate': 264.80,
                'Professional Services': 5.66,
                'Administrative Services': 239.96,
                'Public Administration': 359.17,
                'Education': 57.11,
                'Health Services': 1245.60,
                'Other Services': 1160.78,
                'GDP at 2010 Constant Basic Prices': 18278.21,
                'Net Taxes on Products': 218.96,
                'GDP at 2010 Constant Market Prices': 18497.17
            }
        ]
        all_data = sample_data

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    # Clean and format the data
    if not df.empty:
        # Format numeric columns
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            df[col] = df[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "0.00")

        # Ensure Year column exists
        if 'Year' not in df.columns and 'tyear' in df.columns:
            df['Year'] = df['tyear']

        # Reorder columns to match the expected structure
        desired_columns = [
            'Year', 'Quarter',
            'Agriculture', 'Crop Production', 'Livestock', 'Forestry', 'Fishing',
            'Industry', 'Mining and Quarrying', 'Manufacturing',
            'Electricity Gas Steam', 'Water Supply', 'Construction',
            'Services', 'Trade', 'Accommodation Food', 'Transportation Storage',
            'Information Communication', 'Financial Insurance', 'Real Estate',
            'Professional Services', 'Administrative Services', 'Public Administration',
            'Education', 'Health Services', 'Other Services',
            'GDP at 2010 Constant Basic Prices', 'Net Taxes on Products',
            'GDP at 2010 Constant Market Prices'
        ]

        # Only include columns that exist in the dataframe
        available_columns = [col for col in desired_columns if col in df.columns]
        df = df[available_columns]

    print(f"Successfully processed Real GDP data. Total records: {len(df)}")

    # Save to cache
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'data': df.to_dict('records')
    }

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)

    print(f"Saved data to cache: {CACHE_FILE}")

    return df

if __name__ == "__main__":
    df = fetch_real_gdp()
    print("Real GDP Data Preview:")
    print(df.head())
    print(f"\nColumns: {list(df.columns)}")
    print(f"Shape: {df.shape}")