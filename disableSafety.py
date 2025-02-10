import roslibpy

# Connect to ROS
client = roslibpy.Ros(host='192.168.8.104', port=9012)
client.run()

if client.is_connected:
    print("Connected to ROS!")

    # Define the parameter in the 'omega' namespace
    safety_override_param = roslibpy.Param(client, '/omega/motion_control/safety_override')

    # Get the value of the parameter
    def on_response(value):
        print(f"The value of '/omega/motion_control/safety_override' is: {value}")

    safety_override_param.get(on_response)
else:
    print("Failed to connect to ROS. Check your ROS setup.")

# Clean up after query
client.terminate()



# import time # import time library
# import roslibpy # import roslibpy library

# # establish roslibpy connection to ROS
# #ros_node = roslibpy.Ros(host='127.0.0.1', port=9012)
# ros_node = roslibpy.Ros(host='192.168.8.104', port=9012)


# # start ROSLIBPY node
# ros_node.run()



# # define robot name we will connect to
# robot_name = 'omega'


# print(ros_node.get_param('/omega/safety_override'))



# # create publisher on the cmd_lightring topic, use https://iroboteducation.github.io/create3_docs/api/ros2/ for message type specification
# cmd_vel_pub = roslibpy.Topic(ros_node, f'/{robot_name}/cmd_vel', 'geometry_msgs/Twist')





# ros_node.set_param(f'/{robot_name}/safety_override', 'full')


# # Movement parameters
# speed = 0.2  # Linear speed
# turn_speed = 1.0  # Angular speed

# # Initialize the cmd_vel message
# velocities = {
#     'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
#     'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
# }


# # Main loop
# running = True
# count = 0
# while running:
    
#     # Default movement: no movement
#     velocities['linear']['x'] = -0.2
#     velocities['angular']['z'] = 0.0

#     # Create a message dictionary to match ROS Twist format
#     twist_message = roslibpy.Message({
#         'linear': {
#             'x': velocities['linear']['x'],
#             'y': velocities['linear']['y'],
#             'z': velocities['linear']['z']
#         },
#         'angular': {
#             'x': velocities['angular']['x'],
#             'y': velocities['angular']['y'],
#             'z': velocities['angular']['z']
#         }
#     })


#     # Publish the twist message to ROS
#     cmd_vel_pub.publish(twist_message)
#     time.sleep(0.2)
#     if count > 30:
#         running = False
#     count +=1

# # Clean up and close the Pygame window and ROS connection
# cmd_vel_pub.unadvertise()

# ros_node.terminate()