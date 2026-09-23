import pygame


class Crosshair(pygame.sprite.Sprite):
    def __init__(self):

        super().__init__()

        self.image = pygame.image.load("assets/mira_vj2.png").convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (50, 50)
        )

        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()