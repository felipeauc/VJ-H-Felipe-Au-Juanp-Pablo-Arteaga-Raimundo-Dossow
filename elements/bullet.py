if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.math import Vector2

import customization
import habilidades


_cache_balas = {}


def cargar_bala(archivo):
    if archivo not in _cache_balas:
        imagen = pygame.image.load(archivo).convert_alpha()
        _cache_balas[archivo] = pygame.transform.scale(imagen, (26, 14))

    return _cache_balas[archivo]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, direction, screen_width, screen_height, rapid_fire=False):
        super().__init__()

        if rapid_fire:
            archivo = "assets/bullet_rapid_fire.png"
        else:
            archivo = customization.obtener_asset("bullet")

        imagen_base = cargar_bala(archivo)

        self.speed = 20
        self.direction = Vector2(direction)
        self.screen_width = screen_width
        self.screen_height = screen_height

        # mejoras permanentes
        self.dano = habilidades.dano()
        self.penetracion_restante = habilidades.penetracion()

        # evita golpear dos veces al mismo enemigo
        self.enemigos_golpeados = set()

        angle = self.direction.angle_to(Vector2(1, 0))

        self.image = pygame.transform.rotate(imagen_base, angle)
        self.rect = self.image.get_rect(center=start_pos)

        self.posicion = Vector2(start_pos)


    def update(self):
        self.posicion += self.direction * self.speed
        self.rect.center = (round(self.posicion.x), round(self.posicion.y))

        if self.rect.right < 0 or self.rect.left > self.screen_width or self.rect.bottom < 0 or self.rect.top > self.screen_height:
            super().kill()


    # cada impacto consume una penetracion
    def kill(self):
        if self.penetracion_restante > 1:
            self.penetracion_restante -= 1
        else:
            self.penetracion_restante = 0
            super().kill()