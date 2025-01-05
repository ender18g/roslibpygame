# this is the robot create3 sprite
import pygame
from math import cos, sin, degrees

from topic import Topic

class Create3(pygame.sprite.Sprite):
    def __init__(self, screen, ros_instance, name='juliet'):
        pygame.sprite.Sprite.__init__(self)
        print(f'Creating robot {name}')
        self.image = pygame.image.load('./assets/images/create3.png')
        self.image = self.image.convert_alpha()

        # rotate the image
        self.image = pygame.transform.rotate(self.image, -90)
        # zoom out the image
        self.image = pygame.transform.smoothscale_by(self.image, 0.2)
        
        #self.make_image()

        self.og_image = self.image
        self.rect = self.image.get_rect()
        self.robot_width = self.rect.width

        self.rect.center = screen.get_rect().center
        self.screen = screen
        self.theta = 0 # angle in radians
        self.theta_dot = 0 # angular velocity in rad/s
        self.x = screen.get_rect().centerx # x position in meters
        self.y = screen.get_rect().centery
        self.v = 0 # linear velocity in m/s
        self.ros = ros_instance
        self.velocity_multiplier = 5
        # make topics needed
        self.cmd_vel_topic = Topic(ros_instance, f'{name}/cmd_vel', 'geometry_msgs/Twist')
        self.odom_topic = Topic(ros_instance, f'{name}/odom', 'nav_msgs/Odometry')

    def make_image(self):
        # Draw the robot with a large circle
        w = 1000
        h = 1000
        
        # Create a transparent surface
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # draw wheelbase
        wheel_width = 200
        pygame.draw.rect(self.image, (0, 0, 0), (0, h // 2 - wheel_width // 2, w, wheel_width))
        # Draw circles with anti-aliasing in mind
        pygame.draw.circle(self.image, (0, 0, 0), (w // 2, h // 2), w // 2)
        pygame.draw.circle(self.image, (200, 200, 200), (w // 2, h // 2), w // 2 - 40)

        # put white oval at the top
        pygame.draw.ellipse(self.image, (255, 255, 255), (w // 2 - 100, h // 2 - 300, 200, 80))

        self.image = pygame.transform.rotate(self.image, -90)
        # Reduce the size of the image with smooth scaling
        scale = 0.1
        scaled_size = (int(w * scale), int(h * scale))
        self.image = pygame.transform.smoothscale(self.image, scaled_size)

    def check_wall(self,point):
        # checks to see if point has r value less than 200, if so, return True
        point = (int(point[0]), int(point[1]))

        # point is an xy pixel coordinate
        rgb_val = self.ros.background.get_at(point)

        if rgb_val[0] < 200:
            return True
        
        return False


    def update(self):
        # check for \cmd_vel topic
        if self.cmd_vel_topic.msg:
            # update the velocity and angular velocity
            self.v = self.cmd_vel_topic.msg['linear']['x']
            self.theta_dot = self.cmd_vel_topic.msg['angular']['z']

        # move the robot
        new_x = self.x + self.v * cos(self.theta) * self.velocity_multiplier
        new_y = self.y - self.v * sin(self.theta) * self.velocity_multiplier
        new_theta = self.theta + self.theta_dot

        # check for collision
        # get the four corners of the robot
        corners = [
            (new_x - self.robot_width//2, new_y - self.robot_width//2),
            (new_x + self.robot_width//2, new_y - self.robot_width//2),
            (new_x + self.robot_width//2, new_y + self.robot_width//2),
            (new_x - self.robot_width//2, new_y + self.robot_width//2)
        ]

        # check if any of the corners are in a wall
        corner_bools = [self.check_wall(corner) for corner in corners]
        if any(corner_bools):
            # if there is a collision, don't move
            return
        
        # update the position and angle
        self.x = new_x
        self.y = new_y
        self.theta = new_theta
        

        # update the rect
        self.rect.center = (self.x, self.y)

        # move and rotate the robot about its center
        self.image = pygame.transform.rotate(self.og_image, degrees(self.theta))
        self.rect = self.image.get_rect(center=self.rect.center)

        # publish the odometry topic
        self.publish_odom()

    def publish_odom(self):
        self.odom_topic.publish({
            'pose': {
                'position': {'x': self.x, 'y': self.y, 'z': 0},
                'orientation': {'x' : 0, 'y': 0, 'z': sin(self.theta/2), 'w': cos(self.theta/2)}
            },
            'twist': {
                'linear': {'x': self.v, 'y': 0, 'z': 0},
                'angular': {'x': 0, 'y': 0, 'z': self.theta_dot}
            }
        })