import numpy as np
import matplotlib.pyplot as plt

def projectile_motion(v0, theta, total_time, dt):
    # Convert angle from degrees to radians for calculation
    theta_rad = np.radians(theta)
    
    # Constants
    g = 9.81  # Gravity (m/s^2)
    rho = 1.225  # Air density (kg/m^3)
    A = 0.045  # Cross-sectional area of the projectile (m^2)
    C_d = 0.47  # Drag coefficient (sphere)
    
    # Initial conditions
    vx = v0 * np.cos(theta_rad)
    vy = v0 * np.sin(theta_rad)
    x = 0
    y = 0
    
    # Number of steps
    steps = int(total_time / dt)
    
    # Initialize arrays
    x_points = np.zeros(steps)
    y_points = np.zeros(steps)
    
    # Time simulation
    for i in range(steps):
        # Update positions
        x += vx * dt
        y += vy * dt
        
        # Update velocities
        v = np.sqrt(vx**2 + vy**2)  # Total velocity
        drag_force = 0.5 * rho * A * C_d * v**2
        vx -= (drag_force / v) * vx * dt / v0
        vy -= (g + (drag_force / v) * vy / v0) * dt
        
        # Store points
        x_points[i] = x
        y_points[i] = y
        
        # Stop if projectile hits the ground
        if y < 0:
            x_points = x_points[:i]
            y_points = y_points[:i]
            break
    
    return x_points, y_points

def plot_trajectory(x, y):
    plt.figure(figsize=(10, 5))
    plt.plot(x, y)
    plt.title("Projectile Motion Simulation")
    plt.xlabel("Distance (m)")
    plt.ylabel("Height (m)")
    plt.grid(True)
    plt.show()

# Simulation parameters
initial_velocity = 60  # m/s
launch_angle = 20  # degrees
simulation_time = 20 # seconds
time_step = 0.01  # Time step for the Euler method

# Calculate trajectory
x, y = projectile_motion(initial_velocity, launch_angle, simulation_time, time_step)

# Plot the trajectory
plot_trajectory(x, y)
