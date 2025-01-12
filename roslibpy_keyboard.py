import pygame
import roslibpy
import threading
import time
import random


# Initialize Pygame
pygame.init()

clock = pygame.time.Clock()

# Set up the Pygame window
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Control Create3 Robot")

# Connect to ROS
robot_name = 'juliet'
ros_node = roslibpy.Ros(host='127.0.0.1', port=9012) # simulator
#ros_node = roslibpy.Ros(host='192.168.8.104', port=9012) # hardware (rosbridge)

ros_node.run() # this is a non-blocking call

# Create a publisher for the /juliet/cmd_vel topic (Twist messages)
cmd_vel_pub = roslibpy.Topic(ros_node, f'/{robot_name}/cmd_vel', 'geometry_msgs/Twist')

cmd_lightring_pub = roslibpy.Topic(ros_node, f'/{robot_name}/cmd_lightring', 'irobot_create_msgs/LightringLeds')

# Movement parameters
speed = 0.2  # Linear speed
turn_speed = 1.0  # Angular speed

# Initialize the cmd_vel message
velocities = {
    'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
    'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
}


# Function to handle the IR intensity messages
def odom_callback(message):
    print(f'Odometry message received: {message}')
    
def imu_callback(message):
    print(f'IMU message received: {message}')

def ir_callback(message):
    print(f'IR message received: {message}')
 

# Create a subscriber to the /juliet/odom topic
odom_sub = roslibpy.Topic(ros_node, f'/{robot_name}/odom', 'nav_msgs/Odometry')
imu_sub = roslibpy.Topic(ros_node, f'/{robot_name}/imu', 'sensor_msgs/Imu')
ir_sub = roslibpy.Topic(ros_node, f'/{robot_name}/ir_intensity', 'irobot_create_msgs/IrIntensityVector')

# Subscribe to the /juliet/odom topic
#odom_sub.subscribe(odom_callback)
#imu_sub.subscribe(imu_callback)
#ir_sub.subscribe(ir_callback)

# Main loop
running = True
lightflag = True
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
    if keys[pygame.K_b]:
        lightflag = True
    if keys[pygame.K_q]:
        running = False

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


    # Define the message
    # Example: Set 6 LEDs with specified colors (RGB values)
    led_colors = [
        {'red': random.randint(0,255), 'green': random.randint(0,255), 'blue': random.randint(0,255)},  # Red
        {'red': random.randint(0,255), 'green': random.randint(0,255), 'blue': random.randint(0,255)},  # Green
        {'red': random.randint(0,255), 'green': random.randint(0,255), 'blue': random.randint(0,255)},  # Blue
        {'red': random.randint(0,255), 'green': random.randint(0,255), 'blue': random.randint(0,255)},  # Yellow
        {'red': random.randint(0,255), 'green': random.randint(0,255), 'blue': random.randint(0,255)},  # Cyan
        {'red': random.randint(0,255), 'green': random.randint(0,255), 'blue': random.randint(0,255)},  # Magenta
    ]

    message_light = roslibpy.Message({
        'leds': led_colors,
        'override_system': True
    })

    # create a python dictionary variable with correct key-value structure
    #vector3_message = {"x": 10.0, "y": 20.0, "z": 30.0}
    # create a ROS message from the dictionary using roslibpy.Message method
    #vector3_ROS_message = roslibpy.Message(vector3_message) 


    # Publish the twist message to ROS
    cmd_vel_pub.publish(twist_message)

    if lightflag:
        cmd_lightring_pub.publish(message_light)
        #lightflag = False

    # Refresh the display
    screen.fill((0, 0, 0))  # Black background
    pygame.display.flip()

    # make it run at 10Hz
    clock.tick(10)
# Clean up and close the Pygame window and ROS connection
pygame.quit()
ros_node.terminate()