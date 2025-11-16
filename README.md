# Naija Economic Dashboard

A real-time economic data dashboard for Nigeria built with Plotly Dash.

## Background

I've been using Plotly for visualizations for a while now and honestly became their biggest fan. One day I discovered they had this thing called Dash for building interactive web dashboards. Figured I'd give it a shot and see what I could build.

This is my first Dash app. I wanted to track Nigerian economic indicators without jumping between different websites, so I pulled data from the Central Bank of Nigeria's APIs and put everything in one place.

## What It Shows

The dashboard displays live economic data including:

- Macro indicators (inflation, money supply, interest rates)
- NFEM exchange rates
- Multi-currency exchange rate trends
- Crude oil prices
- Nominal GDP breakdown by sector
- Money and credit statistics

Data refreshes every 24 hours via cached API calls.

## Tech Stack

- Python 3.11.14
- Plotly Dash for the web framework
- Pandas for data handling
- Dash Bootstrap Components for layout
- CBN public APIs for data

## Setup

Install dependencies:

```bash
pip install dash plotly pandas dash-bootstrap-components requests
```

Run the app:

```bash
python app.py
```

Visit `http://127.0.0.1:8050` in your browser.

## Project Structure

```
naija-economic-dash/
├── app.py                 # Main dashboard application
├── fetch/                 # Data fetching modules
│   ├── cbn_indicators.py
│   ├── crude_oil.py
│   ├── exchange_rates.py
│   ├── financial_data.py
│   ├── inflation.py
│   ├── money_credit.py
│   ├── nfem_rates.py
│   └── nominal_gdp.py
├── data/                  # Cached JSON data
└── assets/                # CSS styling
```

## Data Source

All economic data comes from the Central Bank of Nigeria (CBN) public APIs. The dashboard caches responses to reduce API calls and improve load times.

## Notes

This was a learning project to get familiar with Dash. The code works but could definitely be cleaner. If you're also learning Dash, feel free to use this as a reference or starting point.

The green color scheme is intentional. Nigerian currency and all that.

## License

[MIT](LICENSE)
