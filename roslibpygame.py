# This is the main class for the ROSlibPygame library
import pygame
from create3 import Create3
import threading

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
        offset = 100
        # returns background that is size of screen
        background = pygame.Surface(self.screen.get_size())
        # fill with white
        background.fill((255, 255, 255))
        gray_tile = pygame.Surface((20, 20))
        gray_tile.fill((100, 100, 100))
        # draw gray tiles at
        for x in range(0, self.screen.get_width(), 20):
            for y in range(0, self.screen.get_height(), 20):
                if x == offset or y == offset or x == W - offset or y == H - offset:
                    background.blit(gray_tile, (x, y))
        
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
            text = font.render(f'FPS: {fps:.2f}', True, (0, 0, 0))
            self.screen.blit(text, (0, 0))

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

    # make a subscriber
    #odom_topic.subscribe(lambda msg: print(f'Odometry message received: {msg}'))

    # publish a message to the topic
    cmd_vel_topic.publish({'linear': {'x': 0.1}, 'angular': {'z': 0.01}})

    # start the main loop - run_forever is blocking
    ros.run_forever()