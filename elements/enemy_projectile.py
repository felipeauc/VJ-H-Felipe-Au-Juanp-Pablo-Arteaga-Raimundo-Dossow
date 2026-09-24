if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.math import Vector2


#---- FEATURE NUEVOS ENEMIGOS - PROYECTILES ENEMIGOS ----
class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, tipo, screen):

        super().__init__()

        self.tipo = tipo

        imagen = pygame.image.load(f"assets/proyectil_{tipo}.png").convert_alpha()

        if tipo == "M":
            self.image = pygame.transform.scale(imagen, (35, 35))
            self.speed = 5

        else:
            self.image = pygame.transform.scale(imagen, (42, 42))
            self.speed = 6

        self.rect = self.image.get_rect(center=start_pos)

        distancia = Vector2(target_pos) - Vector2(start_pos)

        if distancia.length() == 0:
            self.direction = Vector2(-1, 0)

        else:
            self.direction = distancia.normalize()

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

    def update(self):

        self.rect.move_ip(
            self.direction.x * self.speed,
            self.direction.y * self.speed
        )

        if (
            self.rect.right < 0
            or self.rect.left > self.screen_width
            or self.rect.bottom < 0
            or self.rect.top > self.screen_height
        ):
            self.kill()
#----