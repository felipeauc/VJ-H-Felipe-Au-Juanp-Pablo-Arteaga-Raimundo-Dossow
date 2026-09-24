if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import random

import pygame


#---- FEATURE PROGRESION DE NIVELES - ENEMIGOS NIVEL 2 ----
class EnemyLevel2(pygame.sprite.Sprite):
    def __init__(self, screen, imagen):

        super().__init__()

        enemy_png = pygame.image.load(imagen).convert_alpha()
        self.image = pygame.transform.scale(enemy_png, (70, 70))

        self.rect = self.image.get_rect(
            center=(
                screen.get_width() + 100,
                random.randint(40, screen.get_height() - 40),
            )
        )

        self.speed = random.randint(4, 6)

    def update(self):

        self.rect.move_ip(-self.speed, 0)

        if self.rect.right < 0:
            self.kill()
#----