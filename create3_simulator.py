import pygame
from math import cos, sin, degrees
import json
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor, task

import random


class Create3(pygame.sprite.Sprite):
    def __init__(self, screen, ros_instance, name='juliet'):
        super().__init__()
        print(f'Creating robot {name}')
        
        self.image = pygame.image.load('./assets/images/create3.png').convert_alpha()
        self.image = pygame.transform.rotate(self.image, -90)
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() // 5, self.image.get_height() // 5))

        self.og_image = self.image
        self.rect = self.image.get_rect(center=screen.get_rect().center)
        self.robot_width = self.rect.width
        self.screen = screen

        # Robot state
        self.theta = 0
        self.theta_dot = 0
        self.x = self.rect.centerx # this should be in meters
        self.y = self.rect.centery # this should be in meters
        self.v = 0                 # linear velocity in m/s 
        self.pixel_per_meter = 200

        # timing variables
        self.fps = 60
        self.dt = 1 / self.fps

        # ROS topics
        self.ros = ros_instance
        self.cmd_vel_topic = Topic(ros_instance, f'{name}/cmd_vel', 'geometry_msgs/Twist')
        self.odom_topic = Topic(ros_instance, f'{name}/odom', 'nav_msgs/Odometry')


    def update(self):
        # Update velocities from cmd_vel topic

        if self.cmd_vel_topic.msg:
            self.v = self.cmd_vel_topic.msg['linear']['x']
            self.theta_dot = self.cmd_vel_topic.msg['angular']['z']

        # Calculate new position with TIME_STEP
        new_x = self.x + self.v * cos(self.theta) * self.dt  * self.pixel_per_meter
        new_y = self.y - self.v * sin(self.theta) * self.dt * self.pixel_per_meter
        new_theta = self.theta + self.theta_dot * self.dt

        # Check for collisions
        if self.check_wall((new_x, new_y)):
            return

        # Update robot state
        self.x, self.y, self.theta = new_x, new_y, new_theta
        self.rect.center = (self.x, self.y)
        self.image = pygame.transform.rotate(self.og_image, degrees(self.theta))
        self.rect = self.image.get_rect(center=self.rect.center)

        # Publish odometry
        self.publish_odom()

    def check_wall(self, point):
        point = (int(point[0]), int(point[1]))
        rgb_val = self.ros.background.get_at(point)
        return rgb_val[0] < 200  # Check for a "wall"

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
        
        if self.ros.broadcast_payload:
            self.ros.broadcast_payload({
                    'op': 'publish',
                    'topic': f'{self.ros.robot_name}/odom',
                    'msg': msg
                })
        else:
            print('No broadcast payload callback set!')
        
       


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
        self.cmd_vel_topic = Topic(ros_instance, f'{self.robot_name}/cmd_vel', 'geometry_msgs/Twist')

        # create a callback for sending messages to the network
        self.ros.broadcast_payload = lambda payload: self.sendMessage(json.dumps(payload).encode('utf8'))
        

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
