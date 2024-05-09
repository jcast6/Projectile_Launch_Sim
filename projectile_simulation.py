import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

# Function to calculate air viscosity based on temperature (Sutherland's formula)
def air_viscosity(T):
    T0 = 273.15  # Reference temperature (Kelvin)
    mu0 = 1.716e-5  # Reference dynamic viscosity (kg/m·s at 273.15 K)
    C = 111  # Sutherland's constant (Kelvin)
    return mu0 * ((T0 + C) / (T + C)) * ((T / T0) ** 1.5)

# Simulation of projectile motion considering air resistance
def projectile_motion(v0, theta, mass, dt, drag_coefficient, include_drag=True, T=293.15, diameter=0.1):
    theta_rad = np.radians(theta)  # Convert angle to radians
    g = 9.81  # Acceleration due to gravity (m/s^2)
    rho = 1.225 if include_drag else 0  # Air density (kg/m^3)
    A = np.pi * (diameter / 2) ** 2 if include_drag else 0  # Cross-sectional area of the projectile
    vx = v0 * np.cos(theta_rad)  # Initial horizontal velocity
    vy = v0 * np.sin(theta_rad)  # Initial vertical velocity
    x = 0  # Initial horizontal position
    y = 0  # Initial vertical position

    while True:
        next_x = x + vx * dt  # Calculate next horizontal position
        next_y = y + vy * dt  # Calculate next vertical position

        if next_y < 0:  # Check if projectile hits the ground
            t = -y / vy  # Time to reach y=0, assuming vy != 0
            x += vx * t  # Adjust x to the impact point
            y = 0  # Projectile hits the ground
            yield x, y
            break

        x, y = next_x, next_y  # Update position

        if include_drag and y > 0:
            v = np.sqrt(vx**2 + vy**2)  # Speed of the projectile
            drag_force = 0.5 * rho * A * drag_coefficient * v**2  # Drag force calculation
            acceleration_drag = drag_force / mass  # Acceleration due to drag
            vx -= (acceleration_drag / v) * vx * dt  # Update horizontal velocity
            vy -= (g + (acceleration_drag / v) * vy) * dt  # Update vertical velocity
        else:
            vy -= g * dt  # Only gravity affects vertical velocity when no drag

        yield x, y

app = dash.Dash(__name__)

trajectory_data_p1 = []
projectile_generator_p1 = None

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Label("Initial Velocity (m/s): ", style={'marginRight': '10px'}),
                dcc.Input(id='velocity-input', type='number', value=60)
            ], style={'display': 'flex', 'alignItems': 'center'}),

            html.Div([
                html.Label("Launch Angle (degrees): ", style={'marginRight': '10px'}),
                dcc.Input(id='angle-input', type='number', value=20)
            ], style={'display': 'flex', 'alignItems': 'center'}),

            html.Div([
                html.Label("Mass of the Projectile (kg): ", style={'marginRight': '10px'}),
                dcc.Input(id='mass-input', type='number', value=1)
            ], style={'display': 'flex', 'alignItems': 'center'}),

            html.Div([
                html.Label("Time Step (seconds): ", style={'marginRight': '10px'}),
                dcc.Input(id='time-step-input', type='number', value=0.01)
            ], style={'display': 'flex', 'alignItems': 'center'}),

            html.Div([
                html.Label("Drag Coefficient: ", style={'marginRight': '10px'}),
                dcc.Input(id='drag-coefficient-input', type='number', value=0.47, step=0.01)
            ], style={'display': 'flex', 'alignItems': 'center'}),

            html.Div([
                html.Label("Include Air Resistance: ", style={'marginRight': '10px'}),
                dcc.Dropdown(
                    id='drag-input',
                    options=[
                        {'label': 'Yes', 'value': 'yes'},
                        {'label': 'No', 'value': 'no'}
                    ],
                    value='yes'
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'gap': '10px', 'maxWidth': '500px'}),
    ], style={'padding': '20px'}),

    html.Button(
        'Run Simulation', 
        style={
            'marginRight': '10px', 
            'color': '#fff', 
            'backgroundColor': '#007BFF', 
            'border': 'none',
            'borderRadius': '5px',
            'padding': '10px 20px',
            'fontSize': '16px',
            'fontWeight': 'bold',
            'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)'
        }, 
        id='run-button', 
        n_clicks=0
    ),
    html.Button(
        'Reset Simulation', 
        style={
            'color': '#fff', 
            'backgroundColor': '#6c757d', 
            'border': 'none',
            'borderRadius': '5px',
            'padding': '10px 20px',
            'fontSize': '16px',
            'fontWeight': 'bold',
            'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)'
        }, 
        id='reset-button', 
        n_clicks=0
    ),
    dcc.Graph(id='trajectory-plot'),
    dash_table.DataTable(
        id='trajectory-table',
        columns=[
            {"name": "Time Step", "id": "time_step", 'type': 'numeric', 'format': {'specifier': '.3f'}},
            {"name": "X Position", "id": "x", 'type': 'numeric', 'format': {'specifier': '.3f'}},
            {"name": "Y Position", "id": "y", 'type': 'numeric', 'format': {'specifier': '.3f'}}
        ],
        data=[],
        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '120px', 'maxWidth': '140px'},
        style_table={'height' : '155px', 'width': '50%', 'overflowY' : 'scroll'},
        style_header={'backgroundColor': 'white', 'fontWeight': 'bold'}
    ),
    dcc.Interval(id='interval-component', interval=100, n_intervals=0, disabled=True)
])


@app.callback(
    [Output('trajectory-plot', 'figure'),
     Output('trajectory-table', 'data'),
     Output('interval-component', 'disabled')],
    [Input('interval-component', 'n_intervals'),
     Input('run-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('velocity-input', 'value'),
     State('angle-input', 'value'),
     State('mass-input', 'value'),
     State('time-step-input', 'value'),
     State('drag-coefficient-input', 'value'),
     State('drag-input', 'value')]
)
def update_simulation(n_intervals, run_clicks, reset_clicks, v0, theta, mass, dt, drag_coefficient, drag):
    global projectile_generator_p1, trajectory_data_p1

    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'run-button' and ctx.triggered[0]['value']:
        include_drag = drag == 'yes'
        projectile_generator_p1 = projectile_motion(v0, theta, mass, dt, drag_coefficient, include_drag)
        return go.Figure(), [], False  # Start the interval and initiate plotting

    if triggered_id == 'reset-button' and ctx.triggered[0]['value']:
        projectile_generator_p1 = None
        trajectory_data_p1 = []  # Clear the data for projectile 1
        return go.Figure(), [], True  # Reset the plot and disable the interval

    if projectile_generator_p1 is not None:
        try:
            x_p1, y_p1 = next(projectile_generator_p1)
            trajectory_data_p1.append({'time_step': n_intervals * dt, 'x': x_p1, 'y': y_p1})
            fig = go.Figure(data=[
                go.Scatter(x=[point['x'] for point in trajectory_data_p1], y=[point['y'] for point in trajectory_data_p1], mode='lines+markers', name='Trajectory')
            ])
            fig.update_layout(title="Projectile Trajectory", xaxis_title="Distance (m)", yaxis_title="Height (m)")
            return fig, trajectory_data_p1, False  # Keep the interval active
        except StopIteration:
            return dash.no_update, trajectory_data_p1, True  # Disable further updates without clearing the plot

    raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
