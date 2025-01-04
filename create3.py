# this is the robot create3 sprite
import pygame
from math import cos, sin, degrees

from topic import Topic

class Create3(pygame.sprite.Sprite):
    def __init__(self, screen, ros_instance, name='juliet'):
        pygame.sprite.Sprite.__init__(self)
        print(f'Creating robot {name}')
        self.image = pygame.image.load('./assets/images/create3.png')
        # zoom out the image
        self.image = pygame.transform.rotozoom(self.image, -90, 0.2)
        self.og_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = screen.get_rect().center
        self.screen = screen
        self.theta = 0 # angle in radians
        self.theta_dot = 0 # angular velocity in rad/s
        self.x = screen.get_rect().centerx # x position in meters
        self.y = screen.get_rect().centery
        self.v = 0 # linear velocity in m/s
        self.ros = ros_instance
        self.cmd_vel_topic = Topic(ros_instance, f'{name}/cmd_vel', 'geometry_msgs/Twist')
        self.velocity_multiplier = 5

    def update(self):
        # check for \cmd_vel topic
        if self.cmd_vel_topic.msg:
            # update the velocity and angular velocity
            self.v = self.cmd_vel_topic.msg['linear']['x']
            self.theta_dot = self.cmd_vel_topic.msg['angular']['z']

        # move the robot
        self.x += self.v * cos(self.theta) * self.velocity_multiplier
        self.y -= self.v * sin(self.theta) * self.velocity_multiplier
        self.theta += self.theta_dot

        # update the rect
        self.rect.center = (self.x, self.y)

        # move and rotate the robot about its center
        self.image = pygame.transform.rotate(self.og_image, degrees(self.theta))
        self.rect = self.image.get_rect(center=self.rect.center)

        # publish the odometry topic



