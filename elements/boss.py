if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import os
import random

import pygame
from pygame.math import Vector2


#---- FEATURE BOSS FIGHT - PROYECTILES DEL BOSS ----
class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, posicion, direccion, screen):

        super().__init__()

        imagen = pygame.image.load("assets/proyectil_B.png").convert_alpha()
        self.image = pygame.transform.scale(imagen, (42, 42))

        self.rect = self.image.get_rect(center=posicion)

        self.direction = Vector2(direccion)

        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

        self.speed = 7
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

    def update(self):

        self.rect.x += int(self.direction.x * self.speed)
        self.rect.y += int(self.direction.y * self.speed)

        if self.rect.right < 0 or self.rect.left > self.screen_width or self.rect.bottom < 0 or self.rect.top > self.screen_height:
            self.kill()
#----


#---- FEATURE BOSS FIGHT - METEORITOS ----
class Meteorito(pygame.sprite.Sprite):
    def __init__(self, screen):

        super().__init__()

        if os.path.exists("assets/meteorito.png"):
            imagen = pygame.image.load("assets/meteorito.png").convert_alpha()

        else:
            imagen = pygame.image.load("assets/proyectil_B.png").convert_alpha()

        tamaño = random.randint(45, 70)

        self.image = pygame.transform.scale(imagen, (tamaño, tamaño))

        self.rect = self.image.get_rect(
            center=(
                random.randint(40, screen.get_width() - 40),
                -80
            )
        )

        self.speed_y = random.randint(8, 13)
        self.speed_x = random.randint(-2, 2)

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

    def update(self):

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top > self.screen_height:
            self.kill()
#----


#---- FEATURE BOSS FIGHT - JEFE FINAL ----
class Boss(pygame.sprite.Sprite):
    def __init__(self, screen):

        super().__init__()

        imagen = pygame.image.load("assets/boss.png").convert_alpha()

        self.image = pygame.transform.scale(imagen, (200, 200))

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.rect = self.image.get_rect(
            center=(self.screen_width - 140, self.screen_height // 2)
        )

        #---- FEATURE BOSS FIGHT - VIDA ----
        self.max_vidas = 300
        self.vidas = 300
        #----

        #---- FEATURE BOSS FIGHT - MOVIMIENTO ----
        self.velocidad_vertical = 3
        #----

        #---- FEATURE BOSS FIGHT - ATAQUES ----
        self.patron = 0

        self.ultimo_ataque = pygame.time.get_ticks()
        self.cooldown_ataque = 1900

        self.en_embestida = False

        self.direccion_embestida = Vector2(0, 0)
        self.velocidad_embestida = 15
        #----

        #---- FEATURE BOSS FIGHT - FASE METEORITOS ----
        self.fase_meteoritos = False
        self.fase_meteoritos_hecha = False

        self.inicio_fase_meteoritos = 0
        self.duracion_fase_meteoritos = 8000

        self.ultimo_meteorito = 0
        self.cooldown_meteorito = 350
        #----


    def update(self, objetivos, proyectiles, meteoritos):

        ahora = pygame.time.get_ticks()


        #---- FEATURE BOSS FIGHT - FASE METEORITOS ----
        if self.fase_meteoritos:

            if ahora - self.ultimo_meteorito >= self.cooldown_meteorito:

                meteorito = Meteorito(
                    pygame.display.get_surface()
                )

                meteoritos.add(meteorito)

                self.ultimo_meteorito = ahora


            if ahora - self.inicio_fase_meteoritos >= self.duracion_fase_meteoritos:

                self.terminar_fase_meteoritos()

            return
        #----


        #---- FEATURE BOSS FIGHT - EMBESTIDA ----
        if self.en_embestida:

            self.rect.x += int(
                self.direccion_embestida.x
                * self.velocidad_embestida
            )

            self.rect.y += int(
                self.direccion_embestida.y
                * self.velocidad_embestida
            )

            if (
                self.rect.right < -100
                or self.rect.left > self.screen_width + 100
                or self.rect.bottom < -100
                or self.rect.top > self.screen_height + 100
            ):

                self.terminar_embestida()

            return
        #----


        #---- FEATURE BOSS FIGHT - MOVIMIENTO NORMAL ----
        self.rect.y += self.velocidad_vertical

        if self.rect.top <= 70:

            self.rect.top = 70
            self.velocidad_vertical = abs(self.velocidad_vertical)

        if self.rect.bottom >= self.screen_height - 30:

            self.rect.bottom = self.screen_height - 30
            self.velocidad_vertical = -abs(self.velocidad_vertical)
        #----


        if len(objetivos) == 0:
            return


        if ahora - self.ultimo_ataque >= self.cooldown_ataque:

            self.ultimo_ataque = ahora

            self.patron += 1

            if self.patron > 3:
                self.patron = 1

            objetivo = random.choice(objetivos)


            #---- PATRON 1 - TRIPLE DISPARO ----
            if self.patron == 1:

                direccion = Vector2(objetivo) - Vector2(self.rect.center)

                if direccion.length() != 0:

                    direccion = direccion.normalize()

                    for angulo in [-15, 0, 15]:

                        proyectil = BossProjectile(
                            self.rect.center,
                            direccion.rotate(angulo),
                            pygame.display.get_surface()
                        )

                        proyectiles.add(proyectil)
            #----


            #---- PATRON 2 - CIRCULO DE PROYECTILES ----
            elif self.patron == 2:

                for angulo in range(0, 360, 30):

                    direccion = Vector2(1, 0).rotate(angulo)

                    proyectil = BossProjectile(
                        self.rect.center,
                        direccion,
                        pygame.display.get_surface()
                    )

                    proyectiles.add(proyectil)
            #----


            #---- PATRON 3 - EMBESTIDA ----
            elif self.patron == 3:

                direccion = Vector2(objetivo) - Vector2(self.rect.center)

                if direccion.length() != 0:

                    self.direccion_embestida = direccion.normalize()

                    self.en_embestida = True
            #----


    #---- FEATURE BOSS FIGHT - FASE METEORITOS ----
    def iniciar_fase_meteoritos(self):

        self.fase_meteoritos = True
        self.fase_meteoritos_hecha = True

        self.en_embestida = False

        self.inicio_fase_meteoritos = pygame.time.get_ticks()
        self.ultimo_meteorito = 0

        # Boss se va de la pantalla
        self.rect.center = (
            self.screen_width + 400,
            -300
        )


    def terminar_fase_meteoritos(self):

        self.fase_meteoritos = False

        self.rect.center = (
            self.screen_width - 140,
            self.screen_height // 2
        )

        self.ultimo_ataque = pygame.time.get_ticks()
    #----


    #---- FEATURE BOSS FIGHT - EMBESTIDA ----
    def terminar_embestida(self):

        self.en_embestida = False

        self.rect.center = (
            self.screen_width - 140,
            self.screen_height // 2
        )

        self.ultimo_ataque = pygame.time.get_ticks()
    #----


    #---- FEATURE BOSS FIGHT - RECIBIR DAÑO ----
    def recibir_dano(self, cantidad=1):

        if self.fase_meteoritos:
            return False

        self.vidas -= cantidad


        # Cuando llega a mitad de vida comienza la fase especial
        if self.vidas <= 150 and not self.fase_meteoritos_hecha:

            self.iniciar_fase_meteoritos()


        if self.vidas <= 0:

            self.vidas = 0

            self.kill()

            return True


        return False
    #----
#----