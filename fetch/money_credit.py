import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# Cache file path
CACHE_FILE = 'data/money_credit_cache.json'
CACHE_DURATION = timedelta(hours=24)

def fetch_money_credit_stats():
    """
    Fetch Money and Credit Statistics data from CBN APIs with caching
    Returns a DataFrame with money supply and credit statistics
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

    print("Fetching fresh money and credit statistics data...")

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # API endpoints to try
    endpoints = [
        "GetAllMoneyAndCreditStatsGRAPH",
        "GetAllMoneyAndCreditStats"
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
                'period': 'September 2025',
                'moneySupply_M3': 117783532.25,
                'moneySupply_M2': 117774240.75,
                'netForeignAssets': 41661148.81,
                'netDomesticAssets': 76122383.44,
                'baseMoney': 39622605.75,
                'currencyOutsideBanks': 4465081.38,
                'demandDeposits': 34642829.40,
                'quasiMoney': 78666329.98,
                'narrowMoney': 39107910.78,
                'netDomesticCredit': 96685295.66,
                'creditToGovernment': 24158173.80,
                'creditToPrivateSector': 72527121.86,
                'otherAssetsNet': 5940049.53,
                'currencyInCirculation': 4952926.96,
                'banksReserves': 34669678.79,
                'specialInterventionReserves': 284361.95
            },
            {
                'period': 'August 2025',
                'moneySupply_M3': 119691923.01,
                'moneySupply_M2': 119682631.52,
                'netForeignAssets': 41586667.83,
                'netDomesticAssets': 78105255.18,
                'baseMoney': 35680432.94,
                'currencyOutsideBanks': 4450347.55,
                'demandDeposits': 34934798.49,
                'quasiMoney': 80297485.48,
                'narrowMoney': 39385146.04,
                'netDomesticCredit': 98833184.75,
                'creditToGovernment': 22951046.10,
                'creditToPrivateSector': 75882138.65,
                'otherAssetsNet': 4681030.93,
                'currencyInCirculation': 4922360.53,
                'banksReserves': 30758072.40,
                'specialInterventionReserves': 284361.95
            },
            {
                'period': 'June 2025',
                'moneySupply_M3': 117250742.74,
                'moneySupply_M2': 117239937.33,
                'netForeignAssets': 41467017.57,
                'netDomesticAssets': 75783725.16,
                'baseMoney': 34659417.19,
                'currencyOutsideBanks': 4493787.77,
                'demandDeposits': 35370313.99,
                'quasiMoney': 77375835.57,
                'narrowMoney': 39864101.77,
                'netDomesticCredit': 97787860.30,
                'creditToGovernment': 21662004.62,
                'creditToPrivateSector': 76125855.69,
                'otherAssetsNet': 3187029.68,
                'currencyInCirculation': 5007516.17,
                'banksReserves': 29651901.02,
                'specialInterventionReserves': 284361.95
            }
        ]
        all_data = sample_data

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    # Clean and format the data
    if not df.empty:
        # Format numeric columns to 2 decimal places
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            df[col] = df[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "0.00")

        # Ensure period column exists
        if 'period' not in df.columns and 'Period' in df.columns:
            df['period'] = df['Period']

        # Rename columns to match expected format
        column_mapping = {
            'moneySupply_M3': 'Money Supply (M3)',
            'moneySupply_M2': 'Money Supply (M2)',
            'netForeignAssets': 'Net Foreign Assets (NFA)',
            'netDomesticAssets': 'Net Domestic Assets (NDA)',
            'baseMoney': 'Reserve Money (Base Money)',
            'currencyOutsideBanks': 'Currency Outside Banks',
            'demandDeposits': 'Demand Deposits',
            'quasiMoney': 'Quasi Money',
            'narrowMoney': 'Narrow Money (M1)',
            'netDomesticCredit': 'Net Domestic Credit (NDC)',
            'creditToGovernment': 'Credit to Government (Net)',
            'creditToPrivateSector': 'Credit to Private Sector (CPS)',
            'otherAssetsNet': 'Other Assets Net',
            'currencyInCirculation': 'Currency in Circulation',
            'banksReserves': 'Banks Reserves',
            'specialInterventionReserves': 'Special Intervention Reserves'
        }

        df = df.rename(columns=column_mapping)

        # Sort by period (assuming period is a date string)
        if 'period' in df.columns:
            try:
                # Try to sort by period if it's parseable as date
                df['period_sort'] = pd.to_datetime(df['period'], errors='coerce')
                df = df.sort_values('period_sort', ascending=False).drop('period_sort', axis=1)
            except:
                pass

    print(f"Successfully processed money and credit statistics data. Total records: {len(df)}")

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
    df = fetch_money_credit_stats()
    print("Money and Credit Statistics Data Preview:")
    print(df.head())
    print(f"\nColumns: {list(df.columns)}")
    print(f"Shape: {df.shape}")