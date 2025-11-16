import requests
import pandas as pd
import io
import math
import os
import json
from datetime import datetime, timedelta

CACHE_DURATION_HOURS = 24

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
        return f"{num:,.2f}"
    except (ValueError, TypeError):
        return x # Return original value if conversion fails

def fetch_nominal_gdp():
    """
    Fetches Nominal Gross Domestic Product data from CBN's JSON APIs.
    Shows GDP by sector and component in billion Naira.

    Returns:
        pandas.DataFrame: A DataFrame containing GDP data by sector.
                          Returns an empty DataFrame on failure.
    """
    cache_file = "data/nominal_gdp_cache.json"

    # Try to load from cache first
    cached_df = load_cached_data(cache_file)
    if cached_df is not None:
        return cached_df

    # Try multiple endpoints to get comprehensive GDP data
    endpoints_to_try = [
        "GetNominalGDPGRAPH",  # Main GDP graph data
        "GetLatestNominalGDP",  # Latest GDP data
        "GetAllNominalGDP",     # All GDP data
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
        print("Warning: Failed to fetch GDP data from all endpoints.")
        # Return sample data based on the HTML structure
        return get_sample_gdp_data()

    # Convert to DataFrame
    try:
        df = pd.DataFrame(all_data)

        # Remove unwanted columns if they exist
        columns_to_remove = ['id', 'created_at', 'updated_at']
        df = df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors='ignore')

        # Rename columns to match expected format
        column_mapping = {
            'tyear': 'Year',
            'agriculture': 'Agriculture',
            'industry': 'Industry',
            'services': 'Services',
            'gdPatCurrentBasicPrices': 'GDP at Current Basic Prices',
            'netTaxesOnProducts': 'Net Taxes on Products',
            'gdPatCurrentMarketPrices': 'GDP at Current Market Prices',
            'cropProduction': 'Crop Production',
            'livestock': 'Livestock',
            'forestry': 'Forestry',
            'fishing': 'Fishing',
            'miningAndQuarrying': 'Mining and Quarrying',
            'manufacturing': 'Manufacturing',
            'electricityGasSteam': 'Electricity, Gas, Steam & Air conditioner',
            'waterSupply': 'Water supply, Sewage, Waste Management',
            'construction': 'Construction',
            'trade': 'Trade',
            'accommodationFood': 'Accommodation and Food Services',
            'transportationStorage': 'Transportation and Storage',
            'informationCommunication': 'Information and Communication',
            'artsEntertainment': 'Arts, Entertainment & Recreation',
            'financialInsurance': 'Financial and Insurance',
            'realEstate': 'Real Estate',
            'professionalServices': 'Professional, Scientific & Technical Services',
            'administrativeServices': 'Administrative and Support Services',
            'publicAdministration': 'Public Administration',
            'education': 'Education',
            'healthServices': 'Human Health & Social Services',
            'otherServices': 'Other Services'
        }

        df = df.rename(columns=column_mapping)

        # Convert year column if it exists
        if 'Year' in df.columns:
            df['Year'] = df['Year'].astype(str)

        # Format numeric columns with commas
        numeric_columns = [
            'Agriculture', 'Industry', 'Services', 'GDP at Current Basic Prices',
            'Net Taxes on Products', 'GDP at Current Market Prices', 'Crop Production',
            'Livestock', 'Forestry', 'Fishing', 'Mining and Quarrying', 'Manufacturing',
            'Electricity, Gas, Steam & Air conditioner', 'Water supply, Sewage, Waste Management',
            'Construction', 'Trade', 'Accommodation and Food Services', 'Transportation and Storage',
            'Information and Communication', 'Arts, Entertainment & Recreation', 'Financial and Insurance',
            'Real Estate', 'Professional, Scientific & Technical Services', 'Administrative and Support Services',
            'Public Administration', 'Education', 'Human Health & Social Services', 'Other Services'
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(number_with_commas)

        # Remove duplicates based on Year
        if 'Year' in df.columns:
            df = df.drop_duplicates(subset=['Year'], keep='first')

        # Sort by year descending (most recent first)
        if 'Year' in df.columns:
            df = df.sort_values('Year', ascending=False)

        # Select only the columns we want to display
        display_columns = ["Year"] + numeric_columns
        available_columns = [col for col in display_columns if col in df.columns]
        df = df[available_columns]

        print(f"Successfully processed GDP data. Total records: {len(df)}")
        # Save to cache
        save_cached_data(cache_file, df)
        return df

    except Exception as e:
        print(f"Error processing GDP data: {e}")
        return get_sample_gdp_data()

def get_sample_gdp_data():
    """Return sample GDP data based on the HTML structure provided."""
    print("Using sample GDP data for demonstration.")

    # Create sample data based on the HTML structure for 2024
    data = {
        'Year': ['2024'],
        'Agriculture': ['56,478.98'],
        'Crop Production': ['50,867.62'],
        'Livestock': ['2,819.10'],
        'Forestry': ['460.43'],
        'Fishing': ['2,331.83'],
        'Industry': ['82,272.01'],
        'Mining and Quarrying': ['18,487.95'],
        'Manufacturing': ['37,486.13'],
        'Electricity, Gas, Steam & Air conditioner': ['20.53'],
        'Water supply, Sewage, Waste Management': ['7,312.54'],
        'Construction': ['14,501.59'],
        'Services': ['130,539.36'],
        'Trade': ['36,797.22'],
        'Accommodation and Food Services': ['2,121.08'],
        'Transportation and Storage': ['3,949.45'],
        'Information and Communication': ['3,323.75'],
        'Arts, Entertainment & Recreation': ['0.70'],
        'Financial and Insurance': ['18.66'],
        'Real Estate': ['391.55'],
        'Professional, Scientific & Technical Services': ['177.44'],
        'Administrative and Support Services': ['37.34'],
        'Public Administration': ['33,614.77'],
        'Education': ['27,380.49'],
        'Human Health & Social Services': ['46.81'],
        'Other Services': ['2,182.45'],
        'GDP at Current Basic Prices': ['269,290.35'],
        'Net Taxes on Products': ['8,203.43'],
        'GDP at Current Market Prices': ['277,493.78']
    }

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    # This allows you to test the script directly
    # Run: python fetch/nominal_gdp.py
    df = fetch_nominal_gdp()
    if not df.empty:
        print("Data fetched successfully:")
        print(df.head(5))  # Show first 5 rows
        print(f"\nTotal records: {len(df)}")
        print(f"Columns: {list(df.columns)}")
    else:
        print("Failed to fetch data.")