import numpy as np
import plotly.graph_objects as go

def projectile_motion(v0, theta, total_time, dt, include_drag=True):
    # Convert angle from degrees to radians for calculation
    theta_rad = np.radians(theta)
    
    # Constants
    g = 9.81  # Gravity (m/s^2)
    rho = 1.225  # Air density (kg/m^3) (used only if include_drag is True)
    A = 0.045  # Cross-sectional area of the projectile (m^2) (used only if include_drag is True)
    C_d = 0.47  # Drag coefficient (sphere) (used only if include_drag is True)
    
    # Initial conditions
    vx = v0 * np.cos(theta_rad)
    vy = v0 * np.sin(theta_rad)
    x = 0
    y = 0
    
    # Number of steps
    steps = int(total_time / dt)
    
    # Initialize arrays for time and positions
    times = np.linspace(0, total_time, num=steps, endpoint=False)
    x_points = np.zeros(steps)
    y_points = np.zeros(steps)
    
    # Time simulation
    for i in range(steps):
        # Update positions
        x += vx * dt
        y += vy * dt
        
        if include_drag:
            # Update velocities with drag
            v = np.sqrt(vx**2 + vy**2)  # Total velocity
            drag_force = 0.5 * rho * A * C_d * v**2
            vx -= (drag_force / v) * vx * dt / v0
            vy -= (g + (drag_force / v) * vy / v0) * dt
        else:
            # Update velocities without drag
            vy -= g * dt
        
        # Store points
        x_points[i] = x
        y_points[i] = y
        
        # Stop if projectile hits the ground
        if y < 0:
            times = times[:i+1]
            x_points = x_points[:i+1]
            y_points = y_points[:i+1]
            break
    
    return times, x_points, y_points

def plot_trajectories_and_table(v0, theta, dt, include_drag=True):
    # Calculate trajectory with drag
    times_drag, x_drag, y_drag = projectile_motion(v0, theta, simulation_time, dt, include_drag=True)
    # Calculate trajectory without drag
    times_no_drag, x_no_drag, y_no_drag = projectile_motion(v0, theta, simulation_time, dt, include_drag=False)

    # Create traces for the plot
    trace1 = go.Scatter(x=x_drag, y=y_drag, mode='lines', name='With Drag')
    trace2 = go.Scatter(x=x_no_drag, y=y_no_drag, mode='lines', name='Without Drag')

    # Create table for comparison
    table = go.Table(
        header=dict(values=['Time (s)', 'Distance With Drag (m)', 'Height With Drag (m)', 
                            'Distance Without Drag (m)', 'Height Without Drag (m)'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[times_drag, x_drag, y_drag, x_no_drag, y_no_drag],
                   fill=dict(color=['lavender', 'white']),
                   align='left'),
        domain=dict(x=[0, 1], y=[0, 0.2])  # Adjust domain to place table lower
    )

    # Create a figure with a subplot for each trace and table
    fig = go.Figure(data=[trace1, trace2, table])

    # Update layout for a clear view
    fig.update_layout(
        title="Projectile Motion Comparison",
        xaxis_title="Distance (m)",
        yaxis_title="Height (m)",
        legend_title="Legend",
        showlegend=True,
        width=1000,
        height=1000,  # Increased height to accommodate more table rows
        plot_bgcolor='rgb(243, 243, 243)',
        paper_bgcolor='rgb(243, 243, 243)'
    )

    # Adjust y-axis of plots to make room for the table
    fig['layout']['yaxis']['domain'] = [0.4, 1]  # Increase the space allocated for the plot

    # Show the figure
    fig.show()

# Simulation parameters
initial_velocity = 60  # m/s
launch_angle = 20  # degrees
simulation_time = 20 # seconds
time_step = 0.01  # Time step for the Euler method

# Plot both trajectories and data table using Plotly
plot_trajectories_and_table(initial_velocity, launch_angle, time_step)
