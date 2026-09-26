if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import random
import pygame
from pygame.math import Vector2

import customization
import robo_vida

from .enemy_projectile import EnemyProjectile


_cache_enemigos = {}


def cargar_imagen(archivo, tamano):
    clave = (archivo, tamano)

    if clave not in _cache_enemigos:
        imagen = pygame.image.load(archivo).convert_alpha()
        _cache_enemigos[clave] = pygame.transform.scale(imagen, tamano)

    return _cache_enemigos[clave]


class EnemyLevel2(pygame.sprite.Sprite):
    def __init__(self, screen, tipo):
        super().__init__()

        self.tipo = tipo
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        if tipo == "normal":
            archivo = customization.obtener_asset("bug")
            tamano = (64, 64)
            self.speed = random.randint(3, 5)
            self.vidas = 1

        elif tipo == "S":
            archivo = "assets/bug_S.png"
            tamano = (48, 48)
            self.speed = 8
            self.vidas = 1

        elif tipo == "G":
            archivo = "assets/bug_G.png"
            tamano = (90, 90)
            self.speed = 2
            self.vidas = 5

        elif tipo == "M":
            archivo = "assets/bug_M.png"
            tamano = (70, 70)
            self.speed = 3
            self.vidas = 1

        else:
            archivo = "assets/bug_D.png"
            tamano = (75, 75)
            self.speed = 4
            self.vidas = 1

        self.image = cargar_imagen(archivo, tamano)

        if tipo == "D":
            self.rect = self.image.get_rect(center=(self.screen_width - 100, random.randint(80, self.screen_height - 80)))
            self.velocidad_D = Vector2(self.speed, 0).rotate(random.randint(0, 359))
            self.ultimo_cambio_direccion = pygame.time.get_ticks()

        else:
            self.rect = self.image.get_rect(center=(self.screen_width + 100, random.randint(self.image.get_height() // 2, self.screen_height - self.image.get_height() // 2)))

        self.ultimo_disparo = pygame.time.get_ticks()

        if tipo == "M":
            self.cooldown_disparo = 1800

        elif tipo == "D":
            self.cooldown_disparo = 1300


    def update(self, player_pos, proyectiles):
        ahora = pygame.time.get_ticks()

        if self.tipo == "D":
            if ahora - self.ultimo_cambio_direccion >= 900:
                self.velocidad_D = self.velocidad_D.rotate(random.randint(-35, 35))
                self.ultimo_cambio_direccion = ahora

            self.rect.x += int(self.velocidad_D.x)
            self.rect.y += int(self.velocidad_D.y)

            if self.rect.left <= 0 or self.rect.right >= self.screen_width:
                self.velocidad_D.x *= -1
                self.rect.left = max(self.rect.left, 0)
                self.rect.right = min(self.rect.right, self.screen_width)

            if self.rect.top <= 0 or self.rect.bottom >= self.screen_height:
                self.velocidad_D.y *= -1
                self.rect.top = max(self.rect.top, 0)
                self.rect.bottom = min(self.rect.bottom, self.screen_height)

        else:
            self.rect.move_ip(-self.speed, 0)

            if self.rect.right < 0:
                self.kill()

        if self.tipo in ("M", "D") and ahora - self.ultimo_disparo >= self.cooldown_disparo:
            proyectil = EnemyProjectile(self.rect.center, player_pos, self.tipo, pygame.display.get_surface())
            proyectiles.add(proyectil)

            self.ultimo_disparo = ahora


    def recibir_dano(self, cantidad=1):
        self.vidas -= cantidad

        if self.vidas <= 0:
            self.vidas = 0

            robo_vida.registrar_muerte()

            self.kill()

            return True

        return False