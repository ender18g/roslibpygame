import pygame
from math import cos, sin, degrees
import json
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor, task

from topic import Topic
from roslibpygame import Ros


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
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.v = 0
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
            #print(self.cmd_vel_topic.msg)
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
        #self.publish_odom()

    def check_wall(self, point):
        point = (int(point[0]), int(point[1]))
        rgb_val = self.ros.background.get_at(point)
        return rgb_val[0] < 200  # Check for a "wall"

    def publish_odom(self):
        self.odom_topic.publish({
            'pose': {
                'position': {'x': self.x, 'y': self.y, 'z': 0},
                'orientation': {'x': 0, 'y': 0, 'z': sin(self.theta/2), 'w': cos(self.theta/2)}
            },
            'twist': {
                'linear': {'x': self.v, 'y': 0, 'z': 0},
                'angular': {'x': 0, 'y': 0, 'z': self.theta_dot}
            }
        })


class WebSocketProtocol(WebSocketServerProtocol):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                message = json.loads(payload.decode('utf8'))
                if 'msg' in message:
                    twist = message['msg']
                    self.robot.cmd_vel_topic.publish(twist)
            except:
                print("Invalid JSON received")
                print(payload)

    def send_odometry_message(self):
        odometry_message = {
            "op": "publish",
            "topic": "/juliet/odom",
            "msg": {
                "pose": {
                    "position": {"x": self.robot.x, "y": self.robot.y, "z": 0.0},
                    "orientation": {"x": 0.0, "y": 0.0, "z": sin(self.robot.theta/2), "w": cos(self.robot.theta/2)}
                },
                "twist": {
                    "linear": {"x": self.robot.v, "y": 0.0, "z": 0.0},
                    "angular": {"x": 0.0, "y": 0.0, "z": self.robot.theta_dot}
                }
            }
        }
        self.sendMessage(json.dumps(odometry_message).encode('utf8'))


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    ros_instance = Ros(host = '127.0.0.1', port = 9090)  # Initialize your ROS instance here
    robot = Create3(screen, ros_instance)

    # Set up WebSocket server
    factory = WebSocketServerFactory("ws://0.0.0.0:9090")
    factory.protocol = lambda: WebSocketProtocol(robot)
    reactor.listenTCP(9090, factory)

    # Integrate Pygame loop with Twisted reactor
    pygame_task = task.LoopingCall(lambda: pygame_event_loop(screen, robot, clock))
    pygame_task.start(1 / 60.0)

    print("WebSocket server running on ws://0.0.0.0:9090")
    reactor.run()


def pygame_event_loop(screen, robot, clock):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            reactor.stop()

    robot.update()
    screen.fill((255, 255, 255))  # Clear the screen
    screen.blit(robot.image, robot.rect.topleft)

    # put fps in top left corner
    fps = clock.get_fps()
    font = pygame.font.Font(None, 24)
    text = font.render(f'FPS: {fps:.2f}', True, (0, 0, 0))
    screen.blit(text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)


if __name__ == "__main__":
    main()
