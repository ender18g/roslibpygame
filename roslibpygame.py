# This is the main class for the ROSlibPygame library
import pygame
from create3 import Create3

class ROSlibPygame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.running = True
        self.robots = pygame.sprite.Group()

    def add_robot(self):
        # add robot to the robot group
        self.robots.add(Create3(self.screen))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update all robots
            self.robots.update()

            # draw all robots
            self.screen.fill((0, 0, 0))
            self.robots.draw(self.screen)

            # update the display
            self.clock.tick(60)
            pygame.display.flip()

        pygame.quit()

if __name__ == '__main__':
    sim = ROSlibPygame()

    # create a robot
    sim.add_robot()

    sim.run()