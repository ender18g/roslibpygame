# This is the main class for the ROSlibPygame library
import pygame
from create3 import Create3
import threading

from topic import Topic

class Ros:
    def __init__(self, host = None, port = None):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.robots = pygame.sprite.Group()
        self.is_connected = False
        self.topic_dict ={}  # dictionary with topic name as key and topic object as value
        self.connect(host, port)

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

    def run_forever(self):
        # Non-blocking loop to run game continuously!
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update all robots
            self.robots.update()

            # Draw all robots
            self.screen.fill((255, 255, 255))
            self.robots.draw(self.screen)

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

    # publish a message to the topic
    cmd_vel_topic.publish({'linear': {'x': 0.1}, 'angular': {'z': 0.01}})

    # start the main loop - run_forever is blocking
    ros.run_forever()