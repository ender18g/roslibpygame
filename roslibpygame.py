# This is the main class for the ROSlibPygame library
import pygame
from create3 import Create3
import threading
import random

from topic import Topic

class Ros:
    def __init__(self, host = None, port = None):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 1000))
        self.clock = pygame.time.Clock()
        self.running = True
        self.robots = pygame.sprite.Group()
        self.is_connected = False
        self.topic_dict ={}  # dictionary with topic name as key and topic object as value
        self.connect(host, port)
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

    def connect(self, host, port):
        if not ( host and port ):
            print("Please provide host and port")
            return
        else:
            print(f"**Connecting to {host}:{port}**")

        # 'Connect' to roslibpy bridge / Create a Robot
        self.is_connected = True
        # main player robot
        self.main_robot = Create3(self.screen, self)
        self.robots.add(self.main_robot)

    def broadcast(self, topic_name, message):
        for topic in self.topics:
            if topic.topic_name == topic_name:
                topic.publish(message)

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


    

    def run_forever(self):
        # Non-blocking loop to run game continuously!
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Draw all robots
            self.screen.blit(self.create_background(), (0, 0))


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

        pygame.quit()



if __name__ == '__main__':
    # this shows how students should use the library
    # create a connection to the robot
    ros = Ros(host = '10.24.5.112', port = 9012)

    if ros.is_connected:
        print("**Connected to Create3 Robot**")

    # make cmd_vel topic
    robot_name = 'juliet'
    cmd_vel_topic = Topic(ros, f'{robot_name}/cmd_vel', 'geometry_msgs/Twist')

    # make odom topic
    odom_topic = Topic(ros, f'{robot_name}/odom', 'nav_msgs/Odometry')

    def odom_callback(msg):
        print(f'Odometry message received: {msg}')

    # make a subscriber
    odom_topic.subscribe(lambda msg: odom_callback(msg))

    # publish a message to the topic
    cmd_vel_topic.publish({'linear': {'x': 0.1}, 'angular': {'z': 0.00}})

    # start the main loop - run_forever is blocking
    ros.run_forever()