import pygame
from math import cos, sin, degrees, radians
import json
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor, task

import random


class Create3(pygame.sprite.Sprite):
    """
This module simulates a Create3 robot using Pygame and integrates with ROS via WebSocket.
Classes:
    Create3(pygame.sprite.Sprite): Represents the Create3 robot with methods to update its state, check for collisions, and publish odometry.
    Topic: Represents a ROS topic with methods to publish and subscribe to messages.
    WebSocketProtocol(WebSocketServerProtocol): Handles WebSocket connections and message broadcasting for ROS topics.
    RosSimulator: Manages the Pygame simulation environment, including robot creation, background setup, and the main simulation loop.
Functions:
    main(): Initializes the ROS simulator, sets up the WebSocket server, and starts the Pygame simulation loop integrated with the Twisted reactor.
Usage:
    Run this module directly to start the Create3 robot simulation with ROS integration.
"""

    def __init__(self, screen, ros_instance, name='juliet'):
        super().__init__()
        print(f'Creating robot {name}')
        
        self.image = pygame.image.load('./assets/images/create3.png').convert_alpha()
        self.image = pygame.transform.rotate(self.image, -90)
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() // 5, self.image.get_height() // 5))

        self.radius = self.image.get_width() // 2 -10# radius of robot in pixels
        self.radius_points = []
        for i in range(0, 360, 30):
            self.radius_points.append((self.radius * cos(i), self.radius * sin(i)))
        self.ir_points = [-65.3,-34,-14.25,3,20,38,65.3] # in degrees, from create3 technical specs
        self.IR_RANGE = 0.1 # in meters

        self.og_image = self.image
        self.rect = self.image.get_rect(center=screen.get_rect().center)
        self.robot_width = self.rect.width
        self.screen = screen

        # Robot state
        self.pixel_per_meter = 200
        self.theta = 0 # in radians
        self.theta_dot = 0 # in radians per second
        self.x, self.y = (0,0)
        self.rect.center = self.get_pixel_position()
        self.v = 0                 # linear velocity in m/s
        self.ir_measurements = [0]*len(self.ir_points)

        # timing variables
        self.fps = 60
        self.dt = 1 / self.fps

        # ROS topics
        self.ros = ros_instance
        self.cmd_vel_topic = Topic(ros_instance, f'/{name}/cmd_vel', 'geometry_msgs/Twist')
        self.odom_topic = Topic(ros_instance, f'/{name}/odom', 'nav_msgs/Odometry')
        self.imu_topic = Topic(ros_instance, f'/{name}/imu', 'sensor_msgs/Imu')
        self.ir_topic = Topic(ros_instance, f'/{name}/ir_intensity', 'irobot_create_msgs/IrIntensityVector')


    def update(self):
        # Update velocities from cmd_vel topic

        if self.cmd_vel_topic.msg:
            self.v = self.cmd_vel_topic.msg['linear']['x']
            self.theta_dot = self.cmd_vel_topic.msg['angular']['z']

        # Calculate new position in METERS with TIME_STEP
        new_x = self.x + self.v * cos(self.theta) * self.dt 
        new_y = self.y + self.v * sin(self.theta) * self.dt
        self.theta = self.theta + self.theta_dot * self.dt # robot always rotates

        if not self.check_collision(new_x, new_y):
            # no collision!
            self.collision = False
            self.x, self.y = new_x, new_y
        else:
            self.collision = True

        # generate IR measurements
        self.ir_measurements = self.measure_IR(self.x, self.y)
        self.rect.center = self.get_pixel_position()
        self.image = pygame.transform.rotate(self.og_image, degrees(self.theta))
        self.rect = self.image.get_rect(center=self.rect.center)

        # Publish sensor messages
        self.publish_odom()
        self.publish_imu()
        self.publish_ir()
    
    def check_collision(self,x_m, y_m):
        x, y = self.get_pixel_position(x_m, y_m) # convert meters to pixels
        
        # look at pixels around the robot radius and check if any of them are walls
        for point in self.radius_points:
            if self.check_wall((x + point[0], y + point[1])):
                return True
        return False

    def get_pixel_position(self, x = None, y = None):
        # if no x, y given, use current self.x, self.y
        if None in (x, y):
            x, y = self.x, self.y
        # take an x,y position in meters and set the pixel position
        pixel_center = self.screen.get_rect().center
        return (x * self.pixel_per_meter + pixel_center[0], pixel_center[1] - y * self.pixel_per_meter)

    def check_wall(self, point):
        #checks pixel value at point and returns True if it is a wall
        point = (int(point[0]), int(point[1]))
        rgb_val = self.ros.background.get_at(point)
        return rgb_val[0] < 200  # Check for a "wall"

    def measure_IR(self,x_m,y_m):
        """Simulates LiDAR and returns range measurements."""
        # cx, cy is the FRONT of the robot
        px, py = self.get_pixel_position() # current position in pixels

        # get front of robot in pixels
        fpx = self.radius * cos(self.theta) + px
        fpy = self.radius * sin(self.theta) + py

        ranges = []

        for angle in self.ir_points:
            ray_dx = cos(self.theta + radians(angle))
            ray_dy = sin(self.theta + radians(angle))
            distance = 0

            while distance < self.IR_RANGE*self.pixel_per_meter:
                distance += 1 # in pixels (resolution distance)
                x = int(fpx + ray_dx * distance) # pixel x
                y = int(fpy + ray_dy * distance) # pixel y

                # Check if the ray collides with a wall or obstacle
                if self.check_wall((x,y)):
                    break
    
            # Store the distance ( for that angle)
            ranges.append(distance)
            # Draw the ray
            endpoint = (fpx + ray_dx * distance, fpy + ray_dy * distance)
            pygame.draw.line(self.screen, (0, 255, 0), (fpx, fpy), endpoint, 1)

            # TODO: add scaling to range to represent real IR numbers
        print(f"IR measurements: {ranges}")
        return ranges

    def publish_odom(self):
        msg = {
                'pose': {
                    'position': {'x': self.x, 'y': self.y, 'z': 0},
                    'orientation': {'x': 0, 'y': 0, 'z': sin(self.theta/2), 'w': cos(self.theta/2)}
                },
                'twist': {
                    'linear': {'x': self.v, 'y': 0, 'z': 0},
                    'angular': {'x': 0, 'y': 0, 'z': self.theta_dot}
                }
            }
        
        self.publish_message('odom', msg)
    
    def publish_imu(self):
        msg = {
                'orientation': {'x': 0, 'y': 0, 'z': sin(self.theta/2), 'w': cos(self.theta/2)
                },
                'angular_velocity': {'x': 0, 'y': 0, 'z': self.theta_dot
                },
                'linear_acceleration': {'x': 0, 'y': 0, 'z': 0
                },
            }
        self.publish_message('imu', msg)

    def publish_ir(self):
        msg = {
                'readings': {'val1': self.ir_measurements[0],'val2': self.ir_measurements[1],'val3': self.ir_measurements[2],'val4': self.ir_measurements[3],'val5': self.ir_measurements[4],'val6': self.ir_measurements[5],'val7': self.ir_measurements[6] 
                }
            }
        self.publish_message('ir_intensity', msg)
        
    def publish_message(self, topic_name, message):
        #print(topic_name, message)
        if self.ros.broadcast_payload:
            self.ros.broadcast_payload({
                    'op': 'publish',
                    'topic': f'/{self.ros.robot_name}/{topic_name}',
                    'msg': message
                })
        else:
            print('No websocket connection to broadcast message', end='\r')


class Topic:
    def __new__(cls, ros_instance, topic_name, message_type):
        # check if the topic already exists and return it!
        if topic_name in ros_instance.topic_dict:
            return ros_instance.topic_dict[topic_name]
        else:
            # otherwise create a new topic
            return super(Topic, cls).__new__(cls)


    def __init__(self, ros_instance, topic_name, message_type):
        self.ros = ros_instance
        self.topic_name = topic_name
        self.message_type = message_type
        # add the topic to the ros instance
        self.ros.add_topic(self)
        self.callbacks = []
        self.msg = None

    def publish(self, message):
        self.msg = message

    def subscribe(self, callback):
        # add the callback to the topic
        self.callbacks.append(callback)

class WebSocketProtocol(WebSocketServerProtocol):
    def __init__(self, ros_instance):
        super().__init__()
        self.ros = ros_instance

        self.robot_name = ros_instance.robot_name

        # create topic for /juliet/cmd_vel
        self.cmd_vel_topic = Topic(ros_instance, f'/{self.robot_name}/cmd_vel', 'geometry_msgs/Twist')

        # create a callback for sending messages to the network
        self.ros.broadcast_payload = lambda payload: self.broadcast_message(payload)

    
    # if we get a connection, set the ros instance to connected
    def onConnect(self, request):
        self.ros.is_connected = True
        print(f'Connected to {request.peer}')

    def broadcast_message(self, payload):
        try:
            self.sendMessage(json.dumps(payload).encode('utf8'))
        except:
            self.ros.is_connected = False
            print('No Websocket Connection!' , end='\r')        

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                message = json.loads(payload.decode('utf8'))
                if 'msg' in message:
                    self.cmd_vel_topic.publish(message.get('msg'))
            except:
                print("Invalid JSON received")

class RosSimulator:
    def __init__(self, robot_name, host = None, port = None):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 1000))
        self.clock = pygame.time.Clock()
        self.running = True
        self.robots = pygame.sprite.Group()
        self.is_connected = False
        self.topic_dict ={}  # dictionary with topic name as key and topic object as value
        self.colors = [
            (13, 27,42),
            (27, 38, 59),
            (65, 90, 119),
            (119, 141, 169),
            (224, 225, 221)
        ]
        self.background = self.create_background()
        # set caption
        pygame.display.set_caption('Create3 Robot Simulation')

        self.is_connected = True
        # main player robot
        self.robot_name = robot_name
        self.main_robot = Create3(self.screen, self, robot_name)
        self.robots.add(self.main_robot)

        self.broadcast_payload = None # callback to send messages to the network

    def add_topic(self, topic):
        self.topic_dict[topic.topic_name] = topic
     

    def create_background(self):
        W = self.screen.get_width()
        H = self.screen.get_height()
        offset = 300
        wall_width = 40
        floor_color = self.colors[4]
        wall_color = self.colors[2]
        # returns background that is size of screen
        background = pygame.Surface(self.screen.get_size())
        background.fill(floor_color)
        
        # now make inside offset grey
        wall_rect = background.get_rect().inflate(-offset, -offset)
        background.fill(wall_color, wall_rect)

        yard_rect = wall_rect.inflate(-wall_width, -wall_width) 
        background.fill(floor_color, yard_rect)

        # put an opening on top/bottom wall
        door_width = 200
        doors_rect = pygame.rect.Rect(0,0, door_width, H)
        doors_rect.center = background.get_rect().center
        background.fill(floor_color, doors_rect)


        return background

    def run_once(self):
        # Non-blocking loop to run game continuously!
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('Exiting...')
                self.running = False

        # Draw background
        self.screen.blit(self.background, (0, 0))

        # Update all robots
        self.robots.update()
        self.robots.draw(self.screen)

        # put fps in top left corner
        fps = self.clock.get_fps()
        font = pygame.font.Font(None, 24)
        text = font.render(f'FPS: {fps:.2f}', True, self.colors[1])
        self.screen.blit(text, (10, 10))

        # if 'p' pressed, take a screenshot
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            pygame.image.save(self.screen, f'assets/screenshots/{random.randint(0, 1000)}.png')
            # sleep for 1 second to prevent multiple screenshots
            pygame.time.wait(1000)

        
        self.clock.tick(60)
        pygame.display.flip()
    
    def run_with_exit(self, reactor):
        if self.running:
            self.run_once()
        else: 
            pygame.quit()
            reactor.stop()


def main():

    ip = '0.0.0.0'
    port = 9012
    robot_name = 'juliet'


    ros = RosSimulator(robot_name)

    # Set up WebSocket server
    factory = WebSocketServerFactory(f"ws://{ip}:{port}")
    factory.protocol = lambda: WebSocketProtocol(ros)
    reactor.listenTCP(port, factory)

    # Integrate Pygame loop with Twisted reactor
    pygame_task = task.LoopingCall(ros.run_with_exit, reactor)
    pygame_task.start(1/61)

    print(f"Simulated Robot: {robot_name} on ws://{ip}:{port}")
    reactor.run()



if __name__ == "__main__":
    main()
