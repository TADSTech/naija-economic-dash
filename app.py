import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import datetime
import re

from fetch.cbn_indicators import fetch_macro_indicators
from fetch.nfem_rates import fetch_nfem_rates
from fetch.exchange_rates import fetch_exchange_rates
from fetch.crude_oil import fetch_crude_oil_prices
from fetch.financial_data import fetch_financial_data
from fetch.nominal_gdp import fetch_nominal_gdp
from fetch.inflation import fetch_inflation_rates
from fetch.money_credit import fetch_money_credit_stats

def to_numeric(value):
    """Convert formatted string numbers (with commas) to float for calculations"""
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(',', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0
    return 0

df_macro = fetch_macro_indicators()
df_nfem = fetch_nfem_rates()
df_exchange = fetch_exchange_rates()
df_crude_oil = fetch_crude_oil_prices()
df_financial = fetch_financial_data()
df_gdp = fetch_nominal_gdp()
df_inflation = fetch_inflation_rates()
df_money_credit = fetch_money_credit_stats()

# Convert string numbers to numeric for graphing
if not df_money_credit.empty:
    for col in df_money_credit.columns:
        if col not in ['period', 'id', 'tyear', 'tmonth']:
            df_money_credit[col] = df_money_credit[col].apply(to_numeric)

if not df_inflation.empty:
    for col in df_inflation.columns:
        if col not in ['period', 'id', 'tyear', 'tmonth']:
            df_inflation[col] = df_inflation[col].apply(to_numeric)

if not df_financial.empty and 'Date' not in df_financial.columns:
    df_financial['Record'] = range(1, len(df_financial) + 1)

# Custom Plotly theme - green color scheme
custom_template = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#fcfcfc',
        font=dict(color='#333333', family='Inter, sans-serif'),
        title=dict(
            font=dict(size=20, color='#2E8B57', family='Inter, sans-serif'),
            x=0.05,
            xanchor='left'
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#e0e0e0',
            linecolor='#cccccc',
            tickfont=dict(color='#555555')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e0e0e0',
            linecolor='#cccccc',
            tickfont=dict(color='#555555')
        ),
        colorway=['#2E8B57', '#32CD32', '#228B22', '#006400', '#90EE90', '#66CDAA', '#3CB371'],
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
)

app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
    ],
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}
    ]
)
app.title = "Naija Economic Dashboard"
server = app.server

# Inline CSS for styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                color: #2c3e50;
            }
            
            .app-header {
                background: linear-gradient(135deg, #2E8B57 0%, #1e5f3f 100%);
                color: white;
                padding: 3rem 0;
                text-align: center;
                box-shadow: 0 4px 15px rgba(46, 139, 87, 0.2);
                margin-bottom: 2rem;
            }
            
            .app-header h1 {
                margin: 0;
                font-size: 2.8em;
                font-weight: 700;
                letter-spacing: -0.5px;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            .app-header p {
                margin: 0.5rem 0 0 0;
                font-size: 1.15em;
                opacity: 0.95;
                font-weight: 300;
                letter-spacing: 0.3px;
            }
            
            .section-title {
                color: #2E8B57;
                font-weight: 700;
                font-size: 1.75em;
                margin: 2.5rem 0 1.5rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 3px solid #2E8B57;
                letter-spacing: -0.3px;
            }
            
            .card {
                border: none;
                border-radius: 12px;
                transition: all 0.3s ease;
                background: white;
                overflow: hidden;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 25px rgba(46, 139, 87, 0.15) !important;
            }
            
            .card-title {
                color: #555;
                font-size: 0.95em;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 1rem;
            }
            
            .card-body {
                padding: 1.75rem;
            }
            
            h3 {
                font-size: 2em;
                font-weight: 700;
                margin: 0.5rem 0;
                letter-spacing: -0.5px;
            }
            
            .shadow-sm {
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
            }
            
            .dropdown {
                margin-bottom: 1rem;
            }
            
            .Select-control {
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                background-color: white;
            }
            
            .Select-control:hover {
                border-color: #2E8B57;
            }
            
            .app-content {
                padding: 0 1rem;
            }
            
            .datatable {
                font-size: 0.9em;
            }
            
            .dash-table-container {
                border-radius: 8px;
                overflow: hidden;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer style="text-align: center; padding: 2rem; color: #666; margin-top: 3rem; border-top: 1px solid #e0e0e0;">
            <p style="margin: 0; font-size: 0.9em;">
                <strong>Naija Economic Dashboard</strong> | Data Source: Central Bank of Nigeria (CBN)
            </p>
        </footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

def create_kpi_card(title, value, date):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title", style={'textAlign': 'center'}),
            html.H3(value, className="card-text", style={'textAlign': 'center', 'color': '#2E8B57', 'fontWeight': '600'}),
            html.P(f"As at: {date}", style={'textAlign': 'center', 'fontSize': '0.8em', 'color': '#6c757d'})
        ]),
        className="shadow-sm h-100"
    )

def create_dashboard_card(card_id, title, children):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title", style={'color': '#2E8B57', 'fontWeight': '600'}),
            *children
        ]),
        className="shadow-sm mb-4 h-100",
        id=card_id
    )

def create_graph_card(graph_id, title, dropdown=None):
    children = [dropdown] if dropdown else []
    children.append(dcc.Graph(id=graph_id, config={'displaylogo': False, 'responsive': True}, style={'height': '400px'}))
    return create_dashboard_card(f"{graph_id}-card", title, children)

def create_table_card(table_id, title, columns, data, page_size=10):
    return create_dashboard_card(
        f"{table_id}-card",
        title,
        [
            dash_table.DataTable(
                id=table_id,
                columns=[{"name": i, "id": i} for i in columns],
                data=data,
                page_current=0,
                page_size=page_size,
                page_action='native',
                style_cell={'fontFamily': 'Inter, sans-serif', 'textAlign': 'left', 'padding': '8px', 'fontSize': '0.9em'},
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': '600',
                    'color': '#2E8B57',
                    'borderBottom': '2px solid #2E8B57'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#fdfdfd'}
                ],
                style_table={'overflowX': 'auto'}
            )
        ]
    )

# Prepare KPI data for header cards
try:
    crude_oil = df_macro.loc[df_macro['Economic Indicators'].str.contains('Crude Oil', case=False, na=False), ['Value', 'As at:']].iloc[0]
    inflation_rate = df_macro.loc[df_macro['Economic Indicators'].str.contains('Inflation', case=False, na=False), ['Value', 'As at:']].iloc[0]
    mpr_rate = df_macro.loc[df_macro['Economic Indicators'].str.contains('Monetary Policy', case=False, na=False), ['Value', 'As at:']].iloc[0]
    money_supply = df_macro.loc[df_macro['Economic Indicators'].str.contains('Money Supply', case=False, na=False), ['Value', 'As at:']].iloc[0]
except (IndexError, KeyError):
    crude_oil = pd.Series({'Value': 'N/A', 'As at:': 'N/A'})
    inflation_rate = pd.Series({'Value': 'N/A', 'As at:': 'N/A'})
    mpr_rate = pd.Series({'Value': 'N/A', 'As at:': 'N/A'})
    money_supply = pd.Series({'Value': 'N/A', 'As at:': 'N/A'})

app.layout = html.Div(className="app-container", children=[
    html.Div(className="app-header", children=[
        html.H1('Naija Economic Dashboard', style={'margin': '0', 'fontSize': '2.5em', 'fontWeight': '700'}),
        html.P('Key Nigerian Economic Indicators (Data from CBN)', style={'fontSize': '1.1em', 'opacity': '0.9'})
    ]),

    dbc.Container(fluid=True, className="app-content", children=[
        html.H2("Key Indicators", className="section-title"),
        dbc.Row(className="mb-4", children=[
            dbc.Col(lg=3, md=6, sm=12, className="mb-4", children=[
                create_kpi_card("Crude Oil Price", crude_oil['Value'], crude_oil['As at:'])
            ]),
            dbc.Col(lg=3, md=6, sm=12, className="mb-4", children=[
                create_kpi_card("Inflation Rate (Y-o-Y)", inflation_rate['Value'], inflation_rate['As at:'])
            ]),
            dbc.Col(lg=3, md=6, sm=12, className="mb-4", children=[
                create_kpi_card("Monetary Policy Rate", mpr_rate['Value'], mpr_rate['As at:'])
            ]),
            dbc.Col(lg=3, md=6, sm=12, className="mb-4", children=[
                create_kpi_card("Money Supply (M3)", money_supply['Value'], money_supply['As at:'])
            ]),
        ]),

        html.H2("Live Macro-Economic Indicators", className="section-title"),
        dbc.Row(className="mb-4", children=[
            dbc.Col(children=[
                create_table_card('macro-table', 'CBN Macro Indicators', df_macro.columns, df_macro.to_dict('records'), page_size=5)
            ])
        ]),

        html.H2("Data Trends", className="section-title"),
        
        dbc.Row(className="mb-4", children=[
            dbc.Col(md=6, className="mb-4", children=[
                create_graph_card('nfem-graph', "NFEM Rate Trends")
            ]),
            dbc.Col(md=6, className="mb-4", children=[
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Exchange Rate Trends (All Currencies vs Naira)", className="card-title", style={'color': '#2E8B57', 'fontWeight': '600'}),
                        dcc.Graph(id='exchange-graph', config={'displaylogo': False, 'responsive': True}, style={'height': '400px'})
                    ]),
                    className="shadow-sm mb-4 h-100",
                    id="exchange-graph-card"
                )
            ]),
        ]),

        dbc.Row(className="mb-4", children=[
            dbc.Col(md=12, className="mb-4", children=[
                create_graph_card('crude-oil-graph', "Crude Oil Price Trends")
            ]),
        ]),

        dbc.Row(className="mb-4", children=[
            dbc.Col(md=6, className="mb-4", children=[
                create_graph_card('gdp-graph', "Nominal GDP by Sector (in ₦'b)")
            ]),
            dbc.Col(md=6, className="mb-4", children=[
                create_graph_card('gdp-pie-chart', "Nominal GDP Composition")
            ]),
        ]),

        dbc.Row(className="mb-4", children=[
            dbc.Col(md=6, className="mb-4", children=[
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Inflation Rate Trends (%)", className="card-title", style={'color': '#2E8B57', 'fontWeight': '600'}),
                        dcc.Dropdown(
                            id='inflation-metric-dropdown',
                            options=[{'label': c, 'value': c} for c in df_inflation.columns if c != 'period'] if not df_inflation.empty else [],
                            value=df_inflation.columns[1] if not df_inflation.empty and len(df_inflation.columns) > 1 else None,
                            clearable=False,
                            className="mb-3"
                        ),
                        dcc.Graph(id='detailed-inflation-graph', config={'displaylogo': False, 'responsive': True}, style={'height': '400px'})
                    ]),
                    className="shadow-sm mb-4 h-100",
                    id="detailed-inflation-graph-card"
                )
            ]),
            dbc.Col(md=6, className="mb-4", children=[
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Money and Credit Trends (in ₦'m)", className="card-title", style={'color': '#2E8B57', 'fontWeight': '600'}),
                        dcc.Dropdown(
                            id='money-metric-dropdown',
                            options=[{'label': c, 'value': c} for c in df_money_credit.columns if c != 'period'] if not df_money_credit.empty else [],
                            value=df_money_credit.columns[1] if not df_money_credit.empty and len(df_money_credit.columns) > 1 else None,
                            clearable=False,
                            className="mb-3"
                        ),
                        dcc.Graph(id='money-credit-graph', config={'displaylogo': False, 'responsive': True}, style={'height': '400px'})
                    ]),
                    className="shadow-sm mb-4 h-100",
                    id="money-credit-graph-card"
                )
            ]),
        ]),

        html.H2("Detailed Data Tables", className="section-title"),

        dbc.Row(className="mb-4", children=[
            dbc.Col(md=6, className="mb-4", children=[
                create_table_card('nfem-table', 'NFEM Rates', df_nfem.columns, df_nfem.to_dict('records'))
            ]),
            dbc.Col(md=6, className="mb-4", children=[
                create_table_card('exchange-table', 'Exchange Rates', df_exchange.columns, df_exchange.to_dict('records'))
            ]),
        ]),
        dbc.Row(className="mb-4", children=[
            dbc.Col(md=6, className="mb-4", children=[
                create_table_card('crude-oil-table', 'Crude Oil Prices', df_crude_oil.columns, df_crude_oil.to_dict('records'))
            ]),
            dbc.Col(md=6, className="mb-4", children=[
                create_table_card('gdp-table', 'Nominal GDP', df_gdp.columns, df_gdp.to_dict('records'), page_size=5)
            ]),
        ]),
        dbc.Row(className="mb-4", children=[
            dbc.Col(md=12, className="mb-4", children=[
                create_table_card('financial-table', 'Financial Operations', df_financial.columns, df_financial.to_dict('records'))
            ]),
        ]),
        dbc.Row(className="mb-4", children=[
            dbc.Col(md=12, className="mb-4", children=[
                create_table_card(
                    'money-credit-table',
                    'Money & Credit Statistics',
                    df_money_credit.columns,
                    df_money_credit.to_dict('records'),
                    page_size=5
                ) if not df_money_credit.empty else dbc.Card(
                    dbc.CardBody([html.P("No money and credit data available")]),
                    className="shadow-sm mb-4"
                )
            ]),
        ]),
    ])
])

# Callbacks - connect interactive components to graphs

@app.callback(
    Output('nfem-graph', 'figure'),
    Input('nfem-graph', 'id')
)
def update_nfem_graph(_):
    if df_nfem.empty:
        return go.Figure().add_annotation(text="No NFEM rate data available")
    
    df_plot = df_nfem.sort_values('Date')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_plot['Date'],
        y=df_plot['Highest Rate'],
        name='Highest Rate',
        line=dict(color='#90EE90', width=0),
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=df_plot['Date'],
        y=df_plot['Lowest Rate'],
        name='Lowest Rate',
        line=dict(color='#90EE90', width=0),
        fill='tonexty',
        fillcolor='rgba(144, 238, 144, 0.2)',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=df_plot['Date'],
        y=df_plot['NFEM Rate'],
        name='NFEM Rate',
        line=dict(color='#2E8B57', width=3),
        mode='lines+markers',
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        template=custom_template,
        title=None,
        yaxis_title='Rate (₦/US$)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig

@app.callback(
    Output('exchange-graph', 'figure'),
    Input('exchange-graph', 'id')
)
def update_exchange_graph(_):
    if df_exchange.empty:
        return go.Figure().add_annotation(text="No exchange rate data available")
    
    df_plot = df_exchange.copy()
    if 'Date' in df_plot.columns:
        df_plot['Year'] = pd.to_datetime(df_plot['Date'], errors='coerce').dt.year
        
        df_grouped = df_plot.groupby(['Currency', 'Year']).agg({
            'Central Rate': lambda x: to_numeric(x.iloc[0]) if len(x) > 0 else 0
        }).reset_index()
        
        fig = go.Figure()
        
        for currency in df_grouped['Currency'].unique():
            currency_data = df_grouped[df_grouped['Currency'] == currency].sort_values('Year')
            fig.add_trace(go.Scatter(
                x=currency_data['Year'],
                y=currency_data['Central Rate'],
                name=currency,
                mode='lines+markers',
                line=dict(width=2.5),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            template=custom_template,
            title=None,
            xaxis_title='Year',
            yaxis_title='Exchange Rate (₦)',
            hovermode='x unified',
            legend=dict(
                orientation='v',
                yanchor='top',
                y=1,
                xanchor='left',
                x=1.02
            )
        )
    else:
        fig = go.Figure().add_annotation(text="Date information not available")
    
    return fig

@app.callback(
    Output('crude-oil-graph', 'figure'),
    Input('crude-oil-graph', 'id')
)
def update_crude_oil_graph(_):
    if df_crude_oil.empty:
        return go.Figure().add_annotation(text="No crude oil price data available")
    
    df_plot = df_crude_oil.copy()
    if 'Date' not in df_plot.columns:
        df_plot['Index'] = range(len(df_plot))
        x_col = 'Index'
        x_title = 'Data Point'
    else:
        df_plot = df_plot.sort_values('Date')
        x_col = 'Date'
        x_title = 'Date'
    
    fig = px.line(
        df_plot,
        x=x_col,
        y='Crude Oil Price',
        title='Crude Oil Price Over Time',
        markers=True
    )
    fig.update_layout(
        template=custom_template,
        title=None,
        xaxis_title=x_title,
        yaxis_title='Price (US$/bbl)',
        hovermode='x unified'
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
    return fig

@app.callback(
    Output('gdp-graph', 'figure'),
    Input('gdp-graph', 'id')
)
def update_gdp_graph(_):
    if df_gdp.empty:
        return go.Figure().add_annotation(text="No nominal GDP data available")
    
    df_melted = df_gdp.melt(
        id_vars=['Year'],
        value_vars=['Agriculture', 'Industry', 'Services'],
        var_name='Sector',
        value_name='GDP (Billion ₦)'
    )
    
    fig = px.area(
        df_melted,
        x='Year',
        y='GDP (Billion ₦)',
        color='Sector',
        title='Nominal GDP by Sector',
        line_shape='spline'
    )
    fig.update_layout(
        template=custom_template,
        title=None,
        hovermode='x unified'
    )
    return fig

@app.callback(
    Output('gdp-pie-chart', 'figure'),
    Input('gdp-pie-chart', 'id')
)
def update_gdp_pie_chart(_):
    if df_gdp.empty:
        return go.Figure().add_annotation(text="No nominal GDP data available")
    
    latest_year = df_gdp.iloc[0]
    
    sectors = ['Agriculture', 'Industry', 'Services']
    values = []
    
    for sector in sectors:
        if sector in df_gdp.columns:
            value = to_numeric(latest_year[sector])
            values.append(value)
        else:
            values.append(0)
    
    fig = go.Figure(data=[go.Pie(
        labels=sectors,
        values=values,
        hole=0.3,
        marker=dict(colors=['#2E8B57', '#32CD32', '#90EE90']),
        textinfo='label+percent',
        textposition='auto',
        hovertemplate='<b>%{label}</b><br>₦%{value:,.2f}B<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        template=custom_template,
        title=None,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        ),
        annotations=[dict(text=f'{latest_year["Year"]}', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    return fig

@app.callback(
    Output('detailed-inflation-graph', 'figure'),
    Input('inflation-metric-dropdown', 'value')
)
def update_inflation_graph(selected_metric):
    if df_inflation.empty or selected_metric is None:
        return go.Figure().add_annotation(text="No inflation data available")
    
    df_plot = df_inflation.copy()
    if 'period' in df_plot.columns:
        df_plot = df_plot.sort_values('period')
    
    fig = px.area(
        df_plot,
        x='period',
        y=selected_metric,
        title=f'{selected_metric} Over Time',
        line_shape='spline'
    )
    fig.update_traces(
        line=dict(width=3, color='#2E8B57'),
        fillcolor='rgba(46, 139, 87, 0.3)'
    )
    fig.update_layout(
        template=custom_template,
        title=None,
        xaxis_title='Period',
        yaxis_title='Inflation Rate (%)',
        hovermode='x unified'
    )
    return fig

@app.callback(
    Output('money-credit-graph', 'figure'),
    Input('money-metric-dropdown', 'value')
)
def update_money_credit_graph(selected_metric):
    if df_money_credit.empty or selected_metric is None:
        return go.Figure().add_annotation(text="No money and credit data available")
    
    df_plot = df_money_credit.copy()
    if 'period' in df_plot.columns:
        df_plot = df_plot.sort_values('period')
    
    fig = px.bar(
        df_plot,
        x='period',
        y=selected_metric,
        title=f'{selected_metric} Over Time',
        color=selected_metric,
        color_continuous_scale=['#90EE90', '#2E8B57', '#006400']
    )
    fig.update_layout(
        template=custom_template,
        title=None,
        xaxis_title='Period',
        yaxis_title="Amount (₦'m)",
        hovermode='x unified',
        showlegend=False
    )
    fig.update_traces(marker_line_width=0)
    return fig

if __name__ == '__main__':
    app.run(debug=False)