# this is the robot create3 sprite
import pygame

class Create3(pygame.sprite.Sprite):
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('./assets/images/create3.png')
        # zoom out the image
        self.image = pygame.transform.rotozoom(self.image, 0, 0.2)
        self.rect = self.image.get_rect()
        self.rect.center = screen.get_rect().center
        self.screen = screen
        self.theta = 0 # angle in degrees
        self.v = 0 # velocity in m/s

    def update(self):
        pass

