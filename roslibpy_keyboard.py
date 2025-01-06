import pygame
import roslibpy
import threading

# Initialize Pygame
pygame.init()

# Set up the Pygame window
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Control Create3 Robot")

# ROS WebSocket connection details
ros_host = 'ws://127.0.0.1:9090'
ros_node_name = 'create3_teleop'

# Connect to ROS
ros_node = roslibpy.Ros(host='127.0.0.1', port=9090)
ros_node.run()

# Create a publisher for the /juliet/cmd_vel topic (Twist messages)
cmd_vel_pub = roslibpy.Topic(ros_node, '/juliet/cmd_vel', 'geometry_msgs/Twist')

# Movement parameters
speed = 0.2  # Linear speed
turn_speed = 1.0  # Angular speed

# Initialize the velocity dictionary
velocities = {
    'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
    'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
}


# Function to handle the IR intensity messages
def ir_intensity_callback(message):
    # Print the IR intensity data to the console
    print('new msg')

# Create a subscriber to the /juliet/ir_intensity topic
ir_intensity_sub = roslibpy.Topic(ros_node, '/juliet/imu', 'sensor_msgs/Imu')

# Main loopd
running = True
while running:
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Default movement: no movement
    velocities['linear']['x'] = 0.0
    velocities['angular']['z'] = 0.0

    # Read the state of the keys (W, A, S, D for movement)
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        velocities['linear']['x'] = speed  # Move forward
    if keys[pygame.K_s]:
        velocities['linear']['x'] = -speed  # Move backward
    if keys[pygame.K_a]:
        velocities['angular']['z'] = turn_speed  # Turn left
    if keys[pygame.K_d]:
        velocities['angular']['z'] = -turn_speed  # Turn right

    # Create a message dictionary to match ROS Twist format
    twist_message = roslibpy.Message({
        'linear': {
            'x': velocities['linear']['x'],
            'y': velocities['linear']['y'],
            'z': velocities['linear']['z']
        },
        'angular': {
            'x': velocities['angular']['x'],
            'y': velocities['angular']['y'],
            'z': velocities['angular']['z']
        }
    })

    # Publish the twist message to ROS
    cmd_vel_pub.publish(twist_message)

    # Refresh the display
    screen.fill((0, 0, 0))  # Black background
    pygame.display.flip()

# Clean up and close the Pygame window and ROS connection
pygame.quit()
ros_node.terminate()