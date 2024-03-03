import json
import pandas as pd
import plotly.express as px
import dash

from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from urllib.request import urlopen

# Load and preprocess data
df = pd.read_csv('sells.csv')
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
min_date, max_date = df['order_purchase_timestamp'].min(), df['order_purchase_timestamp'].max()

# Load Brazil state coordinates/shape
with urlopen("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson") as response:
    brazil = json.load(response)
for feature in brazil["features"]:
    feature["id"] = feature["properties"]["sigla"]

# Define global style settings
colors = dict(
    background='#f3f3f3',
    text='#000000',
    fontFamily='Open Sans',
    plot_background='#f3f3f3'
)

# Initialize Dash app
app = dash.Dash(__name__)

# App layout definition
app.layout = html.Div(
    children=[
        # App title
        html.H1(
            children='Brazil Olist Dashboard',
            style={'textAlign': 'center', 'color': colors['text'], 'fontFamily': colors['fontFamily'], 'marginBottom': '22px'}
        ),

        # Map selector (Sellers or Customers)
        html.Div([
            html.Label('Aggregated information by state about:', style={'color': colors['text'], 'fontFamily': colors['fontFamily']}),
            dcc.RadioItems(
                id='map-seller-customer-view',
                options=[{'label': 'Sellers', 'value': 'sellers'}, {'label': 'Customers', 'value': 'customers'}],
                value='sellers',
                style={'color': colors['text'], 'fontFamily': colors['fontFamily']}
            ),
            dcc.Graph(id='state-regions-map'),
        ], style={'marginBottom': '20px', 'flex': '100%'}),

        # Button to reset state filter
        html.Div(
            html.Button('Reset state filter', id='reset-state-button', hidden=True, n_clicks=0, style={
                'fontSize': '14px', 'fontWeight': 'bold', 'color': 'black', 'backgroundColor': '#ffadad',
                'padding': '12px 24px', 'borderRadius': '12px', 'cursor': 'pointer', 'outline': 'none', 'margin': '10px'
            }),
            style={'textAlign': 'center', 'margin': '20px'}
        ),

        # Dropdowns and date pickers for seller and customer data
        html.Div([
            # Seller's state selection
            html.Div([
                html.Label("Select seller's state:", style={'color': colors['text'], 'fontFamily': colors['fontFamily']}),
                dcc.Dropdown(
                    id='seller-state-dropdown',
                    options=[{'label': 'Whole Brazil', 'value': 'FULL_VIEW'}] +
                            [{'label': state, 'value': state} for state in df['seller_state'].unique()],
                    value='FULL_VIEW',
                    multi=True,
                    style={'color': colors['text'], 'backgroundColor': colors['background'], 'marginBottom': '10px', 'fontFamily': colors['fontFamily'], 'marginRight': '20px'}
                ),
                # Order status selection for sellers
                html.Label('Select order status:', style={'color': colors['text'], 'fontFamily': colors['fontFamily']}),
                dcc.Dropdown(
                    id='order-status-dropdown',
                    options=[{'label': 'All statuses', 'value': 'FULL_VIEW'}] +
                            [{'label': status, 'value': status} for status in df['order_status'].unique()],
                    value=['FULL_VIEW'],
                    multi=True,
                    style={'color': colors['text'], 'backgroundColor': colors['background'], 'marginBottom': '20px', 'fontFamily': colors['fontFamily'], 'marginRight': '20px'}
                ),
                # Date range picker for sellers
                dcc.DatePickerRange(
                    id='seller-date-picker-range',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    start_date=min_date,
                    end_date=max_date,
                    style={'color': colors['text'], 'fontFamily': colors['fontFamily']}
                ),
                # Graph for seller category sales
                dcc.Graph(id='seller-category-sales-distribution', style={'marginBottom': '20px'}),
            ], style={'marginBottom': '20px', 'flex': '60%'}),

            # Customer's state selection
            html.Div([
                html.Label("Select customer's state:", style={'color': colors['text'], 'fontFamily': colors['fontFamily']}),
                dcc.Dropdown(
                    id='customer-state-dropdown',
                    options=[{'label': 'Whole Brazil', 'value': 'FULL_VIEW'}] +
                            [{'label': state, 'value': state} for state in df['customer_state'].unique()],
                    value='FULL_VIEW',
                    multi=True,
                    style={'color': colors['text'], 'backgroundColor': colors['background'], 'marginBottom': '10px', 'fontFamily': colors['fontFamily']}
                ),
                # Order status selection for customers
                html.Label('Select order status:', style={'color': colors['text'], 'fontFamily': colors['fontFamily']}),
                dcc.Dropdown(
                    id='customer-order-status-dropdown',
                    options=[{'label': 'All statuses', 'value': 'FULL_VIEW'}] +
                            [{'label': status, 'value': status} for status in df['order_status'].unique()],
                    value=['FULL_VIEW'],
                    multi=True,
                    style={'color': colors['text'], 'backgroundColor': colors['background'], 'marginBottom': '20px', 'fontFamily': colors['fontFamily']}
                ),
                # Date range picker for customers
                dcc.DatePickerRange(
                    id='customer-date-picker-range',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    start_date=min_date,
                    end_date=max_date,
                    style={'color': colors['text'], 'fontFamily': colors['fontFamily']}
                ),
                # Graph for customer category purchases
                dcc.Graph(id='customer-category-purchases-distribution'),
            ], style={'marginBottom': '20px', 'flex': '60%'}),
        ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-between'}),

        # Store for selected state
        dcc.Store(id='selected-state', storage_type='session'),
    ],
    style={'backgroundColor': colors['background']}
)


# Callback to set or reset selected state
@app.callback(
    Output('selected-state', 'data'),
    [
        Input('state-regions-map', 'clickData'),
        Input('reset-state-button', 'n_clicks')
    ],
    [
        State('selected-state', 'data')
    ]
)
def create_or_kill_view(click, n_clicks, selected_state_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'state-regions-map' and click:
        state_id = click['points'][0]['location']
        return {'state': state_id}
    elif trigger_id == 'reset-state-button' and n_clicks:
        return {}
    return selected_state_data


# Callback to update dropdown values
@app.callback(
    Output('seller-state-dropdown', 'value'),
    Output('customer-state-dropdown', 'value'),
    [Input('selected-state', 'data')]
)
def update_dropdowns(selected_state_data):
    if selected_state_data and 'state' in selected_state_data:
        selected_state = selected_state_data['state']
        return selected_state, selected_state
    else:
        return 'FULL_VIEW', 'FULL_VIEW'


# Callback to update the state map
@app.callback(
    Output('state-regions-map', 'figure'),
    [
        Input('map-seller-customer-view', 'value'),
        Input('seller-state-dropdown', 'value'),
        Input('customer-state-dropdown', 'value'),
        Input('order-status-dropdown', 'value'),
        Input('customer-order-status-dropdown', 'value'),
        Input('seller-date-picker-range', 'start_date'),
        Input('seller-date-picker-range', 'end_date'),
        Input('customer-date-picker-range', 'start_date'),
        Input('customer-date-picker-range', 'end_date'),
        Input('selected-state', 'data')
    ]
)
def update_map(map_view_type,
               seller_states, customer_states,
               seller_statuses, customer_statuses,
               seller_start_date, seller_end_date,
               customer_start_date, customer_end_date,
               selected_state_data):
    # Create dataframe with states counts
    brazil_states = [feature["id"] for feature in brazil["features"]]
    all_states_df = pd.DataFrame({'id': brazil_states, 'count': 0})

    seller_states = seller_states if isinstance(seller_states, list) else [seller_states]
    customer_states = customer_states if isinstance(customer_states, list) else [customer_states]
    selected_state = selected_state_data.get('state') if selected_state_data else None

    if map_view_type == 'sellers':
        filtered_data = df if 'FULL_VIEW' in seller_states else df[df['seller_state'].isin(seller_states)]
        filtered_data = filtered_data if 'FULL_VIEW' in seller_statuses else filtered_data[filtered_data['order_status'].isin(seller_statuses)]
        filtered_data = filtered_data if not seller_start_date else filtered_data[filtered_data['order_purchase_timestamp'] >= seller_start_date]
        filtered_data = filtered_data if not seller_end_date else filtered_data[filtered_data['order_purchase_timestamp'] <= seller_end_date]

        visualisation_data = filtered_data.groupby('seller_state').size().reset_index(name='count').rename(columns={'seller_state': 'id'})
        visualisation_data = all_states_df.merge(visualisation_data, on='id', how='left').fillna(0).rename(columns={'count_y': 'count'})
    elif map_view_type == 'customers':
        filtered_data = df if 'FULL_VIEW' in customer_states else df[df['customer_state'].isin(customer_states)]
        filtered_data = filtered_data if 'FULL_VIEW' in customer_statuses else filtered_data[filtered_data['order_status'].isin(customer_statuses)]
        filtered_data = filtered_data if not customer_start_date else filtered_data[filtered_data['order_purchase_timestamp'] >= customer_start_date]
        filtered_data = filtered_data if not customer_end_date else filtered_data[filtered_data['order_purchase_timestamp'] <= customer_end_date]

        visualisation_data = filtered_data.groupby('customer_state').size().reset_index(name='count').rename(columns={'customer_state': 'id'})
        visualisation_data = all_states_df.merge(visualisation_data, on='id', how='left').fillna(0).rename(columns={'count_y': 'count'})

    visualisation_data['hover_info'] = "State: " + visualisation_data['id'] + \
                                       "<br>Quantity of " + map_view_type + ": " + visualisation_data['count'].astype(str)

    if selected_state:
        single_state_data = visualisation_data[visualisation_data['id'] == selected_state]
        fig = px.choropleth(
            single_state_data,
            geojson=brazil,
            locations='id',
            color='count',
            color_continuous_scale='burgyl',
            custom_data='hover_info',
            featureidkey="properties.sigla",
            projection="mercator"
        )

        fig.update_traces(hovertemplate='%{customdata[0]}')
        fig.update_geos(fitbounds="locations", visible=True)
        fig.update_layout(
            hovermode='closest',
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Open Sans")
        )
        fig.add_annotation(
            x=0.5,
            y=1.0,
            xref="paper",
            yref="paper",
            text=f"<b>{single_state_data['hover_info'].iloc[0]}<b>",
            showarrow=False,
            font=dict(
                family='Open Sans',
                size=16,
                color="black"
            ),
            align="left",
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        )
    else:
        fig = px.choropleth(
            visualisation_data,
            geojson=brazil,
            locations='id',
            color='count',
            color_continuous_scale='burgyl',
            featureidkey="properties.sigla",
            custom_data='hover_info',
            projection="mercator"
        )
        fig.update_traces(hovertemplate='%{customdata[0]}')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            hovermode='closest',
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Open Sans"
            )
        )
    return fig


# Callback to reset state button
@app.callback(
    Output('reset-state-button', 'hidden'),
    [Input('selected-state', 'data')]
)
def toggle_reset_button_visibility(selected_state_data):
    if selected_state_data and 'state' in selected_state_data:
        return False
    return True


# Callback for sales distribution by categories
@app.callback(
    Output('seller-category-sales-distribution', 'figure'),
    [
        Input('seller-state-dropdown', 'value'),
        Input('order-status-dropdown', 'value'),
        Input('seller-date-picker-range', 'start_date'),
        Input('seller-date-picker-range', 'end_date')
    ]
)
def update_seller_graph(selected_states, selected_statuses, start_date, end_date):
    selected_states = selected_states if isinstance(selected_states, list) else [selected_states]
    filtered_data = df
    if 'FULL_VIEW' not in selected_states:
        filtered_data = filtered_data[filtered_data['seller_state'].isin(selected_states)]
    if 'FULL_VIEW' not in selected_statuses:
        filtered_data = filtered_data[filtered_data['order_status'].isin(selected_statuses)]
    if start_date:
        filtered_data = filtered_data[filtered_data['order_purchase_timestamp'] >= start_date]
    if end_date:
        filtered_data = filtered_data[filtered_data['order_purchase_timestamp'] <= end_date]

    category_counter = filtered_data['product_category_name_english'].value_counts().reset_index().sort_values('count', ascending=True)
    category_counter = category_counter[category_counter['count'] >= 1_000]

    sales_distribution = px.bar(category_counter, y='product_category_name_english', x='count',
                                title='Distribution of sales category by states <br>(with more than 1 000 sales)',
                                labels={'count': 'Number of sales', 'product_category_name_english': ''},
                                color_discrete_sequence=['#cce4fa'])
    sales_distribution.update_layout(
        font=dict(family='Open Sans', size=14),
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        plot_bgcolor=colors['plot_background'],
        height=1500
    )

    return sales_distribution


# Callback for purchases distribution by categories
@app.callback(
    Output('customer-category-purchases-distribution', 'figure'),
    [
        Input('customer-state-dropdown', 'value'),
        Input('customer-order-status-dropdown', 'value'),
        Input('customer-date-picker-range', 'start_date'),
        Input('customer-date-picker-range', 'end_date')
    ]
)
def update_customer_distribution(selected_states, selected_order_statuses, start_date, end_date):
    filtered_data = df
    selected_states = selected_states if isinstance(selected_states, list) else [selected_states]
    if 'FULL_VIEW' not in selected_states:
        filtered_data = filtered_data[filtered_data['customer_state'].isin(selected_states)]
    if 'FULL_VIEW' not in selected_order_statuses:
        filtered_data = filtered_data[filtered_data['order_status'].isin(selected_order_statuses)]
    if start_date:
        filtered_data = filtered_data[filtered_data['order_purchase_timestamp'] >= start_date]
    if end_date:
        filtered_data = filtered_data[filtered_data['order_purchase_timestamp'] <= end_date]

    category_counter = filtered_data['product_category_name_english'].value_counts().reset_index().sort_values('count', ascending=True)
    category_counter = category_counter[category_counter['count'] >= 1_000]

    purchases_distribution = px.bar(category_counter, y='product_category_name_english', x='count',
                                    title='Distribution of purchases category by states <br>(with more than 1 000 purchases)',
                                    labels={'count': 'Number of purchases', 'product_category_name_english': ''},
                                    color_discrete_sequence=['#cce4fa'])
    purchases_distribution.update_layout(
        font=dict(family='Open Sans', size=14),
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        plot_bgcolor=colors['plot_background'],
        height=1500
    )
    return purchases_distribution


# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
