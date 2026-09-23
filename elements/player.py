if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import math

import pygame
from pygame.locals import K_a, K_d, K_s, K_w
from pygame.math import Vector2

from elements import Bullet

JorgePNG = pygame.image.load("assets/jorge.png")
JorgePNG_scaled = pygame.transform.scale(JorgePNG, (80, 80))


class Player(pygame.sprite.Sprite):
    def __init__(self, screen):

        # ? super().__init__() inicializa la clase padre (Sprite)
        super().__init__()

        self.image = JorgePNG_scaled
        self.rect = self.image.get_rect()
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # TODO (2.4): Crear grupo de balas
        self.bullets = pygame.sprite.Group()

        # Sobrecalentamiento del arma
        self.disparos = 0
        self.max_disparos = 5
        self.sobrecalentado = False
        self.inicio_sobrecalentamiento = 0
        self.tiempo_sobrecalentamiento = 3000



    def update(self, pressed_keys):
        # ? Mover a Jorge
        if pressed_keys[K_w]:
            self.rect.move_ip(0, -4)
        if pressed_keys[K_s]:
            self.rect.move_ip(0, 4)
        if pressed_keys[K_a]:
            self.rect.move_ip(-4, 0)
        if pressed_keys[K_d]:
            self.rect.move_ip(4, 0)

        # ? Mantener a Jorge en Pantalla
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.screen_height)

        # TODO (2.4): Actualizar las balas
        self.bullets.update()

        if self.sobrecalentado:
            ahora = pygame.time.get_ticks()

            if ahora - self.inicio_sobrecalentamiento >= self.tiempo_sobrecalentamiento:
                self.sobrecalentado = False
                self.disparos = 0

    def shoot(self, mouse_pos):

        if self.sobrecalentado:
            return


        # TODO (2.4): Calcular direccion de la bala
        distance =  Vector2(mouse_pos) - Vector2(self.rect.center)
        direction = distance.normalize()

        # TODO (2.4): Crear bala y agregarla al grupo de balas
        bullet = Bullet ( 
            self.rect.center,
            direction,
            self.screen_width,
            self.screen_height,
            )
        self.bullets.add(bullet)
        self.disparos += 1
        if self.disparos >= self.max_disparos:
            self.sobrecalentado = True
            self.inicio_sobrecalentamiento = pygame.time.get_ticks()

        pass
