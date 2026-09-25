if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import random

import pygame

from pygame.math import Vector2

import customization

from .enemy_projectile import EnemyProjectile


# enemigos especiales del nivel 2 / 3
class EnemyLevel2(pygame.sprite.Sprite):
    def __init__(self, screen, tipo):

        super().__init__()


        self.tipo = tipo

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()


        if tipo == "normal":

            imagen = pygame.image.load(
                customization.obtener_asset("bug")
            ).convert_alpha()

            tamaño = (64, 64)

            self.speed = random.randint(3, 5)

            self.vidas = 1


        elif tipo == "S":

            imagen = pygame.image.load(
                "assets/bug_S.png"
            ).convert_alpha()

            tamaño = (48, 48)

            self.speed = 8

            self.vidas = 1


        elif tipo == "G":

            imagen = pygame.image.load(
                "assets/bug_G.png"
            ).convert_alpha()

            tamaño = (90, 90)

            self.speed = 2

            self.vidas = 5


        elif tipo == "M":

            imagen = pygame.image.load(
                "assets/bug_M.png"
            ).convert_alpha()

            tamaño = (70, 70)

            self.speed = 3

            self.vidas = 1


        elif tipo == "D":

            imagen = pygame.image.load(
                "assets/bug_D.png"
            ).convert_alpha()

            tamaño = (75, 75)

            self.speed = 4

            self.vidas = 1


        self.image = pygame.transform.scale(
            imagen,
            tamaño
        )


        # D queda adentro del mapa pq rebota
        if tipo == "D":

            self.rect = self.image.get_rect(
                center=(
                    self.screen_width - 100,
                    random.randint(
                        80,
                        self.screen_height - 80
                    )
                )
            )


            self.velocidad_D = Vector2(
                self.speed,
                0
            ).rotate(
                random.randint(0, 359)
            )


            self.ultimo_cambio_direccion = pygame.time.get_ticks()


        else:

            self.rect = self.image.get_rect(
                center=(
                    self.screen_width + 100,
                    random.randint(
                        self.image.get_height() // 2,
                        self.screen_height - self.image.get_height() // 2
                    )
                )
            )


        self.ultimo_disparo = pygame.time.get_ticks()


        if tipo == "M":

            self.cooldown_disparo = 1800


        elif tipo == "D":

            self.cooldown_disparo = 1300


    def update(self, player_pos, proyectiles):

        ahora = pygame.time.get_ticks()


        # dragon D movimiento medio random
        if self.tipo == "D":

            if ahora - self.ultimo_cambio_direccion >= 900:

                self.velocidad_D = self.velocidad_D.rotate(
                    random.randint(-35, 35)
                )

                self.ultimo_cambio_direccion = ahora


            self.rect.x += int(self.velocidad_D.x)

            self.rect.y += int(self.velocidad_D.y)


            if (
                self.rect.left <= 0
                or self.rect.right >= self.screen_width
            ):

                self.velocidad_D.x *= -1


                self.rect.left = max(
                    self.rect.left,
                    0
                )

                self.rect.right = min(
                    self.rect.right,
                    self.screen_width
                )


            if (
                self.rect.top <= 0
                or self.rect.bottom >= self.screen_height
            ):

                self.velocidad_D.y *= -1


                self.rect.top = max(
                    self.rect.top,
                    0
                )

                self.rect.bottom = min(
                    self.rect.bottom,
                    self.screen_height
                )


        else:

            self.rect.move_ip(
                -self.speed,
                0
            )


            if self.rect.right < 0:

                self.kill()


        # M y D disparan
        if self.tipo == "M" or self.tipo == "D":

            if ahora - self.ultimo_disparo >= self.cooldown_disparo:

                proyectil = EnemyProjectile(
                    self.rect.center,
                    player_pos,
                    self.tipo,
                    pygame.display.get_surface()
                )

                proyectiles.add(
                    proyectil
                )

                self.ultimo_disparo = ahora


    # ahora acepta el daño que tenga la flecha
    def recibir_dano(self, cantidad=1):

        self.vidas -= cantidad


        if self.vidas <= 0:

            self.kill()

            return True


        return False