import dash
from dash import dcc, html, Input, Output, State, dash_table, no_update, ctx
import pandas as pd
import datetime

# Sample transaction history data
data = pd.DataFrame({
    'Driver ID': ['D001', 'D002', 'D003'],
    'Date': ['2025-02-10', '2025-02-15', '2025-02-20'],
    'Usage Category': ['Charging', 'Maintenance', 'Charging'],
    'Cost': [20, 50, 30],
    'Amount Paid': [20, 50, 30],
    'Battery Percentage': [80, 60, 90],
    'Remaining Balance': [200, 150, 300]
})

# Initialize Dash app
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=["https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"]
)
app.title = "Fleet Manager Dashboard"
server = app.server  # Needed for deployment

# Session store to track login state
app.layout = html.Div(
    style={'backgroundColor': '#2E2E2E', 'minHeight': '100vh', 'padding': '20px'},
    children=[
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='session', storage_type='local'),  # Stores login session
        dcc.Store(id='current-driver', storage_type='memory'),  # Stores selected driver info
        html.Div(id='page-content')
    ]
)

# ---------- Layout for the login page ----------
# A simple navbar for the login screen without logout button
login_navbar = html.Nav(
    [
        html.Div(
            [
                html.Div(
                    [html.Img(src="/assets/logo.png", style={"height": "50px"})],
                    style={"flex": "1", "textAlign": "left"}
                ),
                # Keep the right side empty to avoid logout or other links
                html.Div([], style={"flex": "1", "textAlign": "right"})
            ],
            style={"display": "flex", "alignItems": "center", "width": "100%"}
        )
    ],
    className="nav-wrapper blue darken-3"
)

login_layout = html.Div([
    # Insert the login navbar on top
    html.Div([login_navbar], className="container"),

    # Wrap the login form in its own container
    html.Div([
        html.H4("Login", className="center-align white-text", style={'marginTop': '30px'}),
        html.Div([
            dcc.Input(
                id='username',
                type='text',
                placeholder='Enter username',
                className="input-field col s12"
            ),
            dcc.Input(
                id='password',
                type='password',
                placeholder='Enter password',
                className="input-field col s12"
            ),
            html.Button(
                "Login",
                id='login-button',
                n_clicks=0,
                className="waves-effect waves-light btn green darken-3 col s12"
            ),
            html.Div(
                id='login-output',
                className='red-text center-align mt-2'
            )
        ], className="row")
    ], className="container center-align", style={'marginTop': '30px'})
])

# ---------- Layout for the main (dashboard) page ----------

# Navbar
navbar = html.Nav(
    [
        html.Div(
            [
                html.Div(
                    [html.Img(src="/assets/logo.png", style={"height": "50px"})],
                    style={"flex": "1", "textAlign": "left"}
                ),
                html.Div(
                    [
                        html.Ul(
                            [
                                html.Li(
                                    html.A(
                                        "Logout",
                                        id="logout-button",
                                        className="waves-effect waves-light btn red darken-3"
                                    )
                                )
                            ],
                            className="right"
                        )
                    ],
                    style={"flex": "1", "textAlign": "right"}
                )
            ],
            style={"display": "flex", "alignItems": "center", "width": "100%"}
        )
    ],
    className="nav-wrapper blue darken-3"
)

header_section = html.Div(
    [
        html.H1("Fleet Manager Dashboard", className="center-align white-text")
    ],
    className="container"
)

search_section = html.Div(
    [
        html.H3("Driver Search", className="white-text"),
        html.Label("Enter Driver ID:"),
        dcc.Input(id='driver-id', type='text', className="input-field"),
        html.Button('Search', id='search-button', className="btn waves-effect waves-light")
    ],
    className="container"
)

# Separate containers for different sections in the dashboard
battery_container = html.Div(
    [
        html.Div(id='battery-usage', className="card-panel blue darken-3 white-text center col s12 m4"),
        html.Div(id='remaining-balance', className="card-panel green darken-3 white-text center col s12 m4"),
        html.Div(id='total-cost', className="card-panel red darken-3 white-text center col s12 m4")
    ],
    className="container row",
    style={'marginTop': '20px'}
)

# Updated transaction_container and payment_container to be stacked instead of in a row
transaction_container = html.Div(
    [
        html.H3("Transaction History", className="center-align"),
        dash_table.DataTable(
            id='transaction-table',
            columns=[{'name': col, 'id': col} for col in data.columns],
            data=[],
            style_table={'overflowX': 'auto'}
        )
    ],
    className="container card-panel",
    style={'marginTop': '20px', 'textAlign': 'center', 'marginLeft': 'auto', 'marginRight': 'auto'}
)

payment_container = html.Div(
    [
        html.H3("Update Payment", className="center-align"),
        dcc.Input(id='amount', type='number', placeholder='Enter amount', className="input-field"),
        dcc.DatePickerSingle(
            id='date-picker',
            min_date_allowed=datetime.date(2025, 1, 1),
            max_date_allowed=datetime.date(2025, 12, 31),
            date=datetime.date(2025, 2, 18)
        ),
        html.Button('Update', id='update-button', className="btn waves-effect waves-light"),
        html.Div(id='update-message', className="green-text")
    ],
    className="container card-panel",
    style={'marginTop': '20px', 'textAlign': 'center', 'marginLeft': 'auto', 'marginRight': 'auto'}
)

dashboard_content = html.Div(
    id='dashboard-content',
    style={'display': 'none'},
    children=[
        battery_container,
        transaction_container,
        payment_container
    ]
)

# Combine everything into a single dashboard layout
# (nav, header, search, main content)

dashboard_layout = html.Div(
    [
        html.Div([navbar], className="container"),
        header_section,
        search_section,
        dashboard_content
    ]
)

# ---------- Callbacks ----------

# Page selection callback
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('session', 'data')
)
def display_page(pathname, session_data):
    if session_data and session_data.get('logged_in'):
        return dashboard_layout
    return login_layout

# Login callback
@app.callback(
    [Output('session', 'data'), Output('url', 'pathname'), Output('login-output', 'children')],
    Input('login-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value')
)
def login(n_clicks, username, password):
    if n_clicks and username == 'admin' and password == 'password':
        return {'logged_in': True}, '/dashboard', ""
    elif n_clicks:
        return None, '/', "Invalid Credentials. Try again."
    return no_update, no_update, ""

# Logout callback
@app.callback(
    Output('session', 'data', allow_duplicate=True),
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call='initial_duplicate'
)
def logout(n_clicks):
    if n_clicks:
        return None, '/'  # Clears session and returns to login
    return no_update, no_update

# Update the main dashboard content after searching a driver
@app.callback(
    [Output('dashboard-content', 'style'),
     Output('battery-usage', 'children'),
     Output('remaining-balance', 'children'),
     Output('total-cost', 'children'),
     Output('transaction-table', 'data')],
    Input('search-button', 'n_clicks'),
    State('driver-id', 'value')
)
def update_dashboard(n_clicks, driver_id):
    if n_clicks and driver_id:
        filtered_data = data[data['Driver ID'] == driver_id]
        if not filtered_data.empty:
            battery = f"Battery Usage: {filtered_data['Battery Percentage'].values[0]}%"
            balance = f"Remaining Balance: £{filtered_data['Remaining Balance'].values[0]}"
            total_cost = f"Total Cost Last 30 Days: £{filtered_data['Cost'].sum()}"
            return {'display': 'block'}, battery, balance, total_cost, filtered_data.to_dict('records')
    return {'display': 'none'}, "Battery Usage: N/A", "Remaining Balance: N/A", "Total Cost Last 30 Days: N/A", []

# (Optional) Callback to handle payment updates
@app.callback(
    [Output('transaction-table', 'data', allow_duplicate=True),
     Output('update-message', 'children')],
    Input('update-button', 'n_clicks'),
    State('amount', 'value'),
    State('date-picker', 'date'),
    State('driver-id', 'value'),
    prevent_initial_call=True
)
def update_payment(n_clicks, amount, date, driver_id):
    if n_clicks and amount is not None and date is not None and driver_id:
        global data
        # Create a new transaction record
        new_transaction = pd.DataFrame({
            'Driver ID': [driver_id],
            'Date': [date],
            'Usage Category': ['Payment'],
            'Cost': [0],
            'Amount Paid': [amount],
            'Battery Percentage': [data[data['Driver ID'] == driver_id]['Battery Percentage'].values[0]],
            'Remaining Balance': [data[data['Driver ID'] == driver_id]['Remaining Balance'].values[0] - amount]
        })
        data = pd.concat([data, new_transaction], ignore_index=True)
        updated_data = data[data['Driver ID'] == driver_id].to_dict('records')
        return updated_data, f"Payment of £{amount} recorded for driver {driver_id}."
    return no_update, "Invalid payment request."

if __name__ == '__main__':
    app.run_server(debug=True)
