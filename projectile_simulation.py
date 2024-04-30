import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objects as go
from itertools import zip_longest

def projectile_motion(v0, theta, mass, dt, include_drag=True):
    theta_rad = np.radians(theta)
    g = 9.81  # acceleration due to gravity
    rho = 1.225 if include_drag else 0  # air density
    A = 0.045 if include_drag else 0  # cross-sectional area
    C_d = 0.47 if include_drag else 0  # drag coefficient
    vx = v0 * np.cos(theta_rad)
    vy = v0 * np.sin(theta_rad)
    x = 0
    y = 0

    while True:
        next_x = x + vx * dt
        next_y = y + vy * dt

        # Check if the projectile hits the ground on the next step
        if next_y < 0:
            # Interpolate to find the exact point where y crosses zero
            t = -y / vy  # time to reach y=0
            x += vx * t
            y = 0  # set y exactly to zero
            yield x, y  # yield the final point where y is exactly zero
            break  # exit after reaching the ground

        # Continue with the motion update
        yield x, y
        x, y = next_x, next_y

        # Update velocities considering drag
        if include_drag and y > 0:
            v = np.sqrt(vx**2 + vy**2)
            drag_force = 0.5 * rho * A * C_d * v**2
            acceleration_drag = drag_force / mass
            vx -= (acceleration_drag / v) * vx * dt
            vy -= (g + (acceleration_drag / v) * vy) * dt
        else:
            vy -= g * dt
app = dash.Dash(__name__)

# Global variables to store trajectory data and generators
trajectory_data_p1 = []
trajectory_data_p2 = []
projectile_generator_p1 = None
projectile_generator_p2 = None

app.layout = html.Div([
    html.Div([
        # Input controls for Projectile 1
        html.Div([
            html.Label("Initial Velocity (m/s) P1:"),
            dcc.Input(id='velocity-input-p1', type='number', value=60, style={'margin': '10px'}),
            html.Label("Launch Angle (degrees) P1:"),
            dcc.Input(id='angle-input-p1', type='number', value=20, style={'margin': '10px'}),
            html.Label("Mass of the Projectile (kg) P1:"),
            dcc.Input(id='mass-input-p1', type='number', value=1, style={'margin': '10px'}),
            html.Label("Time Step (seconds) P1:"),
            dcc.Input(id='time-step-input-p1', type='number', value=0.01, style={'margin': '10px'}),
            html.Label("Include Air Resistance P1:"),
            dcc.Dropdown(id='drag-input-p1', options=[
                {'label': 'Yes', 'value': 'yes'}, {'label': 'No', 'value': 'no'}
            ], value='yes', style={'width': '100px', 'margin': '10px'}),
        ], style={'width': '48%', 'display': 'inline-block'}),

        # Input controls for Projectile 2
        html.Div([
            html.Label("Initial Velocity (m/s) P2:"),
            dcc.Input(id='velocity-input-p2', type='number', value=60, style={'margin': '10px'}),
            html.Label("Launch Angle (degrees) P2:"),
            dcc.Input(id='angle-input-p2', type='number', value=20, style={'margin': '10px'}),
            html.Label("Mass of the Projectile (kg) P2:"),
            dcc.Input(id='mass-input-p2', type='number', value=1, style={'margin': '10px'}),
            html.Label("Time Step (seconds) P2:"),
            dcc.Input(id='time-step-input-p2', type='number', value=0.01, style={'margin': '10px'}),
            html.Label("Include Air Resistance P2:"),
            dcc.Dropdown(id='drag-input-p2', options=[
                {'label': 'Yes', 'value': 'yes'}, {'label': 'No', 'value': 'no'}
            ], value='yes', style={'width': '100px', 'margin': '10px'}),
        ], style={'width': '48%', 'display': 'inline-block'}),
    ]),
    html.Button('Run Simulation', id='run-button', n_clicks=0, style={'margin': '10px'}),
    html.Button('Reset Simulation', id='reset-button', n_clicks=0, style={'margin': '10px'}),
    html.Div([
        # Plots for each projectile
        dcc.Graph(id='trajectory-plot-p1'),
        dcc.Graph(id='trajectory-plot-p2'),
    ], style={'display': 'flex'}),
    dcc.Interval(id='interval-component', interval=100, n_intervals=0, disabled=True),

        html.Div([
            dash_table.DataTable(
                id='trajectory-table',
                columns=[
                    {"name": "Time Step", "id": "time_step"},
                    {"name": "X P1", "id": "x_p1"},
                    {"name": "Y P1", "id": "y_p1"},
                    {"name": "X P2", "id": "x_p2"},
                    {"name": "Y P2", "id": "y_p2"}
                ],
                data=[],
                style_table={'height': '300px', 'overflowY': 'auto'}
            )
        ], style={'width': '100%', 'display': 'inline-block'})
])
@app.callback(
    [Output('trajectory-plot-p1', 'figure'),
     Output('trajectory-plot-p2', 'figure'),
     Output('trajectory-table', 'data'), 
     Output('interval-component', 'disabled')],
    [Input('interval-component', 'n_intervals'),
     Input('run-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('velocity-input-p1', 'value'),
     State('angle-input-p1', 'value'),
     State('mass-input-p1', 'value'),
     State('time-step-input-p1', 'value'),
     State('drag-input-p1', 'value'),
     State('velocity-input-p2', 'value'),
     State('angle-input-p2', 'value'),
     State('mass-input-p2', 'value'),
     State('time-step-input-p2', 'value'),
     State('drag-input-p2', 'value')]
)
def update_simulation(n_intervals, run_clicks, reset_clicks, v0_p1, theta_p1, mass_p1, dt_p1, drag_p1, v0_p2, theta_p2, mass_p2, dt_p2, drag_p2):
    global projectile_generator_p1, projectile_generator_p2, trajectory_data_p1, trajectory_data_p2
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'run-button':
        include_drag_p1 = drag_p1 == 'yes'
        projectile_generator_p1 = projectile_motion(v0_p1, theta_p1, mass_p1, dt_p1, include_drag_p1)
        include_drag_p2 = drag_p2 == 'yes'
        projectile_generator_p2 = projectile_motion(v0_p2, theta_p2, mass_p2, dt_p2, include_drag_p2)

    elif triggered_id == 'reset-button':
        trajectory_data_p1 = []
        trajectory_data_p2 = []
        projectile_generator_p1 = None
        projectile_generator_p2 = None
        return go.Figure(), go.Figure(), [], True

    finished1 = finished2 = True

    if projectile_generator_p1 is not None:
        try:
            x_p1, y_p1 = next(projectile_generator_p1)
            trajectory_data_p1.append((x_p1, y_p1))
            finished1 = False
        except StopIteration:
            projectile_generator_p1 = None
            finished1 = True

    if projectile_generator_p2 is not None:
        try:
            x_p2, y_p2 = next(projectile_generator_p2)
            trajectory_data_p2.append((x_p2, y_p2))
            finished2 = False
        except StopIteration:
            projectile_generator_p2 = None
            finished2 = True

    data_table = [
        {
            "time_step": i,
            "x_p1": f"{point[0]:.3f}" if i < len(trajectory_data_p1) else "",
            "y_p1": f"{point[1]:.3f}" if i < len(trajectory_data_p1) else "",
            "x_p2": f"{point2[0]:.3f}" if i < len(trajectory_data_p2) else "",
            "y_p2": f"{point2[1]:.3f}" if i < len(trajectory_data_p2) else ""
        }
        for i, (point, point2) in enumerate(zip_longest(trajectory_data_p1, trajectory_data_p2, fillvalue=(None, None)))
    ]

    def update_figure(data, title, line_color):
        fig = go.Figure(data=[
            go.Scatter(
                x=[point[0] for point in data], 
                y=[point[1] for point in data], 
                mode='lines+markers', 
                name='Trajectory',
                line=dict(color=line_color)
            )
        ])
        fig.update_layout(title=title, xaxis_title="Distance (m)", yaxis_title="Height (m)")
        return fig
    

    fig1 = update_figure(trajectory_data_p1, "Projectile 1 Plot", 'blue')
    fig2 = update_figure(trajectory_data_p2, "Projectile 2 Plot", 'red')

    all_finished = finished1 and finished2
    return fig1, fig2, data_table, all_finished

if __name__ == '__main__':
    app.run_server(debug=True)

